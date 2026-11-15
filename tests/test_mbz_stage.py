"""Tests for the MBZ source staging tool (copies plus quelle-manifest.json)."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'mbz_stage', ROOT / 'agents/moodle-mbz/skills/moodle-mbz/scripts/stage.py')
stage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage)
_main = stage.main


def quiet_main(argv):
    """Run the CLI without printing its report into the test output."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return _main(argv)


stage.main = quiet_main


class StageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.course = Path(self.tmp.name) / 'kurs'
        self.plan = self.course / 'moodle-mbz'
        (self.course / '06-design').mkdir(parents=True)
        self.plan.mkdir()
        (self.course / '06-design/a.html').write_bytes(b'<p>A</p>\r\n')
        (self.course / '06-design/b.html').write_bytes(b'<p>B</p>\n')
        self.write_mapping({'quelle/html/a.html': '06-design/a.html', 'quelle/html/b.html': '06-design/b.html'})

    def tearDown(self):
        self.tmp.cleanup()

    def write_mapping(self, mapping):
        (self.plan / stage.MAPPING).write_text(json.dumps(mapping), encoding='utf-8')

    def test_copy_is_byte_identical_and_passes(self):
        self.assertEqual(stage.main(['kopieren', '--plan-ordner', str(self.plan)]), 0)
        self.assertEqual((self.plan / 'quelle/html/a.html').read_bytes(), b'<p>A</p>\r\n')
        manifest = json.loads((self.plan / stage.MANIFEST).read_text(encoding='utf-8'))
        self.assertEqual(sorted(manifest), ['quelle/html/a.html', 'quelle/html/b.html'])

    def test_changed_source_is_reported_and_only_named_copy_replaced(self):
        stage.main(['kopieren', '--plan-ordner', str(self.plan)])
        (self.course / '06-design/a.html').write_bytes(b'<p>A2</p>\n')
        (self.course / '06-design/b.html').write_bytes(b'<p>B2</p>\n')
        self.assertEqual(len(stage.check(self.plan)), 2)
        self.assertEqual(stage.main(['kopieren', '--plan-ordner', str(self.plan), 'quelle/html/a.html']), 1)
        self.assertEqual((self.plan / 'quelle/html/a.html').read_bytes(), b'<p>A2</p>\n')
        self.assertEqual((self.plan / 'quelle/html/b.html').read_bytes(), b'<p>B</p>\n')
        self.assertEqual(stage.check(self.plan), ['QUELLE GEAENDERT: 06-design/b.html -> quelle/html/b.html'])

    def test_tampered_copy_and_unmapped_file_fail(self):
        stage.main(['kopieren', '--plan-ordner', str(self.plan)])
        (self.plan / 'quelle/html/b.html').write_bytes(b'x')
        (self.plan / 'quelle/extra.txt').write_bytes(b'x')
        self.assertEqual(stage.check(self.plan), [
            'KOPIE WEICHT VOM MANIFEST AB: quelle/html/b.html', 'NICHT ZUGEORDNET: quelle/extra.txt'])

    def test_paths_outside_course_or_quelle_are_rejected(self):
        for mapping in ({'quelle/a.html': '../fremd.html'}, {'andere/a.html': '06-design/a.html'},
                        {'quelle/../a.html': '06-design/a.html'}, {'quelle/a.html': 'C:/x.html'}):
            self.write_mapping(mapping)
            self.assertEqual(stage.main(['pruefen', '--plan-ordner', str(self.plan)]), 2)


if __name__ == '__main__':
    unittest.main()
