"""Authored bridge tests, pending central execution. All model/tool data are doubles."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]/'projects/05-sandboxed-engineering/learning'
sys.path.insert(0,str(BASE))
try:
    spec=importlib.util.spec_from_file_location('eca_whole_team_delivery',BASE/'delivery_package.py')
    package=importlib.util.module_from_spec(spec);sys.modules[spec.name]=package;spec.loader.exec_module(package)
finally:sys.path.pop(0)
from test_engineering_semantic_team import team,ProviderDouble,ExecutorDouble,GOOD

class WholeTeamDeliveryTests(unittest.TestCase):
    def fixture(self,root):
        evidence=root/'evidence';evidence.mkdir()
        result=team.run_team(ProviderDouble(initial=GOOD),ExecutorDouble(),team.EvidenceStore(evidence),
            {'title':'Explicit package fixture','product_request':'Sum nonnegative integer minor units'},allow_offline=True)
        return result,evidence
    def rewrite_completion(self,evidence,result):
        paths=list(evidence.glob('*-completion.json'));self.assertEqual(len(paths),1)
        paths[0].write_text(json.dumps(result))
    def test_fixture_default_rejected_never_promoted_to_actual(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root)
            with self.assertRaises(ValueError):package.package_delivery(result,root/'delivery.zip',evidence)
            self.assertFalse((root/'delivery.zip').exists())
    def test_exact_generated_source_artifacts_and_receipts_are_packaged(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root)
            receipt=package.package_delivery(result,root/'delivery.zip',evidence,allow_offline_fixture=True)
            self.assertEqual(receipt['manifest']['deliveryStatus'],'OFFLINE_FIXTURE_NOT_PRODUCTION')
            self.assertTrue(receipt['independentAcceptanceRequired'])
            with zipfile.ZipFile(root/'delivery.zip') as archive:
                self.assertIsNone(archive.testzip())
                for name,body in result['files'].items():self.assertEqual(archive.read(name),body.encode())
                self.assertEqual(json.loads(archive.read('.eca/whole-team-result.json')),result)
                self.assertEqual(archive.read('test_course_acceptance.py'),team.ACCEPTANCE_TESTS.encode())
                self.assertEqual(archive.read('test_independent_qa.py'),result['artifacts']['qa_plan']['content']['tests'].encode())
    def test_changed_result_missing_or_symlink_completion_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root)
            result['files']['README.md']+='tampered'
            with self.assertRaises(ValueError):package.package_delivery(result,root/'delivery.zip',evidence,True)
            original=next(evidence.glob('*-completion.json'));backup=root/'completion.json';original.rename(backup)
            original.symlink_to(backup)
            with self.assertRaises((ValueError,OSError)):package.package_delivery(result,root/'delivery.zip',evidence,True)
    def test_failed_receipt_cannot_be_packaged_by_claiming_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root)
            final=result['attempts'][-1]['receipt'];final['returncode']=1
            result['attempts'][-1]['receipt_sha256']=team.sha(final)
            self.rewrite_completion(evidence,result)
            with self.assertRaises(ValueError):package.package_delivery(result,root/'delivery.zip',evidence,True)
    def test_path_escape_extra_file_and_corrupt_lineage_are_rejected(self):
        for change in [lambda r:r['files'].update({'../escape.py':'pass'}),
                       lambda r:r['calls'][0].update(response_sha256='f'*64)]:
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory);result,evidence=self.fixture(root);change(result);self.rewrite_completion(evidence,result)
                with self.assertRaises(ValueError):package.package_delivery(result,root/'delivery.zip',evidence,True)
    def test_existing_destination_and_racing_writer_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root);destination=root/'delivery.zip'
            destination.write_bytes(b'original')
            with self.assertRaises(FileExistsError):package.package_delivery(result,destination,evidence,True)
            self.assertEqual(destination.read_bytes(),b'original');destination.unlink()
            with patch.object(package.os,'link',side_effect=FileExistsError('concurrent writer')):
                with self.assertRaises(FileExistsError):package.package_delivery(result,destination,evidence,True)
            self.assertFalse(list(root.glob('.eca-delivery-*')))
    def test_archive_quota_holds_without_partial_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root)
            with patch.object(package,'MAX_ARCHIVE_BYTES',1):
                with self.assertRaises(ValueError):package.package_delivery(result,root/'delivery.zip',evidence,True)
            self.assertFalse((root/'delivery.zip').exists());self.assertFalse(list(root.glob('.eca-delivery-*')))
    def test_host_delivery_binding_rejects_a_changed_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);result,evidence=self.fixture(root)
            receipt=package.package_delivery(result,root/'delivery.zip',evidence,True)
            (root/'delivery-receipt.json').write_text(json.dumps(receipt))
            spec=importlib.util.spec_from_file_location('eca_delivery_host_boundary',BASE/'container_launch.py')
            launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
            with self.assertRaises(ValueError):launcher.verified_delivery(root,result)
            verified=launcher.verified_delivery(root,result,allow_offline_fixture=True)
            self.assertEqual(verified['archiveSha256'],receipt['archiveSha256'])
            (root/'delivery.zip').write_bytes(b'changed')
            with self.assertRaises(ValueError):launcher.verified_delivery(root,result,allow_offline_fixture=True)
if __name__=='__main__':unittest.main()
