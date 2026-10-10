#!/usr/bin/env python3
"""
Golden tests for validate_pipeline_consistency.py — prove each check fires on a known
fault (synthetic injection) and stays quiet on known-good input, before trusting it.

Run via:
    python -m pytest scripts/validation/tests/test_pipeline_consistency.py -v
or:
    make validate-collections-conformance-test
"""

import copy
import json
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "validation"))

import validate_pipeline_consistency as V  # noqa: E402

SPEC = yaml.safe_load((REPO_ROOT / "openapi" / "c2mapiv2-openapi-spec-final.yaml").read_text())
SPECX = yaml.safe_load((REPO_ROOT / "openapi" / "c2mapiv2-openapi-spec-final-with-examples.yaml").read_text())
BASE = yaml.safe_load((REPO_ROOT / "openapi" / "c2mapiv2-openapi-spec-base.yaml").read_text())
HINTS = yaml.safe_load((REPO_ROOT / "config" / "faker_hints.yaml").read_text())["faker_hints"]
DD = V.DDModel(REPO_ROOT / "data_dictionary" / "c2mapiv2-dd.ebnf")

ADDRESS = {"firstName": "A", "lastName": "B", "address1": "1 Main St", "city": "Springfield",
           "state": "IL", "zip": "62701", "country": "USA"}
CLEAN_BODY = {"docSourceAll": {"documentIdSource": {"documentId": 1}},
              "recipientAddressSource": {"recipientAddressByList": {"addressList": [ADDRESS]}}}
STATIC_CODES = sorted(SPEC["paths"]["/static"]["post"]["responses"])


def request(body, responses=(), tests=None):
    item = {"name": "POST /static", "request": {
        "method": "POST",
        "url": {"raw": "{{baseUrl}}/static", "host": ["{{baseUrl}}"], "path": ["static"]},
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "auth": {"type": "bearer"},
        "body": {"mode": "raw", "raw": json.dumps(body)}},
        "response": list(responses)}
    if tests:
        item["event"] = [{"listen": "test", "script": {"exec": [tests]}}]
    return item


def error_example(code, error_type, error_code, tracking="TRK-20260115-ABC123", details="{}"):
    return {"name": f"{code} example", "code": int(code),
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": json.dumps({"errorType": error_type, "errorMessage": "m", "errorCode": error_code,
                                "errorDetails": details, "errorTrackingId": tracking}),
            "originalRequest": {"method": "POST", "url": {"path": ["static"]},
                                "body": {"mode": "raw", "raw": json.dumps(CLEAN_BODY)}}}


def all_dd_error_examples():
    """Saved responses exactly as the spec declares them for POST /static (D10: the spec's
    examples, generated from the DD, are what every collection must carry)."""
    out = []
    for st, r in SPEC["paths"]["/static"]["post"]["responses"].items():
        for ex in r["content"]["application/json"].get("examples", {}).values():
            out.append({"name": ex.get("summary", st), "code": int(st),
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "body": json.dumps(ex["value"]),
                        "originalRequest": {"method": "POST", "url": {"path": ["static"]},
                                            "body": {"mode": "raw", "raw": json.dumps(CLEAN_BODY)}}})
    return out


def run_collection(items, typed=False):
    F = V.Findings()
    V.check_collection("Synthetic", {"item": items, "auth": {"type": "bearer"}}, typed, SPEC, V.SpecTools(SPEC), F)
    return {cat for (cat, _scope) in F.items}


def run_dd(specs):
    F = V.Findings()
    V.check_dd_to_spec(DD, specs, HINTS, F)
    return F


