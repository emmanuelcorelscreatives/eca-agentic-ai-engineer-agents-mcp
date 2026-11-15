"""Offline student setup, retrieval and selected-source regressions for project 1."""
import asyncio
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/01-digital-twin'
sys.path.insert(0, str(PROJECT))

import agents_adapter
from config import Settings, load_profile_sections
from evaluate import evaluate_cases
import make_pdf_fixture
from service import TwinService
from twin import DigitalTwin


class StudentProject01Tests(unittest.TestCase):
    def setUp(self):
        for target in ('socket.socket.connect', 'socket.create_connection'):
            guard = patch(target, side_effect=AssertionError('network is forbidden in offline tests'))
            guard.start()
            self.addCleanup(guard.stop)
        environment = patch.dict(os.environ, {'TWIN_PROFILE': '', 'TWIN_LIVE_MODEL_ENABLED': 'false'})
        environment.start()
        self.addCleanup(environment.stop)

    def core(self, sections=None):
        core = DigitalTwin(load_profile_sections() if sections is None else sections)
        self.addCleanup(core.db.close)
        return core

    def test_persona_only_overlap_does_not_support_absent_facts(self):
        core = self.core()
        for question in ('Has Amara won a national award?', "What is Amara's salary?",
                         'Does Amara Okoye have an AWS certification?', 'Amara Okoye',
                         'National astronaut award', 'Salary and personal contact details'):
            with self.subTest(question=question):
                response = core.answer(question)
                self.assertEqual(response['status'], 'insufficient_evidence')
                self.assertEqual(response['citations'], [])

    def test_supported_subjects_still_retrieve_approved_sections(self):
        core = self.core()
        for question, citation in [('What Python experience does Amara have?', 'profile-01'),
                                   ('Amara Okoye public portfolio', 'profile-02'),
                                   ('Input validation', 'profile-02')]:
            with self.subTest(question=question):
                response = core.answer(question)
                self.assertEqual(response['status'], 'supported')
                self.assertIn(citation, response['citations'])
                self.assertNotIn('private-01', response['citations'])

    def test_profile_loader_preserves_review_flags_and_unicode(self):
        sections = [dict(id='reviewed', title='Café', text='Café reporting', approved=True),
                    dict(id='private', title='Private', text='Private fixture', approved=False)]
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / 'sections-reviewed.json'
            for payload in (sections, {'sections': sections}):
                profile.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
                loaded = load_profile_sections(profile)
                self.assertEqual(loaded, sections)
                self.assertEqual(self.core(loaded).answer('Private')['status'], 'insufficient_evidence')

    def test_profile_loader_rejects_non_section_containers(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / 'invalid.json'
            for payload in ({}, 'not sections', [False]):
                profile.write_text(json.dumps(payload), encoding='utf-8')
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    load_profile_sections(profile)

    def test_settings_select_private_profile_without_enabling_live_mode(self):
        settings = Settings.from_env({'TWIN_PROFILE': '/private/practice/sections-reviewed.json'})
        self.assertEqual(settings.profile, '/private/practice/sections-reviewed.json')
        self.assertFalse(settings.live_model_enabled)

    def fake_sdk(self, citation, observations):
        module = ModuleType('agents')

        async def run(agent, payload, **options):
            observations.append(json.loads(payload))
            answer = SimpleNamespace(cited_section_ids=[citation], insufficient_evidence=False)
            answer.model_dump = lambda: {'answer': 'Offline injected response',
                                         'cited_section_ids': [citation],
                                         'insufficient_evidence': False}
            return SimpleNamespace(final_output=answer)

        module.Runner = SimpleNamespace(run=run)
        module.RunConfig = lambda **options: options
        return module

    def test_live_service_routes_selected_sections_to_injected_runner(self):
        sections = [dict(id='reviewed-cafe', title='Café reporting', text='Reviewed synthetic café pipeline.', approved=True),
                    dict(id='unreviewed', title='Café secret', text='Unapproved synthetic café detail.', approved=False)]
        service = TwinService(sections, Settings(':memory:', live_model_enabled=True, model='offline-double'))
        observations = []
        with patch.dict(sys.modules, {'agents': self.fake_sdk('reviewed-cafe', observations)}), \
                patch.object(agents_adapter, 'build_agent', return_value=object()), \
                patch.object(agents_adapter, 'load_profile_sections', side_effect=AssertionError('must not reload the starter')):
            response = asyncio.run(service.answer_with_model('offline', 'Café reporting'))
        expected = service.answer('baseline', 'Café reporting')['citations']
        self.assertEqual(response['model_answer']['cited_section_ids'], expected)
        self.assertEqual([section['section_id'] for section in observations[0]['evidence']], ['reviewed-cafe'])

    def test_explicit_empty_sections_do_not_fall_back_to_starter(self):
        observations = []
        with patch.dict(sys.modules, {'agents': self.fake_sdk('profile-01', observations)}), \
                patch.object(agents_adapter, 'build_agent') as build:
            response = asyncio.run(agents_adapter.answer('Python experience', 'offline-double', sections=[]))
        self.assertEqual(response['status'], 'insufficient_evidence')
        self.assertEqual(observations, [])
        build.assert_not_called()

    def test_direct_adapter_retains_default_starter_with_injected_runner(self):
        observations = []
        with patch.dict(sys.modules, {'agents': self.fake_sdk('profile-01', observations)}), \
                patch.object(agents_adapter, 'build_agent', return_value=object()):
            response = asyncio.run(agents_adapter.answer('Python experience', 'offline-double'))
        self.assertEqual(response['model_answer']['cited_section_ids'], ['profile-01'])

    def test_cli_accepts_reviewed_profile_and_flag_overrides_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / 'sections-reviewed.json'
            profile.write_text(json.dumps([dict(id='local-review', title='Robotics',
                                                text='Synthetic robotics practice.', approved=True)]), encoding='utf-8')
            for arguments, selected in [(['--profile', str(profile)], 'missing-profile.json'),
                                        ([], str(profile))]:
                environment = {**os.environ, 'TWIN_PROFILE': selected, 'PYTHONDONTWRITEBYTECODE': '1'}
                result = subprocess.run([sys.executable, '-B', str(PROJECT / 'twin.py'),
                                         *arguments, 'Robotics'], cwd=ROOT, env=environment,
                                        capture_output=True, text=True, check=True)
                response = json.loads(result.stdout)
                self.assertEqual(response['citations'], ['local-review'])

    def test_pdf_cli_requires_an_explicit_output_destination(self):
        result = subprocess.run([sys.executable, '-B', str(PROJECT / 'make_pdf_fixture.py'),
                                 '--font', 'unused-font.ttf'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--output-dir', result.stderr)

    def test_pdf_generator_keeps_existing_output_without_generating(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'existing'
            destination.mkdir()
            retained = destination / 'retained.txt'
            retained.write_text('retained', encoding='utf-8')
            font = Path(directory) / 'fixture-font.ttf'
            font.write_bytes(b'not a real font; the writer must never run')
            with patch.object(make_pdf_fixture, '_write_unicode_pdf') as writer:
                with self.assertRaises(FileExistsError):
                    make_pdf_fixture.generate_documents(destination, font)
            writer.assert_not_called()
            self.assertEqual(retained.read_text(encoding='utf-8'), 'retained')

    def test_evaluation_keeps_24_cases_and_package_parity(self):
        source = (PROJECT / 'data/evaluation/professional-questions.jsonl').read_bytes()
        self.assertEqual(source, (PROJECT / 'twin_data/professional-questions.jsonl').read_bytes())
        self.assertEqual((PROJECT / 'fixtures/profile.json').read_bytes(), (PROJECT / 'twin_data/profile.json').read_bytes())
        cases = [json.loads(line) for line in source.decode('utf-8').splitlines()]
        self.assertEqual(cases[6]['question'], 'Has Amara won a national award?')
        self.assertEqual(cases[7]['question'], "What is Amara's salary?")
        report = evaluate_cases()
        self.assertEqual(report['total'], 24)
        self.assertEqual(report['failures'], [])
        self.assertIn('NOT_EVALUATED', report['modelQuality'])

    def test_existing_successful_pdf_bytes_are_unchanged(self):
        expected = {
            'fixtures/generated/synthetic-resume.pdf': '50158dc52b680e54ea4c1db5909644268c022eabc955b5ee07cb86e4bbb27544',
            'fixtures/generated/synthetic-portfolio.pdf': 'ad562d3c3264e97cd51fcde62cc0aca3e388696b5b1f0eff456f39e01b2fcd7f',
            'fixtures/synthetic-resume.pdf': '4927b8eae4dea95165c052ac7a4cbf5db935dba4d3068b65798f4625e3af8c20',
        }
        for relative, digest in expected.items():
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((PROJECT / relative).read_bytes()).hexdigest(), digest)

    def test_worked_solution_outputs_match_documented_results(self):
        readme = (PROJECT / 'README.md').read_text(encoding='utf-8')
        example = re.search(r'```python\n(.*?)\n```', readme, re.DOTALL).group(1)
        with patch.object(sys, 'path', list(sys.path)), contextlib.redirect_stdout(io.StringIO()) as output:
            exec(compile(example, 'README worked solution', 'exec'), {})
        self.assertEqual(output.getvalue().splitlines(),
                         ["['ok', 'rejected', 'ok']", '1', 'True stored_locally pending'])

    def test_project_guides_use_local_paths_without_production_gates(self):
        deployment = (PROJECT / 'docs/deploy.md').read_text(encoding='utf-8')
        self.assertLess(deployment.index('cd projects/01-digital-twin'),
                        deployment.index('docker build -t academy-twin .'))
        ingestion = (PROJECT / 'docs/ingestion.md').read_text(encoding='utf-8')
        self.assertNotIn('--output-dir projects/01-digital-twin/fixtures/generated', ingestion)
        guides = [PROJECT / 'README.md', *sorted((PROJECT / 'docs').glob('*.md')),
                  PROJECT / 'fixtures/document-provenance.json']
        for guide in guides:
            text = guide.read_text(encoding='utf-8')
            with self.subTest(path=guide.name):
                for marker in ('Central QA', '/var/lib/trejj-studio', 'resource guard', 'downstream lesson/visual'):
                    self.assertNotIn(marker, text)


if __name__ == '__main__':
    unittest.main()
