#!/usr/bin/env python3
"""
generate_dd_table.py — Generate data dictionary tables from the EBNF.

Reads data_dictionary/c2mapiv2-dd.ebnf and produces four files:

  reports/data-dictionary-table.md           — one section per EBNF rule (type reference)
  reports/data-dictionary-table.csv          — flat CSV of the same
  reports/data-dictionary-endpoints-expanded.md  — each endpoint expanded to primitive leaves
  reports/data-dictionary-endpoints-expanded.csv — flat CSV of the same

Usage:
  python scripts/active/generate_dd_table.py [--ebnf PATH] [--output-dir DIR]
"""

import argparse
import csv
import io
import re
import sys
from pathlib import Path
try:
    import yaml as _yaml
except ImportError:
    _yaml = None

# ---------------------------------------------------------------------------
# Description fallback catalog.
# Checked by _desc() only when no (* @doc *) annotation exists in the EBNF DD.
#
# Contains ONLY entries for things that cannot carry @doc annotations:
#   (a) Endpoint param rules — these have @summary in the EBNF; kept here for
#       backwards compatibility in case parse_ebnf() is called before @doc extraction
#   (b) Bare primitive type names (string, integer, etc.) — not defined as EBNF rules
#   (c) Quoted-key payment variant discriminators ('"creditCard"' etc.) — not EBNF rules
#
# All other rules are now documented via (* @doc Text. *) annotations in the EBNF DD.
# ---------------------------------------------------------------------------
_DESC: dict[str, str] = {
    # Endpoint request body shapes (have @summary in EBNF)
    "submitDocParams":
        "Request body for POST /static — submit a single document to one or more recipients.",
    "submitSinglePdfAddressCaptureParams":
        "Request body for POST /static/address-capture — recipient addresses are captured "
        "from the document by OCR rather than provided inline.",
    "submitSinglePdfSplitParams":
        "Request body for POST /batch/split — split a single PDF into page ranges and mail "
        "each range to a different recipient.",
    "submitSinglePdfSplitAddressCaptureParams":
        "Request body for POST /batch/split/address-capture — page-range PDF split with "
        "recipient addresses captured externally (no inline addresses required).",
    "submitMultiDocMergeParams":
        "Request body for POST /mail-merge — merge multiple documents into one mailing "
        "sent to a single recipient.",
    "submitMultiZipParams":
        "Request body for POST /batch/zip — mail individual files from a ZIP archive, "
        "each file to its own recipient.",
    "submitMultiZipAddressCaptureParams":
        "Request body for POST /batch/zip/address-capture — ZIP-based mailing batch with "
        "recipient addresses captured externally.",
    # Bare primitive type names (shown as array-item elements in the type-reference table)
    "id":            "Integer identifier — alias for integer, used for all ID fields.",
    "number":        "Numeric value (integer or decimal).",
    "string":        "A plain text string value.",
    "integer":       "A whole-number integer value.",
    "boolean":       "A boolean true/false value.",
    # Payment variant type-discriminator keys (JSON property name that identifies the variant)
    '"creditCard"':  "JSON property key identifying the credit-card payment variant.",
    '"invoice"':     "JSON property key identifying the invoice payment variant.",
    '"ach"':         "JSON property key identifying the ACH bank-transfer payment variant.",
    '"userCredit"':  "JSON property key identifying the account-credit payment variant.",
}

# Populated by parse_ebnf() from (* @doc Text. *) preceding-line annotations in the EBNF DD.
# Checked first by _desc() before falling back to _DESC above.
_DOC_ANNOTATIONS: dict[str, str] = {}

# Which rules are the top-level endpoint param shapes and their endpoint path
_ENDPOINT_MAP: dict[str, tuple[str, str]] = {
    "submitDocParams":                        ("POST", "/static"),
    "submitSinglePdfAddressCaptureParams":    ("POST", "/static/address-capture"),
    "submitSinglePdfSplitParams":             ("POST", "/batch/split"),
    "submitSinglePdfSplitAddressCaptureParams": ("POST", "/batch/split/address-capture"),
    "submitMultiDocMergeParams":              ("POST", "/mail-merge"),
    "submitMultiZipParams":                   ("POST", "/batch/zip"),
    "submitMultiZipAddressCaptureParams":     ("POST", "/batch/zip/address-capture"),
}

PRIMITIVES = {"string", "integer", "id", "number", "boolean"}


