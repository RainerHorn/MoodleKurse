"""Targeted evidence lifecycle tests. All generated files stay in a temp directory."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / "scripts/check_runner.py"


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.input = self.base / "input.txt"
        self.input.write_text("one")
        self.validator = self.base / "validate.py"
        self.validator.write_text("from pathlib import Path\nPath('report.txt').write_text('report')\n")
        self.spec = self.base / "checks.json"
        self.config = {"checks": [{"id": "sample", "phase": "test", "property": "fixture",
            "scope": "local fixture only", "command": ["{python}", "validate.py"],
            "inputs": ["input.txt"], "validators": ["validate.py"],
            "environment": {"dependencies": "stdlib"}, "reason": "change", "cacheable": True}]}
        self.save()

    def save(self):
        self.spec.write_text(json.dumps(self.config))

    def run_check(self, *args):
        return subprocess.run([sys.executable, str(RUNNER), "run", "--spec", str(self.spec), *args],
                              capture_output=True, text=True)

    def test_reuse_report_exclusion_and_input_invalidation(self):
        self.assertIn("PASS", self.run_check().stdout)
        (self.base / "report.txt").write_text("changed output")
        self.assertIn("REUSED", self.run_check().stdout)
        self.input.write_text("two")
        self.assertIn("PASS", self.run_check().stdout)

    def test_validator_and_environment_invalidation(self):
        self.assertIn("PASS", self.run_check().stdout)
        self.validator.write_text("print('new validator')")
        self.assertIn("PASS", self.run_check().stdout)
        self.config["checks"][0]["environment"]["dependencies"] = "changed"
        self.save()
        self.assertIn("PASS", self.run_check().stdout)

    def test_forced_failure_cannot_reuse_previous_success(self):
        self.validator.write_text("from pathlib import Path\nraise SystemExit(int(Path('fail.flag').exists()))")
        self.assertIn("PASS", self.run_check().stdout)
        (self.base / "fail.flag").touch()
        result = self.run_check("--force-reason", "suspected external change")
        self.assertEqual(1, result.returncode)
        self.assertEqual(1, self.run_check().returncode)

    def test_input_mutation_and_missing_dependency_fail(self):
        self.validator.write_text("from pathlib import Path\nPath('input.txt').write_text('mutated')")
        self.assertEqual(1, self.run_check().returncode)
        self.input.unlink()
        self.assertEqual(2, self.run_check().returncode)

    def test_noncacheable_and_timeout(self):
        self.config["checks"][0]["cacheable"] = False
        self.save()
        self.assertIn("PASS", self.run_check().stdout)
        self.assertIn("PASS", self.run_check().stdout)
        self.validator.write_text("import time\ntime.sleep(2)")
        self.config["checks"][0]["timeout_seconds"] = 0.05
        self.save()
        self.assertEqual(1, self.run_check().returncode)

    def test_reported_metrics_unknown_duration_and_lock(self):
        result = subprocess.run([sys.executable, str(RUNNER), "event", "--spec", str(self.spec),
            "--phase", "moodle", "--reason", "change", "--source", "fixture", "--reads", "1"],
            capture_output=True, text=True)
        self.assertEqual(0, result.returncode)
        root = self.base / "checks.pruefung-intern"
        event = json.loads((root / "events.jsonl").read_text())
        self.assertNotIn("duration_seconds", event)
        self.assertEqual(1, event["reads"])
        (root / ".lock").touch()
        self.assertEqual(2, self.run_check().returncode)


if __name__ == "__main__":
    unittest.main()
