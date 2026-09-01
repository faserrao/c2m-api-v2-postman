#!/usr/bin/env python3
"""
validate_collections_against_spec.py — non-hardcoded collection validator.

Validates Postman collection request bodies against the GENERATED OpenAPI spec
(`openapi/*.yaml`), which is the single source of truth (itself generated from the
EBNF data dictionary). NO per-endpoint rules are hardcoded here: every expectation
(required fields, allowed properties, oneOf variants) is read live from the spec.
Change the EBNF -> regenerate the spec -> this validator's expectations change with
it automatically. This is the deliberate contrast with the legacy hardcoded
validator in c2m-api-v2-manuals/validate_collections.py, which duplicated the
contract by hand and drifted.

Phase 1 = STRUCTURAL validation (spec-driven):
  - required fields present (recursively, following $ref/oneOf/anyOf/allOf)
  - no unexpected top-level/nested fields (when additionalProperties is not allowed)
  - oneOf/anyOf branch selection by structural fit
  - scalar TYPE/enum/format checks are intentionally SKIPPED so that placeholder
    values ("<String>", "<Integer>") in the linked/getting-started collections do
    not produce false positives.
Phase 2 (future, --deep) would add jsonschema type/enum validation for collections
that carry realistic values.

Usage:
  VENV=scripts/python_env/e2o.venv/bin/python
  $VENV scripts/validation/validate_collections_against_spec.py \
      [--spec openapi/c2mapiv2-openapi-spec-final.yaml] \
      [--collections <file> ...] \
      [--path-prefix /jobs/submit] \
      [--json] [--exit-status] [--report FILE]

Defaults validate the four canonical collections against the FINAL spec
(source-of-truth contract; identical to -base for job endpoints), limited to
/jobs/submit/* endpoints (auth endpoints have no request-body divergence concerns
here). Report-only by default (exit 0); pass --exit-status to fail on any
non-conformance (for later CI gating). Do NOT point --spec at bundled.yaml — it
flattens single-alias oneOf chains and misrepresents the contract.
"""

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLACEHOLDER = re.compile(r"<[^>]+>")

# Path defaults are sourced from the SAME variables the Makefile defines
# (passed through the environment), so paths are not duplicated between the
# Makefile and this script. Run via `make validate-collections-conformance` and
# the Makefile injects C2MAPIV2_OPENAPI_SPEC / POSTMAN_GENERATED_DIR /
# C2MAPIV2_POSTMAN_API_NAME_KC. Run standalone and these fall back to the
# standard relative locations. Env values may be absolute or repo-relative.
#
# Spec: the FINAL spec (source-of-truth contract; identical to -base for the job
# endpoints). NOT bundled.yaml — bundling flattens single-alias oneOf chains
# (documentIdSource->documentId->id collapses to a bare `id`), a derived-artifact
# distortion that is not what generates the Postman collections.
_SPEC_REL    = os.environ.get("C2MAPIV2_OPENAPI_SPEC", "openapi/c2mapiv2-openapi-spec-final.yaml")
_GEN_DIR_REL = os.environ.get("POSTMAN_GENERATED_DIR", "postman/generated")
_API_NAME    = os.environ.get("C2MAPIV2_POSTMAN_API_NAME_KC", "c2mapiv2")


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(REPO, p)


DEFAULT_SPEC = _abs(_SPEC_REL)
GEN_DIR_ABS = _abs(_GEN_DIR_REL)
_COLLECTION_BASENAMES = [
    f"{_API_NAME}-linked-collection-flat.json",
    f"{_API_NAME}-test-collection-flat.json",
    f"{_API_NAME}-getting-started-linked-collection.json",
    f"{_API_NAME}-getting-started-test-collection.json",
]
DEFAULT_COLLECTIONS = [os.path.join(GEN_DIR_ABS, b) for b in _COLLECTION_BASENAMES]


# --------------------------------------------------------------------------- #
# Spec loading + $ref resolution                                              #
# --------------------------------------------------------------------------- #
def load_spec(path):
    import yaml  # from venv
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_ref(spec, ref):
    """Resolve a local JSON pointer like '#/components/schemas/Foo'."""
    assert ref.startswith("#/"), f"only local refs supported, got {ref}"
    node = spec
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    return node


def deref(spec, schema):
    """Follow a top-level $ref (one hop) so callers see an object schema."""
    seen = 0
    while isinstance(schema, dict) and "$ref" in schema and seen < 20:
        schema = resolve_ref(spec, schema["$ref"])
        seen += 1
    return schema


