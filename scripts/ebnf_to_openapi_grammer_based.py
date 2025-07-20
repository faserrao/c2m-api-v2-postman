#!/usr/bin/env python3
"""
ebnf_to_openapi_v8.py
-----------------------
* Auto-classifies EBNF productions as Object / Property / Enum.
* Applies naming conventions (PascalCase vs camelCase).
* Adds servers, security, operationId, and 4XX responses.
* Prunes unused components automatically.
* Converts PascalCase field names to camelCase.
* Removes empty `required` arrays.
* Supports --server-url CLI argument (default: https://api.example.com).
* Outputs a classification and pruning report.
"""

import re
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
from lark import Lark, Transformer

# ────────────────────────── Regex Helpers ──────────────────────────
ENDLINE = re.compile(r"Endpoint:\s*(\w+)\s+(\S+)", re.I)
PRODHEAD = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
PRIM_RE = re.compile(r"^(string|number|integer|boolean)$", re.I)
REF = lambda s: {"$ref": f"#/components/schemas/{s}"}

# ────────────────────────── Name Conversion ──────────────────────────
def pascal_to_camel(name: str) -> str:
    return name[0].lower() + name[1:] if name and name[0].isupper() else name

# ────────────────────────── Grammar ──────────────────────────
GRAMMAR = r"""
    start      : (production ";")+
    production : SYMBOL "=" expr
    expr       : alt
    alt        : concat ("|" concat)*
    concat     : term ("+" term)*
    term       : SYMBOL
               | DQSTRING            -> str_lit
               | SQSTRING            -> str_lit
               | NUMBER              -> int_lit
               | "[" expr "]"        -> optional
               | "(" expr ")"        -> group
               | "{" expr "}"        -> repeat
    SYMBOL   : /[A-Za-z_][A-Za-z0-9_]*/
    DQSTRING : /"[^"]*"/
    SQSTRING : /'[^']*'/
    NUMBER   : /\d+/
    %ignore /[ \t\r\n]+/
    %ignore /(?s:\(\*.*?\*\))/
"""

class AST(Transformer):
    start = list
    expr  = lambda _, i: i[0]
    term  = lambda _, i: i[0]
    alt   = lambda _, i: {"oneOf": i} if len(i) > 1 else i[0]
    concat= lambda _, i: {"sequence": i} if len(i) > 1 else i[0]
    optional=lambda _, i: {"optional": i[0]}
    group  = lambda _, i: i[0]
    repeat = lambda _, i: {"repeat":  i[0]}
    SYMBOL = str
    def str_lit(self, t): return {"literal": t[0][1:-1]}
    def int_lit(self, t): return {"int_literal": int(t[0])}
    production = lambda _, i: (i[0], i[1])

PARSER = Lark(GRAMMAR, start="start", parser="lalr", transformer=AST())

# ────────────────────────── Utility Functions ──────────────────────────
def enum_vals(node) -> Tuple[str, List]:
    if isinstance(node, dict) and "oneOf" in node:
        alts = node["oneOf"]
        if all(isinstance(a, dict) and "literal" in a for a in alts):
            return "string", [a["literal"] for a in alts]
        if all(isinstance(a, dict) and "int_literal" in a for a in alts):
            return "integer", [a["int_literal"] for a in alts]
    return "", []

def classify(name: str, rhs) -> str:
    t, vals = enum_vals(rhs)
    if vals:
        return "enum"
    if name[0].isupper() and isinstance(rhs, dict) and (
        "sequence" in rhs or "oneOf" in rhs or "repeat" in rhs):
        return "object"
    return "property"

def build_schema(node, refs: Set[str]):
    if isinstance(node, dict):
        if "literal" in node:     return {"type": "string", "enum": [node["literal"]]}
        if "int_literal" in node: return {"type": "integer", "enum": [node["int_literal"]]}
    if isinstance(node, str):
        if PRIM_RE.match(node): return {"type": node.lower()}
        refs.add(node)
        return REF(node)
    if isinstance(node, dict) and "optional" in node:
        return build_schema(node["optional"], refs)
    if isinstance(node, dict) and "repeat" in node:
        return {"type": "array", "items": build_schema(node["repeat"], refs)}
    if isinstance(node, dict) and "oneOf" in node:
        t, vals = enum_vals(node)
        if vals: return {"type": t, "enum": vals}
        return {"oneOf": [build_schema(x, refs) for x in node["oneOf"]]}
    if isinstance(node, dict) and "sequence" in node:
        props, req = {}, []
        for part in node["sequence"]:
            opt = isinstance(part, dict) and "optional" in part
            core = part["optional"] if opt else part
            name = core if isinstance(core, str) else "__anon__"
            name = pascal_to_camel(name)
            props[name] = build_schema(core, refs)
            if not opt: req.append(name)
        return {"type": "object", "properties": props, "required": req}
    raise TypeError(node)

def generate_operation_id(method: str, path: str) -> str:
    clean = path.strip("/").replace("/", "_")
    return f"{method.lower()}_{clean}"

