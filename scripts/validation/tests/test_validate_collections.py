#!/usr/bin/env python3
"""
Golden test suite for validate_collections_against_spec.py.

Proves the validator is trustworthy BEFORE it is used to measure the
dual-template merge. Three test classes (per the agreed methodology):

  1. Positive controls — the EBNF-driven Linked/Test collections (System A)
     MUST pass with zero failures. Guards against false positives (the exact
     failure mode of the legacy hardcoded validator).

  2. Negative controls / golden §5a — the Getting Started collections
     (System B) MUST fail on precisely the endpoints documented in the
     DUAL_TEMPLATE_SYSTEM_FINDINGS §5a divergence table, and MUST pass the
     known-good ones (multi/zip; the 8 conforming single/doc examples).
     Guards against false negatives.

  3. Synthetic fault injection — hand-crafted request bodies with known
     defects (wrong field name, missing required, unexpected field) plus known
     clean bodies, validated against real spec schemas. Exercises edge cases the
     real collections don't, independent of the merge.

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
PREFIX = "/jobs/submit"

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


# --------------------------------------------------------------------------- #
# 1. Positive controls — System A must be clean                               #
# --------------------------------------------------------------------------- #
def test_positive_controls():
    print("\n[1] Positive controls (System A, EBNF-driven) — expect ZERO failures")
    for rel in ["c2mapiv2-linked-collection-flat.json",
                "c2mapiv2-test-collection-flat.json"]:
        res = V.validate_collection(SPEC, load_collection(rel), PREFIX, True)
        nfail = sum(1 for r in res if r["status"] == "FAIL")
        check(nfail == 0, f"{rel}: {nfail} failures (expected 0)")


# --------------------------------------------------------------------------- #
# 2. Negative controls — golden §5a divergence table                          #
# --------------------------------------------------------------------------- #
# Expected number of FAILING examples per endpoint in the Getting Started
# collections (System B). Derived from the verified §5a table.
GOLDEN_FAIL = {
    "/jobs/submit/single/doc": 2,                     # mail merge + naming addressList
    "/jobs/submit/single/pdf/addressCapture": 1,      # docSourceAll vs docSourceStandard
    "/jobs/submit/single/pdf/split": 1,               # docSourceAll+jobs
    "/jobs/submit/single/pdf/split/addressCapture": 1,# docSourceAll + missing list
    "/jobs/submit/multi/doc": 2,                       # jobs vs multiDocJobs (2 examples)
    "/jobs/submit/multi/doc/merge": 1,                # documentsToMerge vs mergeDocumentSource
    "/jobs/submit/multi/zip/addressCapture": 1,       # docSourceAll vs zipDocumentSource
}
# These endpoints must be fully clean in System B (the §5a "match" cases).
GOLDEN_CLEAN = ["/jobs/submit/multi/zip"]


def test_negative_controls():
    print("\n[2] Negative controls (System B, Getting Started) — golden §5a table")
    for rel in ["c2mapiv2-getting-started-linked-collection.json",
                "c2mapiv2-getting-started-test-collection.json"]:
        res = V.validate_collection(SPEC, load_collection(rel), PREFIX, True)
        fc = fail_counts_by_path(res)
        print(f"  {rel}")
        for path, expected in GOLDEN_FAIL.items():
            check(fc.get(path, 0) == expected,
                  f"{path}: {fc.get(path,0)} failing examples (expected {expected})")
        for path in GOLDEN_CLEAN:
            check(fc.get(path, 0) == 0,
                  f"{path}: {fc.get(path,0)} failures (expected 0 — known-good)")
        # And the specific missing-field diagnostics must be present:
        joined = "\n".join(e for r in res for e in r["errors"])
        check("missing required field 'multiDocJobs'" in joined,
              "diagnostic present: missing multiDocJobs")
        check("unexpected field 'jobs'" in joined,
              "diagnostic present: unexpected 'jobs'")
        check("missing required field 'docSourceStandard'" in joined,
              "diagnostic present: missing docSourceStandard")


# --------------------------------------------------------------------------- #
# 3. Synthetic fault injection — known defects vs known-clean                  #
# --------------------------------------------------------------------------- #
def errs_for(path, body):
    schema = V.request_body_schema(SPEC, path, "post")
    assert schema is not None, f"no schema for {path}"
    return V.structural_errors(body, schema, SPEC, "body", True)


def test_synthetic_faults():
    print("\n[3] Synthetic fault injection")

    # 3a. Clean multi/doc body -> no errors
    clean_multidoc = {"multiDocJobs": [
        {"docSourceAll": {"documentId": 1},
         "recipientAddressSource": {"singleAddress": {"firstName": "A", "lastName": "B",
            "address1": "1 St", "city": "X", "state": "NY", "zip": "10001", "country": "USA"}}}]}
    check(errs_for("/jobs/submit/multi/doc", clean_multidoc) == [],
          "clean multi/doc body -> no errors")

    # 3b. Wrong wrapper key (jobs instead of multiDocJobs) -> 2 defects
    e = errs_for("/jobs/submit/multi/doc", {"jobs": []})
    check(any("missing required field 'multiDocJobs'" in x for x in e),
          "wrong-wrapper multi/doc -> flags missing multiDocJobs")
    check(any("unexpected field 'jobs'" in x for x in e),
          "wrong-wrapper multi/doc -> flags unexpected 'jobs'")

    # 3c. Empty body -> missing required
    e = errs_for("/jobs/submit/multi/doc", {})
    check(any("missing required field 'multiDocJobs'" in x for x in e),
          "empty multi/doc -> flags missing multiDocJobs")

    # 3d. Clean single/doc -> no errors
    clean_single = {"docSourceAll": {"documentId": 1},
                    "recipientAddressSource": {"singleAddress": {"firstName": "A"}}}
    check(errs_for("/jobs/submit/single/doc", clean_single) == [],
          "clean single/doc body -> no errors")

    # 3e. Unexpected top-level field -> flagged
    e = errs_for("/jobs/submit/single/doc", dict(clean_single, bogusField=1))
    check(any("unexpected field 'bogusField'" in x for x in e),
          "single/doc with extra field -> flags unexpected 'bogusField'")

    # 3f. Missing a required field -> flagged
    e = errs_for("/jobs/submit/single/doc", {"docSourceAll": {"documentId": 1}})
    check(any("missing required field 'recipientAddressSource'" in x for x in e),
          "single/doc missing recipientAddressSource -> flagged")

    # 3g. Placeholder values must NOT cause type false-positives
    ph = {"docSourceAll": {"documentId": "<Integer>"},
          "recipientAddressSource": {"singleAddress": {"firstName": "<String>"}},
          "jobTemplate": "<String>"}
    check(errs_for("/jobs/submit/single/doc", ph) == [],
          "placeholder single/doc body -> no false positives")

    # 3h. pdf/split wrong field names -> both required flagged
    e = errs_for("/jobs/submit/single/pdf/split", {"docSourceAll": {}, "jobs": []})
    check(any("missing required field 'docSourceStandard'" in x for x in e) and
          any("missing required field 'pdfSplitJobsWithAddress'" in x for x in e),
          "pdf/split wrong names -> flags both missing required fields")


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
