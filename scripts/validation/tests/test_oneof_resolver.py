#!/usr/bin/env python3
"""
Unit tests for scripts/utilities/oneof_resolver.py
"""
import sys
import os
import unittest
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utilities.oneof_resolver import (
    find_variant_by_discriminator_key,
    build_variant_placeholder_structure,
)

# Minimal synthetic spec for testing without the real spec on disk
SYNTHETIC_SPEC = {
    "components": {
        "schemas": {
            "docSourceAll": {
                "oneOf": [
                    {"$ref": "#/components/schemas/docSourceStandard"},
                ]
            },
            "docSourceStandard": {
                "oneOf": [
                    {"$ref": "#/components/schemas/requestIdSource"},
                    {"$ref": "#/components/schemas/documentIdSource"},
                    {"$ref": "#/components/schemas/urlSource"},
                ]
            },
            "requestIdSource": {
                "type": "object",
                "properties": {"requestId": {"type": "integer"}}
            },
            "documentIdSource": {
                "type": "object",
                "properties": {"documentId": {"type": "integer"}}
            },
            "urlSource": {
                "type": "object",
                "properties": {"url": {"type": "string"}}
            },
            "recipientAddressSource": {
                "oneOf": [
                    {"$ref": "#/components/schemas/recipientAddressBySingle"},
                    {"$ref": "#/components/schemas/recipientAddressByList"},
                ]
            },
            "recipientAddressBySingle": {
                "type": "object",
                "properties": {
                    "singleAddress": {
                        "type": "object",
                        "properties": {
                            "firstName": {"type": "string"},
                            "lastName":  {"type": "string"},
                        }
                    }
                }
            },
            "recipientAddressByList": {
                "type": "object",
                "properties": {
                    "addressList": {"type": "array", "items": {"type": "object"}},
                    "mappingId": {"type": "integer"},
                }
            },
            "paymentDetails": {
                "oneOf": [
                    {"$ref": "#/components/schemas/creditCardPayment"},
                ]
            },
            "creditCardPayment": {
                "type": "object",
                "properties": {
                    "creditCard": {
                        "type": "object",
                        "properties": {"cardType": {"type": "string"}}
                    }
                }
            },
        }
    }
}


class TestFindVariantByDiscriminatorKey(unittest.TestCase):

    def test_direct_oneof_match(self):
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "recipientAddressSource", "singleAddress"
        )
        self.assertEqual(name, "recipientAddressBySingle")
        self.assertIsNotNone(schema)

    def test_nested_oneof_match(self):
        """docSourceAll → docSourceStandard → requestIdSource (two levels deep)"""
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "docSourceAll", "requestId"
        )
        self.assertEqual(name, "requestIdSource")
        self.assertIsNotNone(schema)

    def test_nested_oneof_url_variant(self):
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "docSourceAll", "url"
        )
        self.assertEqual(name, "urlSource")

    def test_payment_variant(self):
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "paymentDetails", "creditCard"
        )
        self.assertEqual(name, "creditCardPayment")

    def test_unknown_discriminator_key_returns_none(self):
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "docSourceAll", "nonExistentKey"
        )
        self.assertIsNone(name)
        self.assertIsNone(schema)

    def test_unknown_field_returns_none(self):
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "unknownField", "requestId"
        )
        self.assertIsNone(name)

    def test_address_list_variant(self):
        name, schema = find_variant_by_discriminator_key(
            SYNTHETIC_SPEC, "recipientAddressSource", "addressList"
        )
        self.assertEqual(name, "recipientAddressByList")


class TestBuildVariantPlaceholderStructure(unittest.TestCase):

    def test_simple_object(self):
        structure = build_variant_placeholder_structure(SYNTHETIC_SPEC, "requestIdSource")
        self.assertEqual(structure, {"requestId": "<Integer>"})

    def test_nested_object(self):
        structure = build_variant_placeholder_structure(
            SYNTHETIC_SPEC, "recipientAddressBySingle"
        )
        self.assertIn("singleAddress", structure)
        self.assertIn("firstName", structure["singleAddress"])
        self.assertEqual(structure["singleAddress"]["firstName"], "<String>")

    def test_unknown_schema_returns_none(self):
        result = build_variant_placeholder_structure(SYNTHETIC_SPEC, "doesNotExist")
        self.assertIsNone(result)


class TestWithRealSpec(unittest.TestCase):
    """
    Integration tests against the real generated spec.
    Skipped if the spec has not been generated yet.
    CI runs these against the spec it just built.
    """

    SPEC_PATH = Path("openapi/c2mapiv2-openapi-spec-base.yaml")

    @classmethod
    def setUpClass(cls):
        if not cls.SPEC_PATH.exists():
            raise unittest.SkipTest(
                f"Real spec not found at {cls.SPEC_PATH}. Run 'make openapi-build' first."
            )
        import yaml
        with open(cls.SPEC_PATH) as f:
            cls.spec = yaml.safe_load(f)

    def test_request_id_source(self):
        name, _ = find_variant_by_discriminator_key(self.spec, "docSourceAll", "requestId")
        self.assertIsNotNone(name, "requestId variant not found in docSourceAll")

    def test_document_id_source(self):
        name, _ = find_variant_by_discriminator_key(self.spec, "docSourceAll", "documentId")
        self.assertIsNotNone(name)

    def test_single_address(self):
        name, _ = find_variant_by_discriminator_key(
            self.spec, "recipientAddressSource", "singleAddress"
        )
        self.assertIsNotNone(name)

    def test_credit_card(self):
        name, _ = find_variant_by_discriminator_key(self.spec, "paymentDetails", "creditCard")
        self.assertIsNotNone(name)

    def test_all_known_variants_resolve(self):
        """Ensure every variant that the YAML configs use resolves correctly."""
        known_variants = [
            ("docSourceAll",           "requestId"),
            ("docSourceAll",           "documentId"),
            ("docSourceAll",           "url"),
            ("recipientAddressSource", "singleAddress"),
            ("recipientAddressSource", "addressList"),
            ("recipientAddressSource", "addressListId"),
            ("paymentDetails",         "creditCard"),
            ("paymentDetails",         "ach"),
            ("paymentDetails",         "invoice"),
        ]
        failures = []
        for field, key in known_variants:
            name, _ = find_variant_by_discriminator_key(self.spec, field, key)
            if name is None:
                failures.append(f"{field}/{key}")
        self.assertFalse(
            failures,
            f"The following variants could not be resolved from the spec: {failures}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