# ---------------------------------------------------------------------------
# Spec-derived helpers
# ---------------------------------------------------------------------------

def _read_spec_title(spec_path: str) -> str | None:
    """Return the API title from the spec's info.title, or None on any error."""
    if _yaml is None:
        return None
    try:
        with open(spec_path) as f:
            spec = _yaml.safe_load(f)
        return (spec.get('info') or {}).get('title')
    except Exception:
        return None


def _load_endpoint_map_from_spec(spec_path: str) -> dict:
    """Derive {rule_name: (method, path)} from OpenAPI spec operationId fields.

    Falls back gracefully (returns {}) if yaml is unavailable or spec can't be read.
    """
    if _yaml is None:
        print("⚠️  PyYAML not available — cannot derive endpoint map from spec; using built-in _ENDPOINT_MAP", file=sys.stderr)
        return {}
    try:
        with open(spec_path) as f:
            spec = _yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️  Could not load spec '{spec_path}': {e} — using built-in _ENDPOINT_MAP", file=sys.stderr)
        return {}
    result = {}
    for path, path_item in (spec.get("paths") or {}).items():
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            op_id = operation.get("operationId")
            if op_id:
                result[op_id] = (method.upper(), path)
    return result


def _desc_completeness_check(rules: dict) -> None:
    """Warn about DD rules that have no @doc annotation or _DESC fallback entry."""
    missing = [name for name in rules if name not in _DOC_ANNOTATIONS and name not in _DESC]
    if missing:
        print(
            f"\n⚠️  {len(missing)} DD rules have no @doc annotation "
            f"(add (* @doc Description. *) in the EBNF DD to improve table quality):",
            file=sys.stderr,
        )
        for name in sorted(missing):
            print(f"   • {name}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _strip_comments(text: str) -> str:
    """Remove all (* ... *) block comments (handles multi-line)."""
    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)


def _extract_doc_annotations(text: str) -> dict[str, str]:
    """Pre-pass: extract (* @doc text *) annotations before comment stripping.

    Annotation placement (preceding-line, same pattern as @summary/@description):
        (* @doc Description text. *)
        ruleName = ...
    """
    doc_map: dict[str, str] = {}
    pattern = re.compile(
        r'\(\*\s*@doc\s+(.*?)\s*\*\)\s*\n\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=',
        re.DOTALL,
    )
    for m in pattern.finditer(text):
        doc_text = re.sub(r'\s+', ' ', m.group(1).strip())
        rule_name = m.group(2)
        doc_map[rule_name] = doc_text
    return doc_map


def _split_top_level(text: str, sep: str) -> list[str]:
    """Split text on `sep` only at bracket depth 0."""
    depth = 0
    parts: list[str] = []
    cur = ""
    for ch in text:
        if ch in "([{":
            depth += 1
            cur += ch
        elif ch in ")]}":
            depth -= 1
            cur += ch
        elif ch == sep and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def _classify(rhs: str) -> str:
    rhs = rhs.strip()
    if rhs in PRIMITIVES:
        return "primitive"
    # All alternatives are quoted string literals → enum
    alts = _split_top_level(rhs, "|")
    if len(alts) > 1 and all(re.fullmatch(r'"[^"]*"', a.strip()) for a in alts):
        return "enum"
    # Top-level | at depth 0 → union
    top_chars = ""
    depth = 0
    for ch in rhs:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0:
            top_chars += ch
    if "|" in top_chars:
        return "union"
    if "+" in top_chars:
        return "object"
    if rhs.startswith("{") and rhs.endswith("}"):
        return "array"
    return "alias"  # single rule reference or primitive alias


def _parse_elements(rhs: str, kind: str) -> list[dict]:
    """Return list of {name, required, elem_kind} dicts."""
    if kind == "object":
        elements = []
        for part in _split_top_level(rhs, "+"):
            part = part.strip()
            if part.startswith("[") and part.endswith("]"):
                inner = part[1:-1].strip()
                elements.append({"name": inner, "required": False, "elem_kind": "field"})
            elif part.startswith("{") and part.endswith("}"):
                inner = part[1:-1].strip()
                elements.append({"name": inner, "required": False, "elem_kind": "array"})
            elif part:
                # Remove inline comment fragments that slipped through
                part = re.sub(r"\(\*.*?\*\)", "", part).strip()
                if part:
                    elements.append({"name": part, "required": True, "elem_kind": "field"})
        return elements
    if kind == "union":
        elements = []
        for part in _split_top_level(rhs, "|"):
            part = part.strip()
            if part.startswith('"') and part.endswith('"'):
                elements.append({"name": part.strip('"'), "required": False, "elem_kind": "enum_value"})
            elif part:
                elements.append({"name": part, "required": False, "elem_kind": "variant"})
        return elements
    if kind == "enum":
        return [
            {"name": p.strip().strip('"'), "required": False, "elem_kind": "enum_value"}
            for p in _split_top_level(rhs, "|") if p.strip()
        ]
    if kind == "array":
        inner = rhs[1:-1].strip()
        return [{"name": inner, "required": False, "elem_kind": "array_item"}]
    if kind in ("primitive", "alias"):
        return [{"name": rhs.strip(), "required": True, "elem_kind": kind}]
    return []


