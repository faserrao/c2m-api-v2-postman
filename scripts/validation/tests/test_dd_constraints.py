#!/usr/bin/env python3
"""
test_dd_constraints.py

Tests for DD constraint infrastructure: enum propagation, numeric constraint
parsing, valid_combinations parsing, and provider mapping coverage.

Run via:
    python -m pytest scripts/validation/tests/test_dd_constraints.py -v
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
sys.path.insert(0, str(REPO_ROOT / "scripts" / "active"))

from ebnf_to_openapi_dynamic_v3 import EBNFToOpenAPITranslator

EBNF_PATH = REPO_ROOT / "data_dictionary" / "c2mapiv2-dd.ebnf"
PROVIDER_MAPPINGS_PATH = REPO_ROOT / "config" / "c2m_provider_mappings.yaml"

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

    # ── 1. EBNF file loads without parse errors ──────────────────────────────

    def test_ebnf_parses_without_errors(self):
        errors = [i for i in self.translator.issues if i.severity == "error"]
        self.assertEqual(errors, [], f"EBNF parse errors: {errors}")

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

    def test_quantity_minimum(self):
        nc = self.translator.numeric_constraints
        qty = nc.get("quantity", {})
        self.assertEqual(qty.get("minimum"), 1)

    def test_month_schema_has_constraints(self):
        schema = self.schemas.get("month", {})
        self.assertEqual(schema.get("minimum"), 1)
        self.assertEqual(schema.get("maximum"), 12)

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

    # ── 7. x-http-error-map still emitted (regression) ───────────────────────

    def test_spec_info_still_has_http_error_map(self):
        info = self.spec.get("info", {})
        self.assertIn("x-http-error-map", info)
        em = info["x-http-error-map"]
        self.assertIn("400", em)
        self.assertIn("500", em)

    # ── 8. Provider mappings file ─────────────────────────────────────────────

    @classmethod
    def _load_provider_mappings(cls):
        with open(PROVIDER_MAPPINGS_PATH) as f:
            return yaml.safe_load(f)

    def test_provider_mappings_file_exists(self):
        self.assertTrue(PROVIDER_MAPPINGS_PATH.exists(),
                        f"Missing: {PROVIDER_MAPPINGS_PATH}")

    def test_provider_mappings_covers_all_enum_fields(self):
        mappings = self._load_provider_mappings()
        enum_fields = ("mailClass", "color", "paperType", "printOption",
                       "productionTime", "envelope", "documentClass", "layout")
        for field in enum_fields:
            with self.subTest(field=field):
                self.assertIn(field, mappings,
                              f"Provider mappings must cover field: {field}")

    def test_provider_mappings_canonical_values_match_ebnf(self):
        mappings = self._load_provider_mappings()
        for field in ("mailClass", "color", "paperType", "printOption",
                      "productionTime", "envelope", "documentClass", "layout"):
            schema = self.schemas.get(field, {})
            ebnf_enum = set(schema.get("enum", []))
            if not ebnf_enum:
                continue
            mapping_keys = {k for k in mappings.get(field, {}).keys()
                            if not k.startswith("_")}
            with self.subTest(field=field):
                missing = ebnf_enum - mapping_keys
                self.assertEqual(missing, set(),
                                 f"{field}: canonical values in EBNF not covered by "
                                 f"provider mappings: {missing}")

    def test_layout_alias_maps_to_canonical(self):
        mappings = self._load_provider_mappings()
        layout = mappings.get("layout", {})
        aliases = layout.get("_aliases", {})
        self.assertEqual(aliases.get("address_on_top"), "address_on_first_page",
                         "Legacy address_on_top must alias to address_on_first_page")

    # ── 9. No address_on_top in getting-started-template ─────────────────────

    def test_getting_started_template_uses_canonical_layout(self):
        template_path = REPO_ROOT / "config" / "getting-started-template.yaml"
        content = template_path.read_text(encoding="utf-8")
        self.assertNotIn("address_on_top", content,
                         "getting-started-template.yaml must not use legacy address_on_top")
        self.assertIn("address_on_first_page", content,
                      "getting-started-template.yaml must use address_on_first_page")


if __name__ == "__main__":
    unittest.main()
