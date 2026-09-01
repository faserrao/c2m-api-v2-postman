#!/usr/bin/env python3
"""
diff_collections.py — structural before/after diff for Postman collections.

Second acceptance check for the dual-template merge, complementing the
spec-driven validator (validate_collections_against_spec.py). The validator
confirms TOP-LEVEL conformance to the OpenAPI spec; this tool shows EVERY
structural change between two collections — including the oneOf interiors and
the flattening the validator intentionally does not cover — so a merge or
regeneration can be reviewed before anything is published.

STRUCTURAL, not value-level: it compares the set of field PATHS + kinds (array
indices normalized to `[]`, scalar VALUES ignored) so random example data does
not create noise. What surfaces is real structure: `jobs` -> `multiDocJobs`,
wrapper add/removal, object-vs-array flips, nesting/flattening, added/removed
fields, and whether examples are preserved.

Two views:
  1. Endpoint rollup (name-independent) — per method+path, the union of field
     paths, each marked [both] / [-before-only] / [+after-only]. Always
     meaningful even when example NAMES differ between the two collections
     (as they do across the two template systems).
  2. Request-level — for requests whose (method, path, name) match in both, the
     per-request added/removed paths; plus the lists of unmatched (before-only /
     after-only) request names, so nothing is hidden.

Usage:
  VENV=scripts/python_env/e2o.venv/bin/python
  $VENV scripts/validation/diff_collections.py \
      --before postman/generated/<current>.json \
      --after  postman/generated/<regenerated>.json \
      [--path-prefix /jobs/submit] [--json]

Exit code is 0 always (this is a report, not a gate). Read it and decide.
"""

import argparse
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate_collections_against_spec as V  # reuse iter_requests / REPO  # noqa: E402


# --------------------------------------------------------------------------- #
# Structural signature                                                        #
# --------------------------------------------------------------------------- #
def _kind(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "num"
    if v is None:
        return "null"
    if isinstance(v, str):
        if v.startswith("<") and v.endswith(">"):
            return f"ph{v}"   # placeholder token, e.g. ph<oneOf>, ph<String>
        return "str"
    return "scalar"


def signature(value, path="", out=None):
    """Set of 'path:kind' entries. Array indices collapse to '[]'; scalar values
    are ignored (only their kind is kept)."""
    if out is None:
        out = set()
    if isinstance(value, dict):
        if path:
            out.add(f"{path}:obj")
        for k, v in value.items():
            signature(v, f"{path}.{k}" if path else k, out)
    elif isinstance(value, list):
        out.add(f"{path or '(root)'}:arr")
        for el in value:
            signature(el, f"{path}[]", out)
    else:
        out.add(f"{path or '(root)'}:{_kind(value)}")
    return out


# --------------------------------------------------------------------------- #
# Load                                                                        #
# --------------------------------------------------------------------------- #
def load_requests(path, prefix):
    with open(path) as f:
        col = json.load(f)
    reqs = []
    for r in V.iter_requests(col):
        if prefix and not r["path"].startswith(prefix):
            continue
        raw = (r.get("raw") or "").strip()
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"__unparseable__": True}
        r["_body"] = body
        r["_sig"] = signature(body)
        reqs.append(r)
    return reqs


# --------------------------------------------------------------------------- #
# Views                                                                       #
# --------------------------------------------------------------------------- #
def endpoint_rollup(before, after):
    """Per (method, path): union signature on each side + names."""
    def group(reqs):
        d = defaultdict(lambda: {"names": [], "sig": set()})
        for r in reqs:
            g = d[(r["method"], r["path"])]
            g["names"].append(r["name"])
            g["sig"] |= r["_sig"]
        return d
    b, a = group(before), group(after)
    keys = sorted(set(b) | set(a), key=lambda k: k[1])
    rows = []
    for k in keys:
        bs = b.get(k, {"names": [], "sig": set()})
        as_ = a.get(k, {"names": [], "sig": set()})
        rows.append({
            "method": k[0], "path": k[1],
            "before_names": bs["names"], "after_names": as_["names"],
            "both": sorted(bs["sig"] & as_["sig"]),
            "before_only": sorted(bs["sig"] - as_["sig"]),
            "after_only": sorted(as_["sig"] - bs["sig"]),
        })
    return rows


