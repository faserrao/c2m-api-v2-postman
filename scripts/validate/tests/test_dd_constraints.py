#!/usr/bin/env python3
"""
test_dd_constraints.py

Tests for DD constraint infrastructure: enum propagation, numeric constraint
parsing, valid_combinations parsing, and provider mapping coverage.

Run via:
    python -m pytest scripts/validate/tests/test_dd_constraints.py -v
or:
    make validate-collections-conformance-test
"""

import os
import sys
import unittest
import yaml
from pathlib import Path

# Locate repo root relative to this file
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "build-spec"))

from ebnf_to_openapi_dynamic_v3 import EBNFToOpenAPITranslator

EBNF_PATH = REPO_ROOT / "data_dictionary" / "c2mapiv2-dd.ebnf"
PROVIDER_MAPPINGS_PATH = REPO_ROOT / "config" / "c2m_provider_mappings.yaml"
PROVIDER_ALIASES_PATH  = REPO_ROOT / "config" / "c2m_provider_aliases.yaml"

# ─── helpers ────────────────────────────────────────────────────────────────

def _translator() -> EBNFToOpenAPITranslator:
    t = EBNFToOpenAPITranslator()
    t.parse_ebnf(EBNF_PATH.read_text(encoding="utf-8"))
    return t

def _spec(translator: EBNFToOpenAPITranslator | None = None) -> dict:
    t = translator or _translator()
    return t.generate_openapi()

# ─── test class ─────────────────────────────────────────────────────────────

