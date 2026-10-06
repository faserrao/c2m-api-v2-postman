#!/usr/bin/env python3
"""
validate_pipeline_consistency.py

End-to-end consistency gate for the DD → OpenAPI → Postman pipeline. Covers what the
request-body validators do not (see audit-reports/DD_SPEC_POSTMAN_CONSISTENCY_AUDIT_2026-10-05.md):

  Layer A  DD → spec, rule by rule. The expected JSON Schema for every EBNF rule is derived
           independently from the DD conventions + @structural roles (only the translator's
           parser is reused), then diffed against the spec. Also: endpoints, annotation
           blocks vs x- extensions and responses, @hint vs faker_hints.yaml, @doc, spec drift.
  Layer B  spec → every canonical Postman collection, request by request: paths, URL,
           headers, auth, bodies (jsonschema, placeholder-aware for typed collections),
           unknown fields, DD cross-field rules, saved response examples (status declared,
           body schema, errorCode/errorType vs DD map, tracking-ID format, originalRequest),
           placeholder residue, Newman status assertions.
  Layer C  spec-internal examples: presence and validity.

Severity: every finding category is an ERROR unless it is listed in KNOWN_OPEN with the
audit/decision ID that tracks it, in which case it is a WARN. When a KNOWN_OPEN entry no
longer produces findings it is reported as STALE so the list can be pruned.

Usage:
    python3 scripts/validation/validate_pipeline_consistency.py [--exit-status] [--report FILE]
Paths default to Makefile-provided env vars (see `make validate-pipeline-consistency`).
"""

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator
from jsonschema.validators import RefResolver

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "active"))
from ebnf_to_openapi_dynamic_v3 import EBNFToOpenAPITranslator, _extract_structural_annotations  # noqa: E402

CONTENT_TYPE_JSON = "application/json"
PRIMITIVES = {"string": "string", "integer": "integer", "number": "number", "boolean": "boolean"}
PLACEHOLDER = re.compile(r"^(<[^<>]+>|ph<.*>)$")
TRACKING_ID = re.compile(r"^TRK-\d{8}-[0-9A-F]{6}$")
UNRESOLVED_TOKEN = re.compile(r"\{[A-Za-z_]\w*\}")  # e.g. {mailClass_enum} left in a JSON string
HINT_TYPES = {"faker", "static", "random_int"}

# Collection label -> (file name suffix after "<api-name>-", typed?)
COLLECTIONS = {
    "Linked": ("linked-collection-flat.json", True),
    "Test": ("test-collection-flat.json", False),
    "GS-Linked": ("getting-started-linked-collection.json", True),
    "GS-Test": ("getting-started-test-collection.json", False),
    "Real-World": ("real-world-use-cases-collection.json", False),
}

# (category, scope) -> tracking reference. scope is a collection label, or "*" for any.
# Categories not listed here are ERRORs. Remove an entry as soon as its fix lands.
KNOWN_OPEN = {
    ("A-TAG-LITERAL-DROPPED", "*"): "X5 / decision D1 (payment type tags)",
    ("A-UNREACHABLE-RULE", "*"): "X6 / D2 (addressName orphan); multiDocJobs reserved for /static/multi; HTTP_* aliases",
    ("A-PRIMER-ENDPOINT-UNDEFINED", "*"): "/static/multi is PLANNED in the DD primer",
    ("A-VALID-COMBINATION-NOOP", "*"): "X11 / decision D5 (envelope=none rule)",
    ("A-HINT-INVALID-TYPE", "*"): "L1 (routingNumber @hint has no type)",
    ("A-HINT-EMPTY-STATIC", "*"): "L1 (address3 empty static hint)",
    ("A-DOC-NOT-IN-SPEC", "*"): "X4 (@doc not emitted as spec descriptions)",
    ("A-DOC-TYPE-CLAIM", "*"): "L2 / decision D6 (errorDetails object vs string)",
    ("A-DOC-CARDINALITY-UNENFORCED", "*"): "X9 / decision D4 (array minimums)",
    ("B-OPERATION-NOT-IN-COLLECTION", "GS-Linked"): "L10 (Getting Started has no auth endpoints)",
    ("B-OPERATION-NOT-IN-COLLECTION", "GS-Test"): "L10 (Getting Started has no auth endpoints)",
    ("B-OPERATION-NOT-IN-COLLECTION", "Real-World"): "L10 (Real-World covers 4 of 7 job endpoints)",
    ("B-NO-AUTH", "Real-World"): "L8 (Real-World has no auth / pre-request script)",
    ("B-MERGE-MINIMUM", "*"): "X9b / decision D4 (merge minimum 1 or 2)",
    ("B-PLACEHOLDER-IN-EXAMPLE", "Test"): "L6 (auth examples carry <dateTime>/<string>)",
    ("B-PLACEHOLDER-IN-EXAMPLE", "Real-World"): "X2 (saved responses copied from typed Linked)",
    ("B-FILLER-VALUE", "*"): "L7 (example_ filler values)",
    ("B-EXAMPLE-BODY-SCHEMA", "Real-World"): "X2 (saved responses copied from typed Linked)",
    ("B-EXAMPLE-ERROR-MAP", "Linked"): "X1 (converter synthesises error examples)",
    ("B-EXAMPLE-ERROR-COVERAGE", "Linked"): "X1 (converter writes one example per status, not per DD code)",
    ("B-EXAMPLE-ERROR-COVERAGE", "Real-World"): "X1/X2 (saved responses copied from Linked)",
    ("B-EXAMPLE-ERROR-MAP", "Real-World"): "X1/X2 (copied from Linked)",
    ("B-EXAMPLE-ORIGINAL-REQUEST", "Real-World"): "X2 (typed originalRequest bodies)",
    ("B-EXAMPLE-ORIGINAL-REQUEST", "Linked"): "X9b (merge minimum in saved examples)",
    ("B-EXAMPLE-ORIGINAL-REQUEST", "Test"): "L6 (random auth ttl_seconds can fall below 3600 — intermittent)",
    ("B-TEST-STATUS-ASSERTION", "*"): "X12 / decision D7 (global allowed-codes list)",
    ("C-REQUEST-EXAMPLE-MISSING", "*"): "C1 (no request-example generator for job endpoints)",
}