# ────────────────────────── Pruning ──────────────────────────
def prune_unused_schemas(schemas: Dict, paths: Dict) -> Tuple[Dict, List[str]]:
    used = set()

    def collect_refs(schema):
        if isinstance(schema, dict):
            if "$ref" in schema:
                used.add(schema["$ref"].split("/")[-1])
            for v in schema.values():
                collect_refs(v)
        elif isinstance(schema, list):
            for item in schema:
                collect_refs(item)

    for p in paths.values():
        for op in p.values():
            collect_refs(op)

    changed = True
    while changed:
        changed = False
        for sname, sdef in list(schemas.items()):
            if sname in used:
                prev = len(used)
                collect_refs(sdef)
                if len(used) > prev:
                    changed = True

    removed = [s for s in schemas if s not in used]
    for r in removed:
        del schemas[r]
    return schemas, removed

# ────────────────────────── Prune Empty Required ──────────────────────────
def prune_empty_required(schema):
    if isinstance(schema, dict):
        if "required" in schema and (not schema["required"] or len(schema["required"]) == 0):
            del schema["required"]
        for v in schema.values():
            prune_empty_required(v)
    elif isinstance(schema, list):
        for item in schema:
            prune_empty_required(item)

# ────────────────────────── Main Conversion ──────────────────────────
def ebnf_to_openapi(src: str, server_url: str) -> Tuple[Dict, Dict, List[str]]:
    lines = src.splitlines()
    endpoints = []
    for idx, l in enumerate(lines):
        if m := ENDLINE.search(l):
            endpoints.append((idx, m.group(1).upper(), m.group(2)))

    clean = "\n".join(lines)
    prods = PARSER.parse(clean)

    schemas, refs = {}, set()
    objects, props, enums = [], [], []

    for name, rhs in prods:
        name = pascal_to_camel(name)
        kind = classify(name, rhs)
        if kind == "enum":
            t, vals = enum_vals(rhs)
            schemas[name] = {"type": t, "enum": vals}
            enums.append((name, vals))
        elif kind == "object":
            schemas[name] = build_schema(rhs, refs)
            objects.append(name)
        else:
            schemas[name] = build_schema(rhs, refs)
            props.append(name)

    for r in refs:
        schemas.setdefault(pascal_to_camel(r), {"type": "string"})

    paths = {}
    covered = set()
    for ln, meth, pth in endpoints:
        nxt = ln + 1
        while nxt < len(lines) and not PRODHEAD.match(lines[nxt]):
            nxt += 1
        if nxt < len(lines):
            obj = pascal_to_camel(PRODHEAD.match(lines[nxt]).group(1))
            opid = generate_operation_id(meth, pth)
            paths.setdefault(pth, {})[meth.lower()] = {
                "summary": f"{meth} {pth}",
                "operationId": opid,
                "requestBody": {"required": True,
                    "content": {"application/json": {"schema": REF(obj)}}},
                "responses": {
                    "200": {"description": "OK",
                            "content": {"application/json": {"schema": REF(obj)}}},
                    "400": {"description": "Bad Request"}
                },
                "security": [{"bearerAuth": []}]
            }
            covered.add(obj)

    for obj in objects:
        if obj in covered: continue
        p = "/" + obj[0].lower() + obj[1:]
        opid = generate_operation_id("POST", p)
        paths.setdefault(p, {})["post"] = {
            "summary": f"Create {obj}",
            "operationId": opid,
            "requestBody": {"required": True,
                "content": {"application/json": {"schema": REF(obj)}}},
            "responses": {
                "200": {"description": "OK",
                        "content": {"application/json": {"schema": REF(obj)}}},
                "400": {"description": "Bad Request"}
            },
            "security": [{"bearerAuth": []}]
        }

    # Prune unused components
    schemas, removed = prune_unused_schemas(schemas, paths)
    prune_empty_required(schemas)

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Generated from EBNF",
            "version": "8.0.0",
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}
        },
        "servers": [{"url": server_url}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http", "scheme": "bearer", "bearerFormat": "JWT"
                }
            },
            "schemas": schemas
        },
        "security": [{"bearerAuth": []}]
    }

    report = {"Objects": objects, "Properties": props, "Enums": enums}
    return spec, report, removed

# ────────────────────────── CLI ──────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert EBNF to OpenAPI")
    parser.add_argument("input", help="Input EBNF file")
    parser.add_argument("output", help="Output OpenAPI YAML file")
    parser.add_argument("--server-url", default="https://api.example.com", help="Server URL for OpenAPI")
    args = parser.parse_args()

    inp, out = Path(args.input), Path(args.output)
    spec, report, removed = ebnf_to_openapi(inp.read_text(), args.server_url)
    yaml.safe_dump(spec, out.open("w"), sort_keys=False)
    print(f"✅ OpenAPI written to {out}\n")
    print("---- Classification Report ----")
    print("Objects:", ", ".join(report["Objects"]) or "(none)")
    print("Properties:", ", ".join(report["Properties"]) or "(none)")
    if report["Enums"]:
        print("Enums:")
        for name, vals in report["Enums"]:
            print(f"  {name}: {vals}")
    else:
        print("Enums: (none)")
    if removed:
        print("\n---- Pruned Components ----")
        for r in removed:
            print(f"  - {r}")
