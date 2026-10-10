#!/usr/bin/env python3
"""
Golden tests for validate_migration.py — each check must fire on a known fault and
stay quiet on a correctly declared change, before the tool is trusted on a migration.

Run via:
    python -m pytest scripts/validation/tests/test_migration_validator.py -v
or:
    make validate-collections-conformance-test
"""

import copy
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "validation"))

import validate_migration as M  # noqa: E402

OLD = "recipientAddressSource.singleAddress."
NEW = "recipientAddressSource.recipientAddressByList.addressList[0]."


def snapshot(single=True, schema_extra=None):
    """A minimal snapshot before (single=True) or after (single=False) the D2-style change."""
    p = OLD if single else NEW
    body = {f"{p}firstName": "John", f"{p}zip": "78701", "docSourceAll.documentIdSource.documentId": 12345}
    schemas = {"address": {"type": "object"},
               "recipientAddressSource": {"oneOf": ["single" if single else "list"]}}
    if single:
        schemas["singleAddress"] = {"$ref": "#/components/schemas/address"}
    schemas.update(schema_extra or {})
    return {
        "meta": {"commit": "test"},
        "dd": {"address": "a", "recipientAddressSource": "s1" if single else "s2",
               **({"singleAddress": "x"} if single else {})},
        "spec": {"schemas": schemas, "operations": {"POST /static": {
            "requestBody": "#/components/schemas/submitDocParams",
            "responses": {"400": {"invalid-format": {"errorDetails": f'{{"field": "{p}zip"}}'}}}}}},
        "configs": {"catalog": {"Ex": {"method": "POST", "path": "/static",
                                        "select": {"recipientAddressSource": "singleAddress" if single else "recipientAddressByList"},
                                        "values": {f"{p}firstName": "John"}}},
                    "template": {}},
        "collections": {label: {"POST /static": {"method": "POST", "path": "/static", "body": dict(body),
                                                 "saved": [{"code": 200, "name": "ok", "body": {"status": "accepted"}}]}}
                        for label in M.COLLECTIONS},
    }


MIGRATION = M.Migration({
    "name": "test D2",
    "path_rewrites": [{"from": OLD, "to": NEW}],
    "select_rewrites": {"recipientAddressSource": {"singleAddress": "recipientAddressByList"}},
    "rules": {"removed": ["singleAddress"], "changed": ["recipientAddressSource"]},
    "schemas": {"removed": ["singleAddress"], "changed": ["recipientAddressSource"]},
})
NEVER_RANDOM = (lambda name: False)


def kinds(rep):
    return {(k, a.split(" ")[0]) for k, a, _m in rep.items}


