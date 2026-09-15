#!/usr/bin/env python3
"""
Deep field-level audit of all generated Postman collections against the OpenAPI spec.

Checks every request body for:
  - Valid oneOf wrapper keys (named-wrapper format)
  - No unknown fields
  - All required fields present

Usage:
  python3 scripts/validation/validate_collections_deep.py
  python3 scripts/validation/validate_collections_deep.py --dir postman/generated
  python3 scripts/validation/validate_collections_deep.py --spec openapi/c2mapiv2-openapi-spec-final.yaml
  python3 scripts/validation/validate_collections_deep.py --verbose

Exit code: 0 if no errors, 1 if any errors found.
"""
import argparse
import json
import re
import sys
import yaml
from pathlib import Path


def build_arg_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", default="postman/generated",
                   help="Directory to scan for *.json collection files (default: postman/generated)")
    p.add_argument("--spec", default="openapi/c2mapiv2-openapi-spec-final.yaml",
                   help="Path to the OpenAPI spec (default: openapi/c2mapiv2-openapi-spec-final.yaml)")
    p.add_argument("--verbose", action="store_true",
                   help="Print each collection being checked")
    return p


def load_spec(spec_path):
    with open(spec_path) as f:
        return yaml.safe_load(f)


def resolve_ref(schemas, ref):
    if isinstance(ref, str) and ref.startswith('#/components/schemas/'):
        return schemas.get(ref.split('/')[-1])
    return None


def resolve_schema(schemas, schema):
    if not isinstance(schema, dict):
        return schema
    if '$ref' in schema:
        resolved = resolve_ref(schemas, schema['$ref'])
        return resolve_schema(schemas, resolved) if resolved else schema
    return schema


def get_allowed_properties(schemas, schema):
    schema = resolve_schema(schemas, schema)
    if not isinstance(schema, dict):
        return None
    props = set(schema.get('properties', {}).keys())
    for sub in schema.get('allOf', []):
        sub = resolve_schema(schemas, sub)
        if isinstance(sub, dict):
            props |= set(sub.get('properties', {}).keys())
    return props if props else None


def get_required_fields(schemas, schema):
    schema = resolve_schema(schemas, schema)
    if not isinstance(schema, dict):
        return set()
    req = set(schema.get('required', []))
    for sub in schema.get('allOf', []):
        sub = resolve_schema(schemas, sub)
        if isinstance(sub, dict):
            req |= set(sub.get('required', []))
    return req


def get_property_schema(schemas, schema, prop_name):
    schema = resolve_schema(schemas, schema)
    if not isinstance(schema, dict):
        return None
    props = schema.get('properties', {})
    if prop_name in props:
        return props[prop_name]
    for sub in schema.get('allOf', []):
        sub = resolve_schema(schemas, sub)
        if isinstance(sub, dict):
            ps = sub.get('properties', {})
            if prop_name in ps:
                return ps[prop_name]
    return None


def oneof_wrapper_keys(schemas, schema):
    schema = resolve_schema(schemas, schema)
    if not isinstance(schema, dict):
        return set()
    keys = set()
    for option in schema.get('oneOf', []):
        if isinstance(option, dict):
            if option.get('type') == 'object' and option.get('properties'):
                keys |= set(option['properties'].keys())
            elif '$ref' in option:
                inner = resolve_schema(schemas, option)
                if isinstance(inner, dict) and inner.get('type') == 'object':
                    keys |= set(inner.get('properties', {}).keys())
    return keys


def audit_value(schemas, val, schema, path, issues, depth=0):
    if depth > 15:
        return
    schema = resolve_schema(schemas, schema)
    if not isinstance(schema, dict):
        return

    if 'oneOf' in schema and isinstance(val, dict):
        valid_wrappers = oneof_wrapper_keys(schemas, schema)
        if valid_wrappers:
            val_keys = set(val.keys())
            matching = val_keys & valid_wrappers
            bad_keys = val_keys - valid_wrappers
            if not matching:
                issues.append(f"  ❌ {path}: oneOf wrapper key missing. Got {sorted(val_keys)}, expected one of {sorted(valid_wrappers)}")
            elif len(matching) > 1:
                issues.append(f"  ❌ {path}: multiple oneOf wrapper keys present: {sorted(matching)}")
            if bad_keys:
                issues.append(f"  ❌ {path}: unknown keys alongside oneOf wrapper: {sorted(bad_keys)}")
            for mk in matching:
                wrapper_schema = None
                for option in schema.get('oneOf', []):
                    if isinstance(option, dict) and option.get('type') == 'object':
                        if mk in option.get('properties', {}):
                            wrapper_schema = option['properties'][mk]
                            break
                if wrapper_schema:
                    audit_value(schemas, val[mk], wrapper_schema, f"{path}.{mk}", issues, depth + 1)
        return

    if schema.get('type') == 'array' and isinstance(val, list):
        item_schema = schema.get('items', {})
        for i, item in enumerate(val):
            audit_value(schemas, item, item_schema, f"{path}[{i}]", issues, depth + 1)
        return

    if schema.get('type') == 'object' and isinstance(val, dict):
        allowed = get_allowed_properties(schemas, schema)
        required = get_required_fields(schemas, schema)
        if allowed is not None:
            for k in val:
                if k not in allowed:
                    issues.append(f"  ❌ {path}.{k}: unknown field (not in spec)")
            for r in required:
                if r not in val:
                    issues.append(f"  ⚠️  {path}.{r}: required field missing")
        for k, v in val.items():
            prop_schema = get_property_schema(schemas, schema, k)
            if prop_schema:
                audit_value(schemas, v, prop_schema, f"{path}.{k}", issues, depth + 1)
        return


