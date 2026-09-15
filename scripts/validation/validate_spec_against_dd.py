#!/usr/bin/env python3
"""
validate_spec_against_dd.py

Validates the generated OpenAPI spec against the EBNF Data Dictionary.
The EBNF DD is the source of truth; the translator (ebnf_to_openapi_dynamic_v3.py)
produces the spec from it.  This script checks whether that translation is faithful.

Checks performed:
  1. Schema existence  — every active EBNF rule has a schema in components/schemas
  2. Enum parity      — EBNF pure-enum rules exactly match spec enum values
  3. Object properties — all fields named in EBNF compositions exist as spec properties
  4. Required fields  — non-optional EBNF fields appear in spec required[]; optional
                        EBNF fields do NOT appear in spec required[]

Usage:
  python3 scripts/validation/validate_spec_against_dd.py \\
      --dd   data_dictionary/c2mapiv2-dd.ebnf \\
      --spec openapi/c2mapiv2-openapi-spec-final.yaml

  # with optional Markdown report:
  ... --report reports/spec-vs-dd-report.md

  # verbose (shows PASSes too):
  ... --verbose
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    print("Error: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Result codes
# ---------------------------------------------------------------------------
PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"

STATUS_ICON = {PASS: "✅", FAIL: "❌", WARN: "⚠️ "}
STATUS_ABBR = {PASS: "PASS", FAIL: "FAIL", WARN: "WARN"}


# ---------------------------------------------------------------------------
# Rules that are EBNF primitives or types, not schema-level constructs.
# The translator does not emit standalone schemas for these bare types.
# ---------------------------------------------------------------------------
PRIMITIVE_TYPES = {"string", "integer", "number"}

# Rules that are just HTTP response alias shorthands.  They DO appear in the
# spec as $ref entries, but checking them adds no signal — they always pass.
HTTP_ALIAS_PREFIX = "HTTP_"

# EBNF rules of the form `a = b ;` (single-symbol body) that represent
# single-field WRAPPER OBJECTS rather than transparent aliases.  These appear
# as discriminated oneOf variants alongside multi-field object siblings, so
# their spec schema must be { type: object, properties: { b: T }, required: [b] }
# rather than a $ref alias.  Must stay in sync with _SINGLE_FIELD_WRAPPER_RULES
# in ebnf_to_openapi_dynamic_v3.py.
SINGLE_FIELD_WRAPPER_RULES: frozenset = frozenset({
    "documentIdSource",   # documentIdSource = documentId ; → { documentId: integer }
    "urlSource",          # urlSource = url ;              → { url: string }
    "zipDocumentIdOnly",  # zipDocumentIdOnly = zipDocumentId ; → { zipDocumentId: integer }
    "zipRequestIdOnly",   # zipRequestIdOnly = requestId ; → { requestId: integer }
    "mergeByDocumentId",  # mergeByDocumentId = documentId ; → { documentId: integer }
})

# oneOf rules whose variants must be named-wrapper objects rather than bare $refs.
# e.g. docSourceStandard → oneOf: [{ type:object, properties:{ requestIdSource:$ref } }]
# Must stay in sync with _NAMED_WRAPPER_ONEOF_RULES in ebnf_to_openapi_dynamic_v3.py.
NAMED_WRAPPER_ONEOF_RULES: frozenset = frozenset({
    "docSourceStandard",
    "docSourceZipFile",
    "docSourceZipFileRef",
    "zipDocumentSource",
    "mergeDocumentRef",
    "recipientAddressSource",
})

# Rules only referenced inside multi-line block comments (Apple Pay /
# Google Pay).  strip_block_comments() removes them from the parsed text, so
# they never appear in extract_rules(); this set is kept for documentation.
COMMENTED_OUT_RULES = {
    "applePayDetails", "applePayToken", "paymentData", "paymentMethod",
    "displayName", "network", "cardTypeApplePay", "transactionAmount",
    "currencyCode", "transactionIdentifier", "billingContact", "givenName",
    "familyName", "emailAddress", "phoneNumber", "addressLines", "locality",
    "administrativeArea", "postalCode", "countryCode",
    "googlePayDetails", "paymentMethodData", "description", "type", "info",
    "cardNetwork", "cardDetails", "tokenizationData", "tokenizationType",
    "token", "billingAddress", "name", "email", "sortingCode",
}


# ---------------------------------------------------------------------------
# EBNF parsing
# ---------------------------------------------------------------------------

def strip_block_comments(text: str) -> str:
    """Remove all (* ... *) comments, including multi-line ones."""
    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)


def extract_rules(ebnf_text: str) -> Dict[str, str]:
    """
    Return {rule_name: body_str} for every rule in the EBNF after comments
    are stripped.  Body is whitespace-normalised.
    """
    clean = strip_block_comments(ebnf_text)
    rules: Dict[str, str] = {}

    for chunk in clean.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        eq_idx = chunk.index("=")
        name = chunk[:eq_idx].strip()
        body = " ".join(chunk[eq_idx + 1:].split())  # normalise whitespace

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name):
            continue
        if not body:
            continue

        rules[name] = body

    return rules


def classify_body(body: str) -> str:
    """
    Return one of:
      'enum'      — all alternatives are quoted strings ("val1" | "val2" | ...)
      'primitive' — body is exactly 'string', 'integer', or 'number'
      'alias'     — body is a single identifier (a = b)
      'array'     — body is { something }
      'object'    — body contains '+' with named fields (and optional [field])
      'tagged'    — body contains '+' but includes a quoted-string literal
                    (e.g. creditCardPayment = "creditCard" + creditCardDetails)
      'oneof'     — body contains '|' where the alternatives are named rules
      'unknown'   — anything else
    """
    if body in PRIMITIVE_TYPES:
        return "primitive"

    # Pure string enum: every | alternative is a quoted string
    pipe_parts = [p.strip() for p in body.split("|")]
    if len(pipe_parts) > 1 and all(re.match(r'^"[^"]+"$', p) for p in pipe_parts):
        return "enum"

    # Array repetition: { ... }
    if re.match(r"^\{[^{}]+\}$", body):
        return "array"

    # Composition with +
    if "+" in body:
        plus_parts = [p.strip() for p in body.split("+")]
        if any(re.match(r'^"[^"]+"$', p) for p in plus_parts):
            return "tagged"
        return "object"

    # Alternatives of named rules
    if "|" in body:
        return "oneof"

    # Single identifier alias
    if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", body):
        return "alias"

    return "unknown"


def enum_values_from_body(body: str) -> List[str]:
    """Extract string values from a pure-enum body."""
    values = []
    for part in body.split("|"):
        m = re.match(r'^"([^"]+)"$', part.strip())
        if m:
            values.append(m.group(1))
    return values


def parse_composition(body: str) -> Tuple[List[str], List[str]]:
    """
    Parse an 'object' body (A + B + [C] + D).
    Returns (required_fields, optional_fields).
    Only top-level single-identifier fields are collected; complex sub-expressions
    are skipped (they are validated when their own rule is checked).
    """
    required: List[str] = []
    optional: List[str] = []

    for part in body.split("+"):
        part = part.strip()
        # Optional field: [ fieldName ]
        m_opt = re.match(r"^\[\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\]$", part)
        if m_opt:
            optional.append(m_opt.group(1))
            continue
        # Required field: plain identifier
        if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", part):
            required.append(part)
        # Quoted strings or other constructs are intentionally ignored here

    return required, optional


# ---------------------------------------------------------------------------
# Spec helpers
# ---------------------------------------------------------------------------

def resolve_ref(ref_str: str, all_schemas: dict) -> Optional[dict]:
    """Follow a single $ref string to its target schema dict."""
    if not isinstance(ref_str, str) or not ref_str.startswith("#/components/schemas/"):
        return None
    name = ref_str.split("/")[-1]
    return all_schemas.get(name)


def effective_schema(schema: dict, all_schemas: dict) -> dict:
    """Resolve a $ref to the concrete schema dict it points to."""
    if "$ref" in schema:
        resolved = resolve_ref(schema["$ref"], all_schemas)
        return resolved if resolved else schema
    return schema


def spec_enum_values(schema: dict, all_schemas: dict) -> Optional[List[str]]:
    """Return enum list from a schema (resolving $ref if needed), or None."""
    sch = effective_schema(schema, all_schemas)
    return sch.get("enum")


def spec_properties(schema: dict, all_schemas: dict) -> Set[str]:
    """Return property names for a schema (resolving $ref if needed)."""
    sch = effective_schema(schema, all_schemas)
    return set(sch.get("properties", {}).keys())


def spec_required_fields(schema: dict, all_schemas: dict) -> Set[str]:
    """Return required field set for a schema (resolving $ref if needed)."""
    sch = effective_schema(schema, all_schemas)
    return set(sch.get("required", []))


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

Finding = Tuple[str, str, str]  # (status, rule_name, message)


def check_schema_existence(
    rules: Dict[str, str],
    all_schemas: dict,
    body_types: Dict[str, str],
) -> List[Finding]:
    """
    Check 1: every active EBNF rule has a schema in components/schemas.
    Leaf rules (primitive aliases) that are missing get WARN; structural
    rules (object, enum, oneof, array, tagged, alias) get FAIL.
    """
    findings: List[Finding] = []

    for name, body in rules.items():
        btype = body_types[name]

        if btype == "primitive":
            # e.g. `firstName = string` — translator may inline rather than emit
            # a standalone schema; only warn if absent
            if name not in all_schemas:
                findings.append((WARN, name, "leaf rule (primitive type) has no standalone schema"))
            else:
                findings.append((PASS, name, "schema present"))
            continue

        if name not in all_schemas:
            findings.append((FAIL, name, f"schema missing from spec [{btype}]"))
        else:
            findings.append((PASS, name, "schema present"))

    return findings


def check_enum_parity(
    rules: Dict[str, str],
    all_schemas: dict,
    body_types: Dict[str, str],
) -> List[Finding]:
    """
    Check 2: for every EBNF pure-enum rule, the spec enum values must match.
    Missing DD values in spec → FAIL.  Extra spec values not in DD → WARN.
    """
    findings: List[Finding] = []

    for name, body in rules.items():
        if body_types[name] != "enum":
            continue
        if name not in all_schemas:
            continue  # already flagged by existence check

        dd_vals = set(enum_values_from_body(body))
        schema = all_schemas[name]
        spec_vals_list = spec_enum_values(schema, all_schemas)

        if spec_vals_list is None:
            findings.append((FAIL, name, "spec schema exists but has no 'enum' list"))
            continue

        spec_vals = set(spec_vals_list)
        missing = dd_vals - spec_vals
        extra   = spec_vals - dd_vals

        if missing:
            findings.append((FAIL, name,
                f"DD enum values missing from spec: {sorted(missing)}"))
        if extra:
            findings.append((WARN, name,
                f"spec has extra enum values not in DD: {sorted(extra)}"))
        if not missing and not extra:
            findings.append((PASS, name,
                f"enum values match ({len(dd_vals)} values)"))

    return findings


def check_object_properties(
    rules: Dict[str, str],
    all_schemas: dict,
    body_types: Dict[str, str],
) -> List[Finding]:
    """
    Check 3: for every EBNF object rule, all fields named in the composition
    must appear as properties in the spec schema.
    """
    findings: List[Finding] = []

    for name, body in rules.items():
        if body_types[name] != "object":
            continue
        if name not in all_schemas:
            continue  # already flagged

        req, opt = parse_composition(body)
        all_dd_fields = set(req) | set(opt)

        if not all_dd_fields:
            # Nothing parseable — skip rather than noise
            continue

        spec_props = spec_properties(all_schemas[name], all_schemas)
        missing = all_dd_fields - spec_props

        if missing:
            findings.append((FAIL, name,
                f"DD fields missing from spec properties: {sorted(missing)}"))
        else:
            findings.append((PASS, name,
                f"all {len(all_dd_fields)} fields present as properties"))

    return findings


def check_required_fields(
    rules: Dict[str, str],
    all_schemas: dict,
    body_types: Dict[str, str],
) -> List[Finding]:
    """
    Check 4: for every EBNF object rule:
    - DD-required fields should be in spec required[]  → FAIL if absent
    - DD-optional fields should NOT be in spec required[] → WARN if present
    """
    findings: List[Finding] = []

    for name, body in rules.items():
        if body_types[name] != "object":
            continue
        if name not in all_schemas:
            continue

        req_dd, opt_dd = parse_composition(body)
        if not req_dd and not opt_dd:
            continue

        spec_req = spec_required_fields(all_schemas[name], all_schemas)

        # DD-required not in spec required
        missing_required = [f for f in req_dd if f not in spec_req]
        # DD-optional incorrectly required in spec
        over_required    = [f for f in opt_dd if f in spec_req]

        if missing_required:
            findings.append((FAIL, name,
                f"DD-required fields missing from spec required[]: {missing_required}"))
        if over_required:
            findings.append((WARN, name,
                f"DD-optional fields incorrectly in spec required[]: {over_required}"))
        if not missing_required and not over_required:
            findings.append((PASS, name,
                f"required fields match ({len(req_dd)} required, {len(opt_dd)} optional)"))

    return findings


def check_wrapper_rules(
    rules: Dict[str, str],
    all_schemas: dict,
    body_types: Dict[str, str],
) -> List[Finding]:
    """
    Check 5: single-field wrapper rules (a = b ; where b is the field name)
    must be emitted as { type: object, properties: { b: T }, required: [b] }
    rather than $ref aliases.  A $ref here means the translator treated it as
    a transparent alias, making the oneOf variants structurally ambiguous.
    """
    findings: List[Finding] = []

    for name in SINGLE_FIELD_WRAPPER_RULES:
        if name not in rules:
            continue  # rule commented out or not present in this DD version
        if name not in all_schemas:
            continue  # already flagged by existence check

        # Derive the expected single field name from the EBNF body
        field_name = rules[name].strip()  # body is just the field identifier
        schema = all_schemas[name]

        if "$ref" in schema:
            findings.append((FAIL, name,
                f"spec emits a $ref alias; expected single-field object "
                f"{{ {field_name}: T }} — translator treated it as a transparent alias"))
            continue

        schema_type = schema.get("type")
        if schema_type != "object":
            findings.append((FAIL, name,
                f"spec schema type is '{schema_type}'; expected 'object' "
                f"with property '{field_name}'"))
            continue

        props = set(schema.get("properties", {}).keys())
        required = set(schema.get("required", []))

        missing_prop = field_name not in props
        missing_req  = field_name not in required

        if missing_prop:
            findings.append((FAIL, name,
                f"spec object missing property '{field_name}'"))
        elif missing_req:
            findings.append((WARN, name,
                f"property '{field_name}' present but not in required[]"))
        else:
            findings.append((PASS, name,
                f"single-field wrapper object correct: {{ {field_name}: T }}"))

    return findings


def check_named_wrapper_oneofs(
    rules: Dict[str, str],
    all_schemas: dict,
) -> List[Finding]:
    """
    Check 6: oneOf rules in NAMED_WRAPPER_ONEOF_RULES must emit each variant as a
    named-wrapper object { type: object, properties: { variantName: $ref }, required: [v] }
    rather than a bare $ref.  A bare $ref means the variant fields are inlined directly
    (no intermediate type-name key in the JSON body).
    """
    findings: List[Finding] = []

    for name in sorted(NAMED_WRAPPER_ONEOF_RULES):
        if name not in all_schemas:
            continue

        schema = all_schemas[name]
        variants = schema.get("oneOf", [])
        if not variants:
            findings.append((FAIL, name, "schema has no oneOf[] — expected named-wrapper variants"))
            continue

        bare_refs = []
        wrapped = []
        for v in variants:
            if "$ref" in v and not v.get("properties"):
                bare_refs.append(v["$ref"].split("/")[-1])
            elif v.get("type") == "object" and v.get("properties"):
                props = list(v["properties"].keys())
                wrapped.append(props[0] if props else "?")

        if bare_refs:
            findings.append((FAIL, name,
                f"bare $ref variants still present: {bare_refs} — "
                f"translator should wrap each in its type name"))
        elif not wrapped:
            findings.append((FAIL, name, "no named-wrapper variants found in oneOf[]"))
        else:
            findings.append((PASS, name,
                f"all {len(wrapped)} variants are named-wrapper objects: {wrapped}"))

    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def tally(findings: List[Finding]) -> Dict[str, int]:
    t: Dict[str, int] = {PASS: 0, FAIL: 0, WARN: 0}
    for status, _, _ in findings:
        t[status] = t.get(status, 0) + 1
    return t


def print_check_section(
    title: str,
    findings: List[Finding],
    verbose: bool,
) -> None:
    t = tally(findings)
    summary = f"PASS={t[PASS]}  FAIL={t[FAIL]}  WARN={t[WARN]}"
    ok = t[FAIL] == 0 and t[WARN] == 0
    icon = "✅" if ok else ("❌" if t[FAIL] else "⚠️ ")
    print(f"\n{icon} {title}  [{summary}]")
    for status, name, msg in sorted(findings, key=lambda x: (x[0] != FAIL, x[0] != WARN, x[1])):
        if status in (FAIL, WARN) or verbose:
            print(f"   {STATUS_ICON[status]} {name}: {msg}")


def build_report_md(
    dd_path: str,
    spec_path: str,
    checks: List[Tuple[str, List[Finding]]],
    totals: Dict[str, int],
) -> str:
    lines = [
        "# OpenAPI Spec vs EBNF DD — Validation Report",
        "",
        f"**DD**: `{dd_path}`  ",
        f"**Spec**: `{spec_path}`",
        "",
        f"**TOTAL: PASS={totals[PASS]}  FAIL={totals[FAIL]}  WARN={totals[WARN]}**",
        "",
        "| Check | PASS | FAIL | WARN |",
        "|-------|------|------|------|",
    ]
    for title, findings in checks:
        t = tally(findings)
        lines.append(f"| {title} | {t[PASS]} | {t[FAIL]} | {t[WARN]} |")

    for title, findings in checks:
        bad = [(s, n, m) for s, n, m in findings if s in (FAIL, WARN)]
        if not bad:
            continue
        lines += ["", f"## {title}", ""]
        for status, name, msg in sorted(bad, key=lambda x: (x[0] != FAIL, x[1])):
            lines.append(f"- **{STATUS_ABBR[status]}** `{name}`: {msg}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the generated OpenAPI spec against the EBNF Data Dictionary."
    )
    parser.add_argument("--dd",   default="data_dictionary/c2mapiv2-dd.ebnf",
                        help="Path to the EBNF DD file")
    parser.add_argument("--spec", default="openapi/c2mapiv2-openapi-spec-final.yaml",
                        help="Path to the OpenAPI spec YAML")
    parser.add_argument("--report", metavar="FILE",
                        help="Write Markdown report to FILE")
    parser.add_argument("--verbose", action="store_true",
                        help="Also print passing results")
    args = parser.parse_args()

    # ---- Load EBNF DD ----
    dd_text = Path(args.dd).read_text()
    rules = extract_rules(dd_text)

    # Skip rules we intentionally exclude
    rules = {
        name: body for name, body in rules.items()
        if name not in COMMENTED_OUT_RULES
    }

    body_types = {name: classify_body(body) for name, body in rules.items()}

    # Summarise what was loaded
    type_counts = {}
    for t in body_types.values():
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"Loading DD: {args.dd}")
    print(f"  {len(rules)} active rules extracted")
    for t, n in sorted(type_counts.items()):
        print(f"    {t:12s} × {n}")

    # ---- Load OpenAPI spec ----
    spec = yaml.safe_load(Path(args.spec).read_text())
    all_schemas: dict = spec.get("components", {}).get("schemas", {})
    print(f"\nLoading spec: {args.spec}")
    print(f"  {len(all_schemas)} schemas in components/schemas")

    # ---- Run checks ----
    print("\n" + "=" * 68)

    check_list = [
        ("1. Schema existence",           check_schema_existence(rules, all_schemas, body_types)),
        ("2. Enum parity",                check_enum_parity(rules, all_schemas, body_types)),
        ("3. Object properties",          check_object_properties(rules, all_schemas, body_types)),
        ("4. Required fields",            check_required_fields(rules, all_schemas, body_types)),
        ("5. Wrapper rule structure",     check_wrapper_rules(rules, all_schemas, body_types)),
        ("6. Named-wrapper oneOf rules",  check_named_wrapper_oneofs(rules, all_schemas)),
    ]

    for title, findings in check_list:
        print_check_section(title, findings, args.verbose)

    # ---- Totals ----
    all_findings = [f for _, flist in check_list for f in flist]
    totals = {PASS: 0, FAIL: 0, WARN: 0}
    for status, _, _ in all_findings:
        totals[status] += 1

    print("\n" + "=" * 68)
    overall_ok = totals[FAIL] == 0
    icon = "✅" if overall_ok else "❌"
    print(f"{icon} TOTAL — PASS={totals[PASS]}  FAIL={totals[FAIL]}  WARN={totals[WARN]}")

    # ---- Optional Markdown report ----
    if args.report:
        md = build_report_md(args.dd, args.spec, check_list, totals)
        Path(args.report).write_text(md)
        print(f"\nReport written to: {args.report}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
