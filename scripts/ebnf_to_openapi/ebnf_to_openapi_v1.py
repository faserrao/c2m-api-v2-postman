#!/usr/bin/env python3
"""
ebnf_to_openapi.py · v6.3
-------------------------
• All productions (uppercase or lowercase) become component schemas.
• Enumerations stay intact for lowercase symbols such as `printOption`.
• Endpoint association & default-path logic unchanged from v6.2.
"""

import sys, re, yaml
from pathlib import Path
from typing import List, Tuple, Dict
from lark import Lark, Transformer, Tree

# ───────────────────────── regex helpers ─────────────────────────
END_RE   = re.compile(r"Endpoint:\s*(\w+)\s+(\S+)", re.I)
PROD_RE  = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
NOISE_RE = re.compile(r"<<|>>")  # skip exotic markup

def preprocess(src: str):
    endpoints, prod_line = [], {}
    lines = src.splitlines()
    for idx, l in enumerate(lines):
        if m := END_RE.search(l):
            endpoints.append((idx, m.group(1).upper(), m.group(2)))
        if m := PROD_RE.match(l):
            prod_line[m.group(1)] = idx
    clean = "\n".join(l for l in lines if not NOISE_RE.search(l))
    return clean, endpoints, prod_line

# ───────────────────────── grammar & transformer ─────────────────
GRAMMAR = r"""
    start      : (production ";")+
    production : SYMBOL "=" expr
    expr       : alt
    alt        : concat ("|" concat)*
    concat     : term ("+" term)*
    term       : SYMBOL
               | DQSTRING              -> str_lit
               | SQSTRING              -> str_lit
               | NUMBER                -> int_lit
               | "[" expr "]"          -> optional
               | "(" expr ")"          -> group
               | "{" expr "}"          -> repeat

    SYMBOL     : /[A-Za-z_][A-Za-z0-9_]*/
    DQSTRING   : /"[^"]*"/
    SQSTRING   : /'[^']*'/
    NUMBER     : /\d+/
    %ignore /[ \t\r\n]+/
    %ignore /(?s:\(\*.*?\*\))/
"""

class AST(Transformer):
    start = list
    expr  = lambda _,i: i[0]
    term  = lambda _,i: i[0]
    alt   = lambda _,i: {"oneOf": i} if len(i)>1 else i[0]
    concat= lambda _,i: {"sequence": i} if len(i)>1 else i[0]
    optional=lambda _,i: {"optional": i[0]}
    group   = lambda _,i: i[0]
    repeat  = lambda _,i: {"repeat":  i[0]}

    SYMBOL  = str
    def str_lit(self,t): return {"literal": t[0][1:-1]}
    def int_lit(self,t): return {"int_literal": int(t[0])}
    production = lambda _,i: (i[0], i[1])

parser = Lark(GRAMMAR, start="start", parser="lalr", transformer=AST())

# ───────────────────────── helpers ──────────────────────────────
PRIM = re.compile(r"^(string|number|integer|boolean)$", re.I)
ref  = lambda s: {"$ref": f"#/components/schemas/{s}"}

def enumish(alts):
    if all(isinstance(a,dict) and "literal" in a for a in alts):
        return "string",[a["literal"] for a in alts]
    if all(isinstance(a,dict) and "int_literal" in a for a in alts):
        return "integer",[a["int_literal"] for a in alts]
    return None

# ───────────────────────── schema builder ───────────────────────
def build(node, refs:set):
    if isinstance(node,Tree):
        raise TypeError(node.pretty())

    if isinstance(node,dict):
        if "literal" in node:     return {"type":"string","enum":[node["literal"]]}
        if "int_literal" in node: return {"type":"integer","enum":[node["int_literal"]]}

    if isinstance(node,str):
        if PRIM.match(node): return {"type": node.lower()}
        refs.add(node)
        return ref(node)

    if isinstance(node,dict) and "optional" in node:
        return build(node["optional"], refs)

    if isinstance(node,dict) and "repeat" in node:
        return {"type":"array","items":build(node["repeat"], refs)}

    if isinstance(node,dict) and "oneOf" in node:
        e = enumish(node["oneOf"])
        return {"type": e[0], "enum": e[1]} if e else {"oneOf": [build(x,refs) for x in node["oneOf"]]}

    if isinstance(node,dict) and "sequence" in node:
        props, req = {}, []
        for part in node["sequence"]:
            opt  = isinstance(part,dict) and "optional" in part
            core = part["optional"] if opt else part
            name = core if isinstance(core,str) else "__anon__"
            props[name] = build(core, refs)
            if not opt: req.append(name)
        return {"type":"object","properties":props,"required":req}

    raise TypeError(node)

# ───────────────────────── conversion driver ────────────────────
def convert(src:str):
    clean,endpoints,prod_line = preprocess(src)
    productions = parser.parse(clean)

    schemas, refs = {}, set()
    declared_objs = set()

    # add EVERY production to component schemas
    for sym, rhs in productions:
        schemas[sym] = build(rhs, refs)
        if sym[0].isupper():
            declared_objs.add(sym)

    # stub any referenced but undeclared
    for r in refs:
        schemas.setdefault(r, {"type":"string"})

    paths = {}

    # bind Endpoint comment to object one line below
    obj_by_line = {prod_line[s]: s for s in schemas if s in prod_line}
    covered=set()
    for ln,meth,path in endpoints:
        obj=obj_by_line.get(ln+1)
        if not obj: continue
        paths.setdefault(path,{})[meth.lower()] = {
            "summary":f"{meth} {path}",
            "requestBody":{"required":True,
                "content":{"application/json":{"schema":ref(obj)}}},
            "responses":{"200":{"description":"OK",
                "content":{"application/json":{"schema":ref(obj)}}}}
        }
        covered.add(obj)

    # default POST /<Object> for PascalCase objects not covered
    for obj in declared_objs - covered:
        p="/"+obj[0].lower()+obj[1:]
        paths.setdefault(p,{})["post"]={
            "summary":f"Create {obj}",
            "requestBody":{"required":True,
                "content":{"application/json":{"schema":ref(obj)}}},
            "responses":{"200":{"description":"OK",
                "content":{"application/json":{"schema":ref(obj)}}}}
        }

    return {"openapi":"3.0.3",
            "info":{"title":"Generated from EBNF","version":"6.3.0"},
            "paths":paths,
            "components":{"schemas":schemas}}

# ───────────────────────── CLI ───────────────────────────
if __name__=="__main__":
    if len(sys.argv)!=3:
        sys.exit("Usage: ebnf_to_openapi.py <input.ebnf> <output.yaml>")
    src,dst=map(Path,sys.argv[1:])
    yaml.safe_dump(convert(src.read_text()), dst.open("w"), sort_keys=False)
    print(f"✅  OpenAPI written to {dst}")
