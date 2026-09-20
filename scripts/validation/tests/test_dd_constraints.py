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