def request_level(before, after):
    def by_key(reqs):
        d = {}
        for r in reqs:
            d[(r["method"], r["path"], r["name"])] = r
        return d
    b, a = by_key(before), by_key(after)
    matched, only_before, only_after = [], [], []
    for k in sorted(set(b) & set(a), key=lambda k: (k[1], k[2])):
        added = sorted(a[k]["_sig"] - b[k]["_sig"])
        removed = sorted(b[k]["_sig"] - a[k]["_sig"])
        if added or removed:
            matched.append({"path": k[1], "name": k[2], "added": added, "removed": removed})
    for k in sorted(set(b) - set(a), key=lambda k: (k[1], k[2])):
        only_before.append({"path": k[1], "name": k[2]})
    for k in sorted(set(a) - set(b), key=lambda k: (k[1], k[2])):
        only_after.append({"path": k[1], "name": k[2]})
    return matched, only_before, only_after


# --------------------------------------------------------------------------- #
# Output                                                                       #
# --------------------------------------------------------------------------- #
def print_human(before_path, after_path, rows, matched, only_b, only_a):
    print("=" * 80)
    print("Collection structural diff (before -> after)")
    print(f"BEFORE: {before_path}")
    print(f"AFTER : {after_path}")
    print("=" * 80)

    changed = [r for r in rows if r["before_only"] or r["after_only"]]
    print(f"\n## Endpoint rollup — {len(changed)}/{len(rows)} endpoints have structural changes\n")
    for r in rows:
        tag = "⚠️ CHANGED" if (r["before_only"] or r["after_only"]) else "· unchanged"
        print(f"[{tag}] {r['path']}   (before {len(r['before_names'])} ex, after {len(r['after_names'])} ex)")
        for p in r["before_only"]:
            print(f"      - {p}")     # removed by the after collection
        for p in r["after_only"]:
            print(f"      + {p}")     # added by the after collection

    print("\n## Request-level (matched by method+path+name)")
    print(f"   matched-with-changes: {len(matched)} | before-only: {len(only_b)} | after-only: {len(only_a)}")
    for m in matched:
        print(f"  ~ [{m['path']}] {m['name']}")
        for p in m["removed"]:
            print(f"      - {p}")
        for p in m["added"]:
            print(f"      + {p}")
    if only_b:
        print("  before-only requests (no same-name match in after):")
        for r in only_b:
            print(f"      - [{r['path']}] {r['name']}")
    if only_a:
        print("  after-only requests (no same-name match in before):")
        for r in only_a:
            print(f"      + [{r['path']}] {r['name']}")

    print("\n" + "-" * 80)
    print("Legend: '-' present only in BEFORE (removed), '+' present only in AFTER (added).")
    print("Structural only — scalar values are ignored; array indices collapse to [].")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--path-prefix", default="/jobs/submit")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    bpath = args.before if os.path.isabs(args.before) else os.path.join(V.REPO, args.before)
    apath = args.after if os.path.isabs(args.after) else os.path.join(V.REPO, args.after)
    before = load_requests(bpath, args.path_prefix)
    after = load_requests(apath, args.path_prefix)

    rows = endpoint_rollup(before, after)
    matched, only_b, only_a = request_level(before, after)

    if args.json:
        print(json.dumps({
            "before": args.before, "after": args.after,
            "endpoint_rollup": rows,
            "request_level": {"matched_with_changes": matched,
                              "before_only": only_b, "after_only": only_a},
        }, indent=2))
    else:
        print_human(args.before, args.after, rows, matched, only_b, only_a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
