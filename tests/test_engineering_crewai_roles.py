"""Author-only semantic tests. Central QA executes, including actual local SDK."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
BASE=Path(__file__).resolve().parents[1]/'projects/05-sandboxed-engineering/learning'
sys.path.insert(0,str(BASE))
try:
    spec=importlib.util.spec_from_file_location('eca_engineering_crewai_roles',BASE/'crewai_roles.py')
    roles=importlib.util.module_from_spec(spec);sys.modules[spec.name]=roles;spec.loader.exec_module(roles)
finally:sys.path.pop(0)

class Evidence:
    def __init__(self):self.rows=[]
    def record(self,label,value):self.rows.append((label,value));return roles.sha(value)
class FixtureBroker:
    def __init__(self):self.calls=[]
    def request(self,role,payload):
        self.calls.append((role,payload))
        return {'role':role,'input_sha256':roles.sha(payload),'request_id':'offline-fixture-1',
                'model':'explicit-offline-fixture','raw':'{"note":"fixture"}','provenance':'offline-test-double'}

class CrewAIRoleSemanticTests(unittest.TestCase):
    def test_message_normalization_and_no_hidden_tools(self):
        self.assertEqual(roles.normalized_messages('hello'),[{'role':'user','content':'hello'}])
        with self.assertRaises(ValueError):roles.normalized_messages([{'role':'user','content':[{'image':'no'}]}])
    def test_output_equivalence_rejects_fabricated_fields(self):
        self.assertEqual(roles.validate_equivalence('{"a":1}','{ "a": 1 }'),{'a':1})
        with self.assertRaises(ValueError):roles.validate_equivalence('{"a":1}','{"a":2}')
    def test_default_provider_never_labels_fixture_as_actual(self):
        try:import crewai
        except ImportError:self.skipTest('Central QA must use the existing pinned CrewAI environment')
        llm=roles.make_broker_llm(FixtureBroker(),'developer',{'schema':{'note':'text'}},Evidence())
        with self.assertRaises(ValueError):llm.call('produce artifact')
    def test_actual_sdk_custom_llm_reserves_exactly_once(self):
        try:import crewai
        except ImportError:self.skipTest('Pinned CrewAI environment required')
        broker=FixtureBroker();evidence=Evidence()
        llm=roles.make_broker_llm(broker,'developer',{'schema':{'note':'text'}},evidence,allow_offline=True)
        self.assertIn('Final Answer:',llm.call('produce artifact'))
        with self.assertRaises(RuntimeError):llm.call('repeat unknown request')
        self.assertEqual(len(broker.calls),1)
        self.assertEqual(llm.actual_response['provenance'],'offline-test-double')
    def test_actual_sdk_task_execution_with_explicit_offline_broker(self):
        try:import crewai
        except ImportError:self.skipTest('Pinned CrewAI environment required')
        broker=FixtureBroker();evidence=Evidence()
        provider=roles.CrewAIRoleProvider(broker,evidence,allow_offline=True)
        payload={'stage':'fixture-structural-check','schema':{'note':'text'}}
        response=provider.request('developer',payload)
        self.assertEqual(json.loads(response['raw']),{'note':'fixture'})
        self.assertEqual(response['input_sha256'],roles.sha(payload))
        self.assertEqual(response['provenance'],'offline-test-double')
        self.assertEqual(len(broker.calls),1)
        self.assertTrue(any(label=='crewai-role-output-binding' for label,value in evidence.rows))
if __name__=='__main__':unittest.main()