def get_endpoint_schema(spec, path_str, method='post'):
    paths = spec.get('paths', {})
    method_obj = paths.get(path_str, {}).get(method, {})
    body = method_obj.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
    schemas = spec.get('components', {}).get('schemas', {})
    return resolve_schema(schemas, body)


def collect_items(items):
    for item in items:
        if 'request' in item:
            yield item
        if 'item' in item:
            yield from collect_items(item['item'])


def audit_collection(spec, col_path):
    with open(col_path) as f:
        col = json.load(f)
    schemas = spec.get('components', {}).get('schemas', {})
    issues = []
    checked = 0
    skipped = 0

    for req in collect_items(col.get('item', [])):
        req_name = req.get('name', '?')
        request = req.get('request', {})
        url_raw = request.get('url', {})
        if isinstance(url_raw, dict):
            path_parts = url_raw.get('path', [])
            url_path = '/' + '/'.join(str(p) for p in path_parts)
        else:
            url_path = str(url_raw)

        if '://' in url_path:
            url_path = '/' + url_path.split('/', 3)[-1] if url_path.count('/') >= 3 else url_path
        url_path = re.sub(r':([^/]+)', r'{\1}', url_path)
        url_path = re.sub(r'\{\{([^}]+)\}\}', r'{\1}', url_path)

        matched_schema = None
        for spec_path in spec.get('paths', {}):
            spec_parts = spec_path.split('/')
            url_parts = url_path.split('/')
            if len(spec_parts) != len(url_parts):
                continue
            if all(sp.startswith('{') or sp == up for sp, up in zip(spec_parts, url_parts)):
                matched_schema = get_endpoint_schema(spec, spec_path)
                break

        body_raw = request.get('body', {}).get('raw', '')
        if not body_raw:
            skipped += 1
            continue
        if not matched_schema:
            issues.append(f"  ⚠️  [{req_name}]: no spec match for path '{url_path}'")
            skipped += 1
            continue

        try:
            body = json.loads(body_raw)
        except Exception as e:
            issues.append(f"  ❌ [{req_name}]: invalid JSON body: {e}")
            continue

        req_issues = []
        audit_value(schemas, body, matched_schema, f"[{req_name}]", req_issues)
        issues.extend(req_issues)
        checked += 1

    return checked, skipped, issues


def discover_collections(directory):
    """Return all *.json files in directory, sorted by name."""
    return sorted(Path(directory).glob("*.json"))


def main():
    args = build_arg_parser().parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    col_dir = Path(args.dir)
    if not col_dir.exists():
        print(f"ERROR: collection directory not found: {col_dir}", file=sys.stderr)
        sys.exit(1)

    collections = discover_collections(col_dir)
    if not collections:
        print(f"WARNING: no *.json files found in {col_dir}", file=sys.stderr)
        sys.exit(0)

    spec = load_spec(spec_path)

    total_errors = 0
    for col_path in collections:
        if args.verbose:
            print(f"Checking {col_path.name} ...", file=sys.stderr)
        checked, skipped, issues = audit_collection(spec, col_path)
        unique = list(dict.fromkeys(issues))
        errors = [i for i in unique if '❌' in i]
        warns  = [i for i in unique if '⚠️' in i]
        status = "✅" if not errors else "❌"
        print(f"\n{status} {col_path.name}  (checked={checked} skipped={skipped} errors={len(errors)} warnings={len(warns)})")
        for iss in unique:
            print(iss)
        total_errors += len(errors)

    print(f"\n{'='*60}")
    print(f"Collections checked: {len(collections)}")
    print(f"TOTAL errors: {total_errors}")

    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
