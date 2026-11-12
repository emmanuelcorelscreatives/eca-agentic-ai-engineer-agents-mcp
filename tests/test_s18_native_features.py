"""Opt-in genuine native SDK tests; deterministic fixtures, zero provider calls.

Authoring is not a test receipt. The central QA owner must actually execute:
  COURSE_SDK_OFFLINE=1 <pinned-python> -m unittest discover -s tests -p test_s18_native_features.py -v
The subprocess tests deliberately reuse the SAME installed Python interpreter.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('COURSE_SDK_OFFLINE') == '1',
                     'Genuine installed LangGraph/SQLite execution is explicitly opt-in')
class NativeDurability(unittest.TestCase):
    def setUp(self):
        from examples.s18 import native_durability as native
        from langchain_core.messages import HumanMessage
        from langgraph.types import Command
        self.native, self.HumanMessage, self.Command = native, HumanMessage, Command
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'checkpoints.sqlite'
        self.ledger_path = Path(self.temp.name) / 'effects.sqlite'
        self.cfg = native.thread_config('academy-A')

    def tearDown(self):
        self.temp.cleanup()

    def graph(self, mode='conversation'):
        return self.native.sqlite_graph(self.database, self.ledger_path, mode=mode)

    def ledger(self):
        return self.native.MockLedger(self.ledger_path)

    def human(self, content, identifier):
        return self.HumanMessage(content=content, id=identifier)

    def proposal(self, identifier='action-original', text='reviewed fixture document'):
        return {'action_id': identifier, 'recipient': 'academy-fixture', 'text': text}

    def decision(self, proposal, kind='approve', edited=None):
        decision = {'decision': kind, 'reviewer': 'academy-fixture-reviewer',
                    'proposal_sha256': self.native.digest(proposal)}
        if edited is not None:
            decision['edited'] = edited
        return self.Command(resume=decision)

    def process(self, *arguments, okay=True):
        process = subprocess.run(
            [sys.executable, '-m', 'examples.s18.native_durability', str(self.database),
             str(self.ledger_path), *arguments], cwd=ROOT,
            capture_output=True, text=True, timeout=45)
        if okay:
            self.assertEqual(process.returncode, 0, process.stderr)
            return json.loads(process.stdout)
        self.assertNotEqual(process.returncode, 0, process.stdout)
        return process

    def test_native_messages_append_replace_and_reopen(self):
        with self.graph() as graph:
            graph.invoke({'messages': [self.human('private first turn', 'user-1')]}, self.cfg)
            result = graph.invoke({'messages': [self.human('second turn', 'user-2')]}, self.cfg)
            self.assertEqual(len(result['messages']), 4)
            self.assertIn('user turns: 2', result['response'])
            original_response_id = result['messages'][1].id
            original_response_content = result['messages'][1].content
            # add_messages replaces an existing ID; it must not append a third user turn.
            graph.update_state(self.cfg, {'messages': [self.human('corrected first turn', 'user-1')]},
                               as_node='respond')
        with self.graph() as reopened:
            state = reopened.get_state(self.cfg)
            self.assertEqual(len(state.values['messages']), 4)
            self.assertEqual(state.values['messages'][0].content, 'corrected first turn')
            self.assertEqual(state.values['messages'][1].id, original_response_id)
            replaced = [message for message in state.values['messages'] if message.id == 'user-1']
            self.assertEqual(len(replaced), 1)
            self.assertIsInstance(replaced[0], self.HumanMessage)
            self.assertEqual(replaced[0].content, 'corrected first turn')
            # Replacement applies to this ID only, not erasure of retained history.
            # The earlier AI quotation remains a truthful record of that old turn.
            self.assertIn('private first turn', original_response_content)
            self.assertEqual(state.values['messages'][1].content, original_response_content)

    def test_real_separate_process_restart_and_private_threads(self):
        first = self.process('academy-A', '--message', 'A-private-sentinel', '--message-id', 'a-1')
        other = self.process('academy-B', '--message', 'B-private-sentinel', '--message-id', 'b-1')
        later = self.process('academy-A', '--message', 'A-followup', '--message-id', 'a-2')
        self.assertNotEqual(first['checkpoint_id'], later['checkpoint_id'])
        self.assertEqual(len(later['messages']), 4)
        self.assertIn('A-private-sentinel', json.dumps(later['messages']))
        self.assertNotIn('B-private-sentinel', json.dumps(later))
        self.assertNotIn('A-private-sentinel', json.dumps(other))
        with self.graph() as graph:
            b = graph.get_state(self.native.thread_config('academy-B'))
            self.assertEqual(len(b.values['messages']), 2)
            self.assertNotIn('A-followup', str(b.values))

    def test_missing_thread_and_missing_user_message_fail(self):
        for bad in ['', ' ', None, 7]:
            with self.assertRaises(ValueError):
                self.native.thread_config(bad)
        with self.graph() as graph:
            with self.assertRaises(ValueError):
                graph.invoke({'messages': [self.human('input', 'one')]}, {})
            with self.assertRaises(ValueError):
                graph.invoke({'messages': []}, self.cfg)

    def test_genuine_historical_replay_executes_node_and_fork_preserves_origin(self):
        with self.graph() as graph:
            original = graph.invoke({'messages': [self.human('original route', 'turn-1')]}, self.cfg)
            history = list(graph.get_state_history(self.cfg))
            selected = next(item for item in history if item.next == ('respond',))
            frozen_values = json.dumps(selected.values, default=lambda v: v.model_dump(), sort_keys=True)
            frozen_id = selected.config['configurable']['checkpoint_id']
            before = len([e for e in self.ledger().observations('academy-A') if e['node'] == 'respond'])
            replay = graph.invoke(None, selected.config)  # Native replay, not copying saved values.
            replay_snapshot = graph.get_state(self.cfg)
            self.assertEqual(replay['response'], original['response'])
            self.assertNotEqual(replay_snapshot.config['configurable']['checkpoint_id'], frozen_id)
            after = len([e for e in self.ledger().observations('academy-A') if e['node'] == 'respond'])
            self.assertEqual(after, before + 1)
            fork_config = graph.update_state(selected.config,
                {'request': 'alternative route',
                 'messages': [self.human('alternative route', 'turn-1')]}, as_node='prepare')
            self.assertNotEqual(fork_config['configurable']['checkpoint_id'], frozen_id)
            fork_state = graph.get_state(fork_config)
            self.assertEqual(fork_state.parent_config['configurable']['checkpoint_id'], frozen_id)
            fork = graph.invoke(None, fork_config)
            self.assertIn('alternative route', fork['response'])
            self.assertNotEqual(fork['response'], replay['response'])
            # Historical origins remain readable byte-for-byte after BOTH continuations.
            self.assertEqual(json.dumps(graph.get_state(selected.config).values,
                default=lambda v: v.model_dump(), sort_keys=True), frozen_values)
            self.assertEqual(graph.get_state(replay_snapshot.config).values['response'], replay['response'])

    def test_interrupt_reject_never_dispatches(self):
        proposal = self.proposal()
        with self.graph('review') as graph:
            paused = graph.invoke({'proposal': proposal}, self.cfg)
            self.assertEqual(paused['__interrupt__'][0].value['proposal_sha256'], self.native.digest(proposal))
            self.assertEqual(self.ledger().effects('academy-A'), [])
        with self.graph('review') as reopened:
            result = reopened.invoke(self.decision(proposal, 'reject'), self.cfg)
            self.assertEqual(result['decision'], 'reject')
            self.assertEqual(reopened.get_state(self.cfg).next, ())
            self.assertEqual(self.ledger().effects('academy-A'), [])

    def test_approval_dispatch_once_and_native_replay_deduplicates(self):
        proposal = self.proposal()
        with self.graph('review') as graph:
            graph.invoke({'proposal': proposal}, self.cfg)
            self.assertEqual(self.ledger().effects('academy-A'), [])
            result = graph.invoke(self.decision(proposal), self.cfg)
            self.assertEqual(result['progress'], 'delivered')
            self.assertEqual(len(self.ledger().effects('academy-A')), 1)
            before_dispatch = next(item for item in graph.get_state_history(self.cfg)
                                   if item.next == ('dispatch',))
            replayed = graph.invoke(None, before_dispatch.config)
            self.assertEqual(replayed['progress'], 'deduplicated')
            self.assertEqual(len(self.ledger().effects('academy-A')), 1)

    def test_edit_requires_a_new_exact_approval_and_old_approval_is_stale(self):
        original, edited = self.proposal(), self.proposal('action-edited', 'changed document')
        with self.graph('review') as graph:
            graph.invoke({'proposal': original}, self.cfg)
            paused_again = graph.invoke(self.decision(original, 'edit', edited), self.cfg)
            self.assertEqual(paused_again['proposal'], edited)
            self.assertEqual(paused_again['approved_sha256'], '')
            self.assertEqual(paused_again['__interrupt__'][0].value['proposal_sha256'], self.native.digest(edited))
            self.assertEqual(self.ledger().effects('academy-A'), [])
            with self.assertRaises(ValueError):
                graph.invoke(self.decision(original), self.cfg)
            self.assertEqual(self.ledger().effects('academy-A'), [])
        # A separate thread proves successful new approval without relying on how
        # a failed resume is retained by the installed LangGraph version.
        second_cfg = self.native.thread_config('academy-edited-approved')
        with self.graph('review') as graph:
            graph.invoke({'proposal': original}, second_cfg)
            graph.invoke(self.decision(original, 'edit', edited), second_cfg)
            result = graph.invoke(self.decision(edited), second_cfg)
            self.assertEqual(result['progress'], 'delivered')
            delivered = self.ledger().effects('academy-edited-approved')
            self.assertEqual(len(delivered), 1)
            self.assertEqual(json.loads(delivered[0]['payload']), edited)

    def test_reviewer_payload_and_edit_schema_negatives(self):
        for index, patch in enumerate([
            {'reviewer': 'model'}, {'proposal_sha256': 'stale'},
            {'decision': 'maybe'}, {'unexpected': True}]):
            cfg = self.native.thread_config(f'invalid-{index}')
            proposal = self.proposal()
            with self.graph('review') as graph:
                graph.invoke({'proposal': proposal}, cfg)
                value = {'decision': 'approve', 'reviewer': 'academy-fixture-reviewer',
                         'proposal_sha256': self.native.digest(proposal)} | patch
                with self.assertRaises(ValueError):
                    graph.invoke(self.Command(resume=value), cfg)
                self.assertEqual(self.ledger().effects(f'invalid-{index}'), [])
        with self.assertRaises(ValueError):
            self.native.checked_proposal(self.proposal() | {'recipient': 'real-person'})
        with self.assertRaises(ValueError):
            self.native.checked_proposal(self.proposal() | {'text': 'x' * 4001})

    def test_separate_process_failure_resume_does_not_repeat_completed_steps(self):
        failed = self.process('recover-A', '--mode', 'recovery', '--run-id', 'run-1',
                              '--failure', 'once', okay=False)
        self.assertIn('InterruptedError', failed.stderr)
        ledger = self.ledger()
        self.assertEqual([row['action_id'] for row in ledger.effects('recover-A')], ['run-1-first'])
        with self.graph('recovery') as graph:
            state = graph.get_state(self.native.thread_config('recover-A'))
            self.assertEqual(state.values['progress'], 'first-done')
            self.assertEqual(state.next, ('second',))
            checkpoint_before = state.config['configurable']['checkpoint_id']
        completed = self.process('recover-A', '--mode', 'recovery', '--resume')
        self.assertEqual(completed['progress'], 'complete:delivered')
        self.assertNotEqual(completed['checkpoint_id'], checkpoint_before)
        self.assertEqual(len(ledger.effects('recover-A')), 2)
        observations = ledger.observations('recover-A')
        self.assertEqual(sum(row['node'] == 'validate' for row in observations), 1)
        self.assertEqual(sum(row['node'] == 'first' for row in observations), 1)
        self.assertEqual(sum(row['node'] == 'second-enter' for row in observations), 2)

    def test_uncertain_effect_is_not_redispatched_after_process_restart(self):
        first = self.process('uncertain-A', '--mode', 'recovery', '--run-id', 'run-unknown',
                             '--failure', 'unknown', okay=False)
        self.assertIn('UncertainOutcome', first.stderr)
        before = self.ledger().effects('uncertain-A')
        self.assertEqual(len(before), 2)
        self.assertEqual([r['status'] for r in before], ['done', 'uncertain'])
        again = self.process('uncertain-A', '--mode', 'recovery', '--resume', okay=False)
        self.assertIn('replay prohibited', again.stderr)
        self.assertEqual(self.ledger().effects('uncertain-A'), before)
        with self.graph('recovery') as graph:
            self.assertEqual(graph.get_state(self.native.thread_config('uncertain-A')).next, ('second',))

    def test_terminal_validation_stays_terminal_and_idempotency_conflict_fails(self):
        self.process('invalid-A', '--mode', 'recovery', '--run-id', 'invalid-run',
                     '--failure', 'validation', okay=False)
        again = self.process('invalid-A', '--mode', 'recovery', '--resume', okay=False)
        self.assertIn('TerminalValidation', again.stderr)
        self.assertEqual(self.ledger().effects('invalid-A'), [])
        ledger = self.ledger()
        self.assertEqual(ledger.effect('local', self.proposal()), 'delivered')
        self.assertEqual(ledger.effect('local', self.proposal()), 'deduplicated')
        with self.assertRaises(ValueError):
            ledger.effect('local', self.proposal(text='conflicting payload'))
        with self.assertRaises(ValueError):
            with self.native.sqlite_graph(self.database, self.database):
                pass


if __name__ == '__main__':
    unittest.main()