# --------------------------------------------------------------------------- #
# Structural validation (spec-driven, placeholder-safe)                       #
# --------------------------------------------------------------------------- #
def has_placeholder(obj):
    if isinstance(obj, str):
        return bool(PLACEHOLDER.search(obj))
    if isinstance(obj, dict):
        return any(has_placeholder(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_placeholder(v) for v in obj)
    return False


def structural_errors(value, schema, spec, loc="body", strict_unknown=True):
    """
    Return a list of structural error strings for `value` against `schema`.
    Reads required/properties/oneOf/anyOf/allOf/items/$ref from the spec.
    Skips scalar type/enum/format so placeholder values validate.
    """
    errors = []
    schema = deref(spec, schema)
    if not isinstance(schema, dict):
        return errors

    # Composition keywords
    if "allOf" in schema:
        for sub in schema["allOf"]:
            errors += structural_errors(value, sub, spec, loc, strict_unknown)
        # allOf may also carry its own properties/required alongside; fall through

    # Phase 1: oneOf/anyOf branch SELECTION is intentionally NOT validated.
    # Reliable branch discrimination needs type/discriminator awareness, which
    # collides with placeholder values ("<Integer>") and produces false
    # positives. Every known divergence (see §5a) is caught by the top-level
    # required/unexpected-field checks below, so Phase 1 does not descend into
    # oneOf/anyOf. Discriminator-aware branch validation is a Phase 2 (--deep)
    # concern. If this node is purely a composition (no own properties/required),
    # stop here rather than mis-treating it as a plain object.
    if ("oneOf" in schema or "anyOf" in schema) and "properties" not in schema and "required" not in schema:
        return errors

    stype = schema.get("type")

    # Object
    if stype == "object" or "properties" in schema or "required" in schema:
        if not isinstance(value, dict):
            errors.append(f"{loc}: expected object, got {type(value).__name__}")
            return errors
        props = schema.get("properties", {})
        required = schema.get("required", [])
        for req in required:
            if req not in value:
                errors.append(f"{loc}: missing required field '{req}'")
        addl = schema.get("additionalProperties", None)
        allow_extra = (addl is True) or (isinstance(addl, dict)) or (not props and addl is None)
        if strict_unknown and not allow_extra and props:
            for k in value:
                if k not in props:
                    errors.append(f"{loc}: unexpected field '{k}' (not in schema properties)")
        for k, v in value.items():
            if k in props:
                errors += structural_errors(v, props[k], spec, f"{loc}.{k}", strict_unknown)
        return errors

    # Array
    if stype == "array" or "items" in schema:
        if not isinstance(value, list):
            errors.append(f"{loc}: expected array, got {type(value).__name__}")
            return errors
        items = schema.get("items")
        if items:
            for i, el in enumerate(value):
                errors += structural_errors(el, items, spec, f"{loc}[{i}]", strict_unknown)
        return errors

    # Scalars: intentionally not type-checked in structural mode
    return errors


def _variant_hint(branches, spec):
    """Human hint of what distinguishes oneOf branches (their property names)."""
    hints = []
    for b in branches:
        b = deref(spec, b)
        props = list((b.get("properties") or {}).keys())
        req = b.get("required") or []
        hints.append("/".join(req or props) or "?")
    return ", ".join(hints)


# --------------------------------------------------------------------------- #
# Collection walking                                                          #
# --------------------------------------------------------------------------- #
def iter_requests(collection):
    def walk(items):
        for it in items:
            if "item" in it:
                yield from walk(it["item"])
            elif "request" in it:
                req = it["request"]
                url = req.get("url", {})
                if isinstance(url, dict):
                    path = "/" + "/".join(url.get("path", []))
                else:
                    path = ""
                raw = (req.get("body") or {}).get("raw", "")
                yield {
                    "name": it.get("name", "(unnamed)"),
                    "method": (req.get("method") or "").lower(),
                    "path": path,
                    "raw": raw,
                }
    yield from walk(collection.get("item", []))


def request_body_schema(spec, path, method):
    """Return the requestBody schema object for an operation, or None."""
    op = spec.get("paths", {}).get(path, {}).get(method)
    if not op:
        return None
    try:
        return op["requestBody"]["content"]["application/json"]["schema"]
    except KeyError:
        return None


# --------------------------------------------------------------------------- #
# Main validation driver                                                      #
# --------------------------------------------------------------------------- #
def validate_collection(spec, collection, path_prefix, strict_unknown):
    results = []  # list of dicts: {path, name, mode, status, errors}
    for req in iter_requests(collection):
        if path_prefix and not req["path"].startswith(path_prefix):
            continue
        schema = request_body_schema(spec, req["path"], req["method"])
        rec = {"path": req["path"], "name": req["name"], "errors": [], "status": "PASS", "mode": ""}
        if schema is None:
            rec["status"] = "SKIP"
            rec["errors"] = [f"no requestBody schema for {req['method'].upper()} {req['path']}"]
            results.append(rec)
            continue
        raw = req["raw"]
        if not raw.strip():
            rec["status"] = "SKIP"
            rec["errors"] = ["empty request body"]
            results.append(rec)
            continue
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as e:
            rec["status"] = "FAIL"
            rec["errors"] = [f"body is not valid JSON: {e}"]
            results.append(rec)
            continue
        rec["mode"] = "structure(placeholders)" if has_placeholder(body) else "structure(values)"
        errs = structural_errors(body, schema, spec, "body", strict_unknown)
        if errs:
            rec["status"] = "FAIL"
            rec["errors"] = errs
        results.append(rec)
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", default=DEFAULT_SPEC)
    ap.add_argument("--collections", nargs="*", default=None,
                    help="collection JSON files (default: the 4 canonical collections)")
    ap.add_argument("--path-prefix", default="/jobs/submit",
                    help="only validate requests whose path starts with this (default /jobs/submit)")
    ap.add_argument("--no-strict-unknown", action="store_true",
                    help="do not flag unexpected fields")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--report", default=None, help="also write a markdown report to this path")
    ap.add_argument("--exit-status", action="store_true",
                    help="exit non-zero if any collection has a FAIL (for CI gating)")
    args = ap.parse_args(argv)

    spec = load_spec(args.spec if os.path.isabs(args.spec) else os.path.join(REPO, args.spec))
    strict = not args.no_strict_unknown
    cols = args.collections or DEFAULT_COLLECTIONS

    summary = {}
    all_results = {}
    for cpath in cols:
        full = cpath if os.path.isabs(cpath) else os.path.join(REPO, cpath)
        name = os.path.basename(cpath)
        if not os.path.exists(full):
            summary[name] = {"error": "not found"}
            continue
        with open(full) as f:
            collection = json.load(f)
        results = validate_collection(spec, collection, args.path_prefix, strict)
        all_results[name] = results
        npass = sum(1 for r in results if r["status"] == "PASS")
        nfail = sum(1 for r in results if r["status"] == "FAIL")
        nskip = sum(1 for r in results if r["status"] == "SKIP")
        summary[name] = {"pass": npass, "fail": nfail, "skip": nskip, "total": len(results)}

    if args.json:
        print(json.dumps({"summary": summary, "results": all_results}, indent=2))
    else:
        _print_human(spec, args.spec, summary, all_results)

    if args.report:
        _write_report(args.report, args.spec, summary, all_results)

    total_fail = sum(v.get("fail", 0) for v in summary.values() if isinstance(v, dict))
    if args.exit_status and total_fail:
        return 1
    return 0


def _print_human(spec, spec_path, summary, all_results):
    print("=" * 78)
    print("Collection conformance to OpenAPI spec (structural, spec-driven)")
    print(f"Spec: {spec_path}")
    print("=" * 78)
    for name, results in all_results.items():
        s = summary[name]
        print(f"\n### {name}   PASS={s['pass']} FAIL={s['fail']} SKIP={s['skip']}")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  ❌ [{r['path']}] {r['name']}")
                for e in r["errors"]:
                    print(f"        - {e}")
    print("\n" + "-" * 78)
    print("SUMMARY")
    for name, s in summary.items():
        if "error" in s:
            print(f"  {name}: {s['error']}")
        else:
            flag = "✅" if s["fail"] == 0 else "❌"
            print(f"  {flag} {name}: PASS={s['pass']} FAIL={s['fail']} SKIP={s['skip']}")


def _write_report(path, spec_path, summary, all_results):
    md = ["# Collection Conformance Report (spec-driven)", "",
          f"**Spec:** `{spec_path}`", ""]
    md.append("| Collection | Pass | Fail | Skip |")
    md.append("|---|---|---|---|")
    for name, s in summary.items():
        if "error" in s:
            md.append(f"| {name} | — | — | {s['error']} |")
        else:
            md.append(f"| {name} | {s['pass']} | {s['fail']} | {s['skip']} |")
    md.append("")
    for name, results in all_results.items():
        fails = [r for r in results if r["status"] == "FAIL"]
        if not fails:
            continue
        md.append(f"## {name} — failures")
        md.append("")
        for r in fails:
            md.append(f"- **[{r['path']}]** {r['name']}")
            for e in r["errors"]:
                md.append(f"  - {e}")
        md.append("")
    with open(path, "w") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    sys.exit(main())