def parse_ebnf(path: Path) -> dict[str, dict]:
    """Parse EBNF file and return dict of {rule_name: rule_info}."""
    global _DOC_ANNOTATIONS
    text = path.read_text(encoding="utf-8")
    # Extract @doc annotations BEFORE stripping comments (which removes all (* ... *) blocks)
    _DOC_ANNOTATIONS = _extract_doc_annotations(text)
    clean = _strip_comments(text)
    flat = re.sub(r"\s+", " ", clean).strip()

    rules: dict[str, dict] = {}
    # Match: name = rhs ;   (non-greedy RHS stops at first semicolon)
    for m in re.finditer(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*?)\s*;", flat):
        name = m.group(1).strip()
        rhs = m.group(2).strip()
        if name.startswith("HTTP_"):
            continue
        kind = _classify(rhs)
        rules[name] = {
            "rhs": rhs,
            "kind": kind,
            "elements": _parse_elements(rhs, kind),
        }
    return rules


# ---------------------------------------------------------------------------
# Type display helpers
# ---------------------------------------------------------------------------

def _display_type(name: str, rules: dict, depth: int = 0) -> str:
    """Return a human-readable type label for a rule name."""
    if depth > 5:
        return name
    if name in PRIMITIVES:
        return name
    if name not in rules:
        return name
    kind = rules[name]["kind"]
    if kind == "primitive":
        return rules[name]["rhs"]
    if kind == "enum":
        values = [e["name"] for e in rules[name]["elements"]]
        return "enum (" + " | ".join(values) + ")"
    if kind == "union":
        return "oneOf"
    if kind == "object":
        return "object"
    if kind == "array":
        items = rules[name]["elements"]
        inner = items[0]["name"] if items else "?"
        inner_type = _display_type(inner, rules, depth + 1)
        return f"{inner_type}[]"
    if kind == "alias":
        return _display_type(rules[name]["rhs"], rules, depth + 1)
    return name


def _desc(name: str) -> str:
    """Return a description for a rule or field name.

    Lookup order:
      1. @doc annotation from the EBNF DD (populated by parse_ebnf)
      2. _DESC fallback (endpoint params, quoted-key variants, primitives)
      3. Generic fallback

    Strips trailing [] array notation before each lookup so that 'tags[]'
    resolves to the description for 'tags'.
    """
    stripped = name.rstrip("]").rstrip("[").rstrip("]").rstrip("[")

    # 1. EBNF @doc annotation (single source of truth for all regular rules)
    if name in _DOC_ANNOTATIONS:
        return _DOC_ANNOTATIONS[name]
    if stripped != name and stripped in _DOC_ANNOTATIONS:
        return _DOC_ANNOTATIONS[stripped]

    # 2. Static fallback dict (endpoint params, primitives, quoted-key discriminators)
    if name in _DESC:
        return _DESC[name]
    if stripped != name and stripped in _DESC:
        return _DESC[stripped]

    return f"See EBNF rule `{name}`."


# ---------------------------------------------------------------------------
# Table row builder
# ---------------------------------------------------------------------------

_CATEGORY_ORDER = [
    "Endpoint",
    "Data Structure",
    "Union Type (oneOf)",
    "Array Type",
    "Enumeration",
    "Alias",
]

def _category(name: str, rules: dict) -> str:
    if name in _ENDPOINT_MAP:
        return "Endpoint"
    if re.match(r'^HTTP_\d{3}_', name):  # HTTP alias shortcuts — not real API fields
        return "__skip__"
    kind = rules[name]["kind"]
    if kind == "object":
        return "Data Structure"
    if kind == "union":
        return "Union Type (oneOf)"
    if kind == "array":
        return "Array Type"
    if kind == "enum":
        return "Enumeration"
    if kind in ("alias", "primitive"):
        return "Alias / Primitive"
    return "Other"