class TestCompare(unittest.TestCase):

    def test_identical_snapshots_with_null_migration_are_clean(self):
        s = snapshot()
        rep = M.compare(s, copy.deepcopy(s), M.Migration({"name": "null"}), NEVER_RANDOM)
        self.assertEqual(rep.items, [])

    def test_correctly_applied_migration_is_clean(self):
        rep = M.compare(snapshot(True), snapshot(False), MIGRATION, NEVER_RANDOM)
        self.assertEqual(rep.items, [])

    def test_lost_value_is_reported(self):
        after = snapshot(False)
        del after["collections"]["Test"]["POST /static"]["body"][f"{NEW}zip"]
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("LOST", "Test"), kinds(rep))

    def test_changed_deterministic_value_is_reported(self):
        after = snapshot(False)
        after["configs"]["catalog"]["Ex"]["values"][f"{NEW}firstName"] = "Jane"
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("UNEXPECTED", "catalog"), kinds(rep))

    def test_random_field_value_change_ignored_but_removal_reported(self):
        after = snapshot(False)
        after["collections"]["Test"]["POST /static"]["body"][f"{NEW}firstName"] = "Random"
        rep = M.compare(snapshot(True), after, MIGRATION, lambda name: name == "firstName")
        self.assertEqual(rep.items, [])
        del after["collections"]["Test"]["POST /static"]["body"][f"{NEW}firstName"]
        rep = M.compare(snapshot(True), after, MIGRATION, lambda name: name == "firstName")
        self.assertIn(("LOST", "Test"), kinds(rep))

    def test_undeclared_schema_change_is_reported(self):
        after = snapshot(False, schema_extra={"address": {"type": "object", "x": 1}})
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("UNEXPECTED", "spec"), kinds(rep))

    def test_declared_removal_not_done_is_incomplete(self):
        after = snapshot(False, schema_extra={"singleAddress": {"$ref": "#/components/schemas/address"}})
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("INCOMPLETE", "spec"), kinds(rep))

    def test_declared_select_rewrite_not_done_is_incomplete(self):
        after = snapshot(False)
        after["configs"]["catalog"]["Ex"]["select"] = {"recipientAddressSource": "singleAddress"}
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("INCOMPLETE", "catalog"), kinds(rep))

    def test_spec_example_paths_follow_the_rewrite(self):
        after = snapshot(False)
        after["spec"]["operations"]["POST /static"]["responses"]["400"]["invalid-format"]["errorDetails"] = \
            '{"field": "recipientAddressSource.singleAddress.zip"}'
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("UNEXPECTED", "spec"), kinds(rep))

    def test_removed_request_is_reported(self):
        after = snapshot(False)
        del after["collections"]["Real-World"]["POST /static"]
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("UNEXPECTED", "Real-World"), kinds(rep))

    def test_saved_response_change_is_reported(self):
        after = snapshot(False)
        after["collections"]["Linked"]["POST /static"]["saved"][0]["body"]["status"] = "queued"
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("UNEXPECTED", "Linked"), kinds(rep))

    def test_unexpected_new_path_is_reported_unless_allowed(self):
        after = snapshot(False)
        after["collections"]["GS-Test"]["POST /static"]["body"]["recipientAddressSource.recipientAddressByList.mappingId"] = 5001
        rep = M.compare(snapshot(True), after, MIGRATION, NEVER_RANDOM)
        self.assertIn(("UNEXPECTED", "GS-Test"), kinds(rep))
        allowing = M.Migration({**{"name": "x", "path_rewrites": [{"from": OLD, "to": NEW}],
                                    "select_rewrites": {"recipientAddressSource": {"singleAddress": "recipientAddressByList"}},
                                    "rules": {"removed": ["singleAddress"], "changed": ["recipientAddressSource"]},
                                    "schemas": {"removed": ["singleAddress"], "changed": ["recipientAddressSource"]}},
                                 "allowed_added_paths": [r"recipientAddressByList\.mappingId$"]})
        self.assertEqual(M.compare(snapshot(True), after, allowing, NEVER_RANDOM).items, [])


    def _rotation(self, variants):
        """Two Test requests whose recipientAddressSource variants are `variants` (in order)."""
        s = snapshot(False)
        reqs = {}
        for i, v in enumerate(variants):
            reqs[f"POST /r{i}"] = {"method": "POST", "path": f"/r{i}", "saved": [],
                                   "body": {f"recipientAddressSource.{v}.x": 1}}
        s["collections"]["Test"] = reqs
        return s

    def test_rotated_field_shift_is_clean_when_variant_set_is_kept(self):
        rotating = M.Migration({"name": "rot", "rotated_fields": {"Test": ["recipientAddressSource"]}})
        rep = M.compare(self._rotation(["a", "b"]), self._rotation(["b", "a"]), rotating, NEVER_RANDOM)
        self.assertEqual(rep.items, [])

    def test_rotated_field_dropped_variant_is_reported(self):
        rotating = M.Migration({"name": "rot", "rotated_fields": {"Test": ["recipientAddressSource"]}})
        rep = M.compare(self._rotation(["a", "b"]), self._rotation(["a", "a"]), rotating, NEVER_RANDOM)
        self.assertIn(("LOST", "Test"), kinds(rep))

    def test_rotated_field_extra_variant_is_accepted(self):
        rotating = M.Migration({"name": "rot", "rotated_fields": {"Test": ["recipientAddressSource"]}})
        rep = M.compare(self._rotation(["a", "a"]), self._rotation(["a", "b"]), rotating, NEVER_RANDOM)
        self.assertEqual(rep.items, [])


class TestRetiredNames(unittest.TestCase):

    def test_retired_name_found_and_archive_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "config").mkdir()
            (root / "config" / "a.yaml").write_text("recipientAddressSource: singleAddress\n")
            (root / "scripts" / "active" / "archive").mkdir(parents=True)
            (root / "scripts" / "active" / "archive" / "old.py").write_text("singleAddress = 1\n")
            (root / "scripts" / "active" / "ok.py").write_text("singleAddressCount = 1  # different word\n")
            hits = M.find_retired(["singleAddress"], root)
        self.assertEqual(hits, ["config/a.yaml:1: singleAddress"])


class TestSnapshotOfRealBuild(unittest.TestCase):

    def test_snapshot_covers_all_layers(self):
        s = M.take_snapshot()
        self.assertGreater(len(s["dd"]), 50)
        self.assertGreater(len(s["spec"]["schemas"]), 50)
        self.assertEqual(len(s["spec"]["operations"]), 10)
        self.assertTrue(s["configs"]["catalog"] and s["configs"]["template"])
        for label in M.COLLECTIONS:
            self.assertTrue(s["collections"][label], f"{label} collection missing from the snapshot")


if __name__ == "__main__":
    unittest.main()
