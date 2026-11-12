import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); sys.modules[name]=module; spec.loader.exec_module(module); return module
side=load('academy_sidekick',ROOT/'projects/06-browser-sidekick/sidekick.py')
factory=load('academy_factory',ROOT/'projects/07-agent-factory/factory.py')

class SidekickTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.database=Path(self.temp.name)/'tasks.sqlite'
        self.store=side.TaskStore(self.database)
    def tearDown(self): self.store.close(); self.temp.cleanup()
    def test_real_fixture_extraction_survives_reopen(self):
        task=self.store.create('Find workshops',[side.Step('extract','workshops.html',criterion='dates present')])
        self.store.close(); self.store=side.TaskStore(self.database)
        self.assertEqual(self.store.advance(task,side.FixtureBrowser(ROOT/'projects/06-browser-sidekick/fixtures')),'step_complete')
        result=self.store.checklist(task)[0]['result']; self.assertIn('2030-04-12',result); self.assertIn('USD 45',result)
        self.assertEqual(self.store.advance(task,None),'complete')
    def test_approval_is_required_before_executor_invocation(self):
        class Never:
            def execute(self,step): raise AssertionError('must not run')
        task=self.store.create('Book',[side.Step('submit','booking',criterion='confirmation received')])
        self.assertEqual(self.store.advance(task,Never()),'awaiting_approval')
    def test_edit_revokes_approval(self):
        task=self.store.create('Send',[side.Step('message','support',value='hello',criterion='sent')])
        self.store.decide(task,0,'approve')
        self.store.decide(task,0,'edit',side.Step('message','another',value='changed',criterion='sent'))
        self.assertEqual(self.store.advance(task,None),'awaiting_approval')
    def test_approved_action_executes_exact_payload_once(self):
        calls=[]
        class Recorder:
            def execute(self,step): calls.append(step); return 'synthetic test adapter accepted'
        step=side.Step('submit','local-fixture',value='test',criterion='adapter confirms')
        task=self.store.create('Demo',[step]); self.store.decide(task,0,'approve')
        self.store.advance(task,Recorder()); self.store.advance(task,Recorder())
        self.assertEqual(calls,[step])
    def test_crashed_execution_is_not_replayed(self):
        task=self.store.create('Read',[side.Step('extract','workshops.html',criterion='read')])
        with self.store.db: self.store.db.execute("UPDATE step SET state='executing' WHERE task=?",(task,))
        self.assertEqual(self.store.advance(task,None),'executing')
    def test_rejection_stops_following_steps(self):
        task=self.store.create('Demo',[side.Step('message','a',criterion='sent'),side.Step('extract','b',criterion='read')])
        self.store.decide(task,0,'reject'); self.assertEqual(self.store.advance(task,None),'rejected')
    def test_fixture_path_escape_rejected(self):
        browser=side.FixtureBrowser(ROOT/'projects/06-browser-sidekick/fixtures')
        with self.assertRaises(ValueError): browser.execute(side.Step('extract','../../07-agent-factory/factory.py',criterion='read'))
    def test_external_browser_origin_rejected(self):
        with self.assertRaises(ValueError): side.PlaywrightBrowser('https://example.org')
    def test_empty_result_is_failed_not_complete(self):
        class Empty:
            def execute(self,step): return ''
        task=self.store.create('Read',[side.Step('extract','a',criterion='content')])
        with self.assertRaises(ValueError): self.store.advance(task,Empty())
        self.assertEqual(self.store.advance(task,None),'failed')
    def test_artifact_save_requires_approval_and_refuses_overwrite(self):
        writer=side.ArtifactTools(None,Path(self.temp.name)/'artifacts')
        step=side.Step('save','finding.txt',value='Synthetic workshop finding',criterion='file saved')
        task=self.store.create('Save',[step])
        self.assertEqual(self.store.advance(task,writer),'awaiting_approval')
        self.assertFalse((Path(self.temp.name)/'artifacts/finding.txt').exists())
        self.store.decide(task,0,'approve'); self.store.advance(task,writer)
        self.assertEqual((Path(self.temp.name)/'artifacts/finding.txt').read_text(),step.value)
        with self.assertRaises(FileExistsError): writer.execute(step)
    def test_artifact_escape_rejected(self):
        writer=side.ArtifactTools(None,Path(self.temp.name)/'artifacts')
        with self.assertRaises(ValueError): writer.execute(side.Step('save','../escape',value='no',criterion='file saved'))
    def test_step_needs_completion_criterion(self):
        with self.assertRaises(ValueError): self.store.create('Read',[side.Step('extract','a')])

class FactoryTests(unittest.TestCase):
    def spec(self): return factory.AgentSpec.from_json(json.loads((ROOT/'projects/07-agent-factory/examples/text_helper.json').read_text()))
    def test_generated_application_tests_really_execute(self):
        receipt=factory.validate_generated(factory.render(self.spec()))
        self.assertEqual(receipt['returncode'],0); self.assertIn('Ran 4 tests',receipt['stderr'])
    def test_build_manifest_matches_output_and_refuses_overwrite(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'agent'; receipt=factory.build(self.spec(),output)
            for name,digest in receipt['sha256'].items(): self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(),digest)
            with self.assertRaises(FileExistsError): factory.build(self.spec(),output)
    def test_code_injection_name_rejected(self):
        data=json.loads((ROOT/'projects/07-agent-factory/examples/text_helper.json').read_text()); data['name']='x;import os'
        with self.assertRaises(ValueError): factory.AgentSpec.from_json(data)
    def test_unknown_framework_not_claimed_supported(self):
        data=json.loads((ROOT/'projects/07-agent-factory/examples/text_helper.json').read_text()); data['framework']='autogen'
        with self.assertRaises(ValueError): factory.AgentSpec.from_json(data)
    def test_untyped_tools_rejected(self):
        data=json.loads((ROOT/'projects/07-agent-factory/examples/text_helper.json').read_text()); data['tools']='word_count'
        with self.assertRaises(ValueError): factory.AgentSpec.from_json(data)
    def test_generated_inventory_and_imports_fail_closed(self):
        files=factory.render(self.spec()); files['agent.py']='import os\n'
        with self.assertRaises(ValueError): factory.validate_generated(files)
    def test_generated_tests_failure_is_reported(self):
        files=factory.render(self.spec()); files['test_agent.py']='raise RuntimeError("deliberate fault")\n'
        with self.assertRaisesRegex(ValueError,'generated tests failed'): factory.validate_generated(files)
    def test_requirements_preserve_policies(self):
        spec=self.spec(); self.assertEqual(factory.requirements(spec)['constraints'],list(spec.policies))

if __name__=='__main__': unittest.main()