class TestCollectionChecks(unittest.TestCase):

    def test_clean_request_and_examples_have_no_findings(self):
        codes = ",".join(STATIC_CODES)
        cats = run_collection([request(CLEAN_BODY, all_dd_error_examples(),
                                       f"pm.expect([{codes}]).to.include(pm.response.code);")])
        self.assertEqual(cats - {"B-OPERATION-NOT-IN-COLLECTION"}, set())

    def test_error_details_not_json(self):
        examples = all_dd_error_examples()
        examples[0] = error_example("400", "ValidationError", "MISSING_REQUIRED_FIELD", details='{"field": oops}')
        self.assertIn("B-EXAMPLE-DETAILS-NOT-JSON", run_collection([request(CLEAN_BODY, examples)]))

    def test_error_details_unresolved_token(self):
        examples = all_dd_error_examples()
        examples[0] = error_example("422", "ValidationError", "INVALID_ENUM_VALUE",
                                    details='{"allowed": {mailClass_enum}}')
        cats = run_collection([request(CLEAN_BODY, examples)])
        self.assertIn("B-EXAMPLE-DETAILS-UNRESOLVED-TOKEN", cats)
        self.assertIn("B-EXAMPLE-DETAILS-NOT-JSON", cats)

    def test_saved_example_differs_from_spec(self):
        """D10/N4: a saved response must equal the spec example for its status and code."""
        examples = all_dd_error_examples()
        for e in examples:
            body = json.loads(e["body"])
            if body.get("errorCode") == "INVALID_TOKEN":
                body["errorDetails"] = '{"reason": "invalid signature"}'
                e["body"] = json.dumps(body)
        self.assertIn("B-EXAMPLE-DIFFERS-FROM-SPEC", run_collection([request(CLEAN_BODY, examples)]))

    def test_error_example_coverage_per_status_and_code(self):
        """N2: a code the DD maps under two statuses needs an example under each."""
        examples = [e for e in all_dd_error_examples()
                    if not (e["code"] == 400 and json.loads(e["body"])["errorCode"] == "INVALID_FORMAT")]
        self.assertIn("B-EXAMPLE-ERROR-COVERAGE", run_collection([request(CLEAN_BODY, examples)]))

    def test_mutual_exclusion(self):
        body = dict(CLEAN_BODY, jobTemplate="t", jobOptions={})
        self.assertIn("B-MUTUAL-EXCLUSION", run_collection([request(body)]))

    def test_unknown_body_field(self):
        self.assertIn("B-BODY-UNKNOWN-FIELD", run_collection([request(dict(CLEAN_BODY, bogusField=1))]))

    def test_body_schema_violation(self):
        self.assertIn("B-BODY-SCHEMA", run_collection([request({"docSourceAll": {}})]))

    def test_example_error_code_not_mapped_to_status(self):
        bad = error_example("400", "ResourceNotFoundError", "INVALID_TOKEN")
        self.assertIn("B-EXAMPLE-ERROR-MAP", run_collection([request(CLEAN_BODY, [bad])]))

    def test_example_status_not_declared(self):
        bad = error_example("418", "ValidationError", "INVALID_JSON")
        self.assertIn("B-EXAMPLE-STATUS-UNDECLARED", run_collection([request(CLEAN_BODY, [bad])]))

    def test_bad_tracking_id(self):
        bad = error_example("400", "ValidationError", "INVALID_JSON", tracking="TRK-x")
        self.assertIn("B-EXAMPLE-TRACKING-ID", run_collection([request(CLEAN_BODY, [bad])]))

    def test_placeholder_in_example_collection(self):
        bad = error_example("400", "ValidationError", "INVALID_JSON", tracking="<string>")
        self.assertIn("B-PLACEHOLDER-IN-EXAMPLE", run_collection([request(CLEAN_BODY, [bad])]))

    def test_placeholders_allowed_in_typed_collection(self):
        typed_body = {"docSourceAll": {"requestIdSource": {"requestId": "<integer>"}},
                      "recipientAddressSource": "<oneOf>"}
        cats = run_collection([request(typed_body)], typed=True)
        self.assertNotIn("B-BODY-SCHEMA", cats)
        self.assertNotIn("B-PLACEHOLDER-IN-EXAMPLE", cats)

    def test_test_script_accepts_undeclared_status(self):
        cats = run_collection([request(CLEAN_BODY, tests="pm.expect([200,201,204]).to.include(pm.response.code);")])
        self.assertIn("B-TEST-STATUS-ASSERTION", cats)

    def test_error_example_field_not_in_body(self):
        """N5: an error example must name a field that exists in the endpoint body."""
        examples = all_dd_error_examples()
        examples[0] = error_example("400", "ValidationError", "MISSING_REQUIRED_FIELD",
                                    details='{"field": "bogusField"}')
        self.assertIn("B-EXAMPLE-FIELD-NOT-IN-BODY", run_collection([request(CLEAN_BODY, examples)]))

    def test_error_example_real_dotted_path_accepted(self):
        examples = all_dd_error_examples()
        examples[0] = error_example("400", "ValidationError", "INVALID_FORMAT",
                                    details='{"errors": [{"field": "recipientAddressSource.recipientAddressByList.addressList[0].zip"}]}')
        cats = run_collection([request(CLEAN_BODY, examples)])
        self.assertNotIn("B-EXAMPLE-FIELD-NOT-IN-BODY", cats)

    def test_mutual_exclusion_example_where_fields_absent_is_impossible(self):
        tools = V.SpecTools(SPEC)
        zip_body = tools.body_paths(SPEC["paths"]["/batch/zip"]["post"]["requestBody"]["content"]
                                    ["application/json"]["schema"])
        problems = V.field_ref_problems('{"fields": ["jobTemplate", "jobOptions"]}',
                                        "MUTUAL_EXCLUSION_VIOLATION", zip_body)
        self.assertEqual({k for k, _ in problems}, {"IMPOSSIBLE-ERROR"})

    def test_auth_error_examples_not_checked_against_dd_error_map(self):
        """Auth endpoints use the overlay's AuthError format (code/message/details); the DD
        error map (errorType/errorCode) applies to job endpoints only."""
        item = {"name": "POST /auth/tokens/short", "request": {
            "method": "POST",
            "url": {"raw": "{{baseUrl}}/auth/tokens/short", "host": ["{{baseUrl}}"], "path": ["auth", "tokens", "short"]},
            "header": [{"key": "Content-Type", "value": "application/json"}], "auth": {"type": "bearer"},
            "body": {"mode": "raw", "raw": json.dumps({"scopes": ["jobs:submit"]})}},
            "response": [{"name": "Bad request", "code": 400,
                          "body": json.dumps({"code": "invalid_request", "message": "Bad request"})}]}
        self.assertNotIn("B-EXAMPLE-ERROR-MAP", run_collection([item]))

    def test_payment_type_must_match_details(self):
        """D1: paymentType must name the details object sent with it."""
        good = dict(CLEAN_BODY, paymentDetails={"paymentType": "invoice",
                                               "invoiceDetails": {"invoiceNumber": "INV-1", "amountDue": 10}})
        bad = dict(CLEAN_BODY, paymentDetails={"paymentType": "invoice",
                                              "creditCardDetails": {"cardType": "visa", "cardNumber": "4111",
                                                                    "expirationDate": {"month": 1, "year": 2030}, "cvv": 123}})
        self.assertNotIn("B-BODY-SCHEMA", run_collection([request(good)]))
        self.assertIn("B-BODY-SCHEMA", run_collection([request(bad)]))

    def test_merge_minimum(self):
        self.assertEqual(
            [c for c, _ in V.cross_field_errors({"mergeDocumentSource": [{}]}, SPEC["info"])], ["B-MERGE-MINIMUM"])


