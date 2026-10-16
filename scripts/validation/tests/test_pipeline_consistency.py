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


def error_example(code, error_type, error_code, tracking="TRK-20260115-ABC123", details=None):
    details = {} if details is None else details
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

    def test_error_details_string_is_not_an_object(self):
        """D6: errorDetails is a JSON object; a string holding JSON (the pre-D6 form) is flagged."""
        for details in ('{"field": "docSourceAll"}', '{"field": oops}', ["docSourceAll"]):
            with self.subTest(details=details):
                examples = all_dd_error_examples()
                examples[0] = error_example("400", "ValidationError", "MISSING_REQUIRED_FIELD", details=details)
                self.assertIn("B-EXAMPLE-DETAILS-NOT-OBJECT", run_collection([request(CLEAN_BODY, examples)]))

    def test_error_details_unresolved_token(self):
        examples = all_dd_error_examples()
        examples[0] = error_example("422", "ValidationError", "INVALID_ENUM_VALUE",
                                    details={"allowed": "{mailClass_enum}"})
        cats = run_collection([request(CLEAN_BODY, examples)])
        self.assertIn("B-EXAMPLE-DETAILS-UNRESOLVED-TOKEN", cats)
        self.assertNotIn("B-EXAMPLE-DETAILS-NOT-OBJECT", cats)

    def test_saved_example_differs_from_spec(self):
        """D10/N4: a saved response must equal the spec example for its status and code."""
        examples = all_dd_error_examples()
        for e in examples:
            body = json.loads(e["body"])
            if body.get("errorCode") == "INVALID_TOKEN":
                body["errorDetails"] = {"reason": "invalid signature"}
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
                                    details={"field": "bogusField"})
        self.assertIn("B-EXAMPLE-FIELD-NOT-IN-BODY", run_collection([request(CLEAN_BODY, examples)]))

    def test_error_example_real_dotted_path_accepted(self):
        examples = all_dd_error_examples()
        examples[0] = error_example("400", "ValidationError", "INVALID_FORMAT",
                                    details={"errors": [{"field": "recipientAddressSource.recipientAddressByList.addressList[0].zip"}]})
        cats = run_collection([request(CLEAN_BODY, examples)])
        self.assertNotIn("B-EXAMPLE-FIELD-NOT-IN-BODY", cats)

    def test_mutual_exclusion_example_where_fields_absent_is_impossible(self):
        """A body without jobTemplate/jobOptions (no job endpoint has one since D3, so the
        /batch/zip body minus the pair stands in for it)."""
        tools = V.SpecTools(SPEC)
        zip_body = tools.body_paths(SPEC["paths"]["/batch/zip"]["post"]["requestBody"]["content"]
                                    ["application/json"]["schema"])
        zip_body = {k: v for k, v in zip_body.items() if not k.startswith(("jobTemplate", "jobOptions"))}
        problems = V.field_ref_problems({"fields": ["jobTemplate", "jobOptions"]},
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

    def test_merge_minimum_comes_from_the_spec(self):
        """D4: a one-document merge fails schema validation (minItems 2 from the DD
        ARRAY CONSTRAINTS block); two documents pass. No hardcoded merge check remains."""
        addr = {"firstName": "A", "lastName": "B", "address1": "1 Main St", "city": "Springfield",
                "state": "IL", "zip": "62701", "country": "USA"}
        doc = {"mergeByDocumentId": {"documentId": 1}}
        body = {"mergeDocumentSource": [doc],
                "recipientAddressSource": {"recipientAddressByList": {"addressList": [addr]}}}
        one = request(body)
        one["request"]["url"] = {"raw": "{{baseUrl}}/mail-merge", "host": ["{{baseUrl}}"], "path": ["mail-merge"]}
        two = copy.deepcopy(one)
        two["request"]["body"]["raw"] = json.dumps(dict(body, mergeDocumentSource=[doc, doc]))
        self.assertIn("B-BODY-SCHEMA", run_collection([one]))
        self.assertNotIn("B-BODY-SCHEMA", run_collection([two]))
        self.assertEqual(V.cross_field_errors({"mergeDocumentSource": [doc]}, SPEC["info"]), [])


class TestPerOperationStatusAssertions(unittest.TestCase):
    """D7 (2026-10-16): add_tests.js writes each request's own operation's statuses, from the spec."""

    SPEC_PATH = REPO_ROOT / "openapi" / "c2mapiv2-openapi-spec-final.yaml"
    SCRIPT = REPO_ROOT / "scripts" / "active" / "add_tests.js"

    @staticmethod
    def item(method, segments, exec_lines=()):
        it = {"name": f"{method} /{'/'.join(segments)}", "request": {
            "method": method, "url": {"raw": "{{baseUrl}}/" + "/".join(segments),
                                      "host": ["{{baseUrl}}"], "path": list(segments)}}}
        if exec_lines:
            it["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": list(exec_lines)}}]
        return it

    def run_script(self, items, *extra):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "in.json", Path(d) / "out.json"
            src.write_text(json.dumps({"info": {"name": "t"}, "item": items}))
            args = list(extra) if extra else ["--spec", str(self.SPEC_PATH)]
            r = subprocess.run(["node", str(self.SCRIPT), str(src), str(out), *args],
                               capture_output=True, text=True)
            return r, (json.loads(out.read_text()) if out.exists() else None)

    def declared(self, method, path):
        return sorted(int(c) for c in SPEC["paths"][path][method.lower()]["responses"])

    def asserted(self, item):
        src = "\n".join(l for e in item.get("event", []) if e["listen"] == "test" for l in e["script"]["exec"])
        arrays = [sorted(int(c) for c in a.split(",")) for a in
                  __import__("re").findall(r"\[(\s*\d{3}(?:\s*,\s*\d{3})*\s*)\]", src)]
        return arrays

    def test_each_request_asserts_its_own_operations_statuses(self):
        items = [self.item("POST", ["static"]), self.item("POST", ["auth", "tokens", "short"]),
                 self.item("POST", ["auth", "tokens", ":tokenId", "revoke"])]
        r, out = self.run_script(items)
        self.assertEqual(r.returncode, 0, r.stderr)
        for it, path in zip(out["item"], ["/static", "/auth/tokens/short", "/auth/tokens/{tokenId}/revoke"]):
            with self.subTest(path=path):
                self.assertEqual(self.asserted(it), [self.declared("POST", path)])

    def test_earlier_global_assertion_is_replaced(self):
        old = 'pm.test("Status code is allowed (200,201,204,400)", function () { pm.expect([200,201,204,400]).to.include(pm.response.code); });'
        r, out = self.run_script([self.item("POST", ["auth", "tokens", "short"], [old])])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.asserted(out["item"][0]), [self.declared("POST", "/auth/tokens/short")])

    def test_request_not_in_spec_stops_the_script(self):
        r, _ = self.run_script([self.item("POST", ["no", "such", "path"])])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not an operation in the spec", r.stderr)

    def test_global_list_option_is_retired(self):
        r, _ = self.run_script([self.item("POST", ["static"])], "--spec", str(self.SPEC_PATH),
                               "--allowed-codes", "200,400")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("retired", r.stderr)

    def test_built_test_collection_has_no_status_assertion_findings(self):
        """Positive control on the real Test collection (built by postman-build-golden-test-fixtures)."""
        path = REPO_ROOT / "postman" / "generated" / "c2mapiv2-test-collection-flat.json"
        cats = {cat for (cat, _s) in run_findings_for(json.loads(path.read_text()))}
        self.assertNotIn("B-TEST-STATUS-ASSERTION", cats)

    def test_status_assertion_mismatch_is_an_error(self):
        """D7: no longer tracked in KNOWN_OPEN."""
        self.assertIsNone(V.Findings.tracking("B-TEST-STATUS-ASSERTION", "Test"))


