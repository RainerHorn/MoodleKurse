"""Targeted regressions for reusable transport and safe profile synchronization."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


xml = module('xml_transport')
links = module('build_links')
sync = module('profile_sync')
audit = module('config_audit')


class TransportTests(unittest.TestCase):
    def test_category_cdata_and_line_endings(self):
        question = b'<question type="essay"><text><![CDATA[<question type="category">keep</question>]]></text></question>'
        source = b'<quiz>\r\n  <question type="category"><category>x</category></question>\r\n' + question + b'</quiz>'
        self.assertEqual(xml.derive(source), (b'<quiz>\r\n' + question + b'</quiz>', 1))

    def test_empty_inline_and_multiple_categories(self):
        self.assertEqual(xml.derive(b'<quiz><question type="category"/><question type="category"></question></quiz>'), (b'<quiz></quiz>', 2))
        self.assertEqual(xml.derive(b'<quiz/>'), (b'<quiz/>', 0))
        with self.assertRaises(ValueError):
            xml.derive(b'<!DOCTYPE quiz [<!ENTITY x "x">]><quiz/>')

    def test_real_course_xml_and_all_pages_without_writing(self):
        import json
        course = ROOT / 'courses/VT/rigging-mathematik-90min'
        source = (course / 'quiz/04_abschlusstest_moodle.xml').read_bytes()
        self.assertEqual(xml.derive(source)[0], (course / 'quiz/07_abschlusstest_moodle_import_ohne_kategorie_intern.xml').read_bytes())
        design = course / '06-design'
        mapping = json.loads((design / 'dist-moodle-testsystem/testlinks-manifest.json').read_text(encoding='utf-8'))
        for name in mapping['pages']:
            with self.subTest(page=name):
                self.assertEqual(links.render((design / 'dist-moodle' / (name + '.html')).read_bytes(), mapping['targets'], 'http://localhost:8080'),
                                 (design / 'dist-moodle-testsystem' / (name + '.html')).read_bytes())

    def test_link_invalid_targets_and_placeholder_context(self):
        target = {'page': {'viewurl': 'https://example.test/mod/page/view.php?id=12', 'cmid': 12, 'modname': 'page', 'source': 'readback'}}
        data = b'<a href="__MOODLE_URL_page__">Test</a>'
        self.assertEqual(links.render(data, target, 'https://example.test'), b'<a href="/mod/page/view.php?id=12">Test</a>')
        for origin, text in [('https://other.test', data), ('https://example.test', b'<i data-href="__MOODLE_URL_page__">')]:
            with self.assertRaises(ValueError):
                links.render(text, target, origin)
        target['page']['cmid'] = 13
        with self.assertRaises(ValueError):
            links.render(data, target, 'https://example.test')

    def test_config_subset_and_forbidden_tools(self):
        text = (ROOT / 'agents/moodle-mcp/config.template.yaml').read_text(encoding='utf-8')
        self.assertIn('moodle_import_page_file', audit.subset(text)['tools'])
        with self.assertRaises(ValueError):
            audit.subset(text.replace('- moodle_get_courses', '- moodle_delete_module'))


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo, self.profiles = self.base / 'repo', self.base / 'profiles'
        self.src = self.repo / 'agents/quiz/SOUL.md'
        self.dst = self.profiles / 'quiz/SOUL.md'
        self.src.parent.mkdir(parents=True)
        self.dst.parent.mkdir(parents=True)
        self.src.write_text('new')
        self.dst.write_text('old')

    def test_preview_keep_and_once_only_backup(self):
        data = sync.plan(self.repo, self.profiles)
        self.assertEqual(sync.apply(data, self.repo, self.profiles), 0)
        data['entries'][0]['decision'] = 'replace'
        self.assertEqual(sync.apply(data, self.repo, self.profiles), 1)
        self.src.write_text('newer')
        data = sync.plan(self.repo, self.profiles)
        data['entries'][0]['decision'] = 'replace'
        sync.apply(data, self.repo, self.profiles)
        self.assertEqual(Path(str(self.dst) + '.bak').read_text(), 'old')
        self.assertEqual(self.dst.read_text(), 'newer')

    def test_stale_plan_and_path_escape_rejected(self):
        data = sync.plan(self.repo, self.profiles)
        data['entries'][0]['decision'] = 'replace'
        self.dst.write_text('user edit')
        with self.assertRaises(ValueError):
            sync.apply(data, self.repo, self.profiles)
        self.assertEqual(self.dst.read_text(), 'user edit')
        data = sync.plan(self.repo, self.profiles)
        data['entries'][0]['target'] = '../outside.md'
        with self.assertRaises(ValueError):
            sync.apply(data, self.repo, self.profiles)

    def test_backup_exclusion_and_whole_plan_preflight(self):
        skills = self.src.parent / 'skills/test'
        skills.mkdir(parents=True)
        (skills / 'SKILL.md').write_text('skill')
        (skills / 'SKILL.md.bak').write_text('old skill')
        data = sync.plan(self.repo, self.profiles)
        self.assertEqual(len(data['entries']), 2)
        for entry in data['entries']:
            entry['decision'] = 'replace'
        data['entries'][-1]['source_sha256'] = 'stale'
        with self.assertRaises(ValueError):
            sync.apply(data, self.repo, self.profiles)
        self.assertEqual(self.dst.read_text(), 'old')

    def test_shared_skill_reaches_every_role_and_collision_rejected(self):
        other = self.repo / 'agents/vt/SOUL.md'
        other.parent.mkdir(parents=True)
        other.write_text('vt')
        shared = self.repo / 'agents/_shared/skills/common/SKILL.md'
        shared.parent.mkdir(parents=True)
        shared.write_text('common')
        mapping = sync.sources(self.repo)
        self.assertEqual(mapping['quiz/skills/common/SKILL.md'], 'agents/_shared/skills/common/SKILL.md')
        self.assertEqual(mapping['vt/skills/common/SKILL.md'], 'agents/_shared/skills/common/SKILL.md')
        self.assertNotIn('_shared/SOUL.md', mapping)
        (self.profiles / 'vt').mkdir()
        data = sync.plan(self.repo, self.profiles)
        for entry in data['entries']:
            entry['decision'] = 'replace'
        self.assertEqual(sync.apply(data, self.repo, self.profiles), 4)
        self.assertEqual((self.profiles / 'vt/skills/common/SKILL.md').read_text(), 'common')
        own = self.repo / 'agents/quiz/skills/common/SKILL.md'
        own.parent.mkdir(parents=True)
        own.write_text('own')
        with self.assertRaises(ValueError):
            sync.sources(self.repo)


if __name__ == '__main__':
    unittest.main()
