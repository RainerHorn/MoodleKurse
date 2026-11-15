"""Only status invariants; no course content tests or external calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("project_status", ROOT / "scripts/project_status.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / "content.txt").write_text("content")
        (self.base / "review.md").write_text("fixture review")
        self.data = json.loads((ROOT / "_templates/prozess/STATUS.json").read_text())
        self.hash = hashlib.sha256(b"content").hexdigest()
        self.data["schema_version"] = 1
        self.data["package"] = {"id": "draft-1", "artifacts": [
            {"path": "content.txt", "owner": "fiae", "sha256": self.hash}
        ]}
        self.data["user_authorization"] = {
            "status": "NOT_GRANTED", "scope": None, "package_id": None,
            "artifact_hashes": {}, "evidence": []
        }

    def review(self):
        return {"status": "APPROVED", "scope": "artifacts", "coverage": "complete",
                "reviewer": "reviewer", "package_id": "draft-1", "evidence": ["review.md"],
                "artifact_hashes": {"content.txt": self.hash}}

    def test_changed_content_invalidates_snapshot(self):
        self.assertEqual([], MODULE.validate(self.data, self.base))
        (self.base / "content.txt").write_text("changed")
        self.assertTrue(MODULE.validate(self.data, self.base))

    def test_approval_requires_binding_and_cannot_have_same_scope_blocker(self):
        review = self.review()
        review["artifact_hashes"] = {}
        self.data["reviews"] = [review]
        self.assertTrue(MODULE.validate(self.data, self.base))
        self.data["reviews"] = [self.review()]
        self.assertEqual([], MODULE.validate(self.data, self.base))
        self.data["findings"] = [{"id": "B1", "status": "OPEN", "owner": "fiae",
            "problem": "error", "acceptance": "correct", "severity": "BLOCKER", "blocks": "artifacts"}]
        self.assertTrue(MODULE.validate(self.data, self.base))

    def test_historical_test_permission_is_not_current_permission(self):
        self.data["user_authorization"] = {"status": "HISTORICAL_TEST_ONLY", "scope": "previous test only", "evidence": ["review.md"]}
        self.assertEqual([], MODULE.validate(self.data, self.base))
        self.data["user_authorization"]["status"] = "GRANTED"
        self.assertTrue(MODULE.validate(self.data, self.base))

    def test_outside_course_evidence_rejected(self):
        review = self.review()
        review["evidence"] = [str(ROOT / "AGENTS.md")]
        self.data["reviews"] = [review]
        with self.assertRaises(ValueError):
            MODULE.validate(self.data, self.base)

    def test_schema2_accepts_file_inventory_without_per_file_hashes(self):
        data = copy.deepcopy(self.data)
        data["schema_version"] = 2
        data["package"] = {
            "id": "draft-2",
            "files": [{"path": "content.txt", "owner": "fiae"}],
            "binding": None,
        }
        data["user_authorization"] = {
            "status": "NOT_GRANTED", "scope": None, "package_id": None,
            "binding": None, "evidence": []
        }
        self.assertEqual([], MODULE.validate(data, self.base))

    def test_schema2_review_uses_one_package_binding(self):
        data = copy.deepcopy(self.data)
        data["schema_version"] = 2
        binding = {"type": "manifest", "value": "a" * 64}
        data["package"] = {
            "id": "review-1",
            "files": [{"path": "content.txt", "owner": "fiae"}],
            "binding": binding,
        }
        data["reviews"] = [{
            "status": "APPROVED", "scope": "artifacts", "coverage": "complete",
            "reviewer": "reviewer", "package_id": "review-1",
            "binding": binding, "evidence": ["review.md"]
        }]
        data["user_authorization"] = {
            "status": "NOT_GRANTED", "scope": None, "package_id": None,
            "binding": None, "evidence": []
        }
        self.assertEqual([], MODULE.validate(data, self.base))
        data["reviews"][0]["binding"] = {"type": "manifest", "value": "b" * 64}
        self.assertTrue(MODULE.validate(data, self.base))


if __name__ == "__main__":
    unittest.main()
