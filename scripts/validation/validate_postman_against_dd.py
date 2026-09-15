#!/usr/bin/env python3
"""
validate_postman_against_dd.py — Detailed Postman-to-DD validator.

Validates generated Postman collection request bodies directly against the EBNF
Data Dictionary, adding four checks that no existing validator covers:

  1. FIELD  — every JSON key in a request body must be a known DD rule name (or a
              tagged-union string-literal discriminator like "creditCard"). Catches
              phantom fields, camelCase drift, and renamed rules.

  2. ENUM   — enum field values (mailClass, color, paperType, envelope, …) must match
              DD enum literals in test collections. Catches "firstClass" vs
              "first_class" drift and invalid values that would be rejected by the API.

  3. RANGE  — numeric fields with constraints (month 1–12, year 2000–2099, quantity ≥1)
              are validated when real values are present. Loaded from x-numeric-constraints
              in the OpenAPI spec so the script stays in sync with the spec.

  4. CROSS  — cross-field constraints in jobOptions are enforced. Loaded from
              x-valid-combinations in the OpenAPI spec:
                • color=black_and_white  → paperType ∈ {white, white_24, ivory}
                • mailClass=non_profit   → documentClass ∈ {letter, flat}
                • envelope=none          → layout ∈ {address_on_first_page, address_on_back_page}

Complement to the existing validators:
  • validate_collections_against_spec.py — structural (required/oneOf/properties); skips enums
  • validate_collections_deep.py         — deep spec walk; checks unknown fields vs spec (not DD)
  • validate_spec_against_dd.py          — spec vs DD (not collections vs DD)

The EBNF is parsed directly, so this script catches drift even before the spec is regenerated.
Placeholder values (<String>, <Integer>, etc.) are intentionally skipped on checks 2, 3, and 4
so the linked/type collections never produce false positives.

Usage:
  python3 scripts/validation/validate_postman_against_dd.py
  python3 scripts/validation/validate_postman_against_dd.py --exit-status
  python3 scripts/validation/validate_postman_against_dd.py --verbose
  python3 scripts/validation/validate_postman_against_dd.py --collections path/to/col.json
  python3 scripts/validation/validate_postman_against_dd.py --report reports/postman-vs-dd.md

  make validate-postman-against-dd

Exit code:
  0 — no FAIL findings
  1 — one or more FAIL findings (when --exit-status is given)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    # fall back to the project venv
    _venv_site = Path(__file__).resolve().parent.parent / "python_env" / "e2o.venv" / "lib"
    _candidates = list(_venv_site.glob("python*/site-packages"))
    if _candidates:
        sys.path.insert(0, str(_candidates[0]))
    import yaml

# ---------------------------------------------------------------------------
# Paths (sourced from env so Makefile can override without duplication)
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent.parent

_DD_REL    = os.environ.get("DD_EBNF_FILE",               "data_dictionary/c2mapiv2-dd.ebnf")
_SPEC_REL  = os.environ.get("C2MAPIV2_OPENAPI_SPEC",       "openapi/c2mapiv2-openapi-spec-final.yaml")
_GEN_REL   = os.environ.get("POSTMAN_GENERATED_DIR",       "postman/generated")
_API_NAME  = os.environ.get("C2MAPIV2_POSTMAN_API_NAME_KC", "c2mapiv2")

DEFAULT_DD   = (Path(_DD_REL)   if Path(_DD_REL).is_absolute()   else REPO / _DD_REL)
DEFAULT_SPEC = (Path(_SPEC_REL) if Path(_SPEC_REL).is_absolute() else REPO / _SPEC_REL)
DEFAULT_GEN  = (Path(_GEN_REL)  if Path(_GEN_REL).is_absolute()  else REPO / _GEN_REL)

_COLLECTION_BASENAMES = [
    f"{_API_NAME}-linked-collection-flat.json",
    f"{_API_NAME}-test-collection-flat.json",
    f"{_API_NAME}-getting-started-linked-collection.json",
    f"{_API_NAME}-getting-started-test-collection.json",
]

# Placeholder pattern — values like <String>, <Integer>, <oneOf>
PLACEHOLDER = re.compile(r"<[^>]+>")

# EBNF rules in the commented-out Apple Pay / Google Pay blocks — excluded from analysis
_COMMENTED_OUT_RULES: FrozenSet[str] = frozenset({
    "applePayDetails", "applePayToken", "paymentData", "paymentMethod",
    "displayName", "network", "cardTypeApplePay", "transactionAmount",
    "currencyCode", "transactionIdentifier", "billingContact", "givenName",
    "familyName", "emailAddress", "phoneNumber", "addressLines", "locality",
    "administrativeArea", "postalCode", "countryCode",
    "googlePayDetails", "paymentMethodData", "description", "type", "info",
    "cardNetwork", "cardDetails", "tokenizationData", "tokenizationType",
    "token", "billingAddress", "name", "email", "sortingCode",
})

# ---------------------------------------------------------------------------
# EBNF parsing  (reuses the same approach as validate_spec_against_dd.py)
# ---------------------------------------------------------------------------

def _strip_block_comments(text: str) -> str:
    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)


def _extract_rules(ebnf_text: str) -> Dict[str, str]:
    """Return {rule_name: normalised_body} for every rule after comment stripping."""
    clean = _strip_block_comments(ebnf_text)
    rules: Dict[str, str] = {}
    for chunk in clean.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        eq = chunk.index("=")
        name = chunk[:eq].strip()
        body = " ".join(chunk[eq + 1:].split())
        if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name) and body:
            rules[name] = body
    return rules


def _classify(body: str) -> str:
    """
    Classify a rule body as:
      enum     — all alternatives are "quoted" strings
      primitive — exactly string / integer / number
      alias    — single bare identifier (a = b)
      array    — { something }
      object   — contains + (named fields, may include optionals)
      tagged   — contains + with at least one "quoted" literal (discriminator)
      oneof    — alternatives of named rules (a | b | c)
      unknown
    """
    if body in ("string", "integer", "number"):
        return "primitive"
    parts = [p.strip() for p in body.split("|")]
    if len(parts) > 1 and all(re.match(r'^"[^"]+"$', p) for p in parts):
        return "enum"
    if re.match(r"^\{[^{}]+\}$", body):
        return "array"
    if "+" in body:
        return "tagged" if re.search(r'"[^"]+"', body) else "object"
    if "|" in body:
        return "oneof"
    if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", body):
        return "alias"
    return "unknown"


def _enum_values(body: str) -> List[str]:
    return [m.group(1) for m in re.finditer(r'"([^"]+)"', body)]


def _string_literals_in_body(body: str) -> List[str]:
    """Quoted string literals that appear as tagged discriminators."""
    return [m.group(1) for m in re.finditer(r'"([^"]+)"', body)]


def _oneof_variants(body: str) -> List[str]:
    """Bare identifiers from a pure oneof body (a | b | c)."""
    return [p.strip() for p in body.split("|") if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", p.strip())]


# ---------------------------------------------------------------------------
# Build working indexes from parsed rules
# ---------------------------------------------------------------------------

def _build_indexes(rules: Dict[str, str]) -> Tuple[
    Dict[str, List[str]],  # enum_map:  rule → [allowed_value, ...]
    Dict[str, List[str]],  # union_map: rule → [variant_name, ...]
    Set[str],              # all_rule_names
    Set[str],              # string_literal_keys (tagged discriminators like "creditCard")
]:
    enum_map: Dict[str, List[str]] = {}
    union_map: Dict[str, List[str]] = {}
    string_literal_keys: Set[str] = set()

    for name, body in rules.items():
        cls = _classify(body)
        if cls == "enum":
            enum_map[name] = _enum_values(body)
        elif cls == "oneof":
            union_map[name] = _oneof_variants(body)
        elif cls in ("tagged", "object", "array", "alias"):
            # Collect quoted-string literals used as JSON discriminator keys
            for lit in _string_literals_in_body(body):
                string_literal_keys.add(lit)

    return enum_map, union_map, set(rules.keys()), string_literal_keys


def _expand_union_json_keys(
    rule: str,
    rules: Dict[str, str],
    union_map: Dict[str, List[str]],
    _seen: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Return ALL valid JSON keys that can appear as the single key inside a
    oneOf wrapper value for `rule`.  Expands transitively through nested
    union rules and resolves tagged discriminators to their string literals.

    Example:
      docSourceAll  →  {requestIdSource, documentIdSource, urlSource,
                        zipDocumentIdSource, zipRequestIdSource,
                        docSourceStandard, docSourceZipFile}
    """
    if _seen is None:
        _seen = set()
    if rule in _seen:
        return set()
    _seen.add(rule)

    variants = union_map.get(rule, [])
    keys: Set[str] = set()

    for v in variants:
        body = rules.get(v, "")
        cls = _classify(body) if body else "unknown"

        if cls == "oneof":
            # Nested union — recurse, but also include the intermediate rule name
            keys.add(v)
            keys |= _expand_union_json_keys(v, rules, union_map, _seen)
        elif cls == "tagged":
            # Tagged discriminator: valid JSON key is the first quoted string
            lits = _string_literals_in_body(body)
            if lits:
                keys.add(lits[0])
            else:
                keys.add(v)
        else:
            # Leaf variant (object, alias, array, primitive) — JSON key = rule name
            keys.add(v)

    return keys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_placeholder(val) -> bool:
    if isinstance(val, str):
        return bool(PLACEHOLDER.search(val))
    return False


