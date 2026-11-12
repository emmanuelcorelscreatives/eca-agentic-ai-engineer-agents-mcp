"""Offline graph and actual Code-node JS tests. Never evidence of a model/n8n run."""
import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / 'examples/s01/first-workflow.n8n.json'

class WorkflowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = json.loads(WORKFLOW.read_text())
        cls.nodes = {x['name']: x for x in cls.workflow['nodes']}

    def execute(self, name, item):
        if not shutil.which('node'):
            self.skipTest('Node.js required for actual offline Code-node execution')
        payload = {'code': self.nodes[name]['parameters']['jsCode'], 'item': item}
        script = r'''const vm=require('node:vm');let raw='';process.stdin.on('data',x=>raw+=x);process.stdin.on('end',()=>{const p=JSON.parse(raw);const fixture={id:'enquiry-001',text:'Where can I find the course exercises?'};const context={$input:{first:()=>({json:p.item})},$:name=>({first:()=>({json:fixture})})};try{const result=vm.runInNewContext('(function(){'+p.code+'})()',context,{timeout:1000});process.stdout.write(JSON.stringify({ok:true,result}));}catch(e){process.stdout.write(JSON.stringify({ok:false,error:e.message}));}});'''
        p = subprocess.run(['node', '-e', script], input=json.dumps(payload), capture_output=True, text=True, check=True, timeout=5)
        return json.loads(p.stdout)

    def classify(self, result):
        return self.execute('Validate model result', {'choices': [{'message': {'content': json.dumps(result)}}]})

    def test_single_model_request_and_no_delivery(self):
        request = [n for n in self.nodes.values() if n['type'] == 'n8n-nodes-base.httpRequest']
        self.assertEqual(len(request), 1)
        self.assertIs(request[0]['retryOnFail'], False)
        self.assertEqual(request[0]['parameters']['method'], 'POST')
        self.assertFalse(self.workflow['active'])
        self.assertEqual(self.workflow['pinData'], {})
        for n in self.nodes.values():
            self.assertIn(n['type'], {'n8n-nodes-base.manualTrigger','n8n-nodes-base.code','n8n-nodes-base.httpRequest','n8n-nodes-base.if'})
            self.assertNotIn('credentials', n)

    def test_graph_requires_model_then_validation_tool_decision(self):
        order=['Manual Trigger','Synthetic enquiry','Classify with configured model','Validate model result','Allowlisted FAQ lookup','Answerable?']
        for start,end in zip(order,order[1:]):
            self.assertEqual(self.workflow['connections'][start]['main'], [[{'node':end,'type':'main','index':0}]])
        branches=self.workflow['connections']['Answerable?']['main']
        self.assertEqual([x[0]['node']for x in branches], ['Draft answer','Human review draft'])

    def test_one_synthetic_input_matches_reference(self):
        items=self.execute('Synthetic enquiry', {})['result']
        self.assertEqual(len(items),1)
        reference=json.loads((ROOT/'data/synthetic/workflow-enquiries.json').read_text())['enquiries'][0]
        self.assertEqual(items[0]['json'], {'id':reference['id'],'text':reference['text']})

    def test_answer_is_grounded_faq_draft(self):
        validated=self.classify({'route':'answer','faq_id':'faq-course-access','confidence':0.9})
        self.assertTrue(validated['ok'])
        tool=self.execute('Allowlisted FAQ lookup', validated['result'][0]['json'])
        self.assertTrue(tool['ok']);self.assertTrue(tool['result'][0]['json']['answerable'])
        result=self.execute('Draft answer', tool['result'][0]['json'])['result'][0]['json']
        faq=json.loads((ROOT/'data/synthetic/workflow-faq.json').read_text())['entries'][0]
        self.assertEqual(result['draft'],faq['answer'])
        self.assertEqual(result['source_faq'],faq['id'])
        self.assertFalse(result['delivery_performed'])

    def test_review_and_low_confidence_never_answer(self):
        for c in [{'route':'human_review','faq_id':None,'confidence':0.9},{'route':'answer','faq_id':'faq-feedback','confidence':0.2}]:
            v=self.classify(c)['result'][0]['json']
            t=self.execute('Allowlisted FAQ lookup',v)['result'][0]['json']
            self.assertFalse(t['answerable'])
            self.assertFalse(self.execute('Draft answer', t)['ok'])
            r=self.execute('Human review draft', t)['result'][0]['json']
            self.assertEqual(r['status'],'human_review_required');self.assertFalse(r['delivery_performed'])

    def test_rejects_unknown_route_arguments_extra_fields_types(self):
        fixtures=json.loads((ROOT/'tests/stage01/fixtures/model-contract-responses.json').read_text())
        self.assertTrue(fixtures['simulated'])
        for case in fixtures['invalid']:
            with self.subTest(name=case['name']):
                self.assertFalse(self.classify(case['response'])['ok'])

    def test_rejects_missing_or_non_json_response(self):
        for raw in [{},{'choices':[{'message':{'content':'```json\n{}\n```'}}]},{'choices':[{'message':{'content':'not JSON'}}]}]:
            self.assertFalse(self.execute('Validate model result',raw)['ok'])

    def test_tool_rejects_non_allowlisted_id_even_if_validator_bypassed(self):
        result=self.execute('Allowlisted FAQ lookup',{'classification':{'route':'answer','faq_id':'https://private.invalid','confidence':1}})
        self.assertFalse(result['ok'])

if __name__ == '__main__': unittest.main()
