#!/usr/bin/env python3
"""
ebnf_to_openapi.py  ·  v4
=========================
Convert a focused EBNF dialect to OpenAPI 3.0.3 YAML.

New in v4
---------
• "[ expr ]" optionals (expr can be repeat/array, etc.)
• Endpoint extractor: lines like
      Endpoint: POST /jobs/submit/single/pdf/split
  add a stub path & method.
• Accepts both "double" and 'single' quoted literals.
"""

import sys, re, yaml
from pathlib import Path
from lark import Lark, Transformer, Tree

# ────────────────────────────────────────────────────────
# 0.  Pre-scan: pull Endpoint lines & strip meta fluff
# ────────────────────────────────────────────────────────
ENDPOINT_RE = re.compile(r"Endpoint:\s*(\w+)\s+(\S+)", re.I)
META_SKIP   = re.compile(r"[']{3}|<<|>>")          # rare EBNF markup

def preprocess(src: str):
    """Return (clean_ebnf, [(method,path),…])."""
    endpoints = ENDPOINT_RE.findall(src)
    clean = "\n".join(
        ln for ln in src.splitlines()
        if not META_SKIP.search(ln)            # drop exotic markup
    )
    return clean, [(m.upper(), p) for m, p in endpoints]

# ────────────────────────────────────────────────────────
# 1.  Grammar
# ────────────────────────────────────────────────────────
EBNF = r"""
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
    %ignore /(?s:\(\*.*?\*\))/          //  (* … *) comments
"""

# ────────────────────────────────────────────────────────
# 2.  Transformer → clean AST
# ────────────────────────────────────────────────────────
class ToAst(Transformer):
    start    = list
    expr     = lambda s,i: i[0]
    term     = lambda s,i: i[0]
    alt      = lambda s,i: {"oneOf": i} if len(i)>1 else i[0]
    concat   = lambda s,i: {"sequence": i} if len(i)>1 else i[0]
    optional = lambda s,i: {"optional": i[0]}
    group    = lambda s,i: i[0]
    repeat   = lambda s,i: {"repeat": i[0]}

    SYMBOL   = str
    def str_lit(self, tok): return {"literal": tok[0][1:-1]}
    def int_lit(self, tok): return {"int_literal": int(tok[0])}
    production = lambda s,i: (i[0], i[1])

parser = Lark(EBNF, start="start", parser="lalr", transformer=ToAst())
parse  = lambda txt: parser.parse(txt)

# ────────────────────────────────────────────────────────
# 3.  Helpers
# ────────────────────────────────────────────────────────
PRIM  = re.compile(r"^(string|number|integer|boolean)$", re.I)
isobj = lambda s: s[0].isupper()
ref   = lambda s: {"$ref": f"#/components/schemas/{s}"}

def enumish(alts):
    if all(isinstance(a,dict) and "literal" in a for a in alts):
        return "string",[a["literal"] for a in alts]
    if all(isinstance(a,dict) and "int_literal" in a for a in alts):
        return "integer",[a["int_literal"] for a in alts]
    return None

# ────────────────────────────────────────────────────────
# 4.  Recursive schema builder
# ────────────────────────────────────────────────────────
def build(node):
    if isinstance(node,Tree):
        raise TypeError(node.pretty())

    if isinstance(node,dict):
        if "literal" in node:     return {"type":"string","enum":[node["literal"]]}
        if "int_literal" in node: return {"type":"integer","enum":[node["int_literal"]]}

    if isinstance(node,str):
        return {"type":node.lower()} if PRIM.match(node) else ref(node)

    if isinstance(node,dict) and "optional" in node:
        return build(node["optional"])

    if isinstance(node,dict) and "repeat" in node:
        return {"type":"array","items":build(node["repeat"])}

    if isinstance(node,dict) and "oneOf" in node:
        em=enumish(node["oneOf"])
        if em: t,vals=em; return {"type":t,"enum":vals}
        return {"oneOf":[build(x) for x in node["oneOf"]]}

    if isinstance(node,dict) and "sequence" in node:
        props,req={},[]
        for part in node["sequence"]:
            opt = isinstance(part,dict) and "optional" in part
            core= part["optional"] if opt else part
            name= core if isinstance(core,str) else "__anon__"
            props[name]=build(core)
            if not opt: req.append(name)
        return {"type":"object","properties":props,"required":req}

    raise TypeError(node)

# ────────────────────────────────────────────────────────
# 5.  Main converter
# ────────────────────────────────────────────────────────
def ebnf_to_openapi(raw: str):
    clean, endpoints = preprocess(raw)
    prods = parse(clean)

    schemas, paths = {}, {}

    for lhs,rhs in prods:
        if isobj(lhs):
            schemas[lhs]=build(rhs)

    # stub paths from schemas
    for obj in schemas:
        p="/"+obj[0].lower()+obj[1:]
        paths.setdefault(p, {})["post"] = {
            "summary": f"Create {obj}",
            "requestBody":{
                "required":True,
                "content":{"application/json":{"schema":ref(obj)}}
            },
            "responses":{"200":{"description":"OK",
                                "content":{"application/json":{"schema":ref(obj)}}}}
        }

    # add Endpoint: lines
    for method,path in endpoints:
        method_l = method.lower()
        paths.setdefault(path, {})[method_l] = {
            "summary": f"{method} {path}",
            "responses": {"200": {"description":"OK"}}
        }

    return {"openapi":"3.0.3",
            "info":{"title":"Generated from EBNF","version":"4.0.0"},
            "paths":paths,
            "components":{"schemas":schemas}}

# ────────────────────────────────────────────────────────
# 6.  CLI
# ────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv)!=3:
        sys.exit("Usage: ebnf_to_openapi.py <input.ebnf> <output.yaml>")
    src,dst=map(Path,sys.argv[1:])
    spec=ebnf_to_openapi(src.read_text())
    yaml.safe_dump(spec, dst.open("w"), sort_keys=False)
    print(f"✅ OpenAPI written to {dst}")
