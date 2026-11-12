"""Author-only boundary tests. Central QA must run; no fake Docker PASS fixtures."""
import asyncio
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from advanced import sha
from docker_validate import plan
from docker_bridge import CentralDockerOwner,_read_tree

IMAGE='python@sha256:'+'a'*64

class DockerBridgeBoundaries(unittest.TestCase):
    def workspace(self,base):
        workspace=base/'workspace';workspace.mkdir()
        (workspace/'agent.py').write_text('answer=42\n')
        (workspace/'test_agent.py').write_text('import unittest\nclass Generated(unittest.TestCase):\n def test_one(self): self.assertTrue(True)\n')
        (workspace/'acceptance').mkdir()
        (workspace/'acceptance/test_contract.py').write_text('import unittest\nclass Independent(unittest.TestCase):\n def test_answer(self):\n  from agent import answer\n  self.assertEqual(answer,42)\n')
        artifacts,suite,_=_read_tree(workspace)
        return workspace,{'artifact_sha256':sha(artifacts),'acceptance_sha256':sha(suite)}
    def owner(self,base):
        root=base/'owner';root.mkdir(mode=0o700)
        key=base/'owner.key';key.write_bytes(b'not-a-production-key-for-offline-contract-test-only');key.chmod(0o600)
        return CentralDockerOwner(image=IMAGE,evidence_root=root,key_path=key,explicitly_authorized=True)
    def test_both_nonempty_suites_are_explicit_plans(self):
        with tempfile.TemporaryDirectory() as d:
            workspace,_=self.workspace(Path(d))
            generated=plan(workspace,IMAGE,suite='generated');independent=plan(workspace,IMAGE,suite='independent')
            self.assertIn('discover(\'/app\'',generated['command'][-1])
            self.assertIn('discover(\'/app/acceptance\'',independent['command'][-1])
            self.assertIn('count>0',independent['command'][-1])
            for p in (generated,independent):
                self.assertEqual(p['status'],'PLANNED_NOT_EXECUTED')
                self.assertIn('--network',p['command']);self.assertIn('none',p['command'])
                self.assertIn('--read-only',p['command']);self.assertIn('--pids-limit',p['command'])
                self.assertIn('--pull',p['command']);self.assertIn('never',p['command'])
    def test_missing_independent_suite_is_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);workspace,_=self.workspace(root)
            (workspace/'acceptance/test_contract.py').unlink()
            with self.assertRaises(ValueError):plan(workspace,IMAGE,suite='independent')
            with self.assertRaises(ValueError):_read_tree(workspace)
    def test_prepared_hash_must_match_actual_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);workspace,prepared=self.workspace(root);owner=self.owner(root)
            (workspace/'acceptance/test_contract.py').write_text('altered immutable suite')
            with self.assertRaises(ValueError):owner._context(workspace,prepared)
    def test_key_and_evidence_cannot_be_mounted_into_container(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);workspace,prepared=self.workspace(root);owner=self.owner(root)
            owner.key_path=workspace/'secret.key'
            with self.assertRaises(ValueError):owner._context(workspace,prepared)
    def test_boolean_fixture_or_self_hash_is_not_owner_execution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);workspace,prepared=self.workspace(root);owner=self.owner(root)
            receipt={'run_id':'1'*32,'kind':'docker-executed','passed':True,'artifact_sha256':prepared['artifact_sha256']}
            receipt['receipt_sha256']=sha(receipt)
            self.assertFalse(asyncio.run(owner.verify(workspace,prepared,receipt)))
            (owner.root/(receipt['run_id']+'.owner-receipt.json')).write_text(json.dumps({'signed':{'receipt':receipt},'owner_hmac_sha256':'0'*64}))
            self.assertFalse(asyncio.run(owner.verify(workspace,prepared,receipt)))
    def test_unknown_reservation_cannot_replay_even_after_workspace_move(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);workspace,prepared=self.workspace(root);owner=self.owner(root)
            with patch('docker_bridge.subprocess.run',side_effect=TimeoutError('simulated inspect interruption, no Docker run')) as transport:
                with self.assertRaises(TimeoutError):owner._execute(workspace,prepared)
                relocated=root/'relocated';workspace.rename(relocated)
                with self.assertRaises(FileExistsError):owner._execute(relocated,prepared)
                self.assertEqual(transport.call_count,1)
            reservations=list(owner.root.glob('once-*'))
            self.assertEqual(len(reservations),1)
            self.assertTrue((reservations[0]/'EXECUTION-UNKNOWN.json').is_file())
            self.assertFalse(list(owner.root.glob('*.owner-receipt.json')))
    def test_owner_key_requires_private_permissions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);owner=self.owner(root);owner.key_path.chmod(0o644)
            with self.assertRaises(PermissionError):CentralDockerOwner(image=IMAGE,evidence_root=owner.root,key_path=owner.key_path,explicitly_authorized=True)
    def test_infrastructure_exit_or_timeout_never_becomes_repair_receipt(self):
        # Negative boundary fixtures only; these never claim an executed Docker PASS.
        for kind in ('docker-infrastructure-failure','docker-runtime-unresolved'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as d:
                root=Path(d);workspace,prepared=self.workspace(root);owner=self.owner(root)
                inspected=SimpleNamespace(returncode=0,stdout=json.dumps({'RepoDigests':[IMAGE],'Id':'sha256:config'}),stderr='')
                negative={'kind':kind,'cleanup_returncode':0,'actually_started':kind=='docker-runtime-unresolved',
                          'suite_completed':False,'returncode':125,'passed':False}
                with patch('docker_bridge.subprocess.run',return_value=inspected),patch('docker_bridge.execute',return_value=negative) as runner:
                    with self.assertRaises(RuntimeError):owner._execute(workspace,prepared)
                    self.assertEqual(runner.call_count,1)
                self.assertFalse(list(owner.root.glob('*.owner-receipt.json')))
                self.assertEqual(len(list(owner.root.glob('once-*/generated-nonrepairable-outcome.json'))),1)

if __name__=='__main__':unittest.main()