class TestSpecChecks(unittest.TestCase):

    def specs(self):
        return {"final": copy.deepcopy(SPEC), "base": BASE, "final-with-examples": SPECX}

    def test_positive_control_dd_to_spec_has_no_errors(self):
        errors, _warns, _stale = run_dd(self.specs()).classified()
        self.assertEqual(errors, {}, f"DD→spec ERROR findings on the real build: {errors}")

    def test_missing_dd_error_status_is_flagged(self):
        specs = self.specs()
        del specs["final"]["paths"]["/static"]["post"]["responses"]["429"]
        self.assertIn(("A-ERROR-STATUS-NOT-DECLARED", "*"), run_dd(specs).items)

    def test_enum_drift_is_flagged(self):
        specs = self.specs()
        specs["final"]["components"]["schemas"]["mailClass"]["enum"].reverse()
        self.assertIn(("A-RULE-STRUCTURE-MISMATCH", "*"), run_dd(specs).items)

    def test_missing_numeric_constraint_is_flagged(self):
        specs = self.specs()
        props = specs["final"]["components"]["schemas"]["pdfSplitJobItemNoAddress"]["properties"]
        props["startPage"].pop("minimum")
        self.assertIn(("A-RULE-STRUCTURE-MISMATCH", "*"), run_dd(specs).items)

    def test_missing_success_example_is_flagged(self):
        spec = copy.deepcopy(SPECX)
        spec["paths"]["/static"]["post"]["responses"]["200"]["content"]["application/json"].pop("examples", None)
        F = V.Findings()
        V.check_spec_examples(spec, DD, F)
        self.assertIn(("C-RESPONSE-EXAMPLE-MISSING", "*"), F.items)

    def test_spec_example_naming_non_body_field_is_flagged(self):
        """N5: the pre-2026-10-07 'recipientAddressSource.postalCode' must be caught."""
        spec = copy.deepcopy(SPECX)
        for ex in spec["paths"]["/static"]["post"]["responses"]["400"]["content"]["application/json"]["examples"].values():
            if ex["value"]["errorCode"] == "INVALID_FORMAT":
                ex["value"]["errorDetails"] = '{"errors": [{"field": "recipientAddressSource.postalCode"}]}'
        F = V.Findings()
        V.check_spec_examples(spec, DD, F)
        self.assertIn(("C-EXAMPLE-FIELD-NOT-IN-BODY", "*"), F.items)

    def test_known_open_entries_reference_a_tracking_id(self):
        for key, ref in V.KNOWN_OPEN.items():
            self.assertRegex(ref, r"(\b[XLDC]\d+[a-z]?\b|/static/multi)", f"{key} has no tracking reference")


if __name__ == "__main__":
    unittest.main()
