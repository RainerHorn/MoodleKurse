import json
import tempfile
import unittest
from pathlib import Path

from scripts.sync_obsidian import discover_courses, render_course_note, sync_courses


class SyncObsidianTests(unittest.TestCase):
    def test_discovers_course_and_renders_metadata_without_sensitive_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            course = root / "courses" / "VT" / "beispielkurs"
            course.mkdir(parents=True)
            (course / "STATUS.json").write_text(json.dumps({
                "schema_version": 2,
                "course": "Beispielkurs",
                "updated_at": "2026-11-14",
                "brief": {
                    "program": "Veranstaltungstechnik",
                    "learning_field": "LF 1",
                    "minutes": 90,
                    "product": "Auswahlkarte"
                },
                "technical": {"status": "OPEN"},
                "user_authorization": {"status": "NOT_GRANTED"},
                "next_action": {"owner": "orchestrator", "action": "Review durchführen"},
                "package": {"binding": "secret-binding", "files": ["geschuetzt/loesung.md"]}
            }), encoding="utf-8")
            (course / "geschuetzt").mkdir()
            (course / "geschuetzt" / "loesung.md").write_text("GEHEIM", encoding="utf-8")

            courses = discover_courses(root)
            self.assertEqual(1, len(courses))
            note = render_course_note(courses[0])

            self.assertIn("# Beispielkurs", note)
            self.assertIn("fachrichtung: VT", note)
            self.assertIn("Review durchführen", note)
            self.assertNotIn("secret-binding", note)
            self.assertNotIn("GEHEIM", note)
            self.assertNotIn("geschuetzt/loesung.md", note)

    def test_sync_preserves_manual_note_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            vault = base / "vault"
            course = source / "courses" / "FIAE" / "demo"
            course.mkdir(parents=True)
            (course / "STATUS.json").write_text(json.dumps({
                "course": "Neuer Kurstitel",
                "brief": {"learning_field": "LF 11a"}
            }), encoding="utf-8")
            target = vault / "10-Kurse" / "FIAE" / "demo.md"
            target.parent.mkdir(parents=True)
            target.write_text(
                "Alter Inhalt\n<!-- BEGIN MANUAL -->\nMeine dauerhafte Notiz\n<!-- END MANUAL -->\n",
                encoding="utf-8",
            )

            changed = sync_courses(source, vault)

            self.assertEqual([target], changed)
            result = target.read_text(encoding="utf-8")
            self.assertIn("# Neuer Kurstitel", result)
            self.assertIn("Meine dauerhafte Notiz", result)
            self.assertNotIn("Alter Inhalt", result)


if __name__ == "__main__":
    unittest.main()