def is_placeholder(value):
    return isinstance(value, str) and bool(PLACEHOLDER.match(value))


class Findings:
    def __init__(self):
        self.items = collections.defaultdict(list)  # (category, scope) -> [msg]

    def add(self, category, scope, msg):
        self.items[(category, scope)].append(msg)

    @staticmethod
    def tracking(category, scope):
        return KNOWN_OPEN.get((category, scope)) or KNOWN_OPEN.get((category, "*"))

    def classified(self):
        errors, warns = {}, {}
        for key, msgs in self.items.items():
            (warns if self.tracking(*key) else errors)[key] = msgs
        used = {k for k in KNOWN_OPEN if any(
            c == k[0] and (k[1] == "*" or s == k[1]) for (c, s) in self.items)}
        stale = sorted(set(KNOWN_OPEN) - used)
        return errors, warns, stale


# --------------------------------------------------------------------------- #
# Schema helpers                                                              #
# --------------------------------------------------------------------------- #
class SpecTools:
    def __init__(self, spec):
        self.spec = spec
        self.resolver = RefResolver(base_uri="", referrer=spec)

    def deref(self, schema):
        while isinstance(schema, dict) and "$ref" in schema:
            node = self.spec
            for part in schema["$ref"].lstrip("#/").split("/"):
                node = node[part]
            schema = node
        return schema

    def _relevant(self, err, typed):
        """Errors not explained by placeholder values (typed collections only)."""
        if typed and is_placeholder(err.instance):
            return []
        if err.validator in ("oneOf", "anyOf"):
            if not err.context:
                return [err]
            by_branch = collections.defaultdict(list)
            for sub in err.context:
                by_branch[sub.schema_path[0]].append(sub)
            best = None
            for i in range(len(err.validator_value)):
                subs = [r for s in by_branch.get(i, []) for r in self._relevant(s, typed)]
                if not subs:
                    return []
                if best is None or len(subs) < len(best):
                    best = subs
            return best or [err]
        return [err]

    def errors(self, instance, schema, typed):
        out = set()
        for err in Draft7Validator(schema, resolver=self.resolver).iter_errors(instance):
            for r in self._relevant(err, typed):
                out.add(f"{'/'.join(map(str, r.absolute_path)) or '<root>'}: {r.message[:160]}")
        return sorted(out)

    def unknown_fields(self, instance, schema, typed, path=""):
        """Keys the (selected) schema does not declare — the spec sets no additionalProperties."""
        s = self.deref(schema)
        if isinstance(s, dict) and ("oneOf" in s or "anyOf" in s):
            if typed and is_placeholder(instance):
                return []
            branches = s.get("oneOf") or s.get("anyOf")
            ok = [b for b in branches if not self.errors(instance, b, typed)] or branches
            return min((self.unknown_fields(instance, b, typed, path) for b in ok), key=len)
        out = []
        if isinstance(instance, dict) and isinstance(s, dict) and "properties" in s:
            for k, v in instance.items():
                if k not in s["properties"]:
                    out.append(f"{path}/{k}")
                else:
                    out += self.unknown_fields(v, s["properties"][k], typed, f"{path}/{k}")
        elif isinstance(instance, list) and isinstance(s, dict) and "items" in s:
            for i, v in enumerate(instance):
                out += self.unknown_fields(v, s["items"], typed, f"{path}[{i}]")
        return out


