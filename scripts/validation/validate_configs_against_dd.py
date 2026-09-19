#!/usr/bin/env python3
"""
validate_configs_against_dd.py — Build-time validator: config files vs. EBNF DD

Checks that every field name used in config files (faker_hints keys, values keys)
corresponds to a rule defined in the EBNF Data Dictionary. This catches renamed or
misspelled DD rule names before they silently produce wrong output.

Files checked:
  - config/curated-examples-catalog.yaml : values: keys in every example
  - config/getting-started-template.yaml : faker_hints: keys

Exit codes:
  0 — all clear (or only warnings)
  1 — one or more errors (key not in DD with no close match, or explicit error flag)

Usage:
    python3 scripts/validation/validate_configs_against_dd.py
    python3 scripts/validation/validate_configs_against_dd.py --strict
    make validate-configs
"""

import re
import sys
import argparse
import difflib
from pathlib import Path

# ── locate repo root relative to this script ────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Add scripts/ to path so utilities.oneof_resolver is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── known intentional extras (not in DD but accepted as custom catalog fields) ──
# Add keys here only for values that: (a) appear in a config file, (b) are not
# DD rules, and (c) are intentionally present (document the reason inline).
# foo1/foo2/addressList are DD rules and don't need an exception.
# customerAccountId was removed from the catalog in the Sep 2026 cleanup.
_KNOWN_EXTRA_KEYS: set = set()

# ── helpers ─────────────────────────────────────────────────────────────────