class TestDDConstraints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.translator = _translator()
        cls.spec = _spec(cls.translator)
        cls.schemas = cls.spec.get("components", {}).get("schemas", {})

    # ── 1. EBNF file loads without parse errors or warnings ──────────────────

    def test_ebnf_parses_without_errors(self):
        errors = [i for i in self.translator.issues if i.severity == "error"]
        self.assertEqual(errors, [], f"EBNF parse errors: {errors}")

    def test_ebnf_has_no_unexpected_warnings(self):
        warnings = [i for i in self.translator.issues if i.severity == "warning"]
        self.assertEqual(warnings, [],
                         f"Unexpected EBNF parse warnings: {warnings}\n"
                         "If any of these are intentional, enumerate them here "
                         "with an explanation rather than silently ignoring them.")

    # ── 2. Enum propagation — jobOptions fields ──────────────────────────────

    def test_mailClass_is_enum(self):
        schema = self.schemas.get("mailClass", {})
        self.assertIn("enum", schema, "mailClass must have an enum")
        self.assertIn("first_class", schema["enum"])
        self.assertIn("standard", schema["enum"])
        self.assertIn("non_profit", schema["enum"])

    def test_color_is_enum(self):
        schema = self.schemas.get("color", {})
        self.assertIn("enum", schema, "color must have an enum")
        self.assertIn("full_color", schema["enum"])
        self.assertIn("black_and_white", schema["enum"])

    def test_paperType_is_enum(self):
        schema = self.schemas.get("paperType", {})
        self.assertIn("enum", schema, "paperType must have an enum")
        expected = {"white", "white_24", "ivory", "glossy"}
        actual = set(schema["enum"])
        self.assertTrue(expected.issubset(actual), f"Missing: {expected - actual}")

    def test_printOption_is_enum(self):
        schema = self.schemas.get("printOption", {})
        self.assertIn("enum", schema)
        self.assertIn("double_sided", schema["enum"])
        self.assertIn("single_sided", schema["enum"])

    def test_productionTime_is_enum(self):
        schema = self.schemas.get("productionTime", {})
        self.assertIn("enum", schema)
        self.assertIn("next_day", schema["enum"])
        self.assertIn("standard", schema["enum"])

    def test_envelope_is_enum(self):
        schema = self.schemas.get("envelope", {})
        self.assertIn("enum", schema)
        self.assertIn("standard", schema["enum"])
        self.assertIn("none", schema["enum"])

    def test_documentClass_is_enum(self):
        schema = self.schemas.get("documentClass", {})
        self.assertIn("enum", schema)
        self.assertIn("letter", schema["enum"])
        self.assertIn("postcard", schema["enum"])

    def test_layout_is_enum(self):
        schema = self.schemas.get("layout", {})
        self.assertIn("enum", schema)
        self.assertIn("address_on_first_page", schema["enum"])
        self.assertNotIn("address_on_top", schema["enum"],
                         "address_on_top is a legacy alias, not a canonical value")

    # ── 3. Enum type is string for all jobOptions enums ──────────────────────

    def test_enum_schemas_are_string_type(self):
        for field in ("mailClass", "color", "paperType", "printOption",
                      "productionTime", "envelope", "documentClass", "layout"):
            with self.subTest(field=field):
                schema = self.schemas.get(field, {})
                self.assertEqual(schema.get("type"), "string",
                                 f"{field} schema should have type: string")

    # ── 4. Numeric constraints parsing ───────────────────────────────────────

    def test_numeric_constraints_parsed(self):
        nc = self.translator.numeric_constraints
        self.assertIsInstance(nc, dict)
        self.assertIn("month", nc, "month must be in @numeric_constraints")
        self.assertIn("startPage", nc, "startPage must be in @numeric_constraints")
        self.assertIn("endPage", nc, "endPage must be in @numeric_constraints")

    def test_startPage_constraints(self):
        nc = self.translator.numeric_constraints
        sp = nc.get("startPage", {})
        self.assertEqual(sp.get("minimum"), 1,
                         "startPage minimum must be 1 (pages are 1-indexed)")

    def test_endPage_constraints(self):
        nc = self.translator.numeric_constraints
        ep = nc.get("endPage", {})
        self.assertEqual(ep.get("minimum"), 1,
                         "endPage minimum must be 1 (pages are 1-indexed)")

    def test_month_constraints(self):
        nc = self.translator.numeric_constraints
        month = nc.get("month", {})
        self.assertEqual(month.get("minimum"), 1)
        self.assertEqual(month.get("maximum"), 12)

    def test_year_constraints(self):
        nc = self.translator.numeric_constraints
        year = nc.get("year", {})
        self.assertEqual(year.get("minimum"), 2000)
        self.assertEqual(year.get("maximum"), 2099)

    def test_numeric_constraints_name_dd_rules(self):
        orphans = set(self.translator.numeric_constraints) - set(self.translator.productions)
        self.assertEqual(orphans, set(),
                         f"@numeric_constraints names fields not defined in the DD: {orphans}")

    def test_numeric_constraints_reach_request_properties(self):
        """Every property schema named after a constrained field must carry the bounds.
        The standalone component schema alone is not enough: request bodies are
        validated against the inline property schemas (H1, 2026-10-05)."""
        nc = self.translator.numeric_constraints
        seen = {name: 0 for name in nc}
        missing = []

        def walk(node, path):
            if isinstance(node, dict):
                for key, prop in (node.get("properties") or {}).items():
                    if key in nc and isinstance(prop, dict) and "$ref" not in prop:
                        seen[key] += 1
                        for kw, val in nc[key].items():
                            if prop.get(kw) != val:
                                missing.append(f"{path}.properties.{key}: {kw}={prop.get(kw)!r}, expected {val!r}")
                for k, v in node.items():
                    walk(v, f"{path}.{k}")
            elif isinstance(node, list):
                for v in node:
                    walk(v, path)

        walk(self.spec.get("components", {}).get("schemas", {}), "schemas")
        walk(self.spec.get("paths", {}), "paths")
        self.assertEqual(missing, [], "Numeric constraints missing on request properties:\n" + "\n".join(missing))
        unused = [name for name, n in seen.items() if n == 0]
        self.assertEqual(unused, [], f"Constrained fields never used as a request property: {unused}")

    def test_month_schema_has_constraints(self):
        schema = self.schemas.get("month", {})
        self.assertEqual(schema.get("minimum"), 1)
        self.assertEqual(schema.get("maximum"), 12)

    # ── 4b. Array constraints (D4, 2026-10-14) ───────────────────────────────

    D4_MINIMUMS = {"addressList": 1, "pdfSplitJobsWithAddress": 1, "pdfSplitJobsNoAddress": 1,
                   "multiZipJobs": 1, "documentsToMerge": 2}

    def test_array_constraints_parsed(self):
        self.assertEqual({n: c.get("minItems") for n, c in self.translator.array_constraints.items()},
                         self.D4_MINIMUMS)

    def test_array_constraints_reach_list_schemas(self):
        """Each list in the block carries minItems on its component schema; a list not in
        the block (tagsList) may be empty."""
        for name, minimum in self.D4_MINIMUMS.items():
            with self.subTest(name=name):
                self.assertEqual(self.schemas[name].get("type"), "array")
                self.assertEqual(self.schemas[name].get("minItems"), minimum)
        self.assertNotIn("minItems", self.schemas["tagsList"])

    def test_merge_request_example_has_two_documents(self):
        content = self.spec["paths"]["/mail-merge"]["post"]["requestBody"]["content"]["application/json"]
        value = content["examples"]["default"]["value"]
        self.assertEqual(len(value["mergeDocumentSource"]), 2)

    def test_array_constraints_must_name_a_list_rule(self):
        text = EBNF_PATH.read_text(encoding="utf-8")
        for bad in ("startPage", "noSuchRule"):
            with self.subTest(bad=bad):
                t = EBNFToOpenAPITranslator()
                with self.assertRaisesRegex(RuntimeError, "not lists"):
                    t.parse_ebnf(text.replace("documentsToMerge: minItems=2", f"{bad}: minItems=2"))

    def test_unreadable_array_constraint_line_stops_the_build(self):
        text = EBNF_PATH.read_text(encoding="utf-8")
        t = EBNFToOpenAPITranslator()
        with self.assertRaisesRegex(RuntimeError, "cannot read line"):
            t.parse_ebnf(text.replace("documentsToMerge: minItems=2", "documentsToMerge: min=2"))

    # ── 5. x-numeric-constraints emitted in spec info ────────────────────────

    def test_spec_info_has_numeric_constraints(self):
        info = self.spec.get("info", {})
        self.assertIn("x-numeric-constraints", info,
                      "x-numeric-constraints must be present in spec info")

    # ── 6. Valid combinations parsing ────────────────────────────────────────

    def test_valid_combinations_parsed(self):
        vc = self.translator.valid_combinations
        self.assertIsInstance(vc, list)
        self.assertGreater(len(vc), 0, "@valid_combinations block must not be empty")

    def test_valid_combinations_structure(self):
        for rule in self.translator.valid_combinations:
            with self.subTest(rule=rule):
                self.assertIn("when_field", rule)
                self.assertIn("when_value", rule)
                self.assertIn("then_field", rule)
                self.assertIn("then_values", rule)
                self.assertIsInstance(rule["then_values"], list)
                self.assertGreater(len(rule["then_values"]), 0)

    def test_spec_info_has_valid_combinations(self):
        info = self.spec.get("info", {})
        self.assertIn("x-valid-combinations", info,
                      "x-valid-combinations must be present in spec info")

    D5_RULE = "envelope=none: documentClass must be one of (postcard|brochure|flat)"

    def test_envelope_none_rule(self):
        """D5 (2026-10-14): with no envelope the mailpiece mails itself, so no letter."""
        rule = {"when_field": "envelope", "when_value": "none",
                "then_field": "documentClass", "then_values": ["postcard", "brochure", "flat"]}
        self.assertIn(rule, self.translator.valid_combinations)
        self.assertIn(rule, self.spec["info"]["x-valid-combinations"])
        self.assertNotIn("layout", [r["then_field"] for r in self.translator.valid_combinations])

    def test_noop_combination_stops_the_build(self):
        """A rule that allows every value of its field restricts nothing (X11)."""
        text = EBNF_PATH.read_text(encoding="utf-8")
        for noop in ("envelope=none: layout must be one of (address_on_first_page|address_on_back_page)",
                     "envelope=none: documentClass must be one of (letter|postcard|brochure|flat)"):
            with self.subTest(noop=noop):
                with self.assertRaisesRegex(RuntimeError, "restricts nothing"):
                    EBNFToOpenAPITranslator().parse_ebnf(text.replace(self.D5_RULE, noop))

    def test_combination_naming_unknown_field_or_value_stops_the_build(self):
        text = EBNF_PATH.read_text(encoding="utf-8")
        for bad, msg in (("envelope=none: noSuchField must be one of (x)", "not a DD enum rule"),
                         ("envelope=nothing: documentClass must be one of (flat)", "not values of envelope"),
                         ("envelope=none: documentClass must be one of (flat|leaflet)", "not values of documentClass")):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(RuntimeError, msg):
                    EBNFToOpenAPITranslator().parse_ebnf(text.replace(self.D5_RULE, bad))

    def test_unreadable_combination_line_stops_the_build(self):
        text = EBNF_PATH.read_text(encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "cannot read line"):
            EBNFToOpenAPITranslator().parse_ebnf(
                text.replace(self.D5_RULE, "envelope=none: documentClass in (postcard|brochure|flat)"))

    # ── D6 (2026-10-16): field types ──────────────────────────────────────────

    def test_error_details_is_a_free_form_object(self):
        """D6: errorDetails is a JSON object (DD primitive `object`), in the schema and in every
        error example, with content unchanged from the DD's @error_examples."""
        free_form = {"type": "object", "additionalProperties": True}
        strip = lambda s: {k: v for k, v in s.items() if k != "description"}
        self.assertEqual(strip(self.schemas["errorDetails"]), free_form)
        self.assertEqual(strip(self.schemas["errorResponse"]["properties"]["errorDetails"]), free_form)
        seen = 0
        for path_item in self.spec["paths"].values():
            for op in path_item.values():
                for resp in op.get("responses", {}).values():
                    for ex in resp.get("content", {}).get("application/json", {}).get("examples", {}).values():
                        if "errorCode" in ex["value"]:
                            seen += 1
                            self.assertIsInstance(ex["value"]["errorDetails"], dict, ex["summary"])
        self.assertGreater(seen, 100)

    def test_error_example_details_must_be_an_object(self):
        """D6: @error_examples details that are valid JSON but not an object stop the build."""
        text = EBNF_PATH.read_text(encoding="utf-8")
        old = 'details: {"field": "{documentField}", "location": "requestBody"}'
        self.assertIn(old, text)
        t = EBNFToOpenAPITranslator()
        t.parse_ebnf(text.replace(old, 'details: ["{documentField}"]'))
        with self.assertRaisesRegex(RuntimeError, "must be a JSON object"):
            t.generate_openapi()

    def test_dd_object_primitive_follows_aliases(self):
        """D6: a rule aliasing the `object` primitive (directly or via another rule) is free-form."""
        text = EBNF_PATH.read_text(encoding="utf-8") + "\nextraContext = errorDetails ;\n"
        t = EBNFToOpenAPITranslator()
        t.parse_ebnf(text)
        self.assertTrue(t._is_free_form_object("errorDetails"))
        self.assertTrue(t._is_free_form_object("extraContext"))
        self.assertFalse(t._is_free_form_object("errorTrackingId"))
        self.assertEqual(t._get_field_type("extraContext")["additionalProperties"], True)

    def test_cvv_is_a_string_with_a_string_hint(self):
        """D6: cvv is a string so a leading zero is kept; its example value is the string "123"."""
        self.assertEqual(self.schemas["cvv"]["type"], "string")
        self.assertEqual(self.schemas["creditCardDetails"]["properties"]["cvv"]["type"], "string")
        self.assertEqual(self.translator.faker_hints["cvv"], {"type": "static", "value": "123"})
        hints = yaml.safe_load((REPO_ROOT / "config" / "faker_hints.yaml").read_text())["faker_hints"]
        self.assertEqual(hints["cvv"]["value"], "123")

    def test_ach_details_have_no_check_digit(self):
        """D6: the routing number's ninth digit is the check digit; no separate field. (The
        retired rule name is not written here: the migration's retired-name scan covers it.)"""
        ach = self.schemas["achDetails"]
        self.assertEqual(sorted(ach["properties"]), ["accountNumber", "routingNumber"])
        self.assertEqual(sorted(ach["required"]), ["accountNumber", "routingNumber"])

    # ── L4 / D8 (2026-10-16): recipient ID variants are wrapper objects ────────

    def test_recipient_id_variants_are_wrapper_objects(self):
        """L4: { "recipientAddressByListId": { "addressListId": 1001 } }, like documentIdSource."""
        import json as _json
        for rule, field in (("recipientAddressByListId", "addressListId"),
                            ("recipientAddressByAddressId", "addressId")):
            with self.subTest(rule=rule):
                schema = self.schemas[rule]
                self.assertEqual(schema.get("type"), "object")
                self.assertEqual(list(schema["properties"]), [field])
                self.assertEqual(schema["required"], [field])
        # Every generated collection sends the object form, with the DD hint value
        hints = yaml.safe_load((REPO_ROOT / "config" / "faker_hints.yaml").read_text())["faker_hints"]
        seen = 0
        for name in ("linked-collection-flat", "test-collection-flat", "getting-started-test-collection",
                     "real-world-use-cases-collection"):
            text = (REPO_ROOT / "postman" / "generated" / f"c2mapiv2-{name}.json").read_text()
            def walk(o):
                nonlocal seen
                if isinstance(o, dict):
                    for rule, field in (("recipientAddressByListId", "addressListId"),
                                        ("recipientAddressByAddressId", "addressId")):
                        if rule in o:
                            seen += 1
                            self.assertEqual(o[rule], {field: hints[field]["value"]}, f"{name}: {o[rule]!r}")
                    for v in o.values():
                        walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)
            for it in _json.loads(text)["item"]:
                stack = [it]
                while stack:
                    x = stack.pop()
                    stack += x.get("item", [])
                    raw = ((x.get("request") or {}).get("body") or {}).get("raw")
                    if raw:
                        walk(_json.loads(raw))
        self.assertGreater(seen, 0)

    def test_typed_collections_share_one_placeholder_style(self):
        """L9 (D8): type placeholders are lowercase everywhere (<string>, <integer>, ...),
        the style openapi-to-postmanv2 writes into Linked; Getting Started — With Types
        and the template used <String>, <Integer>."""
        import re as _re
        capitalised = _re.compile(r'"<(String|Integer|Number|Boolean)>"')
        for path in [REPO_ROOT / "config" / "getting-started-template.yaml",
                     *sorted((REPO_ROOT / "postman" / "generated").glob("c2mapiv2-*.json"))]:
            with self.subTest(path=path.name):
                text = path.read_text()
                if path.suffix == ".yaml":
                    text = _re.sub(r": (<\w+>)", r': "\1"', text)  # quote YAML scalars for one regex
                self.assertIsNone(capitalised.search(text), f"{path.name}: {capitalised.search(text)}")
        gs = (REPO_ROOT / "postman" / "generated" / "c2mapiv2-getting-started-linked-collection.json").read_text()
        self.assertIn('\\"<string>\\"', gs)  # the lowercase form is really there (bodies are JSON strings)

    def test_spec_gate_wrapper_list_comes_from_the_dd(self):
        """L4: validate_spec_against_dd.py checks every @structural single_field_wrapper rule
        (it had a hardcoded list of five), and fails one emitted as a bare type."""
        import copy as _copy
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "validate"))
        import validate_spec_against_dd as G
        from ebnf_to_openapi_dynamic_v3 import _extract_structural_annotations
        text = EBNF_PATH.read_text(encoding="utf-8")
        wrappers = frozenset(n for n, r in _extract_structural_annotations(text).items()
                             if "single_field_wrapper" in r)
        self.assertTrue({"recipientAddressByListId", "recipientAddressByAddressId"} <= wrappers)
        rules = G.extract_rules(text)
        schemas = _copy.deepcopy(self.schemas)
        self.assertEqual([f for f in G.check_wrapper_rules(rules, schemas, {}, wrappers) if f[0] == G.FAIL], [])
        schemas["recipientAddressByListId"] = {"type": "integer"}
        failed = [f[1] for f in G.check_wrapper_rules(rules, schemas, {}, wrappers) if f[0] == G.FAIL]
        self.assertEqual(failed, ["recipientAddressByListId"])

    # ── L11 / L13 (2026-10-16): DD prose matches the contract ─────────────────

    def test_dd_prose_names_only_real_endpoints(self):
        """L11: every endpoint path the DD's prose mentions is a spec path (or the planned
        /static/multi); old names like /single/pdf/split fail."""
        import re as _re
        text = EBNF_PATH.read_text(encoding="utf-8")
        paths = set(self.spec["paths"]) | {"/static/multi"}
        mentioned = set(_re.findall(r"(?<![\w.:/])(/(?:static|batch|mail-merge|single|multi|jobs|auth)(?:/[\w{}-]+)*)", text))
        self.assertEqual(sorted(m for m in mentioned if m not in paths), [])

    def test_dd_has_no_unresolved_markers(self):
        """L11: open questions live in PROJECT_TODO.md, not as markers in the DD."""
        import re as _re
        text = EBNF_PATH.read_text(encoding="utf-8")
        # "*** Name:" notes (not the "(*****)" banner lines), TO CHECK / TODO / FIXME, "??"
        self.assertEqual(_re.findall(r"\*\*\* [A-Za-z]|\bTO CHECK\b|\bTODO\b|\bFIXME\b|\?\?", text), [])

    def test_endpoint_descriptions_do_not_require_optional_fields(self):
        """L13: an endpoint @description must not call an optional body field required
        (/static said payment details were required)."""
        import re as _re
        bad = []
        for ep in self.translator.endpoints:
            body = self.schemas.get(ep.production_name, {})
            optional = set(body.get("properties", {})) - set(body.get("required", []))
            for clause in _re.split(r"[.;]", ep.description or ""):
                if not _re.search(r"\bmust\b|\brequired\b", clause, _re.I) or "optional" in clause.lower():
                    continue
                for field in optional:
                    words = _re.sub(r"(?<!^)([A-Z])", r" \1", field).lower()  # paymentDetails -> payment details
                    if words in clause.lower():
                        bad.append(f"{ep.path}: '{clause.strip()}' calls optional {field} required")
        self.assertEqual(bad, [])

    def test_collection_enforcer_applies_every_rule_on_a_field(self):
        """fix_oneOf_placeholders.js must satisfy all rules on one field together, after it
        normalises jobOptions: non_profit + no envelope leaves only flat (D5)."""
        import json, subprocess, tempfile
        spec = yaml.safe_load((REPO_ROOT / "openapi" / "c2mapiv2-openapi-spec-base.yaml").read_text(encoding="utf-8"))
        for name, first in (("envelope", "none"), ("mailClass", "non_profit")):
            for schema in (spec["components"]["schemas"][name],
                           spec["components"]["schemas"]["jobOptions"]["properties"][name]):
                schema["enum"].remove(first)
                schema["enum"].insert(0, first)
        jo = {f: "x" for f in spec["components"]["schemas"]["jobOptions"]["properties"]}
        body = json.dumps({"jobOptions": jo})
        coll = {"info": {"name": "t"}, "item": [{"name": "r", "request": {
            "method": "POST", "url": "{{baseUrl}}/static", "body": {"mode": "raw", "raw": body}}}]}
        with tempfile.TemporaryDirectory() as d:
            sp, cp = Path(d, "spec.yaml"), Path(d, "c.json")
            sp.write_text(yaml.safe_dump(spec), encoding="utf-8")
            cp.write_text(json.dumps(coll), encoding="utf-8")
            subprocess.run(["node", str(REPO_ROOT / "scripts/build-collections/fix_oneOf_placeholders.js"), str(sp), str(cp), str(cp)],
                           check=True, capture_output=True)
            out = json.loads(json.loads(cp.read_text())["item"][0]["request"]["body"]["raw"])["jobOptions"]
        self.assertEqual((out["envelope"], out["mailClass"], out["documentClass"]), ("none", "non_profit", "flat"))

    # ── 7. x-http-error-map still emitted (regression) ───────────────────────

    def test_spec_info_still_has_http_error_map(self):
        info = self.spec.get("info", {})
        self.assertIn("x-http-error-map", info)
        em = info["x-http-error-map"]
        self.assertIn("400", em)
        self.assertIn("500", em)

    def test_spec_generation_is_repeatable(self):
        """M4: two independent builds from the same DD produce an identical spec
        (no random tracking IDs or wall-clock timestamps in examples)."""
        import json as _json
        first = _json.dumps(_spec(), sort_keys=True, default=str)
        second = _json.dumps(_spec(), sort_keys=True, default=str)
        self.assertEqual(first, second, "Spec output differs between two builds of the same DD")

    def test_every_dd_error_status_declared_on_every_job_endpoint(self):
        """H4: job-endpoint responses are driven by @http_error_map (incl. 429)."""
        em = self.translator.http_error_map
        missing = []
        for ep in self.translator.endpoints:
            op = self.spec["paths"][ep.path][ep.method.lower()]
            for status in em:
                if status not in op.get("responses", {}):
                    missing.append(f"{ep.method} {ep.path}: {status}")
        self.assertEqual(missing, [], "DD error statuses not declared on job endpoints")

    def test_spec_error_examples_match_dd_map_per_status(self):
        """H3/D10: each status's examples carry the codes (and type) the DD maps to it.
        A code may be absent only where its @error_examples tokens cannot be filled for
        that endpoint — i.e. the error cannot occur there (e.g. mutual exclusion on a body
        without jobTemplate/jobOptions)."""
        t = self.translator
        bad = []
        for ep in t.endpoints:
            op = self.spec["paths"][ep.path][ep.method.lower()]
            field_names = t._extract_endpoint_field_names(ep)
            for status, entry in t.http_error_map.items():
                content = op["responses"][status]["content"]["application/json"]
                values = [ex["value"] for ex in content.get("examples", {}).values()]
                present = {v["errorCode"] for v in values}
                bad += [f"{ep.path} {status}: unmapped code {c}" for c in present - set(entry["errorCodes"])]
                for code in set(entry["errorCodes"]) - present:
                    tmpl = t._error_example_entry(status, code)["details"]
                    if t.render_error_details(tmpl, ep, field_names, "check") is not None:
                        bad.append(f"{ep.path} {status}: {code} omitted although it applies")
                bad += [f"{ep.path} {status}: errorType {v['errorType']}" for v in values
                        if v["errorType"] != entry["errorType"]]
        self.assertEqual(bad, [])

    def test_error_example_omitted_where_impossible(self):
        """D10/N5: an endpoint whose body lacks jobTemplate/jobOptions gets no
        MUTUAL_EXCLUSION_VIOLATION example. Since D3 every job endpoint has the pair, so the
        omission is checked on a DD with the pair removed from /batch/zip."""
        def codes(spec, path):
            ex = spec["paths"][path]["post"]["responses"]["422"]["content"]["application/json"]["examples"]
            return {e["value"]["errorCode"] for e in ex.values()}
        for path in ("/static", "/batch/zip"):
            self.assertIn("MUTUAL_EXCLUSION_VIOLATION", codes(self.spec, path))
        text = EBNF_PATH.read_text(encoding="utf-8")
        start = text.index("submitMultiZipParams =")
        rule = text[start:text.index(";", start) + 1]
        stripped = rule.replace("[ jobTemplate ]\n    + ", "").replace("    + [ jobOptions ]\n", "")
        self.assertNotIn("jobOptions", stripped)
        t = EBNFToOpenAPITranslator()
        t.parse_ebnf(text.replace(rule, stripped))
        spec = t.generate_openapi()
        self.assertNotIn("MUTUAL_EXCLUSION_VIOLATION", codes(spec, "/batch/zip"))
        self.assertIn("MUTUAL_EXCLUSION_VIOLATION", codes(spec, "/static"))

    def test_job_endpoints_offer_the_same_request_level_options(self):
        """D3 (user decision 2026-10-13): every job endpoint accepts optional request-level
        jobTemplate, returnAddress, jobOptions, paymentDetails and tags (/batch/zip lacked the
        first three)."""
        missing = []
        for ep in self.translator.endpoints:
            schema = self.schemas[ep.production_name]
            for f in ("jobTemplate", "returnAddress", "jobOptions", "paymentDetails", "tags"):
                if f not in schema.get("properties", {}) or f in schema.get("required", []):
                    missing.append(f"{ep.path}: {f}")
        self.assertEqual(missing, [])

    def test_job_item_template_precedence_is_defined_once_and_referenced(self):
        """D3: the precedence rule (an item's jobTemplate replaces the request-level settings
        for that item) is defined once in the DD and referenced by every endpoint whose job
        items carry jobTemplate."""
        text = EBNF_PATH.read_text(encoding="utf-8")
        self.assertEqual(text.count("Job-item jobTemplate precedence (D3"), 1)
        for path in ("/batch/split", "/batch/split/address-capture", "/batch/zip"):
            start = text.index(f"(* Endpoint: POST {path} ")
            section = text[start:text.index("(* Endpoint:", start + 10) if "(* Endpoint:" in text[start + 10:] else None]
            self.assertIn("Job-item jobTemplate precedence:", section, path)

    def test_error_examples_block_must_cover_error_map(self):
        """D10: a mapped (status, code) without an @error_examples entry is a build error."""
        text = EBNF_PATH.read_text(encoding="utf-8")
        start = text.index("   DATABASE_ERROR\n")
        end = text.index("   EXTERNAL_SERVICE_ERROR\n")
        t = EBNFToOpenAPITranslator()
        with self.assertRaises(RuntimeError):
            t.parse_ebnf(text[:start] + text[end:])

    def test_error_examples_unknown_token_is_build_error(self):
        t = self.translator
        ep = t.endpoints[0]
        with self.assertRaises(RuntimeError):
            t.render_error_details('{"field": "{notAToken}"}', ep, t._extract_endpoint_field_names(ep), "x")

    def test_mutual_exclusion_fields_are_dd_rules(self):
        """The mutual-exclusion group must be real DD rules (guards against the parser
        reading prose that mentions the annotation, as happened once on 2026-10-08)."""
        group = self.translator.mutual_exclusion_fields
        self.assertGreaterEqual(len(group), 2)
        self.assertEqual([f for f in group if f not in self.translator.productions], [])

    def test_success_example_comes_from_dd_hints(self):
        """D10: the 200 example is built from standardResponse's @hint values."""
        hints = self.translator.faker_hints
        for ep in self.translator.endpoints:
            v = self.spec["paths"][ep.path][ep.method.lower()]["responses"]["200"]["content"][
                "application/json"]["examples"]["success"]["value"]
            self.assertEqual(v["status"], hints["status"]["value"])
            self.assertEqual(v["message"], hints["message"]["value"])
            self.assertTrue(hints["requestId"]["min"] <= v["requestId"] <= hints["requestId"]["max"])

    # ── C1: request-body examples ─────────────────────────────────────────────

    def _request_example(self, ep):
        return self.spec["paths"][ep.path][ep.method.lower()]["requestBody"]["content"][
            "application/json"]["examples"]["default"]["value"]

    def test_every_job_endpoint_has_a_valid_request_example(self):
        """C1: each job endpoint's request example exists and validates against its schema."""
        from jsonschema import Draft7Validator
        from jsonschema.validators import RefResolver
        resolver = RefResolver(base_uri="", referrer=self.spec)
        for ep in self.translator.endpoints:
            schema = self.spec["paths"][ep.path][ep.method.lower()]["requestBody"]["content"][
                "application/json"]["schema"]
            errors = [e.message for e in Draft7Validator(schema, resolver=resolver).iter_errors(self._request_example(ep))]
            self.assertEqual(errors, [], f"{ep.method} {ep.path}")

    def test_request_example_values_come_from_dd_hints(self):
        """C1: static @hint values are used as-is; top-level mutual exclusion keeps one field."""
        hints = self.translator.faker_hints
        for ep in self.translator.endpoints:
            v = self._request_example(ep)
            present = [f for f in self.translator.mutual_exclusion_fields if f in v]
            self.assertLessEqual(len(present), 1, f"{ep.path}: {present}")
            if "jobOptions" in v:
                self.assertEqual(v["jobOptions"]["mailClass"], hints["mailClass"]["value"])
            if "tags" in v:
                self.assertEqual(v["tags"], [hints["tags"]["value"]])

    def test_request_example_leaf_without_hint_or_enum_is_build_error(self):
        """C1: a request field with no @hint and no enum stops the build (no filler values)."""
        text = EBNF_PATH.read_text(encoding="utf-8").replace(
            'tags = tagsList ; (* @hint static "q1-campaign" *)', 'tags = tagsList ;')
        t = EBNFToOpenAPITranslator()
        t.parse_ebnf(text)
        with self.assertRaisesRegex(RuntimeError, "tags"):
            t.generate_openapi()

    # ── L1 / L7: hints ─────────────────────────────────────────────────────────

    def test_every_dd_hint_reaches_faker_hints(self):
        """L1: every @hint in the DD has a supported type and an entry in faker_hints
        (an unsupported type used to be dropped silently)."""
        import re
        from ebnf_to_openapi_dynamic_v3 import HINT_TYPES, extract_faker_hints
        text = EBNF_PATH.read_text(encoding="utf-8")
        dd = dict(re.findall(r"^([a-zA-Z_]\w*)\s*=[^;\n]*;[^(\n]*\(\*\s*@hint\s+(\w+)", text, re.M))
        self.assertEqual({n: k for n, k in dd.items() if k not in HINT_TYPES}, {})
        self.assertEqual(sorted(set(dd) - set(extract_faker_hints(text))), [])

    def test_no_empty_static_hint(self):
        """L1: a static hint gives a value; an intentionally empty one is written as \"\"."""
        import re
        text = EBNF_PATH.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^(\w+)\s*=[^;\n]*;\s*\(\*\s*@hint\s+static\s*\*\)", text, re.M), [])

    def test_curated_catalog_country_matches_dd_hint(self):
        """L7: Real-World used country "US" while the DD documents and hints "USA"."""
        catalog = yaml.safe_load((REPO_ROOT / "config" / "curated-examples-catalog.yaml").read_text())
        expected = self.translator.faker_hints["country"]["value"]
        found = []

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "country" and not isinstance(v, (dict, list)):
                        found.append(v)
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(catalog)
        self.assertTrue(found)
        self.assertEqual(sorted({v for v in found if v != expected}), [])

    def test_error_example_fields_exist_in_endpoint_body(self):
        """N5: every field an error example names must be a real path in that endpoint's
        request body (arrays as [0]), and INVALID_ENUM_VALUE's allowedValues must be that
        field's own enum. Since D10 an example whose fields do not exist on an endpoint is
        omitted there, so this covers MUTUAL_EXCLUSION_VIOLATION too."""
        import json as _json
        schemas = self.spec["components"]["schemas"]

        def resolve(s):
            while isinstance(s, dict) and "$ref" in s:
                s = schemas[s["$ref"].split("/")[-1]]
            return s

        def paths(s, prefix, acc, depth=0):
            s = resolve(s)
            if depth > 10 or not isinstance(s, dict):
                return acc
            for b in s.get("oneOf", []):
                paths(b, prefix, acc, depth + 1)
            for k, v in (s.get("properties") or {}).items():
                p = f"{prefix}.{k}" if prefix else k
                acc[p] = resolve(v)
                paths(v, p, acc, depth + 1)
            if "items" in s:
                paths(s["items"], f"{prefix}[0]", acc, depth + 1)
            return acc

        bad = []
        for ep in self.translator.endpoints:
            op = self.spec["paths"][ep.path][ep.method.lower()]
            body = paths(op["requestBody"]["content"]["application/json"]["schema"], "", {})
            for status, resp in op["responses"].items():
                for ex in resp.get("content", {}).get("application/json", {}).get("examples", {}).values():
                    v = ex["value"]
                    if v.get("errorCode") is None:
                        continue
                    d = v.get("errorDetails") or {}  # D6: an object
                    refs = [d.get("field")] + list(d.get("fields") or []) + [e.get("field") for e in d.get("errors", [])]
                    for f in filter(None, refs):
                        if f not in body:
                            bad.append(f"{ep.path} {status} {v['errorCode']}: {f}")
                    if v["errorCode"] == "INVALID_ENUM_VALUE" and d.get("field") in body:
                        leaf = d["field"].split(".")[-1].split("[")[0]
                        expected = self.translator._get_enum_values(leaf) or body[d["field"]].get("enum")
                        if d.get("allowedValues") != expected:
                            bad.append(f"{ep.path} {status}: allowedValues are not {d['field']}'s enum")
        self.assertEqual(bad, [], "Error examples name fields that are not in the endpoint body")

    def test_payment_variants_require_their_payment_type(self):
        """D1: each payment variant requires paymentType fixed to its own DD literal, and
        paymentDetails carries an OpenAPI discriminator mapping those values."""
        schemas = self.schemas
        disc = schemas["paymentDetails"].get("discriminator", {})
        self.assertEqual(disc.get("propertyName"), "paymentType")
        allowed = self.translator._get_enum_values("paymentType")
        self.assertEqual(sorted(disc.get("mapping", {})), sorted(allowed))
        for value, ref in disc["mapping"].items():
            variant = schemas[ref.split("/")[-1]]
            tag = {k: v for k, v in variant["properties"]["paymentType"].items() if k != "description"}  # X4
            self.assertEqual(tag, {"type": "string", "enum": [value]})
            self.assertEqual(variant["required"][0], "paymentType")

    def test_payment_branch_tag_must_be_a_payment_type(self):
        """D1: a branch whose leading literal is not a paymentType value is a build error."""
        text = EBNF_PATH.read_text(encoding="utf-8").replace('"ach"\n    + achDetails', '"bankTransfer"\n    + achDetails')
        self.assertIn('"bankTransfer"', text)
        with self.assertRaises(RuntimeError):
            EBNFToOpenAPITranslator().parse_ebnf(text)

    def test_error_example_scopes_are_issued_by_auth_system(self):
        """H5: 403 example scopes must be scopes the auth system actually issues."""
        import json as _json
        import re as _re
        overlay = yaml.safe_load((REPO_ROOT / "openapi" / "overlays" / "auth.tokens.yaml").read_text())
        issued = set()

        def collect(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "scopes":
                        issued.update(v if isinstance(v, list) else (v or {}).keys())
                    collect(v)
            elif isinstance(node, list):
                for v in node:
                    collect(v)
        collect(overlay)
        self.assertTrue(issued, "no scopes found in the auth overlay")

        used = {}
        for (_status, code), entry in self.translator.error_examples.items():
            if code == "INSUFFICIENT_PERMISSIONS":
                for k, v in _json.loads(entry["details"]).items():
                    if k in ("required", "provided"):
                        used[f"DD @error_examples {code}.{k}"] = v
        self.assertTrue(used, "INSUFFICIENT_PERMISSIONS example has no required/provided scopes")
        js = (REPO_ROOT / "scripts" / "build-collections" / "addRandomDataToRaw.js").read_text()
        for k, v in _re.findall(r"\b(required|provided):\s*\"([a-z]+:[a-z]+)\"", js):
            used[f"addRandomDataToRaw.js {k}"] = v
        bad = {where: scope for where, scope in used.items() if scope not in issued}
        self.assertEqual(bad, {}, f"Scopes not issued by the auth system {sorted(issued)}")

    # ── 8. Provider mappings (generated) + aliases (manually maintained) ─────────
    # c2m_provider_mappings.yaml is a DO NOT EDIT derived artifact: canonical enum
    # values come from the EBNF DD; _aliases are merged from c2m_provider_aliases.yaml.
    # Edit c2m_provider_aliases.yaml and re-run make openapi-build to update mappings.

    @classmethod
    def _load_provider_mappings(cls):
        with open(PROVIDER_MAPPINGS_PATH) as f:
            return yaml.safe_load(f)

    @classmethod
    def _load_provider_aliases(cls):
        with open(PROVIDER_ALIASES_PATH) as f:
            return yaml.safe_load(f) or {}

    def test_provider_mappings_file_exists(self):
        self.assertTrue(PROVIDER_MAPPINGS_PATH.exists(),
                        f"Missing generated file: {PROVIDER_MAPPINGS_PATH} — run make openapi-build")

    def test_provider_aliases_file_exists(self):
        self.assertTrue(PROVIDER_ALIASES_PATH.exists(),
                        f"Missing manually-maintained aliases file: {PROVIDER_ALIASES_PATH}")

    def test_provider_mappings_is_generated(self):
        """Generated file must carry the DO NOT EDIT header."""
        header = PROVIDER_MAPPINGS_PATH.read_text(encoding="utf-8")[:200]
        self.assertIn("DO NOT EDIT", header,
                      "c2m_provider_mappings.yaml must carry DO NOT EDIT header — "
                      "run make openapi-build to regenerate")

    @classmethod
    def _joboptions_enum_fields(cls):
        """Dynamically derive the jobOptions fields that carry enums from the spec.

        Matches the runtime logic of _derive_joboptions_enum_fields() in
        validate_configs_against_dd.py — both read jobOptions.properties from
        the generated spec so the test list never drifts from the actual DD.
        """
        job_props = cls.schemas.get('jobOptions', {}).get('properties', {})
        return [f for f, s in job_props.items() if s.get('enum')]

    def test_provider_mappings_covers_all_enum_fields(self):
        mappings = self._load_provider_mappings()
        for field in self._joboptions_enum_fields():
            with self.subTest(field=field):
                self.assertIn(field, mappings,
                              f"Provider mappings must cover field: {field}")

    def test_provider_mappings_canonical_values_match_ebnf(self):
        """Every canonical key in the generated mappings must equal an EBNF enum value."""
        mappings = self._load_provider_mappings()
        for field in self._joboptions_enum_fields():
            schema = self.schemas.get(field, {})
            ebnf_enum = set(schema.get("enum", []))
            if not ebnf_enum:
                continue
            mapping_keys = {k for k in mappings.get(field, {}).keys()
                            if not k.startswith("_")}
            with self.subTest(field=field):
                missing = ebnf_enum - mapping_keys
                self.assertEqual(missing, set(),
                                 f"{field}: EBNF enum values missing from generated mappings: {missing}")
                extra = mapping_keys - ebnf_enum
                self.assertEqual(extra, set(),
                                 f"{field}: generated mappings contain non-EBNF values: {extra} "
                                 f"— these should only appear as _aliases in c2m_provider_aliases.yaml")

    def test_provider_aliases_values_are_canonical(self):
        """Every alias target in the aliases file must be a valid EBNF enum value."""
        aliases_file = self._load_provider_aliases()
        for field, block in aliases_file.items():
            if not isinstance(block, dict):
                continue
            alias_map = block.get("_aliases", {})
            schema = self.schemas.get(field, {})
            ebnf_enum = set(schema.get("enum", []))
            if not ebnf_enum:
                continue
            for alias_str, target in alias_map.items():
                with self.subTest(field=field, alias=alias_str):
                    self.assertIn(target, ebnf_enum,
                                  f"{field}: alias '{alias_str}' → '{target}' is not a valid "
                                  f"EBNF canonical value. Valid: {sorted(ebnf_enum)}")

    def test_layout_alias_maps_to_canonical(self):
        mappings = self._load_provider_mappings()
        layout = mappings.get("layout", {})
        aliases = layout.get("_aliases", {})
        self.assertEqual(aliases.get("address_on_top"), "address_on_first_page",
                         "Legacy address_on_top must alias to address_on_first_page")

    # ── 9. No address_on_top in getting-started-template or derived hints ───────
    # faker_hints moved from getting-started-template.yaml to EBNF @hint annotations
    # (derived into config/faker_hints.yaml). Check both sources.

    def test_getting_started_template_uses_canonical_layout(self):
        template_path = REPO_ROOT / "config" / "getting-started-template.yaml"
        template_content = template_path.read_text(encoding="utf-8")
        self.assertNotIn("address_on_top", template_content,
                         "getting-started-template.yaml must not use legacy address_on_top")

        # faker_hints now live in the DD (@hint annotations) and derived config/faker_hints.yaml
        dd_path = REPO_ROOT / "data_dictionary" / "c2mapiv2-dd.ebnf"
        dd_content = dd_path.read_text(encoding="utf-8")
        self.assertIn("address_on_first_page", dd_content,
                      "EBNF DD must define address_on_first_page (used as @hint for layout rule)")
        self.assertNotIn("address_on_top", dd_content,
                         "EBNF DD must not reference legacy address_on_top")


if __name__ == "__main__":
    unittest.main()