def _has_any_placeholder(obj) -> bool:
    """True if any string value in a nested structure is a placeholder."""
    if isinstance(obj, str):
        return _is_placeholder(obj)
    if isinstance(obj, dict):
        return any(_has_any_placeholder(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_any_placeholder(v) for v in obj)
    return False


# ---------------------------------------------------------------------------
# Check 1: Field name validity  (key ∈ DD rule names ∪ tagged literals)
# ---------------------------------------------------------------------------

def check_field_names(
    body: dict,
    all_rule_names: Set[str],
    string_literal_keys: Set[str],
) -> List[Tuple[str, str, str]]:
    """
    Return list of (path, key, reason) for every JSON key that is not a known
    DD rule name and not a tagged-union string-literal discriminator.

    Covers all collections (placeholders are irrelevant for key names).
    """
    valid_keys = all_rule_names | string_literal_keys
    findings: List[Tuple[str, str, str]] = []

    def walk(obj, loc: str):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k not in valid_keys:
                    findings.append((loc, k, "not a DD rule name or tagged discriminator"))
                walk(v, f"{loc}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{loc}[{i}]")

    walk(body, "body")
    return findings


# ---------------------------------------------------------------------------
# Check 2: Enum value correctness  (skips placeholders)
# ---------------------------------------------------------------------------

def check_enum_values(
    body: dict,
    enum_map: Dict[str, List[str]],
) -> List[Tuple[str, str, str, str]]:
    """
    Return list of (path, field, actual_value, allowed_values_str) for every
    non-placeholder enum field whose value is not in the DD enum list.
    """
    findings: List[Tuple[str, str, str, str]] = []

    def walk(obj, loc: str):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in enum_map and not _is_placeholder(v) and isinstance(v, str):
                    allowed = enum_map[k]
                    if v not in allowed:
                        findings.append((
                            loc, k, v,
                            " | ".join(f'"{x}"' for x in allowed),
                        ))
                walk(v, f"{loc}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{loc}[{i}]")

    walk(body, "body")
    return findings


# ---------------------------------------------------------------------------
# Check 3: Numeric range validity  (skips placeholders)
# ---------------------------------------------------------------------------

def check_numeric_ranges(
    body: dict,
    numeric_constraints: Dict[str, dict],
) -> List[Tuple[str, str, object, str]]:
    """
    Return list of (path, field, actual_value, constraint_desc) for numeric
    fields that violate their min/max constraints.
    """
    findings: List[Tuple[str, str, object, str]] = []

    def walk(obj, loc: str):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in numeric_constraints and not _is_placeholder(v):
                    if isinstance(v, (int, float)):
                        nc = numeric_constraints[k]
                        mn, mx = nc.get("minimum"), nc.get("maximum")
                        if mn is not None and v < mn:
                            findings.append((loc, k, v, f"minimum {mn}"))
                        elif mx is not None and v > mx:
                            findings.append((loc, k, v, f"maximum {mx}"))
                walk(v, f"{loc}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{loc}[{i}]")

    walk(body, "body")
    return findings


# ---------------------------------------------------------------------------
# Check 4: Cross-field constraint validity  (skips any block with placeholders)
# ---------------------------------------------------------------------------

def check_cross_field_constraints(
    body: dict,
    valid_combinations: List[dict],
) -> List[Tuple[str, str, str, str, str]]:
    """
    Return list of (path, when_field, when_value, then_field, then_values_str)
    for every jobOptions block that violates an x-valid-combinations rule.

    Skips any jobOptions block that contains placeholder values.
    """
    findings: List[Tuple[str, str, str, str, str]] = []

    def check_block(opts: dict, loc: str):
        if _has_any_placeholder(opts):
            return
        for rule in valid_combinations:
            wf   = rule.get("when_field")
            wv   = rule.get("when_value")
            tf   = rule.get("then_field")
            tvs  = rule.get("then_values", [])
            if wf not in opts or tf not in opts:
                continue
            if opts[wf] == wv and opts[tf] not in tvs:
                findings.append((
                    loc, wf, wv, tf,
                    " | ".join(f'"{v}"' for v in tvs),
                ))

    def walk(obj, loc: str):
        if isinstance(obj, dict):
            if "jobOptions" in obj and isinstance(obj["jobOptions"], dict):
                check_block(obj["jobOptions"], f"{loc}.jobOptions")
            for k, v in obj.items():
                walk(v, f"{loc}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{loc}[{i}]")

    walk(body, "body")
    return findings


# ---------------------------------------------------------------------------
# Orchestration: run all checks on one request item
# ---------------------------------------------------------------------------

Finding = Dict  # { check, path, field, detail, severity }


def _finding(check: str, path: str, field: str, detail: str, severity: str = "FAIL") -> Finding:
    return {"check": check, "path": path, "field": field, "detail": detail, "severity": severity}


def _url_path_from_postman(request: dict) -> str:
    """Extract a normalised /a/b/c path string from a Postman request object."""
    url = request.get("url", {})
    if isinstance(url, dict):
        parts = url.get("path", [])
        return "/" + "/".join(str(p) for p in parts) if parts else "/"
    # fallback for string URL
    raw = str(url)
    if "://" in raw:
        try:
            return "/" + raw.split("//", 1)[1].split("/", 1)[1].split("?")[0]
        except IndexError:
            pass
    return raw


def audit_item(
    body: dict,
    all_rule_names: Set[str],
    string_literal_keys: Set[str],
    enum_map: Dict[str, List[str]],
    numeric_constraints: Dict[str, dict],
    valid_combinations: List[dict],
    url_path: str = "",
) -> List[Finding]:
    results: List[Finding] = []

    # FIELD check is scoped to job submission endpoints only.
    # Auth endpoints (/auth/*) use OAuth2/overlay fields (grant_type, client_id, …)
    # that are intentionally outside the EBNF DD scope.
    is_auth_endpoint = url_path.startswith("/auth/") or "/auth/" in url_path

    if not is_auth_endpoint:
        for path, key, reason in check_field_names(body, all_rule_names, string_literal_keys):
            results.append(_finding("FIELD", path, key, reason))

    for path, field, actual, allowed in check_enum_values(body, enum_map):
        results.append(_finding(
            "ENUM", path, field,
            f"value {actual!r} not in DD enum — allowed: {allowed}",
        ))

    for path, field, value, constraint in check_numeric_ranges(body, numeric_constraints):
        results.append(_finding(
            "RANGE", path, field,
            f"value {value} violates {constraint}",
        ))

    for path, wf, wv, tf, tvs in check_cross_field_constraints(body, valid_combinations):
        results.append(_finding(
            "CROSS", path, wf,
            f"when {wf}={wv!r} the field {tf} must be one of {tvs}",
        ))

    return results


# ---------------------------------------------------------------------------
# Collection walking
# ---------------------------------------------------------------------------

def _collect_requests(items: list):
    """Yield every leaf request item, recursively handling folder nesting."""
    for item in items:
        if "request" in item:
            yield item
        if "item" in item:
            yield from _collect_requests(item["item"])


def audit_collection(
    col_path: Path,
    all_rule_names: Set[str],
    string_literal_keys: Set[str],
    enum_map: Dict[str, List[str]],
    numeric_constraints: Dict[str, dict],
    valid_combinations: List[dict],
) -> Tuple[int, int, List[Tuple[str, List[Finding]]]]:
    """
    Audit a single collection file.

    Returns (checked_count, skipped_count, [(request_name, [Finding], ...)])
    """
    with open(col_path) as f:
        col = json.load(f)

    checked = 0
    skipped = 0
    per_request: List[Tuple[str, List[Finding]]] = []

    for req in _collect_requests(col.get("item", [])):
        name    = req.get("name", "<unnamed>")
        request = req.get("request", {})
        method  = request.get("method", "")
        raw     = request.get("body", {}).get("raw", "")

        if not raw or method.upper() not in ("POST", "PUT", "PATCH"):
            skipped += 1
            continue

        try:
            body = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            skipped += 1
            continue

        if not isinstance(body, dict):
            skipped += 1
            continue

        url_path = _url_path_from_postman(request)

        findings = audit_item(
            body, all_rule_names, string_literal_keys,
            enum_map, numeric_constraints, valid_combinations,
            url_path=url_path,
        )
        per_request.append((name, findings))
        checked += 1

    return checked, skipped, per_request


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

CHECK_LABELS = {
    "FIELD": "1. Unknown field names",
    "ENUM":  "2. Enum value correctness",
    "RANGE": "3. Numeric range violations",
    "CROSS": "4. Cross-field constraint violations",
}

SEVERITY_ICON = {"FAIL": "❌", "WARN": "⚠️ ", "PASS": "✅"}


def _tally(per_request: List[Tuple[str, List[Finding]]]) -> Dict[str, int]:
    counts: Dict[str, int] = {"FIELD": 0, "ENUM": 0, "RANGE": 0, "CROSS": 0}
    for _, findings in per_request:
        for f in findings:
            counts[f["check"]] = counts.get(f["check"], 0) + 1
    return counts


def print_collection_report(
    col_name: str,
    checked: int,
    skipped: int,
    per_request: List[Tuple[str, List[Finding]]],
    verbose: bool,
) -> int:
    """Print findings for one collection. Return total FAIL count."""
    total_findings = sum(len(fs) for _, fs in per_request)
    icon = "✅" if total_findings == 0 else "❌"
    counts = _tally(per_request)

    print(f"\n{icon} {col_name}  (checked={checked} skipped={skipped})")
    print(
        f"   FIELD={counts.get('FIELD',0)}  "
        f"ENUM={counts.get('ENUM',0)}  "
        f"RANGE={counts.get('RANGE',0)}  "
        f"CROSS={counts.get('CROSS',0)}"
    )

    if total_findings == 0 and not verbose:
        return 0

    # Group findings by check type for readability
    by_check: Dict[str, List[Tuple[str, Finding]]] = {k: [] for k in CHECK_LABELS}
    for req_name, findings in per_request:
        for f in findings:
            by_check[f["check"]].append((req_name, f))

    for check_key, label in CHECK_LABELS.items():
        items = by_check.get(check_key, [])
        if not items and not verbose:
            continue
        sub_icon = "✅" if not items else "❌"
        print(f"\n   {sub_icon} {label}  ({len(items)} finding{'s' if len(items) != 1 else ''})")
        for req_name, f in items:
            print(f"      [{req_name}] {f['path']}.{f['field']}: {f['detail']}")

    return total_findings


def build_report_md(
    dd_path: str,
    spec_path: str,
    results: List[Tuple[str, int, int, int, Dict[str, int]]],
    grand_total: int,
) -> str:
    lines = [
        "# Postman Collections vs EBNF DD — Validation Report",
        "",
        f"**DD**: `{dd_path}`  ",
        f"**Spec**: `{spec_path}` (for numeric and cross-field constraints)",
        "",
        f"**GRAND TOTAL findings: {grand_total}**",
        "",
        "| Collection | Checked | Skipped | FIELD | ENUM | RANGE | CROSS | Total |",
        "|-----------|---------|---------|-------|------|-------|-------|-------|",
    ]
    for col_name, checked, skipped, total, counts in results:
        lines.append(
            f"| `{col_name}` | {checked} | {skipped} | "
            f"{counts.get('FIELD',0)} | {counts.get('ENUM',0)} | "
            f"{counts.get('RANGE',0)} | {counts.get('CROSS',0)} | {total} |"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Postman collection bodies directly against the EBNF Data Dictionary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dd",
        default=str(DEFAULT_DD),
        help="Path to EBNF Data Dictionary (default: data_dictionary/c2mapiv2-dd.ebnf)",
    )
    parser.add_argument(
        "--spec",
        default=str(DEFAULT_SPEC),
        help="Path to OpenAPI spec for numeric/cross-field constraints (default: openapi/c2mapiv2-openapi-spec-final.yaml)",
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        metavar="FILE",
        default=None,
        help="Collection JSON files to validate (default: all 4 canonical collections in postman/generated/)",
    )
    parser.add_argument(
        "--exit-status",
        action="store_true",
        help="Exit 1 if any FAIL findings are found",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print passing collections and checks too",
    )
    parser.add_argument(
        "--report",
        metavar="FILE",
        help="Write a Markdown summary report to FILE",
    )
    args = parser.parse_args()

    dd_path   = Path(args.dd)
    spec_path = Path(args.spec)

    # ── Validate inputs ────────────────────────────────────────────────────
    for p in (dd_path, spec_path):
        if not p.exists():
            print(f"❌ File not found: {p}", file=sys.stderr)
            return 2

    collections: List[Path] = []
    if args.collections:
        for c in args.collections:
            cp = Path(c)
            if not cp.exists():
                print(f"❌ Collection not found: {cp}", file=sys.stderr)
                return 2
            collections.append(cp)
    else:
        for bn in _COLLECTION_BASENAMES:
            cp = DEFAULT_GEN / bn
            if cp.exists():
                collections.append(cp)
        if not collections:
            print(
                f"⚠️  No canonical collections found in {DEFAULT_GEN}.\n"
                f"   Run 'make postman-build-golden-test-fixtures' first, or pass --collections.",
                file=sys.stderr,
            )
            return 2

    # ── Parse EBNF DD ──────────────────────────────────────────────────────
    print(f"📖 Loading DD: {dd_path}")
    raw_rules = _extract_rules(dd_path.read_text())
    rules = {k: v for k, v in raw_rules.items() if k not in _COMMENTED_OUT_RULES}

    type_counts: Dict[str, int] = {}
    for body in rules.values():
        t = _classify(body)
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"   {len(rules)} active rules  "
          + "  ".join(f"{t}×{n}" for t, n in sorted(type_counts.items())))

    enum_map, union_map, all_rule_names, string_literal_keys = _build_indexes(rules)

    print(
        f"   Enum rules: {len(enum_map)}  "
        f"Union rules: {len(union_map)}  "
        f"Tagged discriminators: {len(string_literal_keys)} {sorted(string_literal_keys)}"
    )

    # ── Load spec extensions ───────────────────────────────────────────────
    print(f"\n📋 Loading spec extensions: {spec_path}")
    spec = yaml.safe_load(spec_path.read_text())
    info = spec.get("info", {})

    numeric_constraints: Dict[str, dict] = info.get("x-numeric-constraints", {})
    valid_combinations: List[dict] = info.get("x-valid-combinations", [])
    print(f"   Numeric constraints: {len(numeric_constraints)} fields  "
          f"({', '.join(sorted(numeric_constraints.keys()))})")
    print(f"   Cross-field rules: {len(valid_combinations)}")

    # ── Audit collections ──────────────────────────────────────────────────
    print(f"\n{'='*68}")

    grand_total = 0
    md_rows: List[Tuple[str, int, int, int, Dict[str, int]]] = []

    for col_path in collections:
        checked, skipped, per_request = audit_collection(
            col_path,
            all_rule_names, string_literal_keys,
            enum_map, numeric_constraints, valid_combinations,
        )
        total = print_collection_report(
            col_path.name, checked, skipped, per_request, args.verbose
        )
        grand_total += total
        md_rows.append((
            col_path.name, checked, skipped, total, _tally(per_request)
        ))

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*68}")
    overall_icon = "✅" if grand_total == 0 else "❌"
    print(f"{overall_icon} GRAND TOTAL — {grand_total} finding(s) across {len(collections)} collection(s)")
    if grand_total > 0:
        print(
            "   Checks performed:\n"
            "     FIELD — JSON key not in EBNF rule names\n"
            "     ENUM  — enum field value not in DD enum list\n"
            "     RANGE — numeric value outside spec constraint range\n"
            "     CROSS — cross-field jobOptions constraint violation"
        )

    # ── Markdown report ────────────────────────────────────────────────────
    if args.report:
        md = build_report_md(str(dd_path), str(spec_path), md_rows, grand_total)
        Path(args.report).write_text(md)
        print(f"\nReport written to: {args.report}")

    return 1 if (args.exit_status and grand_total > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
