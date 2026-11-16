"""The component catalog must match the files it describes."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ComponentsCatalogTest(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / 'platform/components.json').read_text(encoding='utf-8'))

    def test_hashes_match_current_files(self):
        for entry in self.catalog['components']:
            with self.subTest(component=entry['id']):
                actual = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
                self.assertEqual(actual, entry['sha256'],
                                 'Datei geaendert: Hash und ggf. Version in platform/components.json nachziehen')

    def test_evidence_files_exist(self):
        for entry in self.catalog['components']:
            for part in entry['evidence'].split(';'):
                path = part.strip().split('#')[0].split(' ')[0]
                with self.subTest(component=entry['id'], evidence=path):
                    self.assertTrue((ROOT / path).is_file(), 'Nachweisdatei fehlt: ' + path)


if __name__ == '__main__':
    unittest.main()