class TestCollectionCoverage(unittest.TestCase):
    """L10/L8 (D8): Real-World and Getting Started cover every job endpoint (not auth, by
    design); Real-World authenticates like Linked."""

    @staticmethod
    def findings(label, name):
        path = REPO_ROOT / "postman" / "generated" / f"c2mapiv2-{name}.json"
        F = V.Findings()
        V.check_collection(label, json.loads(path.read_text()), V.COLLECTIONS[label][1], SPEC, V.SpecTools(SPEC), F)
        return F

    def test_real_world_covers_every_job_endpoint_and_authenticates(self):
        cats = {c for (c, _s) in self.findings("Real-World", "real-world-use-cases-collection").items}
        self.assertNotIn("B-OPERATION-NOT-IN-COLLECTION", cats)
        self.assertNotIn("B-NO-AUTH", cats)

    def test_getting_started_scope_is_job_endpoints(self):
        cats = {c for (c, _s) in self.findings("GS-Test", "getting-started-test-collection").items}
        self.assertNotIn("B-OPERATION-NOT-IN-COLLECTION", cats)

    def test_job_only_collection_missing_a_job_endpoint_is_flagged(self):
        coll = json.loads((REPO_ROOT / "postman" / "generated" /
                           "c2mapiv2-real-world-use-cases-collection.json").read_text())
        def drop(items):
            return [dict(it, item=drop(it["item"])) if "item" in it else it for it in items
                    if "item" in it or it["request"]["url"].get("path") != ["batch", "split"]]
        coll["item"] = drop(coll["item"])
        F = V.Findings()
        V.check_collection("Real-World", coll, False, SPEC, V.SpecTools(SPEC), F)
        self.assertIn("POST /batch/split", " ".join(F.items.get(("B-OPERATION-NOT-IN-COLLECTION", "Real-World"), [])))

    def test_coverage_findings_are_errors(self):
        for label in ("GS-Linked", "GS-Test", "Real-World"):
            self.assertIsNone(V.Findings.tracking("B-OPERATION-NOT-IN-COLLECTION", label))
        self.assertIsNone(V.Findings.tracking("B-NO-AUTH", "Real-World"))


