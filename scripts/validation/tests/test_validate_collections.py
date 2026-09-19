#!/usr/bin/env python3
"""
Golden test suite for validate_collections_against_spec.py.

Proves the validator is trustworthy. Three test classes:

  1. Positive controls — the EBNF-driven Linked/Test collections (System A)
     MUST pass with zero real failures. Guards against false positives.

     Known spec gap (tracked separately): the EBNF allows `jobTemplate` on
     pdfSplitJobsWithAddress items (EBNF line 741) but the translator omits it
     from the generated schema. The validator therefore flags it as
     "unexpected field 'jobTemplate'" — a false positive. This is filtered
     from the failure count until the translator is fixed.

  2. Negative controls — the Getting Started collections (System B) are now
     CLEAN (field-name drift fixed in commit 14a60e9, Sep 2026). All endpoints
     MUST pass with zero failures. The §5a divergence table is fully resolved.

     False-negative protection is covered by test 3 (synthetic fault injection)
     which uses hardcoded known-bad request bodies independent of live
     collection state.

  3. Synthetic fault injection — hand-crafted request bodies with known
     defects (wrong field name, missing required, unexpected field) plus known
     clean bodies, validated against real spec schemas.

Run:
  scripts/python_env/e2o.venv/bin/python \
      scripts/validation/tests/test_validate_collections.py

Exit code 0 = all golden tests pass; non-zero = a regression in the validator.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VDIR = os.path.dirname(HERE)          # scripts/validation
sys.path.insert(0, VDIR)
import validate_collections_against_spec as V  # noqa: E402
import json  # noqa: E402

SPEC = V.load_spec(V.DEFAULT_SPEC)  # env-aware (Makefile-sourced) spec path
PREFIX = None  # no prefix filter — new paths span /static, /batch, /mail-merge

_failures = []


def check(cond, msg):
    status = "ok  " if cond else "FAIL"
    print(f"    [{status}] {msg}")
    if not cond:
        _failures.append(msg)


def load_collection(rel):
    with open(os.path.join(V.GEN_DIR_ABS, rel)) as f:  # env-aware generated dir
        return json.load(f)


def fail_counts_by_path(results):
    """path -> number of FAIL examples."""
    out = {}
    for r in results:
        if r["status"] == "FAIL":
            out[r["path"]] = out.get(r["path"], 0) + 1
    return out


# Known spec gap: jobTemplate is EBNF-legal on pdfSplitJobsWithAddress items
# (EBNF line 741) but the translator omits it from the generated schema. Filter
# this false-positive until the translator is fixed (see workspace audit).
_KNOWN_GAP_PATTERNS = ("unexpected field 'jobTemplate'",)


def _is_known_gap(result):
    return all(any(p in e for p in _KNOWN_GAP_PATTERNS) for e in result["errors"])


# --------------------------------------------------------------------------- #
# 1. Positive controls — System A must be clean                               #
# --------------------------------------------------------------------------- #
def test_positive_controls():
    print("\n[1] Positive controls (System A, EBNF-driven) — expect ZERO real failures")
    print("    (known gap: jobTemplate false-positive filtered — see translator TODO)")
    for rel in ["c2mapiv2-linked-collection-flat.json",
                "c2mapiv2-test-collection-flat.json"]:
        res = V.validate_collection(SPEC, load_collection(rel), PREFIX, True)
        real_failures = [r for r in res if r["status"] == "FAIL" and not _is_known_gap(r)]
        nfail = len(real_failures)
        check(nfail == 0, f"{rel}: {nfail} failures (expected 0)")


# --------------------------------------------------------------------------- #
# 2. Negative controls — Getting Started must be fully clean                  #
# --------------------------------------------------------------------------- #
# The §5a field-name drift was fixed in commit 14a60e9 (Sep 2026). All
# Getting Started endpoints now match the spec. This test enforces that the
# collections stay clean — any new failures indicate a regression.
#
# False-negative protection (validator CAN catch errors) is in test 3
# (synthetic fault injection) which uses hardcoded known-bad request bodies.
_ALL_JOB_PATHS = [
    "/static",
    "/static/address-capture",
    "/batch/split",
    "/batch/split/address-capture",
    "/mail-merge",
    "/batch/zip",
    "/batch/zip/address-capture",
]


def test_negative_controls():
    print("\n[2] Negative controls (System B, Getting Started) — must be fully clean")
    print("    (false-negative coverage provided by test 3 synthetic fault injection)")
    for rel in ["c2mapiv2-getting-started-linked-collection.json",
                "c2mapiv2-getting-started-test-collection.json"]:
        res = V.validate_collection(SPEC, load_collection(rel), PREFIX, True)
        fc = fail_counts_by_path(res)
        print(f"  {rel}")
        for path in _ALL_JOB_PATHS:
            check(fc.get(path, 0) == 0,
                  f"{path}: {fc.get(path,0)} failures (expected 0)")


# --------------------------------------------------------------------------- #
# 3. Synthetic fault injection — known defects vs known-clean                  #
# --------------------------------------------------------------------------- #
def errs_for(path, body):
    schema = V.request_body_schema(SPEC, path, "post")
    assert schema is not None, f"no schema for {path}"
    return V.structural_errors(body, schema, SPEC, "body", True)


def test_synthetic_faults():
    print("\n[3] Synthetic fault injection")

    # 3d. Clean /static body -> no errors (full address required by V3 branch descent)
    clean_addr = {"firstName": "A", "lastName": "B", "address1": "1 Main St",
                  "city": "Springfield", "state": "IL", "zip": "62701", "country": "USA"}
    clean_single = {"docSourceAll": {"documentIdSource": {"documentId": 1}},
                    "recipientAddressSource": {"singleAddress": clean_addr}}
    check(errs_for("/static", clean_single) == [],
          "clean /static body -> no errors")

    # 3e. Unexpected top-level field -> flagged
    e = errs_for("/static", dict(clean_single, bogusField=1))
    check(any("unexpected field 'bogusField'" in x for x in e),
          "/static with extra field -> flags unexpected 'bogusField'")

    # 3f. Missing a required field -> flagged
    e = errs_for("/static", {"docSourceAll": {"documentIdSource": {"documentId": 1}}})
    check(any("missing required field 'recipientAddressSource'" in x for x in e),
          "/static missing recipientAddressSource -> flagged")

    # 3g. Placeholder values must NOT cause type false-positives (V3 descends, V4 skips placeholders)
    ph_addr = {f: "<String>" for f in ["firstName", "lastName", "address1", "city", "state", "zip", "country"]}
    ph = {"docSourceAll": {"documentIdSource": {"documentId": "<Integer>"}},
          "recipientAddressSource": {"singleAddress": ph_addr},
          "jobTemplate": "<String>"}
    check(errs_for("/static", ph) == [],
          "placeholder /static body -> no false positives")

    # 3h. /batch/split wrong field names -> both required flagged
    e = errs_for("/batch/split", {"docSourceAll": {}, "jobs": []})
    check(any("missing required field 'docSourceStandard'" in x for x in e) and
          any("missing required field 'pdfSplitJobsWithAddress'" in x for x in e),
          "/batch/split wrong names -> flags both missing required fields")

    # 3i. V5 — cross-field page-range constraint
    from validate_collections_against_spec import page_range_errors
    # startPage > endPage must be caught
    bad_range = {"pdfSplitJobsNoAddress": [{"startPage": 9, "endPage": 3}]}
    e = page_range_errors(bad_range)
    check(any("startPage (9) must be <= endPage (3)" in x for x in e),
          "V5: startPage > endPage -> caught")
    # startPage < 1 must be caught
    bad_zero = {"pdfSplitJobsNoAddress": [{"startPage": 0, "endPage": 5}]}
    e = page_range_errors(bad_zero)
    check(any("must be >= 1" in x for x in e),
          "V5: startPage = 0 -> caught")
    # Placeholder values must be skipped (no false positives on typed collection)
    ph_range = {"pdfSplitJobsNoAddress": [{"startPage": "<integer>", "endPage": "<integer>"}]}
    check(page_range_errors(ph_range) == [],
          "V5: placeholder startPage/endPage -> no false positives")
    # Valid range must pass
    ok_range = {"pdfSplitJobsNoAddress": [{"startPage": 3, "endPage": 9}]}
    check(page_range_errors(ok_range) == [],
          "V5: valid startPage < endPage -> no errors")


def main():
    print("=" * 74)
    print("GOLDEN TEST SUITE — validate_collections_against_spec.py")
    print("=" * 74)
    test_positive_controls()
    test_negative_controls()
    test_synthetic_faults()
    print("\n" + "=" * 74)
    if _failures:
        print(f"RESULT: ❌ {len(_failures)} golden assertion(s) FAILED")
        for f in _failures:
            print(f"   - {f}")
        return 1
    print("RESULT: ✅ ALL golden assertions passed — validator is trustworthy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