def build_rows(rules: dict) -> list[dict]:
    """
    Build the flat list of rows for the table.

    Each row: {component, category, endpoint, field, field_type, required, description}
    """
    rows: list[dict] = []

    # Sort rules: endpoints first (in path order), then by category, then alphabetically
    endpoint_names = list(_ENDPOINT_MAP.keys())
    non_endpoint_names = sorted(
        [n for n in rules if n not in _ENDPOINT_MAP and not re.match(r'^HTTP_\d{3}_', n)],
        key=lambda n: (_category(n, rules), n),
    )
    ordered = endpoint_names + non_endpoint_names

    for name in ordered:
        if name not in rules:
            continue
        cat = _category(name, rules)
        if cat == "__skip__":
            continue

        endpoint_label = ""
        if name in _ENDPOINT_MAP:
            method, path = _ENDPOINT_MAP[name]
            endpoint_label = f"{method} {path}"

        comp_desc = _desc(name)
        elements = rules[name]["elements"]

        if not elements or rules[name]["kind"] in ("primitive", "alias"):
            # Component row only — no child elements to expand
            rhs_type = _display_type(name, rules)
            rows.append({
                "component":   name,
                "category":    cat,
                "endpoint":    endpoint_label,
                "field":       "—",
                "field_type":  rhs_type,
                "required":    "—",
                "description": comp_desc,
            })
            continue

        # One header row for the component itself
        comp_type = {
            "object": "object",
            "union": "oneOf",
            "array": "array",
            "enum": "enum",
        }.get(rules[name]["kind"], rules[name]["kind"])

        rows.append({
            "component":   name,
            "category":    cat,
            "endpoint":    endpoint_label,
            "field":       "—",
            "field_type":  comp_type,
            "required":    "—",
            "description": comp_desc,
        })

        # One row per element
        for elem in elements:
            ename = elem["name"]
            ekind = elem["elem_kind"]

            if ekind == "enum_value":
                ftype = "string"
                req = "—"
                fdesc = ""
            elif ekind == "array_item":
                ftype = _display_type(ename, rules) + "[]"
                req = "—"
                fdesc = _desc(ename)
            elif ekind == "variant":
                ftype = _display_type(ename, rules)
                req = "—"
                fdesc = _desc(ename)
            else:  # field or array
                ftype = _display_type(ename, rules)
                if ekind == "array":
                    ftype = _display_type(ename, rules)
                req = "Required" if elem["required"] else "Optional"
                fdesc = _desc(ename)

            rows.append({
                "component":   name,
                "category":    cat,
                "endpoint":    endpoint_label,
                "field":       ename,
                "field_type":  ftype,
                "required":    req,
                "description": fdesc,
            })

    return rows


# ---------------------------------------------------------------------------
# Endpoint expanded breakdown — recursive leaf expansion
# ---------------------------------------------------------------------------

def _fmt_path(path: list) -> str:
    """
    Format a path list into a readable dotted string.

    Each element is (name, step_kind) where step_kind is "field" or "variant".
    Variants fold into the previous segment: foo[variant].bar
    """
    parts: list[str] = []
    for name, step_kind in path:
        if step_kind == "variant":
            if parts:
                parts[-1] += f"[{name}]"
            else:
                parts.append(f"[{name}]")
        else:
            parts.append(name)
    return ".".join(parts)


def _resolve_leaf_type(type_str: str, rules: dict, depth: int = 0) -> str:
    """Follow primitive/alias chains to get a final base type string."""
    if depth > 10:
        return type_str
    if type_str in ("string", "integer", "boolean", "number"):
        return type_str
    if type_str == "id":
        return "integer"
    if type_str not in rules:
        # Undefined field names (e.g. `company`) are implicitly strings.
        return "string"
    r = rules[type_str]
    if r["kind"] == "primitive":
        return _resolve_leaf_type(r["rhs"], rules, depth + 1)
    if r["kind"] == "alias":
        return _resolve_leaf_type(r["rhs"], rules, depth + 1)
    if r["kind"] == "enum":
        values = " | ".join(e["name"] for e in r["elements"])
        return f"enum: {values}"
    return type_str


def _req_label(is_required: bool, in_variant: bool) -> str:
    if not is_required:
        return "Optional"
    return "Required*" if in_variant else "Required"