class TestSavedResponsesEverywhere(unittest.TestCase):
    """D9: every collection carries saved responses, Getting Started included."""

    def test_getting_started_collections_have_the_spec_examples(self):
        for label, name in (("GS-Linked", "getting-started-linked-collection"),
                            ("GS-Test", "getting-started-test-collection")):
            with self.subTest(label=label):
                coll = json.loads((REPO_ROOT / "postman" / "generated" / f"c2mapiv2-{name}.json").read_text())
                F = V.Findings()
                V.check_collection(label, coll, V.COLLECTIONS[label][1], SPEC, V.SpecTools(SPEC), F)
                cats = {c for (c, _s) in F.items}
                self.assertFalse({"B-NO-SAVED-RESPONSES", "B-EXAMPLE-DIFFERS-FROM-SPEC",
                                  "B-EXAMPLE-ERROR-COVERAGE"} & cats, F.items)
                counts = {len(it.get("response") or []) for _f, it in V.iter_requests(coll)}
                self.assertEqual(counts, {len(V.spec_examples(SPEC["paths"]["/static"]["post"]))})

    def test_request_without_saved_responses_is_an_error(self):
        cats = run_collection([request(CLEAN_BODY)])
        self.assertIn("B-NO-SAVED-RESPONSES", cats)
        self.assertIsNone(V.Findings.tracking("B-NO-SAVED-RESPONSES", "GS-Test"))


