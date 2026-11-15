"""Student project 03 regressions using only synthetic records and local files."""
import asyncio
import builtins
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects' / '03-deep-research'
sys.path.insert(0, str(PROJECT))

from research_lab.interface import build_ui, progress
from research_lab.reporting import export_bundle
from research_lab.runtime import run
from research_lab.search import FixtureSearch


class StudentProject03Tests(unittest.TestCase):
    def setUp(self):
        self.records = json.loads((PROJECT / 'data/s09-workshop-sources.json').read_text())['records']

    def test_default_fixture_retains_conflicts_and_provenance(self):
        bundle = asyncio.run(run('Community workshop scheduling', FixtureSearch(self.records)))
        self.assertEqual(['cost'], bundle['quality']['conflicts'])
        self.assertEqual(4, len(bundle['evidence']))
        self.assertIn('synthetic offline corpus', bundle['scope'])
        self.assertIsNone(bundle['events'][-1]['tokens'])
        cost = next(item for item in bundle['findings'] if item['topic'] == 'cost')
        self.assertEqual({'30 credits', '45 credits'}, {item['value'] for item in cost['alternatives']})

    def test_fixture_accepts_case_and_spacing_variations(self):
        bundle = asyncio.run(run('  COMMUNITY   Workshop scheduling  ', FixtureSearch(self.records)))
        self.assertEqual(4, len(bundle['evidence']))

    def test_unrelated_question_rejected_before_search_or_events(self):
        class ObservedFixture(FixtureSearch):
            calls = 0

            async def search(self, query):
                self.calls += 1
                return await super().search(query)

        backend = ObservedFixture(self.records)
        events = []
        with self.assertRaisesRegex(ValueError, 'fixed fixture supports only'):
            asyncio.run(run('galactic asteroid mineral royalties', backend, event_callback=events.append))
        self.assertEqual(0, backend.calls)
        self.assertEqual([], events)

    def test_workshop_keywords_do_not_admit_unrelated_question(self):
        with self.assertRaisesRegex(ValueError, 'no research was performed'):
            asyncio.run(run('Community workshop scheduling for asteroid royalties', FixtureSearch(self.records)))

    def test_missing_fixture_evidence_still_reports_insufficient(self):
        bundle = asyncio.run(run('Community workshop scheduling', FixtureSearch([])))
        self.assertEqual([], bundle['evidence'])
        self.assertEqual('insufficient_evidence', bundle['quality']['decision'])

    def test_progress_propagates_fixture_scope_error(self):
        with self.assertRaisesRegex(ValueError, 'fixed fixture supports only'):
            list(progress('galactic asteroid mineral royalties', self.records))

    def test_offline_export_hashes_match_report_bytes(self):
        bundle = asyncio.run(run('Community workshop scheduling', FixtureSearch(self.records)))
        with tempfile.TemporaryDirectory() as directory:
            hashes = export_bundle(bundle, directory)
            for name, digest in hashes.items():
                self.assertEqual(digest, hashlib.sha256((Path(directory) / name).read_bytes()).hexdigest())

    def test_missing_gradio_points_to_ui_requirements(self):
        original_import = builtins.__import__

        def without_gradio(name, *args, **kwargs):
            if name == 'gradio':
                raise ImportError('optional dependency absent')
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=without_gradio):
            with self.assertRaisesRegex(RuntimeError, 'requirements-ui-stages09-10.txt') as raised:
                build_ui(self.records)
        self.assertNotIn('requirements-optional.txt', str(raised.exception))
        self.assertIn('gradio', (PROJECT / 'requirements-ui-stages09-10.txt').read_text())

    def test_student_guides_relative_links_exist(self):
        pages = [
            PROJECT / 'README.md',
            PROJECT / 'docs/student-guide.md',
            PROJECT / 'docs/stages09-10-architecture.md',
            PROJECT / 'docs/semantic-repair-stages09-10-v2.md',
            PROJECT / 'docs/selective-recovery-and-owned-export-v3.md',
            PROJECT / 'deployment/research-v3/README.md',
        ]
        checked = 0
        for page in pages:
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', page.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                checked += 1
                self.assertTrue((page.parent / target.split('#')[0]).exists(), f'{page}: {target}')
        self.assertGreater(checked, 20)

    def test_deployment_guide_uses_existing_v3_lock_and_entrypoint(self):
        guide = (PROJECT / 'deployment/research-v3/README.md').read_text()
        self.assertTrue((PROJECT / 'deployment/research-v3/requirements.lock').is_file())
        self.assertIn('projects/03-deep-research/deployment/research-v3/Dockerfile', guide)
        self.assertIn('127.0.0.1:7860:7860', guide)
        self.assertIn('UID 10001', guide)
        self.assertIn('external_provider_health: not probed', guide)


if __name__ == '__main__':
    unittest.main()