def _add_leaf(path: list, type_str: str, is_required: bool, in_variant: bool,
              field_key: str, rows: list) -> None:
    rows.append({
        "path": _fmt_path(path),
        "type": type_str,
        "required": _req_label(is_required, in_variant),
        "description": _desc(field_key),
    })


def _expand_object_elements(
    elements: list, rules: dict, path: list,
    is_required: bool, in_variant: bool, rows: list, depth: int,
) -> None:
    """
    Expand object elements, handling the quoted-literal key pattern.

    In payment variants the EBNF encodes: "creditCard" + creditCardDetails
    — the quoted string is the JSON property key and the following rule is
    the value type nested under it.
    """
    i = 0
    while i < len(elements):
        elem = elements[i]
        name = elem["name"]
        elem_req = is_required and elem["required"]

        if name.startswith('"') and name.endswith('"'):
            # Quoted literal → JSON property key; next element is the value type.
            json_key = name[1:-1]
            if i + 1 < len(elements):
                val_elem = elements[i + 1]
                val_req = is_required and val_elem["required"]
                _expand_to_leaves(
                    val_elem["name"], rules,
                    path + [(json_key, "field")],
                    val_req, in_variant, rows, depth + 1,
                )
                i += 2  # consumed the key AND the value element
            else:
                # Lone discriminator literal (edge case — not seen in C2M EBNF)
                _add_leaf(path + [(json_key, "field")], f'"{json_key}"',
                          elem_req, in_variant, json_key, rows)
                i += 1
        else:
            _expand_to_leaves(
                name, rules, path + [(name, "field")],
                elem_req, in_variant, rows, depth + 1,
            )
            i += 1


def _expand_to_leaves(
    rule_name: str,
    rules: dict,
    path: list,          # list of (name, step_kind)
    is_required: bool,
    in_variant: bool,
    rows: list,
    depth: int = 0,
) -> None:
    """Recursively expand rule_name until every branch reaches a primitive leaf."""
    if depth > 25:
        return  # runaway-recursion guard

    # Bare primitive keywords — leaf immediately
    if rule_name in ("string", "integer", "boolean", "number"):
        field_key = path[-1][0] if path else rule_name
        _add_leaf(path, rule_name, is_required, in_variant, field_key, rows)
        return

    if rule_name not in rules:
        field_key = path[-1][0] if path else rule_name
        # Undefined field names (e.g. `company`) are implicitly strings.
        _add_leaf(path, "string", is_required, in_variant, field_key, rows)
        return

    rule = rules[rule_name]
    kind = rule["kind"]

    if kind == "primitive":
        # Named primitive rule (e.g. requestId = id, documentId = id).
        # The rule name is already a path segment (added by the caller).
        field_key = path[-1][0] if path else rule_name
        leaf_type = _resolve_leaf_type(rule["rhs"], rules)
        _add_leaf(path, leaf_type, is_required, in_variant, field_key, rows)

    elif kind == "enum":
        field_key = path[-1][0] if path else rule_name
        values = " | ".join(e["name"] for e in rule["elements"])
        _add_leaf(path, f"enum: {values}", is_required, in_variant, field_key, rows)

    elif kind == "object":
        _expand_object_elements(
            rule["elements"], rules, path, is_required, in_variant, rows, depth,
        )

    elif kind == "union":
        for elem in rule["elements"]:
            variant_name = elem["name"]
            _expand_to_leaves(
                variant_name, rules,
                path + [(variant_name, "variant")],
                is_required, True, rows, depth + 1,
            )

    elif kind == "array":
        item_name = rule["elements"][0]["name"] if rule["elements"] else None
        if item_name is None:
            return
        # Mark the current field as an array by appending [] to the last path segment.
        new_path = (
            path[:-1] + [(path[-1][0] + "[]", path[-1][1])]
            if path else []
        )
        _expand_to_leaves(item_name, rules, new_path, is_required, in_variant, rows, depth + 1)

    elif kind == "alias":
        target = rule["rhs"]
        if target not in rules or target in ("string", "integer", "boolean", "number"):
            # Alias to bare primitive keyword — scalar, no extra path segment
            field_key = path[-1][0] if path else rule_name
            leaf_type = _resolve_leaf_type(target, rules)
            _add_leaf(path, leaf_type, is_required, in_variant, field_key, rows)
        elif rules[target]["kind"] in ("object", "union", "array"):
            # Alias to a complex type — transparent; expand without adding target name.
            _expand_to_leaves(target, rules, path, is_required, in_variant, rows, depth + 1)
        else:
            # Alias to a named scalar/primitive rule — target name IS a JSON field key.
            _expand_to_leaves(
                target, rules,
                path + [(target, "field")],
                is_required, in_variant, rows, depth + 1,
            )


