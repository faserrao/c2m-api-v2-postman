#!/usr/bin/env python3
"""
validate_catalog_against_spec.py — Validate curated-examples-catalog.yaml select: fields
against the OpenAPI spec and linked collection.

For each example in the catalog:
1. Checks that every select: key is a top-level field in the canonical request body
2. Checks that every select: key maps to a <oneOf> field (not a plain field)
3. Checks that every select: value is a valid discriminator key for that oneOf's variants

Note: jobTemplate values are NOT validated here — jobTemplate is defined as
type: string (no enum) in the spec because it is a customer-defined template name
passed verbatim to the C2M API. There is no spec enum to validate against.

Catalog paths (e.g. /static, /batch/split) match the OpenAPI spec paths directly.
The linked collection is used as the canonical source of field structure.

Usage:
    python scripts/validation/validate_catalog_against_spec.py
    python scripts/validation/validate_catalog_against_spec.py --catalog config/curated-examples-catalog.yaml
    python scripts/validation/validate_catalog_against_spec.py --exit-status
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

# Allow importing from scripts/utilities/
sys.path.insert(0, str(Path(__file__).parent.parent))
from utilities.oneof_resolver import find_variant_by_discriminator_key


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _default(env_var: str, fallback: str) -> str:
    return os.environ.get(env_var, fallback)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Linked collection helpers
# ---------------------------------------------------------------------------

def find_canonical_body(linked: dict, method: str, path: str) -> dict | None:
    """Return the parsed request body dict for method+path in the linked collection."""
    for item in linked.get('item', []):
        req = item.get('request', {})
        if req.get('method', '').upper() != method.upper():
            continue
        url = req.get('url', {})
        item_path = '/' + '/'.join(url.get('path', []))
        if item_path == path:
            raw = req.get('body', {}).get('raw', '')
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return None
    return None


def get_oneof_fields(body: dict) -> set[str]:
    """Return top-level field names whose placeholder value is '<oneOf>'."""
    return {k for k, v in body.items() if isinstance(v, str) and v == '<oneOf>'}


# ---------------------------------------------------------------------------
# Core validation
# ---------------------------------------------------------------------------

def validate(
    catalog_path: Path,
    spec_path: Path,
    linked_path: Path,
) -> tuple[int, int, int, int]:
    """
    Validate catalog select: blocks against spec + linked collection.

    Returns (pass_count, fail_count, warn_count, skip_count).
    """
    catalog = load_yaml(catalog_path)
    spec = load_yaml(spec_path)
    linked = load_json(linked_path)

    examples = catalog.get('examples', [])
    errors: list[str] = []
    warnings: list[str] = []
    pass_count = 0
    skip_count = 0

    for example in examples:
        name = example.get('name', '<unnamed>')
        method = example.get('method', 'POST')
        path = example.get('path', '')
        select = example.get('select', {})

        if not select:
            skip_count += 1
            continue

        body = find_canonical_body(linked, method, path)
        if body is None:
            warnings.append(
                f"[{name}] Cannot find canonical body for {method} {path} "
                f"— is the linked collection up to date?"
            )
            skip_count += 1
            continue

        oneof_fields = get_oneof_fields(body)
        example_ok = True

        for sel_key, sel_value in select.items():
            # Check 1: key must exist as a top-level field
            if sel_key not in body:
                errors.append(
                    f"[{name}] select: key '{sel_key}' is not a property of {method} {path}. "
                    f"Available fields: {sorted(body.keys())}"
                )
                example_ok = False
                continue

            # Check 2: key should be a <oneOf> field (warn if not)
            if sel_key not in oneof_fields:
                warnings.append(
                    f"[{name}] select: key '{sel_key}' in {method} {path} "
                    f"is not a <oneOf> placeholder (got {body[sel_key]!r}) — "
                    f"selection may be silently ignored by the generator"
                )

            # Check 3: variant value must be a valid discriminator key
            schema_name, _ = find_variant_by_discriminator_key(spec, sel_key, sel_value)
            if schema_name is None:
                errors.append(
                    f"[{name}] select: '{sel_key}: {sel_value}' — "
                    f"'{sel_value}' is not a valid discriminator key "
                    f"for the '{sel_key}' oneOf variants in the spec"
                )
                example_ok = False

        if example_ok:
            pass_count += 1

    # --- print summary ---
    total_checked = pass_count + len(errors)
    print(f"\nCatalog select: validation")
    print(f"  Catalog:  {catalog_path}")
    print(f"  Spec:     {spec_path}")
    print(f"  Linked:   {linked_path}")
    print(f"  ─────────────────────────────────────")
    print(f"  Checked:  {total_checked} examples with select: blocks")
    print(f"  PASS:     {pass_count}")
    print(f"  SKIP:     {skip_count}  (no select: block)")
    print(f"  WARNINGS: {len(warnings)}")
    print(f"  ERRORS:   {len(errors)}")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠  {w}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  ✗  {e}")
        print(
            "\nTo fix: ensure each select: key matches a field name in the endpoint's "
            "canonical request body, and each select: value matches a property name "
            "that appears inside one of that field's oneOf variant schemas."
        )
    else:
        print("\n✅ All select: keys and variant discriminators are valid")

    return pass_count, len(errors), len(warnings), skip_count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--catalog',
        default=_default('CURATED_EXAMPLES_CATALOG', 'config/curated-examples-catalog.yaml'),
        help='Path to curated-examples-catalog.yaml',
    )
    parser.add_argument(
        '--spec',
        default=_default('C2MAPIV2_OPENAPI_SPEC', 'openapi/c2mapiv2-openapi-spec-final.yaml'),
        help='Path to the final OpenAPI spec',
    )
    parser.add_argument(
        '--linked',
        default=_default(
            'POSTMAN_LINKED_COLLECTION_FLAT',
            'postman/generated/c2mapiv2-linked-collection-flat.json',
        ),
        help='Path to the flat linked collection JSON',
    )
    parser.add_argument(
        '--exit-status',
        action='store_true',
        help='Exit with non-zero status if any errors are found',
    )
    args = parser.parse_args()

    _, fail_count, _, _ = validate(
        catalog_path=Path(args.catalog),
        spec_path=Path(args.spec),
        linked_path=Path(args.linked),
    )

    if args.exit_status and fail_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
