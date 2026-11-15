"""Student navigation and deterministic project 04 contracts; no optional SDK calls."""
import copy
import importlib.util
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/04-market-intelligence'
SPEC = importlib.util.spec_from_file_location('student_project_04_market', PROJECT / 'market.py')
MARKET = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MARKET
SPEC.loader.exec_module(MARKET)


class StudentProject04Tests(unittest.TestCase):
    def test_project_entrypoints_expose_existing_progression(self):
        overview = (PROJECT / 'README.md').read_text()
        for target in ('learning/README.md', 'learning/README.md#stage-12',
                       'advanced/HANDBOOK.md', 'learning/docs/stages11-12-coherence.md'):
            with self.subTest(target=target):
                self.assertIn(f']({target})', overview)
        handbook = (PROJECT / 'advanced/HANDBOOK.md').read_text()
        self.assertEqual(len(re.findall(r'^## \d+\.', handbook, re.MULTILINE)), 14)

    def test_learning_index_links_all_twenty_guides_exercises_and_solutions(self):
        index = (PROJECT / 'learning/README.md').read_text()
        for stage in (11, 12):
            for lesson in range(1, 11):
                for folder in ('docs', 'exercises', 'solutions'):
                    target = f'{folder}/s{stage}-l{lesson:02d}.md'
                    with self.subTest(target=target):
                        self.assertIn(f']({target})', index)

    def test_project_relative_markdown_links_and_anchors_resolve(self):
        for document in PROJECT.rglob('*.md'):
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', document.read_text()):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                destination = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
                with self.subTest(document=str(document.relative_to(ROOT)), target=target):
                    self.assertTrue(destination.is_relative_to(ROOT))
                    self.assertTrue(destination.exists())
                    if parsed.fragment and destination.is_file():
                        headings = re.findall(r'^#{1,6}\s+(.+)$', destination.read_text(), re.MULTILINE)
                        anchors = {
                            re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
                            for heading in headings
                        }
                        self.assertIn(unquote(parsed.fragment), anchors)

    def test_optional_commands_select_the_pinned_environment(self):
        setup = (PROJECT / 'learning/docs/s11-l03.md').read_text()
        self.assertIn('https://docs.astral.sh/uv/getting-started/installation/', setup)
        self.assertIn('uv sync --frozen --extra crewai', setup)
        for filename in ('s11-l09.md', 's12-l05.md', 's12-l10.md'):
            with self.subTest(filename=filename):
                document = (PROJECT / 'learning/docs' / filename).read_text()
                self.assertIn('uv run --frozen --extra crewai python', document)
        handbook = (PROJECT / 'advanced/HANDBOOK.md').read_text()
        self.assertIn('/tmp/eca-market-live/bin/python projects/04-market-intelligence/advanced/live_research.py', handbook)

    def test_internal_production_and_obsolete_owner_instructions_stay_removed(self):
        forbidden = ('central approval', 'central qa', 'production governor',
                     'budget/governor', 'shared workbook/mapping owners',
                     'before production authoring', 'author-only',
                     'pending central', 'approving tutorial captures',
                     'separate maintained sdk local-check script')
        for document in PROJECT.rglob('*.md'):
            text = document.read_text().lower()
            for phrase in forbidden:
                with self.subTest(document=str(document.relative_to(ROOT)), phrase=phrase):
                    self.assertNotIn(phrase, text)
        boundaries = (PROJECT / 'learning/docs/stages11-12-coherence.md').read_text()
        self.assertIn('The workbook follows these debate roles and the `--facts` input', boundaries)
        self.assertIn('missing access or an unknown outcome remains incomplete', boundaries)

    def test_fixture_rankings_and_missing_margin_remain_authoritative(self):
        source = MARKET.FixtureSource(PROJECT / 'companies.json')
        default = MARKET.run(source, MARKET.Criteria())
        self.assertEqual([(row['symbol'], row['score']) for row in default['profiles']],
                         [('CEDAR-DEMO', 3), ('PINE-DEMO', 2), ('MAPLE-DEMO', 1)])
        pine = default['profiles'][1]
        margin = next(check for check in pine['checks'] if check['metric'] == 'margin')
        self.assertIsNone(margin['value'])
        self.assertIsNone(margin['evidence'])
        self.assertFalse(margin['supported'])
        self.assertFalse(margin['passed'])
        self.assertEqual(len(pine['uncertainties']), 1)
        self.assertEqual(default['quality']['unsupported_metric_count'], 1)
        changed = MARKET.run(source, MARKET.Criteria(min_growth=.20))
        self.assertEqual([(row['symbol'], row['score']) for row in changed['profiles']],
                         [('CEDAR-DEMO', 2), ('PINE-DEMO', 2), ('MAPLE-DEMO', 1)])
        cedar = copy.deepcopy(source.companies()[0])
        cedar.evidence.pop('margin')
        unsupported = MARKET.screen(cedar, MARKET.Criteria())
        self.assertEqual(unsupported['score'], 2)
        self.assertEqual(len(unsupported['uncertainties']), 1)


if __name__ == '__main__':
    unittest.main()