def leaf_values(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaf_values(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaf_values(v, f"{path}[{i}]")
    else:
        yield path, obj


# --------------------------------------------------------------------------- #
# Layer A — DD → spec                                                          #
# --------------------------------------------------------------------------- #
class DDModel:
    def __init__(self, dd_path):
        self.text = Path(dd_path).read_text(encoding="utf-8")
        self.t = EBNFToOpenAPITranslator()
        self.t.parse_ebnf(self.text)
        self.rules = {n: p.expression for n, p in self.t.productions.items()}
        self.roles = _extract_structural_annotations(self.text)

    def role(self, name, r):
        return r in self.roles.get(name, set())

    def prim(self, name, seen=()):
        """(type, enum-or-None) if name resolves to a primitive/enum, else None."""
        if name in PRIMITIVES:
            return PRIMITIVES[name], None
        e = self.rules.get(name)
        if e is None or name in seen:
            return None
        if e["type"] == "symbol":
            return self.prim(e["name"], seen + (name,))
        if e["type"] == "alternation" and all(c["type"] == "literal" for c in e["choices"]):
            return "string", [c["value"] for c in e["choices"]]
        return None

    def field_schema(self, name):
        p = self.prim(name)
        if not p:
            return {"$ref": f"#/components/schemas/{name}"}
        s = {"type": p[0]}
        # Name-based format convention (e.g. url -> uri), applied by the translator (audit L5)
        fmt = self.t.format_mappings.get(name.lower())
        if fmt:
            s["format"] = fmt
        if p[1]:
            s["enum"] = p[1]
        s.update(self.t.numeric_constraints.get(name, {}))
        return s

    def branches(self, name):
        out = []
        for c in self.rules[name]["choices"]:
            cn = c["name"]
            if self.role(cn, "transparent_oneof_grouping") and self.rules.get(cn, {}).get("type") == "alternation":
                out += self.branches(cn)
            elif self.role(name, "named_wrapper_oneof"):
                out.append({"type": "object", "properties": {cn: {"$ref": f"#/components/schemas/{cn}"}},
                            "required": [cn]})
            else:
                out.append({"$ref": f"#/components/schemas/{cn}"})
        return out

    def expected(self, name):
        """Expected schema for a rule; '_equivalent_ref' marks alias-to-primitive rules where
        a $ref to the aliased primitive rule is an equivalent representation."""
        e = self.rules[name]
        ty = e["type"]
        if ty == "alternation":
            if all(c["type"] == "literal" for c in e["choices"]):
                return {"type": "string", "enum": [c["value"] for c in e["choices"]]}
            if all(c["type"] == "symbol" for c in e["choices"]):
                return {"oneOf": self.branches(name)}
            return {"_unsupported": "mixed alternation"}
        if ty == "symbol":
            tgt = e["name"]
            if self.role(name, "single_field_wrapper"):
                return {"type": "object", "properties": {tgt: self.field_schema(tgt)}, "required": [tgt]}
            if self.prim(name):
                s = self.field_schema(name)
                s.pop("format", None)  # the translator applies name formats to property usage only
                if tgt not in PRIMITIVES:
                    s["_equivalent_ref"] = f"#/components/schemas/{tgt}"
                return s
            return {"$ref": f"#/components/schemas/{tgt}"}
        if ty == "repeat":
            x = e["expression"]
            if x["type"] != "symbol":
                return {"_unsupported": "repeat of non-symbol"}
            return {"type": "array", "items": self.field_schema(x["name"])}
        if ty == "concatenation":
            props, req, lits = {}, [], []
            for it in e["items"]:
                if it["type"] == "symbol":
                    props[it["name"]] = self.field_schema(it["name"])
                    req.append(it["name"])
                elif it["type"] == "optional" and it["expression"]["type"] == "symbol":
                    props[it["expression"]["name"]] = self.field_schema(it["expression"]["name"])
                elif it["type"] == "literal":
                    lits.append(it["value"])
                else:
                    return {"_unsupported": f"concatenation item {it['type']}"}
            s = {"type": "object", "properties": props}
            if req:
                s["required"] = req
            if lits:
                s["_tag_literals"] = lits
            return s
        return {"_unsupported": ty}


def _strip(schema):
    if isinstance(schema, dict):
        return {k: _strip(v) for k, v in schema.items() if k not in ("description", "example", "examples", "title")}
    if isinstance(schema, list):
        return [_strip(v) for v in schema]
    return schema


def _diff(exp, act, path):
    if isinstance(exp, dict) and isinstance(act, dict):
        for k in sorted(set(exp) | set(act)):
            if k.startswith("_"):
                continue
            if k not in act:
                yield f"{path}.{k}: missing in spec (expected {json.dumps(exp[k])[:120]})"
            elif k not in exp:
                yield f"{path}.{k}: not derived from the DD ({json.dumps(act[k])[:120]})"
            elif k in ("required", "properties") and list(exp[k]) != list(act[k]):
                if set(exp[k]) != set(act[k]):
                    yield f"{path}.{k}: DD {list(exp[k])} spec {list(act[k])}"
                if k == "properties":
                    yield from _diff(exp[k], act[k], f"{path}.{k}")
            else:
                yield from _diff(exp[k], act[k], f"{path}.{k}")
    elif isinstance(exp, list) and isinstance(act, list):
        if len(exp) != len(act):
            yield f"{path}: DD has {len(exp)} entries, spec {len(act)}"
        else:
            for i, (x, y) in enumerate(zip(exp, act)):
                yield from _diff(x, y, f"{path}[{i}]")
    elif exp != act:
        yield f"{path}: DD {json.dumps(exp)} spec {json.dumps(act)}"


def check_dd_to_spec(dd, specs, faker_hints, F):
    spec = specs["final"]
    schemas = spec["components"]["schemas"]
    t = dd.t
    # A1 rule-by-rule structure
    for name in dd.rules:
        if name in PRIMITIVES:
            continue
        exp = dd.expected(name)
        if "_unsupported" in exp:
            F.add("A-UNSUPPORTED-DD-CONSTRUCT", "*", f"{name}: {exp['_unsupported']}")
            continue
        if name not in schemas:
            F.add("A-RULE-MISSING-FROM-SPEC", "*", name)
            continue
        act = _strip(schemas[name])
        if "_equivalent_ref" in exp and act == {"$ref": exp["_equivalent_ref"]}:
            continue
        for d in _diff(exp, act, name):
            F.add("A-RULE-STRUCTURE-MISMATCH", "*", d)
        if "_tag_literals" in exp:
            F.add("A-TAG-LITERAL-DROPPED", "*", f"{name}: DD literal(s) {exp['_tag_literals']} not in spec")
    # A2 reachability
    def refs(e, acc):
        if isinstance(e, dict):
            if e.get("type") == "symbol":
                acc.add(e["name"])
            for v in e.values():
                refs(v, acc)
        elif isinstance(e, list):
            for v in e:
                refs(v, acc)
        return acc
    reach, stack = set(), [ep.production_name for ep in t.endpoints] + ["standardResponse", "errorResponse"]
    while stack:
        n = stack.pop()
        if n in reach or n not in dd.rules:
            continue
        reach.add(n)
        stack += list(refs(dd.rules[n], set()))
    for n in sorted(set(dd.rules) - reach - set(PRIMITIVES)):
        F.add("A-UNREACHABLE-RULE", "*", n)
    for n in sorted({s for r in dd.rules.values() for s in refs(r, set())} - set(dd.rules) - set(PRIMITIVES)):
        F.add("A-UNDEFINED-SYMBOL", "*", n)
    # A3 endpoints
    ops = {(m, p): op for p, o in spec["paths"].items() for m, op in o.items()
           if m in ("get", "post", "put", "patch", "delete")}
    dd_eps = {(e.method.lower(), e.path): e for e in t.endpoints}
    for key, ep in dd_eps.items():
        op = ops.get(key)
        if op is None:
            F.add("A-ENDPOINT-MISSING-FROM-SPEC", "*", f"{key[0].upper()} {key[1]}")
            continue
        body = ((op.get("requestBody") or {}).get("content") or {}).get(CONTENT_TYPE_JSON, {}).get("schema", {})
        if body.get("$ref") != f"#/components/schemas/{ep.production_name}":
            F.add("A-ENDPOINT-BODY-MISMATCH", "*", f"{key}: {body} vs {ep.production_name}")
        if op.get("summary") != ep.summary or op.get("description") != ep.description:
            F.add("A-ENDPOINT-TEXT-MISMATCH", "*", f"{key}: summary/description differ from DD")
        if not (op.get("requestBody") or {}).get("required"):
            F.add("A-ENDPOINT-BODY-NOT-REQUIRED", "*", str(key))
    primer = dd.text.split("If you have never seen EBNF")[0]
    for p in re.findall(r"POST (/\S+)", primer):
        if ("post", p) not in dd_eps:
            F.add("A-PRIMER-ENDPOINT-UNDEFINED", "*", p)
    # A4 annotation blocks
    info = spec["info"]
    for ext, val in (("x-numeric-constraints", t.numeric_constraints), ("x-mutual-exclusion", t.mutual_exclusion_fields),
                     ("x-valid-combinations", t.valid_combinations), ("x-http-error-map", t.http_error_map)):
        if info.get(ext) != val:
            F.add("A-EXTENSION-MISMATCH", "*", f"{ext} differs from the DD annotation block")
    for r in t.valid_combinations:
        for fld, vals in ((r["when_field"], [r["when_value"]]), (r["then_field"], r["then_values"])):
            p = dd.prim(fld)
            if not p or not p[1]:
                F.add("A-VALID-COMBINATION-BAD-FIELD", "*", fld)
            elif any(v not in p[1] for v in vals):
                F.add("A-VALID-COMBINATION-BAD-VALUE", "*", f"{fld}: {[v for v in vals if v not in p[1]]}")
        p = dd.prim(r["then_field"])
        if p and p[1] and set(r["then_values"]) == set(p[1]):
            F.add("A-VALID-COMBINATION-NOOP", "*", json.dumps(r))
    codes, types = dd.prim("errorCode")[1], dd.prim("errorType")[1]
    mapped = collections.Counter(c for v in t.http_error_map.values() for c in v["errorCodes"])
    for st, v in t.http_error_map.items():
        if v["errorType"] not in types:
            F.add("A-ERROR-MAP-UNKNOWN-TYPE", "*", f"{st}: {v['errorType']}")
        for c in v["errorCodes"]:
            if c not in codes:
                F.add("A-ERROR-MAP-UNKNOWN-CODE", "*", f"{st}: {c}")
    for c in codes:
        if mapped[c] == 0:
            F.add("A-ERROR-CODE-UNMAPPED", "*", c)
    for (m, p), op in ops.items():
        if (m, p) not in dd_eps:
            continue
        for st, entry in t.http_error_map.items():
            r = op.get("responses", {}).get(st)
            if r is None:
                F.add("A-ERROR-STATUS-NOT-DECLARED", "*", f"{m.upper()} {p}: {st}")
                continue
            content = (r.get("content") or {}).get(CONTENT_TYPE_JSON, {})
            for ex in (content.get("examples") or {}).values():
                v = ex.get("value", {})
                if v.get("errorCode") not in entry["errorCodes"] or v.get("errorType") != entry["errorType"]:
                    F.add("A-SPEC-ERROR-EXAMPLE-MISMATCH", "*",
                          f"{m.upper()} {p} {st}: {v.get('errorType')}/{v.get('errorCode')}")
        for st in op.get("responses", {}):
            if not st.startswith("2") and st not in t.http_error_map:
                F.add("A-ERROR-STATUS-NOT-IN-DD", "*", f"{m.upper()} {p}: {st}")
    # A5 @hint → faker_hints.yaml
    hint_re = re.compile(r"^([a-zA-Z_]\w*)\s*=[^;]*;[^(\n]*\(\*\s*@hint\s+(.*?)\s*\*\)", re.M)
    dd_hints = {m.group(1): m.group(2) for m in hint_re.finditer(dd.text)}
    for n, h in dd_hints.items():
        parts = h.split()
        kind = parts[0] if parts else ""
        if kind not in HINT_TYPES:
            F.add("A-HINT-INVALID-TYPE", "*", f"{n}: '@hint {h}'")
        if kind == "static" and len(parts) < 2:
            F.add("A-HINT-EMPTY-STATIC", "*", n)
        if n not in faker_hints:
            F.add("A-HINT-NOT-IN-FAKER-HINTS", "*", n)
        p = dd.prim(n)
        if kind == "static" and p and n in faker_hints:
            val = faker_hints[n].get("value")
            if p[1] and val not in p[1]:
                F.add("A-HINT-VALUE-NOT-IN-ENUM", "*", f"{n}: {val!r}")
            if p[0] == "integer" and not isinstance(val, int):
                F.add("A-HINT-TYPE-MISMATCH", "*", f"{n}: {val!r}")
            nc = t.numeric_constraints.get(n, {})
            if isinstance(val, int) and (("minimum" in nc and val < nc["minimum"]) or ("maximum" in nc and val > nc["maximum"])):
                F.add("A-HINT-VIOLATES-CONSTRAINT", "*", f"{n}: {val}")
    for n in faker_hints:
        if n not in dd_hints:
            F.add("A-FAKER-HINT-WITHOUT-DD-HINT", "*", n)
    # A6 @doc
    doc_re = re.compile(r"\(\*\s*@doc\s+(.*?)\s*\*\)\s*\n\s*([a-zA-Z_]\w*)\s*=", re.S)
    docs = {m.group(2): m.group(1) for m in doc_re.finditer(dd.text)}
    in_spec = sum(1 for n in docs if isinstance(schemas.get(n), dict) and schemas[n].get("description"))
    if docs and in_spec < len(docs):
        F.add("A-DOC-NOT-IN-SPEC", "*", f"{len(docs) - in_spec} of {len(docs)} @doc descriptions not emitted")
    for n, d in docs.items():
        p = dd.prim(n)
        if "JSON object" in d and p and p[0] == "string":
            F.add("A-DOC-TYPE-CLAIM", "*", f"{n}: @doc says JSON object, DD type is string")
        if re.search(r"[Mm]inimum (one|two|\d)|at least", d) and "minItems" not in json.dumps(schemas.get(n, {})):
            F.add("A-DOC-CARDINALITY-UNENFORCED", "*", f"{n}: '{d[:70]}'")
    # A7 drift between spec files (DD-derived schemas only)
    for label in ("base", "final-with-examples"):
        other = specs[label]["components"]["schemas"]
        for n in dd.rules:
            if n in schemas and _strip(other.get(n)) != _strip(schemas.get(n)):
                F.add("A-SPEC-FILE-DRIFT", "*", f"{n}: final vs {label}")


# --------------------------------------------------------------------------- #
# Layer B — spec → collections                                                 #
# --------------------------------------------------------------------------- #
def cross_field_errors(body, info):
    """(category, message) pairs for DD cross-field rules."""
    out = []
    if not isinstance(body, dict):
        return out
    present = [f for f in info.get("x-mutual-exclusion", []) if f in body]
    if len(present) > 1:
        out.append(("B-MUTUAL-EXCLUSION", f"fields present together: {present}"))
    jo = body.get("jobOptions")
    if isinstance(jo, dict):
        for r in info.get("x-valid-combinations", []):
            got = jo.get(r["then_field"])
            if jo.get(r["when_field"]) == r["when_value"] and got not in r["then_values"] and not is_placeholder(got):
                out.append(("B-VALID-COMBINATION", f"{r['when_field']}={r['when_value']} but {r['then_field']}={got}"))
    for fld, val in body.items():
        if isinstance(val, list) and fld != "tags" and len(val) == 0:
            out.append(("B-EMPTY-ARRAY", f"{fld} is empty"))
        if isinstance(val, list):
            for i, j in enumerate(val):
                if isinstance(j, dict) and isinstance(j.get("startPage"), int) and isinstance(j.get("endPage"), int) \
                        and j["startPage"] > j["endPage"]:
                    out.append(("B-PAGE-RANGE", f"{fld}[{i}] startPage > endPage"))
    merge = body.get("mergeDocumentSource")
    if isinstance(merge, list) and len(merge) < 2:
        out.append(("B-MERGE-MINIMUM", f"mergeDocumentSource has {len(merge)} entr{'y' if len(merge) == 1 else 'ies'}"))
    return out


def details_problems(details):
    """Problems with an errorDetails string: must be JSON with no unresolved {token}s."""
    if not isinstance(details, str) or is_placeholder(details):
        return []
    out = []
    if UNRESOLVED_TOKEN.search(details):
        out.append(("UNRESOLVED-TOKEN", f"unresolved token {UNRESOLVED_TOKEN.search(details).group(0)}"))
    try:
        json.loads(details)
    except json.JSONDecodeError:
        out.append(("NOT-JSON", f"errorDetails is not valid JSON: {details[:80]!r}"))
    return out


def uses_dd_errors(op):
    """True when the operation's error responses use the DD errorResponse schema (job endpoints)."""
    for code, r in op.get("responses", {}).items():
        ref = ((r.get("content") or {}).get(CONTENT_TYPE_JSON, {}).get("schema") or {}).get("$ref", "")
        if not code.startswith("2") and ref.endswith("/errorResponse"):
            return True
    return False


def iter_requests(collection, folder=()):
    for it in collection.get("item", []):
        if "item" in it:
            yield from iter_requests(it, folder + (it.get("name") or "",))
        else:
            yield "/".join(f for f in folder if f), it


def url_path(url):
    if isinstance(url, dict):
        return re.sub(r"/:([A-Za-z_]\w*)", r"/{\1}", "/" + "/".join(url.get("path", [])))
    return None


def check_collection(label, collection, typed, spec, tools, F):
    info = spec["info"]
    error_map = info.get("x-http-error-map", {})
    ops = {(m, p): op for p, o in spec["paths"].items() for m, op in o.items()
           if m in ("get", "post", "put", "patch", "delete")}
    seen = collections.Counter()
    for folder, it in iter_requests(collection):
        req = it.get("request") or {}
        method = (req.get("method") or "").lower()
        url = req.get("url")
        path = url_path(url)
        tag = f"[{folder}] {it.get('name')}" if folder else str(it.get("name"))
        op = ops.get((method, path))
        if op is None:
            F.add("B-REQUEST-NOT-IN-SPEC", label, f"{tag}: {method.upper()} {path}")
            continue
        seen[(method, path)] += 1
        raw = url.get("raw", "") if isinstance(url, dict) else str(url)
        if not raw.startswith("{{baseUrl}}") or url.get("host") != ["{{baseUrl}}"]:
            F.add("B-URL-BASE", label, f"{tag}: {raw}")
        if re.sub(r"^\{\{baseUrl\}\}", "", raw).split("?")[0] != "/" + "/".join(url.get("path", [])):
            F.add("B-URL-RAW-PATH-MISMATCH", label, f"{tag}: {raw}")
        for q in url.get("query") or []:
            F.add("B-URL-QUERY-NOT-IN-SPEC", label, f"{tag}: {q.get('key')}")
        variables = {v.get("key"): v.get("value") for v in url.get("variable") or []}
        for pv in re.findall(r"\{(\w+)\}", path):
            if pv not in variables:
                F.add("B-URL-PATH-VARIABLE-UNDEFINED", label, f"{tag}: {pv}")
            elif not typed and is_placeholder(variables[pv]):
                F.add("B-PLACEHOLDER-IN-EXAMPLE", label, f"{tag}: url variable {pv}={variables[pv]}")
        headers = {h.get("key", "").lower(): h.get("value") for h in req.get("header") or [] if not h.get("disabled")}
        body_schema = ((op.get("requestBody") or {}).get("content") or {}).get(CONTENT_TYPE_JSON, {}).get("schema")
        if body_schema and headers.get("content-type") != CONTENT_TYPE_JSON:
            F.add("B-CONTENT-TYPE", label, f"{tag}: {headers.get('content-type')}")
        security = op.get("security", spec.get("security"))
        if security and not (req.get("auth") or collection.get("auth") or "authorization" in headers
                             or collection.get("event") or it.get("event")):
            F.add("B-NO-AUTH", label, f"{tag}: spec security {security}")
        # request body
        body_raw = (req.get("body") or {}).get("raw")
        body = None
        if body_schema and not body_raw:
            F.add("B-BODY-MISSING", label, tag)
        if not body_schema and body_raw and body_raw.strip():
            F.add("B-BODY-UNEXPECTED", label, tag)
        if body_schema and body_raw:
            try:
                body = json.loads(body_raw)
            except json.JSONDecodeError as e:
                F.add("B-BODY-NOT-JSON", label, f"{tag}: {e}")
        if body is not None:
            for e in tools.errors(body, body_schema, typed):
                F.add("B-BODY-SCHEMA", label, f"{tag}: {e}")
            for k in tools.unknown_fields(body, body_schema, typed):
                F.add("B-BODY-UNKNOWN-FIELD", label, f"{tag}: {k}")
            for cat, msg in cross_field_errors(body, info):
                F.add(cat, label, f"{tag}: {msg}")
            if not typed:
                for p_, v in leaf_values(body):
                    if is_placeholder(v):
                        F.add("B-PLACEHOLDER-IN-EXAMPLE", label, f"{tag}: body{p_}={v!r}")
                    elif isinstance(v, str) and v.startswith("example_"):
                        F.add("B-FILLER-VALUE", label, f"{tag}: body{p_}={v!r}")
        # saved response examples
        saved_pairs = set()
        for ex in it.get("response") or []:
            code, name = str(ex.get("code")), ex.get("name")
            where = f"{tag} / {name!r} ({code})"
            resp = op.get("responses", {}).get(code)
            if resp is None:
                F.add("B-EXAMPLE-STATUS-UNDECLARED", label, where)
            resp_schema = ((resp or {}).get("content") or {}).get(CONTENT_TYPE_JSON, {}).get("schema")
            ex_body = None
            if ex.get("body"):
                try:
                    ex_body = json.loads(ex["body"])
                except json.JSONDecodeError:
                    F.add("B-EXAMPLE-BODY-NOT-JSON", label, where)
            if ex_body is not None and resp_schema:
                for e in tools.errors(ex_body, resp_schema, typed):
                    F.add("B-EXAMPLE-BODY-SCHEMA", label, f"{where}: {e}")
                for k in tools.unknown_fields(ex_body, resp_schema, typed):
                    F.add("B-EXAMPLE-BODY-SCHEMA", label, f"{where}: unknown field {k}")
            if isinstance(ex_body, dict) and code in error_map:
                entry = error_map[code]
                ec, et = ex_body.get("errorCode"), ex_body.get("errorType")
                if (ec not in entry["errorCodes"] and not is_placeholder(ec)) or \
                        (et != entry["errorType"] and not is_placeholder(et)):
                    F.add("B-EXAMPLE-ERROR-MAP", label, f"{where}: {et}/{ec}")
                if not is_placeholder(ec):
                    saved_pairs.add((code, ec))
                for kind, msg in details_problems(ex_body.get("errorDetails")):
                    F.add(f"B-EXAMPLE-DETAILS-{kind}", label, f"{where}: {msg}")
                tid = ex_body.get("errorTrackingId")
                if isinstance(tid, str) and not is_placeholder(tid) and not TRACKING_ID.match(tid):
                    F.add("B-EXAMPLE-TRACKING-ID", label, f"{where}: {tid}")
            if not typed and ex_body is not None:
                for p_, v in leaf_values(ex_body):
                    if is_placeholder(v):
                        F.add("B-PLACEHOLDER-IN-EXAMPLE", label, f"{where}: response{p_}={v!r}")
            orig = ex.get("originalRequest") or {}
            if orig and (url_path(orig.get("url")), (orig.get("method") or "").lower()) != (path, method):
                F.add("B-EXAMPLE-ORIGINAL-REQUEST", label, f"{where}: targets another operation")
            orig_raw = (orig.get("body") or {}).get("raw")
            if orig_raw and body_schema:
                try:
                    orig_body = json.loads(orig_raw)
                except json.JSONDecodeError:
                    orig_body = None
                if orig_body is not None:
                    problems = tools.errors(orig_body, body_schema, typed)
                    problems += [f"unknown field {k}" for k in tools.unknown_fields(orig_body, body_schema, typed)]
                    problems += [m for _c, m in cross_field_errors(orig_body, info)]
                    for msg in problems:
                        F.add("B-EXAMPLE-ORIGINAL-REQUEST", label, f"{where}: {msg}")
        # Error-example coverage: when an operation carries DD-format error examples, every
        # (status, errorCode) pair the DD maps for its declared statuses must be present (N2)
        if saved_pairs and uses_dd_errors(op):
            expected = {(st, c) for st, entry in error_map.items() if st in op.get("responses", {})
                        for c in entry["errorCodes"]}
            missing = sorted(expected - saved_pairs)
            if missing:
                F.add("B-EXAMPLE-ERROR-COVERAGE", label,
                      f"{tag}: no saved example for {', '.join(f'{st} {c}' for st, c in missing)}")
        # Newman status assertions must match this operation's declared responses
        declared = set(op.get("responses", {}))
        for ev in it.get("event") or []:
            if ev.get("listen") != "test":
                continue
            src = "\n".join((ev.get("script") or {}).get("exec") or [])
            for arr in re.findall(r"\[(\s*\d{3}(?:\s*,\s*\d{3})+\s*)\]", src):
                codes = {c.strip() for c in arr.split(",")}
                if codes != declared:
                    F.add("B-TEST-STATUS-ASSERTION", label,
                          f"{tag}: accepts {sorted(codes - declared)} undeclared, rejects {sorted(declared - codes)} declared")
    for key in ops:
        if seen[key] == 0:
            F.add("B-OPERATION-NOT-IN-COLLECTION", label, f"{key[0].upper()} {key[1]}")


# --------------------------------------------------------------------------- #
# Layer C — spec examples                                                      #
# --------------------------------------------------------------------------- #
def check_spec_examples(spec, dd, F):
    resolver = RefResolver(base_uri="", referrer=spec)
    dd_eps = {(e.method.lower(), e.path) for e in dd.t.endpoints}
    for p, o in spec["paths"].items():
        for m, op in o.items():
            if (m, p) not in dd_eps:
                continue
            rb = ((op.get("requestBody") or {}).get("content") or {}).get(CONTENT_TYPE_JSON, {})
            if rb.get("schema") and "example" not in rb and not rb.get("examples"):
                F.add("C-REQUEST-EXAMPLE-MISSING", "*", f"{m.upper()} {p}")
            for code, r in op.get("responses", {}).items():
                c = (r.get("content") or {}).get(CONTENT_TYPE_JSON, {})
                values = ([c["example"]] if "example" in c else []) + [e.get("value") for e in (c.get("examples") or {}).values()]
                if c.get("schema") and not values:
                    F.add("C-RESPONSE-EXAMPLE-MISSING", "*", f"{m.upper()} {p} {code}")
                for v in values:
                    for e in Draft7Validator(c["schema"], resolver=resolver).iter_errors(v):
                        F.add("C-RESPONSE-EXAMPLE-INVALID", "*", f"{m.upper()} {p} {code}: {e.message[:120]}")
                    if isinstance(v, dict):
                        for kind, msg in details_problems(v.get("errorDetails")):
                            F.add(f"C-EXAMPLE-DETAILS-{kind}", "*", f"{m.upper()} {p} {code}: {msg}")


# --------------------------------------------------------------------------- #
def _env(name, default):
    return os.environ.get(name) or default


def main(argv=None):
    api = _env("C2MAPIV2_POSTMAN_API_NAME_KC", "c2mapiv2")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dd", default=_env("DD_EBNF_FILE", "data_dictionary/c2mapiv2-dd.ebnf"))
    ap.add_argument("--spec", default=_env("C2MAPIV2_OPENAPI_SPEC", f"openapi/{api}-openapi-spec-final.yaml"))
    ap.add_argument("--spec-base", default=_env("C2MAPIV2_OPENAPI_SPEC_BASE", f"openapi/{api}-openapi-spec-base.yaml"))
    ap.add_argument("--spec-with-examples",
                    default=_env("C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES", f"openapi/{api}-openapi-spec-final-with-examples.yaml"))
    ap.add_argument("--collections-dir", default=_env("POSTMAN_GENERATED_DIR", "postman/generated"))
    ap.add_argument("--faker-hints", default="config/faker_hints.yaml")
    ap.add_argument("--report", help="write a Markdown report to this file")
    ap.add_argument("--exit-status", action="store_true", help="exit 1 if any ERROR finding")
    args = ap.parse_args(argv)

    def rel(p):
        p = Path(p)
        return p if p.is_absolute() else REPO_ROOT / p

    F = Findings()
    dd = DDModel(rel(args.dd))
    specs = {"final": yaml.safe_load(rel(args.spec).read_text()),
             "base": yaml.safe_load(rel(args.spec_base).read_text()),
             "final-with-examples": yaml.safe_load(rel(args.spec_with_examples).read_text())}
    faker_hints = (yaml.safe_load(rel(args.faker_hints).read_text()) or {}).get("faker_hints", {})
    check_dd_to_spec(dd, specs, faker_hints, F)
    tools = SpecTools(specs["final"])
    for label, (suffix, typed) in COLLECTIONS.items():
        f = rel(args.collections_dir) / f"{api}-{suffix}"
        if not f.exists():
            F.add("B-COLLECTION-MISSING", label, str(f))
            continue
        check_collection(label, json.loads(f.read_text()), typed, specs["final"], tools, F)
    check_spec_examples(specs["final-with-examples"], dd, F)

    errors, warns, stale = F.classified()
    lines = ["# Pipeline consistency (DD → spec → Postman)", "",
             f"ERROR categories: {len(errors)}  ·  known-open WARN categories: {len(warns)}  ·  stale allowances: {len(stale)}", ""]

    def section(title, groups, show_ref):
        if not groups:
            return
        lines.append(f"## {title}")
        for (cat, scope), msgs in sorted(groups.items()):
            ref = f" — {F.tracking(cat, scope)}" if show_ref else ""
            lines.append(f"- **{cat}** [{scope}] ({len(msgs)}){ref}")
            for m in msgs[:20]:
                lines.append(f"    - {m}")
            if len(msgs) > 20:
                lines.append(f"    - … {len(msgs) - 20} more")
        lines.append("")
    section("❌ ERROR (must be fixed)", errors, False)
    section("⚠️ Known open (tracked)", warns, True)
    if stale:
        lines.append("## 🧹 Stale KNOWN_OPEN entries (no longer occur — remove them)")
        lines += [f"- {c} [{s}] — {KNOWN_OPEN[(c, s)]}" for c, s in stale]
        lines.append("")
    lines.append("✅ No ERROR findings" if not errors else f"❌ {sum(len(v) for v in errors.values())} ERROR finding(s)")
    text = "\n".join(lines)
    print(text)
    if args.report:
        Path(rel(args.report)).parent.mkdir(parents=True, exist_ok=True)
        rel(args.report).write_text(text + "\n")
    return 1 if (args.exit_status and errors) else 0


if __name__ == "__main__":
    sys.exit(main())