def build_endpoint_expanded_rows(rules: dict, endpoint_map: dict | None = None) -> dict:
    """
    Return {endpoint_rule_name: [leaf_rows]} for every endpoint in the given map.

    Each leaf row: {path, type, required, description}
    Falls back to the module-level _ENDPOINT_MAP if endpoint_map is not provided.
    """
    em = endpoint_map if endpoint_map is not None else _ENDPOINT_MAP
    result: dict = {}
    for rule_name in em:
        if rule_name not in rules:
            continue
        rule = rules[rule_name]
        rows: list[dict] = []
        _expand_object_elements(
            rule["elements"], rules, [],
            is_required=True, in_variant=False, rows=rows, depth=0,
        )
        result[rule_name] = rows
    return result


# ---------------------------------------------------------------------------
# Expanded endpoint writers
# ---------------------------------------------------------------------------

def write_endpoint_expanded_md(
    endpoint_rows: dict, out_path: "Path", ebnf_path: "Path",
    endpoint_map: dict | None = None, api_title: str | None = None,
) -> None:
    em = endpoint_map if endpoint_map is not None else _ENDPOINT_MAP
    _title = api_title or "C2M API v2"
    lines = [
        f"# {_title} — Endpoint Field Reference (Expanded to Primitives)",
        "",
        f"*Generated from `{ebnf_path.name}`. "
        "Edit `data_dictionary/c2mapiv2-dd.ebnf` to change the source of truth.*",
        "",
        "> Each endpoint is expanded to its leaf-level primitive fields.",
        "> **Field Path** uses dot notation; `[variant]` shows which `oneOf` branch a field",
        "> belongs to, and `[]` marks array fields.",
        ">",
        "> **Required** — must always be present.",
        "> **Required\\*** — required when the enclosing `[variant]` is selected.",
        "> **Optional** — may be omitted.",
        "",
    ]

    for rule_name in em:
        if rule_name not in endpoint_rows:
            continue
        method, ep_path = em[rule_name]
        rows = endpoint_rows[rule_name]

        lines += [
            "---",
            "",
            f"## `{method} {ep_path}`",
            "",
            f"*Rule: `{rule_name}`* — {_desc(rule_name)}",
            "",
        ]

        if not rows:
            lines += ["*(no fields)*", ""]
            continue

        lines.append(_md_row(["Field Path", "Type", "Required", "Description"]))
        lines.append(_md_row(["---", "---", "---", "---"]))
        for row in rows:
            lines.append(_md_row([
                f"`{row['path']}`",
                row["type"],
                row["required"],
                row["description"],
            ]))
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ {out_path}")


