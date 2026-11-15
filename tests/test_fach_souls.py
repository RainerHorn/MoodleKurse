"""The four subject SOUL files are generated from one template and must not drift."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_fach_souls', ROOT / 'scripts' / 'build_fach_souls.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class FachSoulTests(unittest.TestCase):
    def test_committed_souls_match_template(self):
        rendered = build.render(ROOT)
        self.assertEqual(sorted(rendered), ['agents/fiae/SOUL.md', 'agents/fidp/SOUL.md',
                                            'agents/fisi/SOUL.md', 'agents/vt/SOUL.md'])
        for relative, text in rendered.items():
            with self.subTest(file=relative):
                self.assertEqual((ROOT / relative).read_bytes().decode('utf-8'), text)

    def test_each_role_reads_its_own_curriculum_folder(self):
        for relative, text in build.render(ROOT).items():
            role = relative.split('/')[1]
            with self.subTest(role=role):
                self.assertIn('`_vorgaben/rahmenlehrplaene/' + role.upper() + '/`', text)
                self.assertTrue((ROOT / '_vorgaben' / 'rahmenlehrplaene' / role.upper()).is_dir())
                self.assertNotIn('{{', text)


if __name__ == '__main__':
    unittest.main()
