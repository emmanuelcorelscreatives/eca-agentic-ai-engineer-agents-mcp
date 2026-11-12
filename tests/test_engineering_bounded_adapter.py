"""Actual bounded-output subprocess checks; Docker operations are explicit mocks."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[1]/'projects/05-sandboxed-engineering'
def load(key,path):
    spec=importlib.util.spec_from_file_location(key,path)
    module=importlib.util.module_from_spec(spec);sys.modules[key]=module;spec.loader.exec_module(module)
    return module
sys.path.insert(0,str(BASE))
adapter=load('eca_bounded_live_adapter',BASE/'crewai_adapter.py')
sys.path.pop(0)
sandbox=load('eca_engineering_learning_sandbox_adapter',BASE/'learning/sandbox.py')
REAL_POPEN=subprocess.Popen
IMAGE='python@sha256:'+'a'*64

class BoundedAdapterTests(unittest.TestCase):
    def actual_process(self,code):
        def spawn(argv,**kwargs):
            self.assertIn('--log-driver=none',argv)
            self.assertIn('--network=none',argv)
            self.assertNotIn('shell',kwargs)
            return REAL_POPEN([sys.executable,'-c',code],**kwargs)
        return spawn
    def cleanup(self,argv,**kwargs):
        self.assertEqual(argv[:3],['docker','rm','-f'])
        self.assertRegex(argv[3],r'^eca-learning-[a-f0-9]{32}$')
        return subprocess.CompletedProcess(argv,0)
    def run_case(self,code,timeout=3):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'expense_app.py').write_text('# controlled fixture\n')
            with patch.object(sandbox.subprocess,'Popen',side_effect=self.actual_process(code)), \
                 patch.object(sandbox.subprocess,'run',side_effect=self.cleanup):
                return adapter.docker_qa(root,IMAGE,timeout)
    def test_actual_output_flood_is_capped_and_fails(self):
        result=self.run_case('import os\nwhile True: os.write(1,b"x"*4096)')
        self.assertFalse(result['passed'])
        self.assertTrue(result['truncated'])
        self.assertLessEqual(len(result['stdout'].encode()),16384)
        self.assertTrue(result['cleanup_confirmed'])
    def test_actual_small_output_observed_test_count_required(self):
        result=self.run_case('import sys;sys.stderr.write("Ran 6 tests in 0.01s\\nOK\\n")')
        self.assertTrue(result['passed'])
        self.assertEqual(result['acceptance_test_count'],6)
        result=self.run_case('print("model claims success")')
        self.assertFalse(result['passed'])
    def test_actual_timeout_is_failed_with_exact_cleanup(self):
        result=self.run_case('import time;time.sleep(5)',timeout=.1)
        self.assertFalse(result['passed'])
        self.assertTrue(result['timed_out'])
        self.assertTrue(result['cleanup_confirmed'])
    def test_symlink_file_rejected_before_chmod_or_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);outside=root/'outside';outside.mkdir();work=root/'work';work.mkdir()
            (outside/'secret').write_text('private');(work/'secret').symlink_to(outside/'secret')
            with self.assertRaises(ValueError):adapter.docker_qa(work,IMAGE)
            self.assertEqual((outside/'secret').stat().st_mode & 0o777,0o644)
if __name__=='__main__':unittest.main()
