"""Offline business contracts only; these do not claim real SDK/model execution."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from examples import s21_inventory as inventory
from examples.s22_policy import PolicyService,RequestContext,validate_triage,escalation_draft
from examples.s23_workflow import Approval,digest,approved_transition,route,save_state,load_state,coordinate
from examples.s24_triage import lookup_ticket,search_articles

class InventoryContracts(unittest.TestCase):
    def test_exact_known_stock(self):
        self.assertEqual(inventory.lookup_stock('ECA-KEY-01')['product']['stock'],12)
    def test_unknown_and_malformed_are_distinct(self):
        self.assertEqual(inventory.lookup_stock('ECA-KEY-99')['error'],'unknown_sku')
        self.assertEqual(inventory.lookup_stock('../secret')['error'],'invalid_sku')
    def test_delivery_zone_and_availability(self):
        self.assertEqual(inventory.estimate_delivery('AB12','ECA-KEY-01')['business_days'],2)
        self.assertEqual(inventory.estimate_delivery('CD12','ECA-KEY-01')['business_days'],4)
        self.assertEqual(inventory.estimate_delivery('AB12','ECA-MOUSE-02')['error'],'out_of_stock')
    def test_invalid_postcode_no_guess(self):
        self.assertEqual(inventory.estimate_delivery('ZZ12','ECA-KEY-01')['error'],'unsupported_zone')
        self.assertEqual(inventory.estimate_delivery('bad','ECA-KEY-01')['error'],'invalid_postcode')
    def test_fixture_not_mutated_by_return_values(self):
        item=inventory.lookup_stock('ECA-KEY-01');item['product']['stock']=999
        self.assertEqual(inventory.lookup_stock('ECA-KEY-01')['product']['stock'],12)
    def test_intermediate_events_not_reported_as_final(self):
        def event(id,text,final):
            return SimpleNamespace(id=id,content=SimpleNamespace(parts=[SimpleNamespace(text=text)]),is_final_response=lambda:final)
        result=inventory.summarize_events([event('1','thinking',False),event('2','answer',True)])
        self.assertEqual(result['final_text'],['answer']);self.assertEqual(result['event_ids'],['1','2'])
    def test_real_event_call_identifiers_preserved(self):
        call=SimpleNamespace(id='call-1',name='lookup_stock',args={'sku':'ECA-KEY-01'})
        response=SimpleNamespace(id='call-1',name='lookup_stock',response={'ok':True})
        event=SimpleNamespace(id='evt',content=SimpleNamespace(parts=[SimpleNamespace(function_call=call),SimpleNamespace(function_response=response)]),is_final_response=lambda:False)
        result=inventory.summarize_events([event]);self.assertEqual(result['calls'][0]['id'],result['responses'][0]['id'])

class PolicyContracts(unittest.TestCase):
    def setUp(self):
        self.context=RequestContext('request-a','T-001',PolicyService())
        self.valid={'ticket_id':'T-001','category':'damaged','rationale':'Reported missing key; replacement review is required.','policy_ids':['POL-KEY-1'],'confidence':0.7,'unresolved':['No photo supplied']}
    def test_known_policy_is_product_scoped(self):
        self.assertEqual(PolicyService().lookup('P-KEY')['policies'][0]['id'],'POL-KEY-1')
        self.assertEqual(PolicyService().lookup('P-NONE')['error'],'unknown_product')
    def test_valid_triage(self):
        self.assertEqual(validate_triage(self.valid,self.context),self.valid)
    def test_wrong_ticket_rejected(self):
        value={**self.valid,'ticket_id':'T-002'}
        with self.assertRaises(ValueError):validate_triage(value,self.context)
    def test_unverified_policy_rejected(self):
        value={**self.valid,'policy_ids':['POL-MOUSE-2']}
        with self.assertRaises(ValueError):validate_triage(value,self.context)
    def test_extra_missing_and_confidence_rejected(self):
        for value in ({**self.valid,'extra':1},{k:v for k,v in self.valid.items() if k!='unresolved'},{**self.valid,'confidence':True},{**self.valid,'confidence':1.1}):
            with self.assertRaises(ValueError):validate_triage(value,self.context)
    def test_contexts_do_not_cross_contaminate_concurrent_requests(self):
        def read(ticket_id):
            c=RequestContext('req-'+ticket_id,ticket_id,PolicyService());return c.policies.ticket(c.ticket_id)['id']
        with ThreadPoolExecutor(max_workers=2) as executor:
            self.assertEqual(list(executor.map(read,['T-001','T-002'])),['T-001','T-002'])
    def test_wrong_dependency_rejected(self):
        with self.assertRaises(ValueError):RequestContext('a','T-001',{})
    def test_escalation_never_sends(self):
        result=escalation_draft(self.context,'Missing key')
        self.assertEqual(result['status'],'draft_only');self.assertNotIn('sent',result)

class WorkflowContracts(unittest.TestCase):
    def setUp(self):self.draft={'ticket_id':'T-001','reason':'review damage'}
    def test_unapproved_transition_blocked(self):
        with self.assertRaises(PermissionError):approved_transition(self.draft,Approval('T-001',digest(self.draft),False,'reviewer'))
    def test_approval_bound_to_exact_draft_and_ticket(self):
        approval=Approval('T-001',digest(self.draft),True,'reviewer')
        with self.assertRaises(PermissionError):approved_transition({**self.draft,'reason':'changed'},approval)
        with self.assertRaises(PermissionError):approved_transition(self.draft,Approval('T-002',digest(self.draft),True,'reviewer'))
    def test_approved_value_remains_local(self):
        result=approved_transition(self.draft,Approval('T-001',digest(self.draft),True,'reviewer'))
        self.assertFalse(result['sent']);self.assertEqual(result['status'],'approved_local_draft')
    def test_atomic_state_roundtrip_and_schema_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'state.json';save_state(p,{'ticket_id':'T-001','history':[1,2]})
            self.assertEqual(load_state(p)['history'],[1,2]);self.assertEqual(list(p.parent.glob('.state-*')),[])
            p.write_text('{"schema_version":2,"payload":{}}')
            with self.assertRaises(ValueError):load_state(p)
    def test_unknown_route_is_held_without_specialist_call(self):
        async def fail(_):raise AssertionError('Must not be called')
        result=asyncio.run(coordinate({'id':'T-003','category':'unknown'},{'policy':fail},run_id='r1'))
        self.assertEqual(result['status'],'held')
    def test_specialist_sequence_and_telemetry(self):
        async def policy(ticket):return {'ticket_id':ticket['id'],'draft':True}
        result=asyncio.run(coordinate({'id':'T-001','category':'damaged'},{'policy':policy},run_id='r2'))
        self.assertEqual([e['step'] for e in result['trace']],['route','specialist_result'])
        self.assertTrue(all(e['run_id']=='r2' for e in result['trace']))

class ArticleContracts(unittest.TestCase):
    def test_ticket_lookup(self):self.assertEqual(lookup_ticket('T-001')['ticket']['product_id'],'P-KEY')
    def test_missing_ticket_error(self):self.assertEqual(lookup_ticket('T-999'),{'ok':False,'error':'unknown_ticket'})
    def test_article_scope(self):self.assertEqual([a['id'] for a in search_articles('P-KEY')['articles']],['A-001'])
    def test_unknown_product_has_no_invented_article(self):self.assertEqual(search_articles('P-UNKNOWN'),{'articles':[]})

if __name__=='__main__':unittest.main()
