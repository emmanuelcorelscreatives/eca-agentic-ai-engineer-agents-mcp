"""Authored Stage 19 checks. SDK/browser tests require explicit central-QA opt-in.

Scripted SDK model responses test framework contracts, never provider intelligence.
No test here contacts a model endpoint. Actual provider CLI is separate.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from examples.s19.native_harness import (
    EvidenceStore, SourceEvidence, artifact_hashes, canonical_sha, install_skills,
    run_phase, source_manifest,
)


class ContractTests(unittest.TestCase):
    def test_source_manifest_binds_all_html(self):
        manifest = source_manifest()
        self.assertEqual(set(manifest), {'index.html', 'docs.html', 'form.html'})
        self.assertTrue(all(len(x) == 64 for x in manifest.values()))

    def test_budget_failure_and_unknown_are_charged_durably(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, 'evidence.sqlite')
            store = EvidenceStore(path, budget=2)
            with store.call('first') as output:
                output.update(observed=True)
            with self.assertRaises(ValueError), store.call('second'):
                raise ValueError('deliberate actual failure')
            with self.assertRaises(RuntimeError), EvidenceStore(path, budget=2).call('third'):
                pass
            self.assertEqual(len(store.rows()), 2)
            self.assertEqual(store.rows()[1]['error'], 'ValueError')

    def test_native_skill_layout_and_artifact_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            install_skills(tmp)
            before = artifact_hashes(tmp)
            path = Path(tmp, 'skills/source-research/SKILL.md')
            self.assertTrue(path.read_text().startswith('---\nname: source-research\n'))
            path.write_text(path.read_text() + 'changed')
            self.assertNotEqual(before, artifact_hashes(tmp))

    def test_evidence_origin_not_fixture_model_claim(self):
        value = SourceEvidence('http://127.0.0.1:123/docs.html', 'Title', [], 'f' * 64)
        self.assertEqual(value.observation, 'actual-playwright-owned-fixture')
        self.assertEqual(canonical_sha({'b': 2, 'a': 1}), canonical_sha({'a': 1, 'b': 2}))

    def test_symlink_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'link').symlink_to('/etc/hostname')
            with self.assertRaises(ValueError):
                artifact_hashes(tmp)


@unittest.skipUnless(os.getenv('RUN_S19_NATIVE_SDK') == '1', 'central QA must authorize SDK/browser execution')
class ActualNativeSDKTests(unittest.TestCase):
    def test_distinct_process_checkpoint_resume_no_provider(self):
        """Actual Deep Agents, browser, skills, task, SQLite; scripted model content."""
        repository_root = Path(__file__).resolve().parents[1]
        # Direct script execution otherwise puts only tests/ on sys.path.
        # Replace PYTHONPATH for this child only; never append inherited paths
        # or alter the parent environment or interpreter-wide import search.
        child_env = dict(os.environ)
        child_env['PYTHONPATH'] = str(repository_root)
        with tempfile.TemporaryDirectory() as tmp:
            for phase in ('start', 'resume'):
                completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                    '--sdk-worker', phase, tmp], cwd=repository_root, env=child_env,
                    capture_output=True, text=True, timeout=90)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                result = json.loads(Path(tmp, 'run.json').read_text())
                self.assertEqual(result['phase'], 'interrupted' if phase == 'start' else 'finished')
                if phase == 'start':
                    first_pid = result['process_id']
                    checkpoint = result['checkpoint']
                    self.assertTrue(result['evaluation']['planned'])
                else:
                    self.assertNotEqual(first_pid, result['process_id'])
                    self.assertNotEqual(checkpoint, result['checkpoint'])
                    for key in ('native_delegation_requested', 'search_observed',
                                'strict_docs_observed', 'matching_skill_read_requested', 'report_exists'):
                        self.assertTrue(result['evaluation'][key], key)
                    self.assertFalse(result['evaluation']['unrelated_skill_read_requested'])
                    self.assertEqual(result['evaluation']['failed_or_unknown_browser_calls'], [])

    def test_explicit_native_todos_persist_through_tools_writer_without_model(self):
        """Actual tool/state contracts; no model, browser, or graph.invoke."""
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain.agents.middleware.todo import write_todos
        from langgraph.checkpoint.sqlite import SqliteSaver
        from langgraph.types import Command
        from pydantic import PrivateAttr
        from examples.s19.native_harness import create_native_agent

        class NeverInvokedModel(BaseChatModel):
            model_name: str = 'synthetic-no-inference-planning-contract'
            _calls: int = PrivateAttr(default=0)
            @property
            def _llm_type(self):
                return 'synthetic-no-inference'
            def bind_tools(self, tools, **kwargs):
                return self
            def _generate(self, *args, **kwargs):
                self._calls += 1
                raise AssertionError('Planning persistence must not invoke a model')

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / 'workspace'
            workspace.mkdir()
            install_skills(workspace)
            ledger = EvidenceStore(root / 'evidence.sqlite')
            config = {'configurable': {'thread_id': 'synthetic-direct-todo-contract'}}
            planned = [{'content': 'Inspect the owned source', 'status': 'in_progress'},
                       {'content': 'Compare observed evidence', 'status': 'pending'}]
            command = write_todos.invoke({'name': 'write_todos', 'args': {'todos': planned},
                                          'id': 'synthetic-direct-plan', 'type': 'tool_call'})
            self.assertIsInstance(command, Command)
            self.assertEqual(command.update['todos'], planned)
            database = str(root / 'state.sqlite')
            first_model = NeverInvokedModel()
            with SqliteSaver.from_conn_string(database) as saver:
                graph = create_native_agent(first_model, 'http://127.0.0.1:1', workspace, saver, ledger)
                self.assertIn('todos', graph.channels)
                self.assertIn('tools', graph.get_graph().nodes)
                # The native tool Command is a tools-node write, not fresh input.
                graph.update_state(config, command.update, as_node='tools')
                snapshot = graph.get_state(config)
                self.assertEqual(snapshot.values['todos'], planned)
                checkpoint_id = snapshot.config['configurable']['checkpoint_id']
                self.assertTrue(checkpoint_id)
                self.assertEqual(first_model._calls, 0)
            reopened_model = NeverInvokedModel()
            with SqliteSaver.from_conn_string(database) as saver:
                graph = create_native_agent(reopened_model, 'http://127.0.0.1:1', workspace, saver, ledger)
                snapshot = graph.get_state(config)
                self.assertEqual(snapshot.values['todos'], planned)
                self.assertEqual(snapshot.config['configurable']['checkpoint_id'], checkpoint_id)
                self.assertEqual(reopened_model._calls, 0)
            self.assertEqual(ledger.rows(), [])

    def test_changed_source_blocks_resume_before_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            # State is created by actual native invocation, not a forged checkpoint file.
            run_phase(scripted_model(), tmp, 'start')
            with patch('examples.s19.native_harness.source_manifest', return_value={'changed': 'new'}):
                with self.assertRaisesRegex(ValueError, 'source/thread/budget changed'):
                    run_phase(scripted_model(resume=True), tmp, 'resume')

    def test_actual_browser_origin_rejection(self):
        from examples.s19.native_harness import browser_tools
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                browser_tools('https://example.com', EvidenceStore(Path(tmp, 'ledger.sqlite')))


def scripted_model(resume=False):
    """Actual BaseChatModel protocol with explicitly scripted, deterministic responses."""
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from pydantic import PrivateAttr

    def call(name, args, number):
        return AIMessage(content='', tool_calls=[{'name': name, 'args': args, 'id': f's19-call-{number}', 'type': 'tool_call'}])

    steps = [AIMessage(content='Scripted continuation complete; not a provider observation.')] if resume else [
        call('write_todos', {'todos': [{'content': 'Research owned source, compare, save evidence', 'status': 'in_progress'}]}, 0),
        call('task', {'subagent_type': 'source-researcher', 'description': 'Inspect /docs.html and return exact observed records.'}, 1),
        call('inspect_owned_page', {'path': '/docs.html'}, 2),
        AIMessage(content='Scripted source summary; consult actual tool records in evidence ledger.'),
        call('task', {'subagent_type': 'evidence-critic', 'description': 'Inspect /docs.html independently and check version claims.'}, 4),
        call('inspect_owned_page', {'path': '/docs.html'}, 5),
        AIMessage(content='Scripted critic summary; actual browser records are retained separately.'),
        call('search_owned_docs', {'query': 'Documentation'}, 7),
        call('read_file', {'file_path': '/skills/source-research/SKILL.md'}, 8),
        call('write_file', {'file_path': '/research.md', 'content': 'Scripted orchestration notes. See actual browser evidence ledger.'}, 9),
        call('write_file', {'file_path': '/report.md', 'content': 'Scripted deterministic contract report. Not provider intelligence or factual approval.'}, 10),
        call('review_checkpoint', {'note': 'Contract run pauses at real native HITL.'}, 11),
        AIMessage(content='Scripted final response after continuation.'),
    ]

    class ScriptedChat(BaseChatModel):
        _position: int = PrivateAttr(default=0)
        model_name: str = 'explicit-scripted-contract-model'

        @property
        def _llm_type(self):
            return 'stage19-scripted-contract'

        def bind_tools(self, tools, **kwargs):
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            if 'CALENDAR_BODY_SENTINEL_19' in str(messages):
                raise AssertionError('nonmatching native skill body leaked into model context')
            if self._position >= len(steps):
                raise RuntimeError('script exhausted; never synthesize an approval')
            message = steps[self._position]
            self._position += 1
            return ChatResult(generations=[ChatGeneration(message=message)])

    return ScriptedChat()


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--sdk-worker':
        phase, root = sys.argv[2:]
        run_phase(scripted_model(resume=phase == 'resume'), root, phase)
    else:
        unittest.main()
