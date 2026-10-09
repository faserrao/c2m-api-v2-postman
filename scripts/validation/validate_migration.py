#!/usr/bin/env python3
"""
validate_migration.py — change-impact validator for contract / DD migrations.

Proves that a planned change (e.g. D2: remove singleAddress) was applied completely
and that nothing else in the system changed. Three modes:

  snapshot  Record the system state: DD rules, spec schemas + operations + every
            example, every catalog/template example, and all five canonical
            collections (requests, body field paths/values, saved responses).

  compare   Compare the current state with a snapshot under a migration file that
            declares the intended change. Reports, as errors:
              UNEXPECTED   something changed that the migration does not declare
              INCOMPLETE   something the migration declares did not happen
              LOST         a value present before (after rewrites) is gone
            Request-body fields the generators fill randomly — those whose DD @hint is
            faker/random_int, or that have no hint — are compared by path only. Fields
            with a static hint, saved responses and spec examples are compared by value.

  retired   The migration's retired names must not appear anywhere: DD, spec,
            configs, collections, active scripts and tests.

Migration file (YAML):
  name: D2 — remove singleAddress
  path_rewrites:                      # applied to baseline paths and string values
    - from: "recipientAddressSource.singleAddress."
      to:   "recipientAddressSource.recipientAddressByList.addressList[0]."
  select_rewrites:                    # config `select:` values
    recipientAddressSource: {singleAddress: recipientAddressByList}
  rules:   {removed: [...], changed: [...], added: [...]}     # DD rules
  schemas: {removed: [...], changed: [...], added: [...]}     # spec components
  allowed_added_paths:   [regex, ...] # new body/value paths that are acceptable
  allowed_removed_paths: [regex, ...]
  retired_names: [singleAddress, addressName]
  nondeterministic:                   # optional extra: collection -> body-path regexes compared by path only
    Test: ["\\.someField$"]

Usage:
  python3 scripts/validation/validate_migration.py snapshot --out reports/migration-baseline.json
  python3 scripts/validation/validate_migration.py compare --baseline FILE --migration FILE [--exit-status]
  python3 scripts/validation/validate_migration.py retired --migration FILE [--exit-status]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "active"))
from ebnf_to_openapi_dynamic_v3 import EBNFToOpenAPITranslator  # noqa: E402

CONTENT_TYPE_JSON = "application/json"
COLLECTIONS = {
    "Linked": "linked-collection-flat.json",
    "Test": "test-collection-flat.json",
    "GS-Linked": "getting-started-linked-collection.json",
    "GS-Test": "getting-started-test-collection.json",
    "Real-World": "real-world-use-cases-collection.json",
}
CONFIGS = {"catalog": "config/curated-examples-catalog.yaml", "template": "config/getting-started-template.yaml"}
# Where retired names must not appear: the DD, configs, active code and tests, plus the
# artifacts the pipeline actually builds (the 3 spec files and the 5 canonical collections —
# stale files left in openapi/ or postman/generated/ by old builds are not scanned).
RETIRED_SCAN_DIRS = ["config", "scripts/active", "scripts/validation", "scripts/utilities",
                     "scripts/test_data_generator_for_collections"]
RETIRED_SKIP = re.compile(r"(/archive/|\.bak$|__pycache__|validate_migration\.py$|test_migration_validator\.py$"
                          r"|/migrations/|claude\.log$)")


def retired_scan_files(root=REPO_ROOT):
    api = _api()
    built = [_env("DD_EBNF_FILE", "data_dictionary/c2mapiv2-dd.ebnf"),
             _env("C2MAPIV2_OPENAPI_SPEC_BASE", f"openapi/{api}-openapi-spec-base.yaml"),
             _env("C2MAPIV2_OPENAPI_SPEC", f"openapi/{api}-openapi-spec-final.yaml"),
             _env("C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES", f"openapi/{api}-openapi-spec-final-with-examples.yaml")]
    gen = _env("POSTMAN_GENERATED_DIR", "postman/generated")
    built += [f"{gen}/{api}-{suffix}" for suffix in COLLECTIONS.values()]
    files = [root / p for p in built if (root / p).is_file()]
    for rel in RETIRED_SCAN_DIRS:
        base = root / rel
        if base.exists():
            files += sorted(p for p in base.rglob("*") if p.is_file())
    return files


def _env(name, default):
    return os.environ.get(name) or default


def _api():
    return _env("C2MAPIV2_POSTMAN_API_NAME_KC", "c2mapiv2")


def _strip(schema):
    if isinstance(schema, dict):
        return {k: _strip(v) for k, v in schema.items() if k not in ("description", "title")}
    if isinstance(schema, list):
        return [_strip(v) for v in schema]
    return schema


def flatten(obj, prefix=""):
    """{dotted.path[i]: leaf value} for a JSON-like value."""
    out = {}
    if isinstance(obj, dict):
        if not obj and prefix:
            out[prefix] = {}
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        if not obj and prefix:
            out[prefix] = []
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def _json_or_none(text):
    try:
        return json.loads(text) if text else None
    except (TypeError, json.JSONDecodeError):
        return None


# --------------------------------------------------------------------------- #
# snapshot                                                                     #
# --------------------------------------------------------------------------- #
def take_snapshot(root=REPO_ROOT):
    api = _api()
    dd_path = root / _env("DD_EBNF_FILE", "data_dictionary/c2mapiv2-dd.ebnf")
    spec_path = root / _env("C2MAPIV2_OPENAPI_SPEC", f"openapi/{api}-openapi-spec-final.yaml")
    gen_dir = root / _env("POSTMAN_GENERATED_DIR", "postman/generated")

    t = EBNFToOpenAPITranslator()
    t.parse_ebnf(dd_path.read_text(encoding="utf-8"))
    rules = {n: json.dumps(p.expression, sort_keys=True) for n, p in t.productions.items()}

    spec = yaml.safe_load(spec_path.read_text())
    schemas = {n: _strip(s) for n, s in spec["components"]["schemas"].items()}
    operations = {}
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            body = ((op.get("requestBody") or {}).get("content") or {}).get(CONTENT_TYPE_JSON, {})
            responses = {}
            for status, r in (op.get("responses") or {}).items():
                media = ((r.get("content") or {}).get(CONTENT_TYPE_JSON) or {})
                responses[status] = {k: flatten(e.get("value"))
                                     for k, e in (media.get("examples") or {}).items()}
            operations[f"{method.upper()} {path}"] = {
                "requestBody": (body.get("schema") or {}).get("$ref"),
                "responses": responses,
            }

    configs = {}
    for label, rel in CONFIGS.items():
        raw = yaml.safe_load((root / rel).read_text()) or {}
        examples = raw.get("examples", raw) if isinstance(raw, dict) else raw
        configs[label] = {
            ex["name"]: {"method": ex.get("method"), "path": ex.get("path"),
                         "select": ex.get("select") or {}, "values": flatten(ex.get("values") or {})}
            for ex in (examples or []) if isinstance(ex, dict) and ex.get("name")
        }

    collections = {}
    for label, suffix in COLLECTIONS.items():
        f = gen_dir / f"{api}-{suffix}"
        if not f.exists():
            collections[label] = None
            continue
        c = json.loads(f.read_text())
        reqs = {}

        def walk(items, folder=""):
            for it in items:
                if "item" in it:
                    walk(it["item"], f"{folder}/{it.get('name')}" if folder else it.get("name") or "")
                    continue
                r = it.get("request") or {}
                key = f"{folder}/{it.get('name')}" if folder else it.get("name")
                saved = [{"code": ex.get("code"), "name": ex.get("name"),
                          "body": flatten(_json_or_none(ex.get("body")))} for ex in it.get("response") or []]
                reqs[key] = {
                    "method": r.get("method"),
                    "path": "/" + "/".join((r.get("url") or {}).get("path", [])),
                    "body": flatten(_json_or_none((r.get("body") or {}).get("raw"))),
                    "saved": saved,
                }
        walk(c.get("item", []))
        collections[label] = reqs

    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                                capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = "?"
    return {"meta": {"commit": commit, "created": datetime.datetime.now(datetime.timezone.utc).isoformat()},
            "dd": rules, "spec": {"schemas": schemas, "operations": operations},
            "configs": configs, "collections": collections}


# --------------------------------------------------------------------------- #
# compare                                                                      #
# --------------------------------------------------------------------------- #
class Report:
    def __init__(self):
        self.items = []  # (kind, area, message)

    def add(self, kind, area, msg):
        self.items.append((kind, area, msg))

    def errors(self):
        return [i for i in self.items if i[0] in ("UNEXPECTED", "INCOMPLETE", "LOST")]


class Migration:
    def __init__(self, data):
        self.name = data.get("name", "(unnamed)")
        self.path_rewrites = [(r["from"], r["to"]) for r in data.get("path_rewrites") or []]
        self.select_rewrites = data.get("select_rewrites") or {}
        self.rules = {k: set((data.get("rules") or {}).get(k) or []) for k in ("removed", "changed", "added")}
        self.schemas = {k: set((data.get("schemas") or {}).get(k) or []) for k in ("removed", "changed", "added")}
        self.allowed_added = [re.compile(p) for p in data.get("allowed_added_paths") or []]
        self.allowed_removed = [re.compile(p) for p in data.get("allowed_removed_paths") or []]
        self.retired = data.get("retired_names") or []
        self.nondeterministic = {k: [re.compile(p) for p in v]
                                 for k, v in (data.get("nondeterministic") or {}).items()}

    def rewrite(self, text):
        if not isinstance(text, str):
            return text
        for old, new in self.path_rewrites:
            text = text.replace(old, new)
        return text

    def rewrite_flat(self, flat):
        return {self.rewrite(k): self.rewrite(v) for k, v in (flat or {}).items()}

    def allowed(self, patterns, path):
        return any(p.search(path) for p in patterns)

    def random_value(self, collection, path, random_fields=frozenset()):
        leaf = re.sub(r"\[\d+\]", "", path.split(".")[-1])
        return leaf in random_fields or any(p.search(path) for p in self.nondeterministic.get(collection, []))


def random_fields_from_hints(root=REPO_ROOT):
    """Field names the generators fill randomly: DD @hint faker/random_int, or no hint."""
    hints = (yaml.safe_load((root / "config" / "faker_hints.yaml").read_text()) or {}).get("faker_hints", {})
    static = {n for n, h in hints.items() if (h or {}).get("type") == "static"}
    return lambda name: name not in static


def _compare_flat(rep, area, before, after, mig, collection=None, values=True, is_random=None):
    """Compare two flattened dicts (baseline already rewritten)."""
    for path in sorted(set(before) - set(after)):
        if not mig.allowed(mig.allowed_removed, path):
            rep.add("LOST", area, f"{path} (was {before[path]!r})")
    for path in sorted(set(after) - set(before)):
        if not mig.allowed(mig.allowed_added, path):
            rep.add("UNEXPECTED", area, f"new {path} = {after[path]!r}")
    if not values:
        return
    for path in sorted(set(before) & set(after)):
        if collection and is_random and (is_random(re.sub(r"\[\d+\]", "", path.split(".")[-1]))
                                         or mig.random_value(collection, path)):
            continue
        if before[path] != after[path]:
            rep.add("UNEXPECTED", area, f"{path}: {before[path]!r} -> {after[path]!r}")


def _compare_named(rep, area, before, after, declared):
    """Compare dicts of named items (DD rules / spec schemas) against declared changes."""
    for name in sorted(set(before) | set(after)):
        if name in declared["removed"]:
            if name in after:
                rep.add("INCOMPLETE", area, f"{name} should be removed but is still present")
            continue
        if name in declared["added"]:
            if name not in after:
                rep.add("INCOMPLETE", area, f"{name} should be added but is missing")
            continue
        if name not in after:
            rep.add("UNEXPECTED", area, f"{name} was removed")
        elif name not in before:
            rep.add("UNEXPECTED", area, f"{name} was added")
        elif name in declared["changed"]:
            if before[name] == after[name]:
                rep.add("INCOMPLETE", area, f"{name} should change but is identical")
        elif before[name] != after[name]:
            rep.add("UNEXPECTED", area, f"{name} changed")


def compare(baseline, current, mig, is_random=None):
    rep = Report()
    is_random = is_random or random_fields_from_hints()
    # 1. DD rules and spec schemas
    _compare_named(rep, "DD rule", baseline["dd"], current["dd"], mig.rules)
    _compare_named(rep, "spec schema", baseline["spec"]["schemas"], current["spec"]["schemas"], mig.schemas)

    # 2. spec operations and every example (values rewritten)
    b_ops, c_ops = baseline["spec"]["operations"], current["spec"]["operations"]
    for key in sorted(set(b_ops) | set(c_ops)):
        if key not in c_ops or key not in b_ops:
            rep.add("UNEXPECTED", "spec operation", f"{key} {'removed' if key not in c_ops else 'added'}")
            continue
        b, c = b_ops[key], c_ops[key]
        if b["requestBody"] != c["requestBody"]:
            rep.add("UNEXPECTED", "spec operation", f"{key} requestBody {b['requestBody']} -> {c['requestBody']}")
        if set(b["responses"]) != set(c["responses"]):
            rep.add("UNEXPECTED", "spec operation", f"{key} statuses {sorted(b['responses'])} -> {sorted(c['responses'])}")
        for status in set(b["responses"]) & set(c["responses"]):
            be, ce = b["responses"][status], c["responses"][status]
            if set(be) != set(ce):
                rep.add("UNEXPECTED", "spec example", f"{key} {status} examples {sorted(be)} -> {sorted(ce)}")
            for ex in set(be) & set(ce):
                _compare_flat(rep, f"spec example {key} {status} {ex}", mig.rewrite_flat(be[ex]), ce[ex], mig)

    # 3. config examples: nothing lost, select rewritten as declared
    for label in CONFIGS:
        b_cfg, c_cfg = baseline["configs"].get(label, {}), current["configs"].get(label, {})
        for name in sorted(set(b_cfg) | set(c_cfg)):
            if name not in c_cfg or name not in b_cfg:
                rep.add("UNEXPECTED", f"{label} example", f"{name!r} {'removed' if name not in c_cfg else 'added'}")
                continue
            b, c = b_cfg[name], c_cfg[name]
            for fld in ("method", "path"):
                if b[fld] != c[fld]:
                    rep.add("UNEXPECTED", f"{label} example", f"{name!r} {fld} {b[fld]} -> {c[fld]}")
            expected_select = {k: (mig.select_rewrites.get(k) or {}).get(v, v) for k, v in b["select"].items()}
            if expected_select != c["select"]:
                rep.add("UNEXPECTED" if expected_select == b["select"] else "INCOMPLETE",
                        f"{label} example", f"{name!r} select {b['select']} -> {c['select']} (expected {expected_select})")
            _compare_flat(rep, f"{label} example {name!r}", mig.rewrite_flat(b["values"]), c["values"], mig)

    # 4. collections: same requests; body paths (and deterministic values); saved responses
    for label in COLLECTIONS:
        b_col, c_col = baseline["collections"].get(label), current["collections"].get(label)
        if b_col is None or c_col is None:
            rep.add("UNEXPECTED", "collection", f"{label} missing ({'before' if b_col is None else 'after'})")
            continue
        for key in sorted(set(b_col) | set(c_col)):
            if key not in c_col or key not in b_col:
                rep.add("UNEXPECTED", f"{label} request", f"{key!r} {'removed' if key not in c_col else 'added'}")
                continue
            b, c = b_col[key], c_col[key]
            if (b["method"], b["path"]) != (c["method"], c["path"]):
                rep.add("UNEXPECTED", f"{label} request", f"{key!r} {b['method']} {b['path']} -> {c['method']} {c['path']}")
            _compare_flat(rep, f"{label} {key!r} body", mig.rewrite_flat(b["body"]), c["body"], mig,
                          collection=label, is_random=is_random)
            b_saved = [(s["code"], s["name"]) for s in b["saved"]]
            c_saved = [(s["code"], s["name"]) for s in c["saved"]]
            if b_saved != c_saved:
                rep.add("UNEXPECTED", f"{label} saved responses", f"{key!r} {b_saved} -> {c_saved}")
            else:
                for bs, cs in zip(b["saved"], c["saved"]):
                    _compare_flat(rep, f"{label} {key!r} saved {bs['code']} {bs['name']!r}",
                                  mig.rewrite_flat(bs["body"]), cs["body"], mig, collection=label)
    return rep


# --------------------------------------------------------------------------- #
# retired names                                                                #
# --------------------------------------------------------------------------- #
def find_retired(names, root=REPO_ROOT):
    hits = []
    if not names:
        return hits
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b")
    for f in retired_scan_files(root):
        if RETIRED_SKIP.search(str(f)) or f.suffix not in (".py", ".js", ".yaml", ".yml", ".json", ".ebnf", ".sh"):
            continue
        for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            m = pattern.search(line)
            if m:
                hits.append(f"{f.relative_to(root)}:{n}: {m.group(1)}")
    return hits


# --------------------------------------------------------------------------- #
def _print(rep, title, out=None):
    lines = [f"# Migration check — {title}", ""]
    by_kind = {}
    for kind, area, msg in rep.items:
        by_kind.setdefault(kind, []).append(f"- [{area}] {msg}")
    if "RETIRED" in by_kind:  # always complete: grouped by file
        per_file = {}
        for kind, _area, msg in rep.items:
            if kind == "RETIRED":
                per_file.setdefault(msg.split(":")[0], []).append(msg.split(":")[1])
        by_kind["RETIRED"] = [f"- {fname}: {len(lines)} line(s) ({', '.join(lines[:12])}{'…' if len(lines) > 12 else ''})"
                              for fname, lines in sorted(per_file.items())]
    for kind in ("INCOMPLETE", "LOST", "UNEXPECTED", "RETIRED"):
        if kind in by_kind:
            lines.append(f"## {kind} ({len(by_kind[kind])})")
            lines += by_kind[kind][:200]
            if len(by_kind[kind]) > 200:
                lines.append(f"- … {len(by_kind[kind]) - 200} more")
            lines.append("")
    n = len([i for i in rep.items if i[0] in ("INCOMPLETE", "LOST", "UNEXPECTED", "RETIRED")])
    lines.append("✅ No differences beyond the declared migration" if n == 0 else f"❌ {n} finding(s)")
    text = "\n".join(lines)
    print(text)
    if out:
        Path(out).write_text(text + "\n")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--baseline", required=True)
    c.add_argument("--migration", required=True)
    c.add_argument("--report")
    c.add_argument("--exit-status", action="store_true")
    r = sub.add_parser("retired")
    r.add_argument("--migration", required=True)
    r.add_argument("--exit-status", action="store_true")
    args = ap.parse_args(argv)

    if args.mode == "snapshot":
        snap = take_snapshot()
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(snap, sort_keys=True))
        print(f"Snapshot of {snap['meta']['commit']} written to {args.out}: "
              f"{len(snap['dd'])} DD rules, {len(snap['spec']['schemas'])} schemas, "
              f"{len(snap['spec']['operations'])} operations, "
              + ", ".join(f"{k} {len(v or {})} requests" for k, v in snap["collections"].items()))
        return 0

    mig = Migration(yaml.safe_load(Path(args.migration).read_text()) or {})
    if args.mode == "retired":
        rep = Report()
        for hit in find_retired(mig.retired):
            rep.add("RETIRED", "retired name", hit)
        n = _print(rep, f"{mig.name} — retired names")
        return 1 if (args.exit_status and n) else 0

    baseline = json.loads(Path(args.baseline).read_text())
    rep = compare(baseline, take_snapshot(), mig)
    for hit in find_retired(mig.retired):
        rep.add("RETIRED", "retired name", hit)
    n = _print(rep, f"{mig.name} (baseline {baseline['meta']['commit']})", args.report)
    return 1 if (args.exit_status and n) else 0


if __name__ == "__main__":
    sys.exit(main())