def _extract_dd_rules(ebnf_path: Path) -> set:
    """Return the set of all rule names defined in the EBNF DD."""
    pattern = re.compile(r'^([a-zA-Z][a-zA-Z0-9_]*)\s*=', re.MULTILINE)
    text = ebnf_path.read_text()
    return {m.group(1) for m in pattern.finditer(text)}


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        # Try the project venv
        venv_site = _REPO_ROOT / "scripts" / "python_env" / "e2o.venv" / "lib"
        candidates = list(venv_site.glob("python*/site-packages"))
        if candidates:
            sys.path.insert(0, str(candidates[0]))
        import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def _collect_values_keys(obj, keys: set, depth: int = 0) -> None:
    """Recursively collect all dict keys that appear under a values: section."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            _collect_values_keys(v, keys, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _collect_values_keys(item, keys, depth + 1)


def _suggest(key: str, dd_rules: set, n: int = 3, cutoff: float = 0.6) -> list:
    return difflib.get_close_matches(key, dd_rules, n=n, cutoff=cutoff)


# ── validation logic ─────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors = []   # (file, key, message)
        self.warnings = [] # (file, key, message)

    def error(self, file: str, key: str, msg: str):
        self.errors.append((file, key, msg))

    def warn(self, file: str, key: str, msg: str):
        self.warnings.append((file, key, msg))

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def validate_faker_hints(template_path: Path, dd_rules: set, result: ValidationResult) -> None:
    """Check every key in faker_hints: against the DD rule set."""
    template = _load_yaml(template_path)
    hints = template.get('faker_hints', {})
    if not hints:
        print(f"  ℹ  No faker_hints section found in {template_path.name}")
        return

    file_label = template_path.name
    print(f"  Checking {len(hints)} faker_hints keys in {file_label}...")
    bad = []
    for key in sorted(hints):
        if key in dd_rules:
            continue
        if key in _KNOWN_EXTRA_KEYS:
            result.warn(file_label, key, f"not a DD rule but in known-extras list — verify intentional")
            continue
        suggestions = _suggest(key, dd_rules)
        if suggestions:
            result.error(file_label, key, f"not a DD rule — did you mean: {', '.join(suggestions)}?")
        else:
            result.error(file_label, key, "not a DD rule — no close match found; key may be dead or misspelled")
        bad.append(key)

    if not bad:
        print(f"  ✓ All {len(hints)} faker_hints keys are valid DD rule names")


def validate_catalog_values(catalog_path: Path, dd_rules: set, result: ValidationResult) -> None:
    """Check every key used under values: in every catalog example."""
    catalog = _load_yaml(catalog_path)
    file_label = catalog_path.name

    all_value_keys: set = set()
    for example in catalog.get('examples', []):
        _collect_values_keys(example.get('values', {}), all_value_keys)

    print(f"  Checking {len(all_value_keys)} distinct values keys in {file_label}...")
    bad = []
    for key in sorted(all_value_keys):
        if key in dd_rules:
            continue
        if key in _KNOWN_EXTRA_KEYS:
            result.warn(file_label, key, "not a DD rule but in known-extras list — verify intentional")
            continue
        suggestions = _suggest(key, dd_rules)
        if suggestions:
            result.error(file_label, key, f"not a DD rule — did you mean: {', '.join(suggestions)}?")
        else:
            result.error(file_label, key, "not a DD rule — no close match found; key may be dead or misspelled")
        bad.append(key)

    if not bad:
        print(f"  ✓ All {len(all_value_keys)} values keys are valid DD rule names")


def validate_faker_hints_file(hints_path: Path, dd_rules: set, result: ValidationResult) -> None:
    """Check that a derived config/faker_hints.yaml is consistent with the DD.

    This is the secondary guard: the hints file is generated by the translator,
    so errors here mean the @hint annotation in the DD used a bad rule name.
    """
    if not hints_path.exists():
        print(f"  ℹ  {hints_path.name} not found — skipping derived hints check (run openapi-build first)")
        return

    data = _load_yaml(hints_path)
    hints = data.get('faker_hints', {})
    file_label = hints_path.name
    print(f"  Checking {len(hints)} keys in derived {file_label}...")
    bad = []
    for key in sorted(hints):
        if key in dd_rules:
            continue
        suggestions = _suggest(key, dd_rules)
        if suggestions:
            result.error(file_label, key, f"derived from DD @hint but '{key}' is not a DD rule — annotation error; did you mean: {', '.join(suggestions)}?")
        else:
            result.error(file_label, key, f"derived from DD @hint but '{key}' is not a DD rule — fix the @hint annotation")
        bad.append(key)

    if not bad:
        print(f"  ✓ All {len(hints)} derived faker_hints keys are valid DD rule names")


def validate_template_values(template_path: Path, dd_rules: set, result: ValidationResult) -> None:
    """Check every field key used under values: in each template example against the DD.

    Mirrors validate_catalog_values() but reads from getting-started-template.yaml,
    which uses the same examples[].values structure as the catalog.
    """
    template = _load_yaml(template_path)
    file_label = template_path.name

    all_value_keys: set = set()
    for example in template.get('examples', []):
        _collect_values_keys(example.get('values', {}), all_value_keys)

    if not all_value_keys:
        print(f"  ℹ  No values keys found in {file_label}")
        return

    print(f"  Checking {len(all_value_keys)} distinct values keys in {file_label}...")
    bad = []
    for key in sorted(all_value_keys):
        if key in dd_rules:
            continue
        if key in _KNOWN_EXTRA_KEYS:
            result.warn(file_label, key, "not a DD rule but in known-extras list — verify intentional")
            continue
        suggestions = _suggest(key, dd_rules)
        if suggestions:
            result.error(file_label, key, f"not a DD rule — did you mean: {', '.join(suggestions)}?")
        else:
            result.error(file_label, key, "not a DD rule — no close match found; key may be dead or misspelled")
        bad.append(key)

    if not bad:
        print(f"  ✓ All {len(all_value_keys)} template values keys are valid DD rule names")


def validate_template_select_fields(template_path: Path, spec_path: Path,
                                    result: ValidationResult) -> None:
    """V3: Verify every select: entry in getting-started-template.yaml names a real
    oneOf field+variant in the spec.

    Mirrors validate_catalog_select_fields() for the template. Template entries use the
    same select: map structure; if a variant name drifts (e.g. after a spec refactor) the
    generated Getting Started collections will silently materialise the wrong request body.
    """
    try:
        from utilities.oneof_resolver import find_variant_by_discriminator_key
    except ImportError as e:
        result.warn(template_path.name, "select", f"Cannot import oneof_resolver — skipping V3 check: {e}")
        return

    import yaml
    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    template = _load_yaml(template_path)
    file_label = template_path.name
    total = 0
    bad = []

    print(f"  Checking select: fields in {file_label} against {spec_path.name}...")
    for example in template.get('examples', []):
        ex_name = example.get('name', '<unnamed>')
        for field_name, variant_name in example.get('select', {}).items():
            total += 1
            schema_name, _ = find_variant_by_discriminator_key(spec, field_name, variant_name)
            if schema_name is None:
                msg = (f"variant '{variant_name}' not found in spec oneOf for field '{field_name}' "
                       f"(example: '{ex_name}')")
                result.error(file_label, f"select.{field_name}", msg)
                bad.append(f"{field_name}: {variant_name}")

    if not bad:
        print(f"  ✓ All {total} template select: entries reference valid spec oneOf variants")
    else:
        print(f"  ✗ {len(bad)} invalid select: entry/entries found")


def validate_catalog_jobtemplates(catalog_path: Path, result: ValidationResult) -> None:
    """V1: Report jobTemplate values found in catalog (informational — spec has no enum for this field).

    jobTemplate is type: string with no enum in the OpenAPI spec because template names are
    customer-defined in the C2M system. The values in the catalog are illustrative only.
    This check makes them visible on every CI run so stale or mistyped names aren't invisible.
    """
    catalog = _load_yaml(catalog_path)
    file_label = catalog_path.name

    seen: dict = {}  # value → list of example names
    for example in catalog.get('examples', []):
        jt = example.get('values', {}).get('jobTemplate')
        if jt is not None:
            seen.setdefault(jt, []).append(example.get('name', '<unnamed>'))

    if seen:
        print(f"  ℹ  {len(seen)} distinct jobTemplate value(s) in {file_label} "
              f"(customer-defined, not spec-validated):")
        for val in sorted(seen):
            print(f"     '{val}' — used by: {', '.join(seen[val])}")
    else:
        print(f"  ℹ  No jobTemplate values found in {file_label}")


def validate_catalog_select_fields(catalog_path: Path, spec_path: Path,
                                   result: ValidationResult) -> None:
    """V2: Verify every select: entry in the catalog names a real oneOf field+variant in the spec.

    The select: map drives oneOf variant materialization. An unknown field or variant name
    silently produces a wrong body structure — this check surfaces those errors at build time.
    """
    try:
        from utilities.oneof_resolver import find_variant_by_discriminator_key
    except ImportError as e:
        result.warn(catalog_path.name, "select", f"Cannot import oneof_resolver — skipping V2 check: {e}")
        return

    import yaml
    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    catalog = _load_yaml(catalog_path)
    file_label = catalog_path.name
    total = 0
    bad = []

    print(f"  Checking select: fields in {file_label} against {spec_path.name}...")
    for example in catalog.get('examples', []):
        ex_name = example.get('name', '<unnamed>')
        for field_name, variant_name in example.get('select', {}).items():
            total += 1
            schema_name, _ = find_variant_by_discriminator_key(spec, field_name, variant_name)
            if schema_name is None:
                msg = (f"variant '{variant_name}' not found in spec oneOf for field '{field_name}' "
                       f"(example: '{ex_name}')")
                result.error(file_label, f"select.{field_name}", msg)
                bad.append(f"{field_name}: {variant_name}")

    if not bad:
        print(f"  ✓ All {total} select: entries reference valid spec oneOf variants")
    else:
        print(f"  ✗ {len(bad)} invalid select: entry/entries found")


# ── main ─────────────────────────────────────────────────────────────────────

def _default_path(env_var: str, fallback: str) -> Path:
    import os
    return Path(os.environ.get(env_var, str(_REPO_ROOT / fallback)))


def main():
    parser = argparse.ArgumentParser(
        description="Validate config file field names against the EBNF Data Dictionary"
    )
    parser.add_argument(
        "--dd",
        default=str(_default_path("DD_EBNF_FILE", "data_dictionary/c2mapiv2-dd.ebnf")),
        help="Path to EBNF Data Dictionary",
    )
    parser.add_argument(
        "--catalog",
        default=str(_default_path("CURATED_EXAMPLES_CATALOG", "config/curated-examples-catalog.yaml")),
        help="Path to curated-examples-catalog.yaml",
    )
    parser.add_argument(
        "--template",
        default=str(_default_path("GETTING_STARTED_TEMPLATE", "config/getting-started-template.yaml")),
        help="Path to getting-started-template.yaml",
    )
    parser.add_argument(
        "--faker-hints",
        default=str(_REPO_ROOT / "config" / "faker_hints.yaml"),
        help="Path to derived config/faker_hints.yaml (generated by translator)",
    )
    parser.add_argument(
        "--spec",
        default=str(_default_path("C2MAPIV2_OPENAPI_SPEC_BASE",
                                  "openapi/c2mapiv2-openapi-spec-base.yaml")),
        help="Path to OpenAPI spec (for select: variant validation)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    dd_path = Path(args.dd)
    catalog_path = Path(args.catalog)
    template_path = Path(args.template)
    hints_path = Path(args.faker_hints)
    spec_path = Path(args.spec)

    # Validate required files exist
    for p in (dd_path, catalog_path, template_path):
        if not p.exists():
            print(f"❌ File not found: {p}", file=sys.stderr)
            sys.exit(1)

    print(f"\n📖 Loading DD rule names from {dd_path.name}...")
    dd_rules = _extract_dd_rules(dd_path)
    print(f"   {len(dd_rules)} rules found")

    result = ValidationResult()

    print(f"\n🔍 Checking getting-started-template.yaml faker_hints:")
    validate_faker_hints(template_path, dd_rules, result)

    print(f"\n🔍 Checking curated-examples-catalog.yaml values:")
    validate_catalog_values(catalog_path, dd_rules, result)

    print(f"\n🔍 Checking getting-started-template.yaml values:")
    validate_template_values(template_path, dd_rules, result)

    print(f"\n🔍 Checking derived faker_hints.yaml (if present):")
    validate_faker_hints_file(hints_path, dd_rules, result)

    print(f"\n🔍 Reporting jobTemplate values (V1 — informational):")
    validate_catalog_jobtemplates(catalog_path, result)

    if spec_path.exists():
        print(f"\n🔍 Checking catalog select: entries against spec oneOf variants (V2):")
        validate_catalog_select_fields(catalog_path, spec_path, result)

        print(f"\n🔍 Checking template select: entries against spec oneOf variants (V3):")
        validate_template_select_fields(template_path, spec_path, result)
    else:
        print(f"\n⚠  Skipping select: validation — spec not found at {spec_path}")
        print(f"   (Run openapi-build first, or pass --spec <path>)")

    # ── report ────────────────────────────────────────────────────────────────
    print()
    if result.warnings:
        print(f"⚠  {len(result.warnings)} warning(s):")
        for file, key, msg in result.warnings:
            print(f"   [{file}] {key}: {msg}")

    if result.errors:
        print(f"\n❌ {len(result.errors)} error(s):")
        for file, key, msg in result.errors:
            print(f"   [{file}] {key}: {msg}")
        print("\nFix: update the config file key to match the DD rule name.")
        print("     Use --strict to also fail on warnings.")
        sys.exit(1)
    elif result.warnings and args.strict:
        print(f"\n❌ Failing due to --strict: {len(result.warnings)} warning(s) treated as errors")
        sys.exit(1)
    else:
        print("✅ All config field names are valid DD rule names")


if __name__ == "__main__":
    main()
