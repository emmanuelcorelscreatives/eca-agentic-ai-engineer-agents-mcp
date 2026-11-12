"""Authored boundary tests; central QA separately runs actual CrewAI SDK tests.

Importing the container entrypoint does not import or execute the lazy SDK.
These boundary tests never constitute evidence of CrewAI kickoff completion.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LEARNING = Path(__file__).resolve().parents[1] / 'projects/05-sandboxed-engineering/learning'
spec = importlib.util.spec_from_file_location('container_launch', LEARNING / 'container_launch.py')
launch = importlib.util.module_from_spec(spec)
sys.modules['container_launch'] = launch
spec.loader.exec_module(launch)
spec2 = importlib.util.spec_from_file_location('whole_entry', LEARNING / 'container_entrypoint.py')
entry = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(entry)


class WholeCrewContract(unittest.TestCase):
    def test_image_runtime_declares_required_sdk(self):
        import tomllib
        metadata = tomllib.loads((LEARNING / 'pyproject.toml').read_text())
        self.assertIn('crewai==1.15.40', metadata['project']['dependencies'])

    def test_digest_tag_refused(self):
        with self.assertRaises(ValueError): launch.docker_argv('python:3.12', '.', '.', 'bad')

    def test_canonical_hash_matches_semantic_unicode(self):
        spec = importlib.util.spec_from_file_location('semantic_team', LEARNING / 'semantic_team.py')
        team = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(team)
        import hashlib
        self.assertEqual(hashlib.sha256(launch.canonical({'text': 'café'})).hexdigest(), team.sha({'text': 'café'}))

    def test_json_exclusive_and_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'record.json'
            launch.write_json(path, {'one': 1})
            self.assertEqual(launch.read_json(path), {'one': 1})
            with self.assertRaises(FileExistsError): launch.write_json(path, {'one': 2})
            with self.assertRaises(ValueError): launch.write_json(Path(tmp) / 'large', 'x' * 1100000)

    def test_symlink_json_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'target').write_text('{}')
            (path / 'alias').symlink_to(path / 'target')
            with self.assertRaises(OSError): launch.read_json(path / 'alias')

    def test_json_short_writes_are_completed_before_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'record.json'
            original = launch.os.write
            def short_write(fd, raw):
                self.assertFalse(path.exists())
                return original(fd, raw[:3])
            with patch.object(launch.os, 'write', side_effect=short_write):
                launch.write_json(path, {'complete': 'record'})
            self.assertEqual(launch.read_json(path), {'complete': 'record'})
            self.assertEqual(list(Path(tmp).glob('.pending-*')), [])

    def test_json_failed_write_never_publishes_partial_or_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'record.json'
            with patch.object(launch.os, 'write', return_value=0):
                with self.assertRaises(OSError): launch.write_json(path, {'complete': 'record'})
            self.assertFalse(path.exists())
            self.assertEqual(list(Path(tmp).glob('.pending-*')), [])

    def test_json_parser_rejects_duplicate_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'record.json'
            for raw in ('{"role":"developer","role":"architect"}',
                        '{"a":{"key":1,"key":2}}', '{"value":NaN}',
                        '{"value":Infinity}', '{"value":-Infinity}', '{"value":1e999}'):
                path.write_text(raw)
                with self.assertRaises(ValueError): launch.read_json(path)

    def test_runtime_contains_no_network_or_socket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inputs, mailbox = root / 'inputs', root / 'mailbox'
            inputs.mkdir(); mailbox.mkdir()
            class SmallFS:
                f_blocks = 2048
                f_frsize = 4096
            with patch.object(launch.os, 'statvfs', return_value=SmallFS()):
                argv = launch.docker_argv('local/team@sha256:' + 'a' * 64, inputs, mailbox, 'eca-whole-' + 'b' * 32)
            self.assertIn('--network=none', argv)
            self.assertIn('--pull=never', argv)
            self.assertIn('--read-only', argv)
            self.assertNotIn('/var/run/docker.sock', ' '.join(argv))
            self.assertIn('--memory=768m', argv)

    def test_normal_disk_mailbox_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'inputs').mkdir(); (root / 'mailbox').mkdir()
            class LargeFS:
                f_blocks = 1000000
                f_frsize = 4096
            with patch.object(launch.os, 'statvfs', return_value=LargeFS()):
                with self.assertRaises(ValueError):
                    launch.docker_argv('local/team@sha256:' + 'a' * 64, root / 'inputs', root / 'mailbox', 'eca-whole-' + 'b' * 32)

    def test_provider_budget_cannot_be_expanded(self):
        with self.assertRaises(ValueError): entry.MailboxProvider(max_calls=10)

    def test_host_refuses_invalid_request_without_callback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch.write_json(root / 'request-01.json', {'schema': 1})
            callback = unittest.mock.Mock()
            broker = launch.HostBroker(root, callback)
            with self.assertRaises(ValueError): broker.poll()
            callback.assert_not_called()

    def test_provider_refuses_provenance_test_double(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provider = entry.MailboxProvider(root)
            payload = {'stage': 'requirements'}
            import hashlib
            request = {'schema': 1, 'role': 'product_manager', 'payload': payload,
                       'input_sha': hashlib.sha256(launch.canonical(payload)).hexdigest(), 'ordinal': 1}
            digest = hashlib.sha256(launch.canonical(request)).hexdigest()
            launch.write_json(root / 'response-01.json', {'request_sha': digest, 'response': {
                'role': 'product_manager', 'input_sha256': request['input_sha'], 'request_id': 'test',
                'model': 'fixture', 'raw': '{}', 'provenance': 'offline-test-double'}})
            with self.assertRaises(ValueError): provider.request('product_manager', payload)


if __name__ == '__main__': unittest.main()