class TestAuthExamplesL6(unittest.TestCase):
    """L6: auth saved responses' originalRequest is the request; tokenId is a real value."""

    SCRIPT = REPO_ROOT / "scripts" / "active" / "add_auth_examples.js"
    OVERLAY = REPO_ROOT / "openapi" / "overlays" / "auth.tokens.yaml"

    def run_script(self, items, overlay=None):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "in.json", Path(d) / "out.json"
            src.write_text(json.dumps({"info": {"name": "t"}, "item": items}))
            r = subprocess.run(["node", str(self.SCRIPT), str(src), str(out), "--auth-overlay",
                                str(overlay or self.OVERLAY)], capture_output=True, text=True)
            return r, (json.loads(out.read_text()) if out.exists() else None)

    @staticmethod
    def items():
        stale = {"mode": "raw", "raw": json.dumps({"grant_type": "assertion", "ttl_seconds": 12})}
        long_tok = {"name": "POST /auth/tokens/long", "request": {
            "method": "POST", "url": {"path": ["auth", "tokens", "long"]}, "body": {"mode": "raw", "raw": "{}"}},
            "response": [{"code": 201, "name": "ok", "originalRequest": {"method": "POST", "body": dict(stale)}}]}
        revoke = {"name": "POST /auth/tokens/:tokenId/revoke", "request": {
            "method": "POST", "url": {"path": ["auth", "tokens", ":tokenId", "revoke"],
                                      "variable": [{"key": "tokenId", "value": "<string>"}]}},
            "response": [{"code": 204, "name": "ok", "originalRequest": {
                "method": "POST", "url": {"path": ["auth", "tokens", ":tokenId", "revoke"],
                                          "variable": [{"key": "tokenId", "value": "<string>"}]}}}]}
        return [long_tok, revoke]

    def test_saved_original_request_follows_the_new_body(self):
        r, out = self.run_script(self.items())
        self.assertEqual(r.returncode, 0, r.stderr)
        long_tok = out["item"][0]
        self.assertEqual(long_tok["response"][0]["originalRequest"]["body"]["raw"], long_tok["request"]["body"]["raw"])
        self.assertGreaterEqual(json.loads(long_tok["request"]["body"]["raw"])["ttl_seconds"], 3600)

    def test_token_id_takes_the_overlay_example(self):
        example = yaml.safe_load(self.OVERLAY.read_text())["paths"]["/auth/tokens/{tokenId}/revoke"]["post"]["parameters"][0]["example"]
        r, out = self.run_script(self.items())
        self.assertEqual(r.returncode, 0, r.stderr)
        revoke = out["item"][1]
        self.assertEqual(revoke["request"]["url"]["variable"][0]["value"], example)
        self.assertEqual(revoke["response"][0]["originalRequest"]["url"]["variable"][0]["value"], example)

    def test_path_parameter_without_example_stops_the_script(self):
        import tempfile
        text = self.OVERLAY.read_text().replace('          example: "tok_st_9f3d2c"\n', "")
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(text)
        r, _ = self.run_script(self.items(), overlay=f.name)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("has no example", r.stderr)

    def test_original_request_that_differs_is_an_error(self):
        examples = all_dd_error_examples()
        examples[0]["originalRequest"]["body"]["raw"] = json.dumps({"docSourceAll": "other"})
        cats = run_collection([request(CLEAN_BODY, examples)])
        self.assertIn("B-EXAMPLE-ORIGINAL-REQUEST-DIFFERS", cats)
        self.assertIsNone(V.Findings.tracking("B-EXAMPLE-ORIGINAL-REQUEST-DIFFERS", "Test"))

    def test_nothing_is_tracked_as_open(self):
        """With L6 fixed, the gate's KNOWN_OPEN table is empty: every finding is an ERROR."""
        self.assertEqual(V.KNOWN_OPEN, {})