def write_endpoint_expanded_csv(
    endpoint_rows: dict, out_path: "Path", endpoint_map: dict | None = None,
) -> None:
    em = endpoint_map if endpoint_map is not None else _ENDPOINT_MAP
    fieldnames = ["method", "endpoint", "field_path", "description", "type", "required"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rule_name, rows in endpoint_rows.items():
            method, ep_path = em[rule_name]
            for row in rows:
                writer.writerow({
                    "method": method,
                    "endpoint": ep_path,
                    "field_path": row["path"],
                    "type": row["type"],
                    "required": row["required"],
                    "description": row["description"],
                })
    print(f"  ✅ {out_path}")


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------

def _md_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def write_markdown(rows: list[dict], out_path: Path, ebnf_path: Path, api_title: str | None = None) -> None:
    _title = api_title or "C2M API v2"
    lines = [
        f"# {_title} — Data Dictionary",
        "",
        f"*Generated from `{ebnf_path.name}`. "
        "Edit `data_dictionary/c2mapiv2-dd.ebnf` to change the source of truth.*",
        "",
    ]

    # Group rows by category, then by component
    from collections import OrderedDict
    by_cat: dict[str, dict[str, list[dict]]] = OrderedDict()
    for row in rows:
        cat = row["category"]
        comp = row["component"]
        by_cat.setdefault(cat, OrderedDict()).setdefault(comp, []).append(row)

    cat_order = [
        "Endpoint",
        "Data Structure",
        "Union Type (oneOf)",
        "Array Type",
        "Enumeration",
        "Alias / Primitive",
        "Other",
    ]

    for cat in cat_order:
        if cat not in by_cat:
            continue
        lines += [f"## {cat}s", ""]
        for comp, comp_rows in by_cat[cat].items():
            # Subheading: component name + endpoint path if applicable
            header_row = comp_rows[0]
            ep = f"  `{header_row['endpoint']}`" if header_row["endpoint"] else ""
            lines += [f"### `{comp}`{ep}", ""]
            # Component description (from the "—" row)
            comp_desc_row = next((r for r in comp_rows if r["field"] == "—"), None)
            if comp_desc_row and comp_desc_row["description"]:
                lines += [comp_desc_row["description"], ""]

            element_rows = [r for r in comp_rows if r["field"] != "—"]
            if not element_rows:
                continue

            lines.append(_md_row(["Field / Variant", "Type", "Required", "Description"]))
            lines.append(_md_row(["---", "---", "---", "---"]))
            for r in element_rows:
                lines.append(_md_row([
                    f"`{r['field']}`",
                    r["field_type"],
                    r["required"],
                    r["description"],
                ]))
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ {out_path}")


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def write_csv(rows: list[dict], out_path: Path) -> None:
    fieldnames = ["component", "category", "endpoint", "field", "description",
                  "field_type", "required"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✅ {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ebnf",
        default="data_dictionary/c2mapiv2-dd.ebnf",
        help="Path to the EBNF data dictionary file",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory for output files (default: reports/)",
    )
    parser.add_argument(
        "--spec",
        default=None,
        help="Path to generated OpenAPI spec YAML; when provided, derives _ENDPOINT_MAP "
             "from operationId fields instead of the built-in constant.",
    )
    args = parser.parse_args()

    ebnf_path = Path(args.ebnf)
    out_dir = Path(args.output_dir)

    if not ebnf_path.exists():
        print(f"❌ EBNF file not found: {ebnf_path}", file=sys.stderr)
        return 1

    # Derive the effective endpoint map — spec-provided takes precedence over built-in.
    # _category() and build_rows() still reference _ENDPOINT_MAP via the global; the
    # explicit `endpoint_map` param threads it to the expanded-endpoint writers below.
    api_title: str | None = None
    global _ENDPOINT_MAP
    if args.spec:
        api_title = _read_spec_title(args.spec)
        derived = _load_endpoint_map_from_spec(args.spec)
        if derived:
            _ENDPOINT_MAP = derived
        else:
            print("⚠️  Spec-derived endpoint map is empty — using built-in _ENDPOINT_MAP", file=sys.stderr)
    else:
        print(
            "⚠️  --spec not provided — using built-in _ENDPOINT_MAP which may be stale.\n"
            "    Pass --spec $(C2MAPIV2_OPENAPI_SPEC) to derive operationId→path mapping from the spec.",
            file=sys.stderr,
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"📖 Parsing {ebnf_path}...")
    rules = parse_ebnf(ebnf_path)
    print(f"   Found {len(rules)} rules.")

    _desc_completeness_check(rules)

    rows = build_rows(rules)
    components = len({r["component"] for r in rows})
    elements = len([r for r in rows if r["field"] != "—"])
    print(f"   Built {len(rows)} table rows ({components} components, {elements} elements).")

    print(f"📝 Writing type-reference tables to {out_dir}/")
    write_markdown(rows, out_dir / "data-dictionary-table.md", ebnf_path, api_title=api_title)
    write_csv(rows, out_dir / "data-dictionary-table.csv")

    print(f"🔍 Expanding endpoints to primitive leaves...")
    endpoint_rows = build_endpoint_expanded_rows(rules, endpoint_map=_ENDPOINT_MAP)
    total_leaf = sum(len(r) for r in endpoint_rows.values())
    print(f"   {len(endpoint_rows)} endpoints → {total_leaf} leaf-field rows.")
    write_endpoint_expanded_md(
        endpoint_rows, out_dir / "data-dictionary-endpoints-expanded.md", ebnf_path,
        endpoint_map=_ENDPOINT_MAP, api_title=api_title,
    )
    write_endpoint_expanded_csv(
        endpoint_rows, out_dir / "data-dictionary-endpoints-expanded.csv",
        endpoint_map=_ENDPOINT_MAP,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
