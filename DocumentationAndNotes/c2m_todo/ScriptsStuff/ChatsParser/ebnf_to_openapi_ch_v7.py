#!/usr/bin/env python3
"""
ebnf_to_openapi_v7.py
---------------------
* Classifies EBNF productions → Object / Property / Enum
* Applies simple naming conventions (Pascal vs camel)
* Generates OpenAPI 3.0.3 YAML
* Prints a summary report to the console
"""

import re, sys, yaml, textwrap
from pathlib import Path
from typing import Dict, List, Tuple, Set
from lark import Lark, Transformer, Tree

# ────────────────────────── regex helpers ──────────────────────────
ENDLINE = re.compile(r"Endpoint:\s*(\w+)\s+(\S+)", re.I)
PRODHEAD = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")

# ────────────────────────── grammar & AST ──────────────────────────
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
    expr  = lambda _,i: i[0]
    term  = lambda _,i: i[0]
    alt   = lambda _,i: {"oneOf":i} if len(i)>1 else i[0]
    concat= lambda _,i: {"sequence":i} if len(i)>1 else i[0]
    optional=lambda _,i: {"optional":i[0]}
    group  = lambda _,i: i[0]
    repeat = lambda _,i: {"repeat": i[0]}
    SYMBOL = str
    def str_lit(self,t): return {"literal":t[0][1:-1]}
    def int_lit(self,t): return {"int_literal":int(t[0])}
    production = lambda _,i: (i[0], i[1])

PARSER = Lark(GRAMMAR, start="start", parser="lalr", transformer=AST())

PRIM_RE  = re.compile(r"^(string|number|integer|boolean)$", re.I)
REF = lambda s: {"$ref": f"#/components/schemas/{s}"}

# ────────────────────────── util functions ──────────────────────────
def enum_vals(node)->Tuple[str,List]:
    if isinstance(node,dict) and "oneOf" in node:
        alts=node["oneOf"]
        if all(isinstance(a,dict) and "literal" in a for a in alts):
            return "string",[a["literal"] for a in alts]
        if all(isinstance(a,dict) and "int_literal" in a for a in alts):
            return "integer",[a["int_literal"] for a in alts]
    return "",[]

def classify(name:str, rhs)->str:
    """Return 'object'|'enum'|'property'."""
    t,vals=enum_vals(rhs)
    if vals: return "enum"
    if name[0].isupper() and isinstance(rhs,dict) and (
        "sequence" in rhs or "oneOf" in rhs or "repeat" in rhs):
        return "object"
    return "property"

def build_schema(node, refs:Set[str]):
    if isinstance(node,dict):
        if "literal" in node:     return {"type":"string","enum":[node["literal"]]}
        if "int_literal" in node: return {"type":"integer","enum":[node["int_literal"]]}
    if isinstance(node,str):
        if PRIM_RE.match(node): return {"type":node.lower()}
        refs.add(node); return REF(node)
    if isinstance(node,dict) and "optional" in node:
        return build_schema(node["optional"], refs)
    if isinstance(node,dict) and "repeat" in node:
        return {"type":"array","items":build_schema(node["repeat"], refs)}
    if isinstance(node,dict) and "oneOf" in node:
        t,vals=enum_vals(node)
        if vals: return {"type":t,"enum":vals}
        return {"oneOf":[build_schema(x,refs) for x in node["oneOf"]]}
    if isinstance(node,dict) and "sequence" in node:
        props,req={},[]
        for part in node["sequence"]:
            opt=isinstance(part,dict) and "optional" in part
            core=part["optional"] if opt else part
            name=core if isinstance(core,str) else "__anon__"
            props[name]=build_schema(core,refs)
            if not opt: req.append(name)
        return {"type":"object","properties":props,"required":req}
    raise TypeError(node)

# ────────────────────────── main conversion ──────────────────────────
def ebnf_to_openapi(src:str)->Tuple[Dict,Dict]:
    lines=src.splitlines()
    endpoints=[]          # (lineno, METHOD, PATH)
    for idx,l in enumerate(lines):
        if m:=ENDLINE.search(l):
            endpoints.append((idx,m.group(1).upper(),m.group(2)))

    clean="\n".join(lines)  # (comments already ignored by grammar)
    prods=PARSER.parse(clean)

    schemas, refs={}, set()
    objects,props,enums=[],[],[]

    for name,rhs in prods:
        kind=classify(name,rhs)
        if kind=="enum":
            t,vals=enum_vals(rhs)
            schemas[name]={"type":t,"enum":vals}
            enums.append((name,vals))
        elif kind=="object":
            schemas[name]=build_schema(rhs,refs)
            objects.append(name)
        else:
            schemas[name]=build_schema(rhs,refs)
            props.append(name)

    for r in refs:
        schemas.setdefault(r,{"type":"string"})

    # ----- paths -----
    obj_line={i: n for i,(n,_) in enumerate(zip([l for l in lines if PRODHEAD.match(l)],objects))}
    paths={}
    covered=set()
    for ln,meth,pth in endpoints:
        # object production is next non-empty non-comment
        nxt=ln+1
        while nxt<len(lines) and not PRODHEAD.match(lines[nxt]):
            nxt+=1
        if nxt<len(lines):
            obj=PRODHEAD.match(lines[nxt]).group(1)
            paths.setdefault(pth,{})[meth.lower()]={
                "summary":f"{meth} {pth}",
                "requestBody":{"required":True,
                    "content":{"application/json":{"schema":REF(obj)}}},
                "responses":{"200":{"description":"OK",
                    "content":{"application/json":{"schema":REF(obj)}}}}
            }
            covered.add(obj)

    for obj in objects:
        if obj in covered: continue
        p="/"+obj[0].lower()+obj[1:]
        paths.setdefault(p,{})["post"]={
            "summary":f"Create {obj}",
            "requestBody":{"required":True,
                "content":{"application/json":{"schema":REF(obj)}}},
            "responses":{"200":{"description":"OK",
                "content":{"application/json":{"schema":REF(obj)}}}}
        }

    spec={"openapi":"3.0.3",
          "info":{"title":"Generated from EBNF","version":"7.0.0"},
          "paths":paths,
          "components":{"schemas":schemas}}
    report={"Objects":objects,"Properties":props,"Enums":enums}
    return spec, report

# ────────────────────────── CLI ──────────────────────────
if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: ebnf_to_openapi_v7.py <input.ebnf> <output.yaml>")
        sys.exit(1)
    inp,out=map(Path,sys.argv[1:])
    spec,report=ebnf_to_openapi(inp.read_text())
    yaml.safe_dump(spec, out.open("w"), sort_keys=False)
    print("✅ OpenAPI written to", out)
    print("\n---- Classification Report ----")
    print("Objects:", ", ".join(report["Objects"]))
    print("Properties:", ", ".join(report["Properties"]))
    if report["Enums"]:
        print("Enums:")
        for name,vals in report["Enums"]:
            print(f"  {name}: {vals}")
    else:
        print("Enums: (none)")