def run_findings_for(collection):
    F = V.Findings()
    V.check_collection("Test", collection, False, SPEC, V.SpecTools(SPEC), F)
    return F.items


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

    def test_missing_list_minimum_is_flagged(self):
        """D4: a list schema without the minItems its DD ARRAY CONSTRAINTS entry sets
        (or with a different one) is a structure mismatch."""
        for change in ("drop", "change"):
            with self.subTest(change=change):
                specs = self.specs()
                lst = specs["final"]["components"]["schemas"]["documentsToMerge"]
                lst.pop("minItems") if change == "drop" else lst.update(minItems=1)
                self.assertIn(("A-RULE-STRUCTURE-MISMATCH", "*"), run_dd(specs).items)

    def test_missing_success_example_is_flagged(self):
        spec = copy.deepcopy(SPECX)
        spec["paths"]["/static"]["post"]["responses"]["200"]["content"]["application/json"].pop("examples", None)
        F = V.Findings()
        V.check_spec_examples(spec, DD, F)
        self.assertIn(("C-RESPONSE-EXAMPLE-MISSING", "*"), F.items)

    def test_spec_error_details_string_is_flagged(self):
        """D6: a spec error example whose errorDetails is a string fails the schema and the check."""
        spec = copy.deepcopy(SPECX)
        ex = next(iter(spec["paths"]["/static"]["post"]["responses"]["400"]["content"]["application/json"]["examples"].values()))
        ex["value"]["errorDetails"] = json.dumps(ex["value"]["errorDetails"])
        F = V.Findings()
        V.check_spec_examples(spec, DD, F)
        self.assertIn(("C-EXAMPLE-DETAILS-NOT-OBJECT", "*"), F.items)
        self.assertIn(("C-RESPONSE-EXAMPLE-INVALID", "*"), F.items)

    def test_dd_object_rule_expects_free_form_object_schema(self):
        """D6: the gate's model of a DD `object` rule is type object, additionalProperties true;
        a spec that still types errorDetails as a string is a Layer A finding."""
        self.assertEqual({k: v for k, v in DD.expected("errorDetails").items() if k != "_equivalent_ref"},
                         {"type": "object", "additionalProperties": True})
        specs = self.specs()
        specs["final"]["components"]["schemas"]["errorDetails"] = {
            "description": specs["final"]["components"]["schemas"]["errorDetails"]["description"], "type": "string"}
        F = run_dd(specs)
        self.assertIn("errorDetails", " ".join(F.items.get(("A-RULE-STRUCTURE-MISMATCH", "*"), [])))

    def test_spec_example_naming_non_body_field_is_flagged(self):
        """N5: the pre-2026-10-07 'recipientAddressSource.postalCode' must be caught."""
        spec = copy.deepcopy(SPECX)
        for ex in spec["paths"]["/static"]["post"]["responses"]["400"]["content"]["application/json"]["examples"].values():
            if ex["value"]["errorCode"] == "INVALID_FORMAT":
                ex["value"]["errorDetails"] = {"errors": [{"field": "recipientAddressSource.postalCode"}]}
        F = V.Findings()
        V.check_spec_examples(spec, DD, F)
        self.assertIn(("C-EXAMPLE-FIELD-NOT-IN-BODY", "*"), F.items)

    # X6 / L1 — DD reachability, @reserved, hint types
    def _dd_findings(self, mutate_text):
        import tempfile
        text = mutate_text((REPO_ROOT / "data_dictionary" / "c2mapiv2-dd.ebnf").read_text(encoding="utf-8"))
        with tempfile.NamedTemporaryFile("w", suffix=".ebnf", delete=False, encoding="utf-8") as f:
            f.write(text)
        F = V.Findings()
        V.check_dd_to_spec(V.DDModel(f.name), self.specs(), HINTS, F)
        Path(f.name).unlink()
        return F

    def test_unreferenced_rule_is_an_error(self):
        F = self._dd_findings(lambda t: t + "\norphanRule = string ;\n")
        self.assertIn("orphanRule", F.items.get(("A-UNREACHABLE-RULE", "*"), []))
        errors, _w, _s = F.classified()
        self.assertIn(("A-UNREACHABLE-RULE", "*"), errors)

    def test_discriminator_tag_rule_counts_as_reachable(self):
        """paymentType is used through @structural discriminated_oneof, not a rule reference."""
        self.assertNotIn("paymentType", run_dd(self.specs()).items.get(("A-UNREACHABLE-RULE", "*"), []))

    def test_reserved_rules_are_not_unreachable_and_primer_endpoint_is_planned(self):
        F = run_dd(self.specs())
        unreachable = F.items.get(("A-UNREACHABLE-RULE", "*"), [])
        self.assertNotIn("multiDocJobs", unreachable)
        self.assertNotIn("multiDocJobItem", unreachable)
        self.assertNotIn(("A-PRIMER-ENDPOINT-UNDEFINED", "*"), F.items)

    def test_reserved_rule_in_use_is_flagged(self):
        """A rule marked @reserved but reachable from an endpoint must lose the annotation."""
        F = self._dd_findings(lambda t: t.replace(
            "jobTemplate = string ; (* @hint static standard_letter *)",
            "jobTemplate = string ; (* @reserved POST /static/multi *)"))
        self.assertIn(("A-RESERVED-RULE-IN-USE", "*"), F.items)

    def test_reserved_for_a_defined_endpoint_is_flagged(self):
        F = self._dd_findings(lambda t: t.replace("(* @reserved POST /static/multi *)", "(* @reserved POST /static *)"))
        self.assertIn(("A-RESERVED-ENDPOINT-DEFINED", "*"), F.items)

    def test_unknown_hint_type_is_flagged(self):
        F = self._dd_findings(lambda t: t.replace('(* @hint static "INV-2026-0001" *)', "(* @hint bogus 1 *)"))
        self.assertIn(("A-HINT-INVALID-TYPE", "*"), F.items)

    def test_aba_routing_number_is_a_valid_hint_type(self):
        self.assertNotIn(("A-HINT-INVALID-TYPE", "*"), run_dd(self.specs()).items)

    # C1 — request-body examples in the spec
    def _request_findings(self, mutate=None):
        spec = copy.deepcopy(SPECX)
        content = spec["paths"]["/static"]["post"]["requestBody"]["content"]["application/json"]
        if mutate:
            mutate(content)
        F = V.Findings()
        V.check_spec_examples(spec, DD, F, HINTS)
        return F

    @staticmethod
    def _value(content):
        return content["examples"]["default"]["value"]

    def test_real_request_examples_are_clean(self):
        cats = {c for c, _s in self._request_findings().items if c.startswith("C-REQUEST")}
        self.assertEqual(cats, set())  # D4 closed the last one (one-document merge)

    def test_missing_request_example_is_an_error(self):
        F = self._request_findings(lambda c: c.pop("examples"))
        self.assertIn(("C-REQUEST-EXAMPLE-MISSING", "*"), F.items)
        errors, _w, _s = F.classified()
        self.assertIn(("C-REQUEST-EXAMPLE-MISSING", "*"), errors)

    def test_request_example_schema_violation(self):
        F = self._request_findings(lambda c: self._value(c)["jobOptions"].update(mailClass="bogus"))
        self.assertIn(("C-REQUEST-EXAMPLE-INVALID", "*"), F.items)

    def test_request_example_mutual_exclusion(self):
        F = self._request_findings(lambda c: self._value(c).update(jobTemplate="standard_letter"))
        self.assertIn(("C-REQUEST-EXAMPLE-MUTUAL-EXCLUSION", "*"), F.items)

    def test_request_example_valid_combination(self):
        F = self._request_findings(
            lambda c: self._value(c)["jobOptions"].update(color="black_and_white", paperType="glossy"))
        self.assertIn(("C-REQUEST-EXAMPLE-VALID-COMBINATION", "*"), F.items)

    def test_request_example_value_contradicting_hint(self):
        F = self._request_findings(
            lambda c: self._value(c)["recipientAddressSource"]["recipientAddressByList"].update(mappingId=1))
        self.assertIn(("C-REQUEST-EXAMPLE-HINT-MISMATCH", "*"), F.items)

    def test_request_example_filler_value(self):
        F = self._request_findings(lambda c: self._value(c).update(tags=["example_tags"]))
        self.assertIn(("C-REQUEST-EXAMPLE-FILLER", "*"), F.items)

    # X4 — every DD @doc reaches the spec (component schema + inline properties)
    def _doc_problems(self, mutate):
        specs = self.specs()
        mutate(specs["final"]["components"]["schemas"])
        return [m for m in run_dd(specs).items.get(("A-DOC-NOT-IN-SPEC", "*"), [])]

    def test_doc_missing_on_component_is_flagged(self):
        problems = self._doc_problems(lambda s: s["mailClass"].pop("description"))
        self.assertTrue(any(p.startswith("mailClass: component") for p in problems), problems)

    def test_doc_text_drift_on_component_is_flagged(self):
        problems = self._doc_problems(lambda s: s["jobOptions"].update(description="stale text"))
        self.assertTrue(any(p.startswith("jobOptions: component") for p in problems), problems)

    def test_doc_missing_on_inline_property_is_flagged(self):
        problems = self._doc_problems(lambda s: s["returnAddress"]["properties"]["firstName"].pop("description"))
        self.assertIn("returnAddress.firstName", " ".join(problems))

    def test_doc_missing_on_tag_property_is_flagged(self):
        problems = self._doc_problems(lambda s: s["achPayment"]["properties"]["paymentType"].pop("description"))
        self.assertIn("achPayment.paymentType", " ".join(problems))

    def test_array_alias_target_without_description_is_flagged(self):
        problems = self._doc_problems(lambda s: s["tagsList"].pop("description"))
        self.assertTrue(any(p.startswith("tags: alias") for p in problems), problems)

    def test_non_dd_schema_fields_are_not_checked(self):
        """The auth overlay's AuthError.message is not the DD `message` rule."""
        problems = V.doc_description_problems(
            {"message": "DD text"},
            {"message": {"description": "DD text", "type": "string"},
             "AuthError": {"type": "object", "properties": {"message": {"type": "string"}}}},
            {"message"})
        self.assertEqual(problems, [])

    def test_known_open_entries_reference_a_tracking_id(self):
        for key, ref in V.KNOWN_OPEN.items():
            self.assertRegex(ref, r"(\b[XLDC]\d+[a-z]?\b|/static/multi)", f"{key} has no tracking reference")


if __name__ == "__main__":
    unittest.main()
