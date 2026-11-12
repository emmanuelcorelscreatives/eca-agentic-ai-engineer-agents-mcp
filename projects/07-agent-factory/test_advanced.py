import copy
import json
from pathlib import Path
import tempfile
import unittest
from advanced import (TypedSpec, example_spec, approve, requirements, instructions, catalog_lookup,
                      draft_notification, architecture, scaffold_approved, sha, render_trusted, test_trusted_template, review, write_workspace, artifact_graph, repair_loop, select_adapter)
from docker_validate import plan, execute

class Contracts(unittest.TestCase):
    def setUp(self): self.value=example_spec(); self.spec=TypedSpec.parse(self.value)
    def test_roundtrip_and_immutable(self):
        self.assertEqual(TypedSpec.parse(self.spec.value()).digest,self.spec.digest)
        self.value['purpose']='changed'; self.assertNotEqual(self.value,self.spec.value())
    def test_reject_unknown_duplicate_policy_path_secret(self):
        variants=[]
        for key,value in [('unknown',1),('policies',[]),('datasets',['../secret']),('purpose','sk-'+ 'x'*20),('secret_refs',['TOKEN'])]:
            v=example_spec(); v[key]=value; variants.append(v)
        v=example_spec(); v['tools'].append(v['tools'][0]); variants.append(v)
        v=example_spec(); v['expected_output']['additionalProperties']=True; variants.append(v)
        v=example_spec(); v['tools'][0]['input_schema']['properties']['query']['type']='integer'; variants.append(v)
        for value in variants:
            with self.subTest(value=value),self.assertRaises(ValueError): TypedSpec.parse(value)
    def test_approval_stale_blocks(self):
        approval=approve(self.spec,'learner-human'); value=example_spec(); value['purpose']='new purpose'
        with self.assertRaises(ValueError): requirements(TypedSpec.parse(value),approval)
    def test_lineage(self):
        approval=approve(self.spec,'human'); req=requirements(self.spec,approval)
        self.assertTrue(all(r['source'].startswith('/') for r in req['requirements']))
        graph=artifact_graph(self.spec,approval,{'agent.py':'pass\n'})
        self.assertEqual(graph['artifacts'][0]['inputs'][0],self.spec.digest)
        self.assertIn('no_external_delivery',instructions(self.spec)['policy_sources'])
    def test_real_catalog_and_draft(self):
        rows=[{'id':'one','title':'Agent Engineering','category':'AI'}]
        self.assertEqual(catalog_lookup(rows,{'query':'engineering'})['matches'],rows)
        self.assertFalse(draft_notification({'recipient':'course@example.invalid','body':'A draft'})['delivered'])
        with self.assertRaises(ValueError): catalog_lookup(rows,{'query':'AI','shell':'ls'})
    def test_review_seeded_findings(self):
        report=review({'agent.py':'import json, subprocess\nx = eval("1")\np="../escape"\n'},['test_required'])
        self.assertGreaterEqual(len(report['findings']),4)
        self.assertFalse(report['security_certified'])
    def test_workspace_fresh_and_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'new'; write_workspace(root,{'agent.py':'pass'})
            with self.assertRaises(FileExistsError): write_workspace(root,{'agent.py':'pass'})
            with self.assertRaises(ValueError): write_workspace(Path(d)/'bad',{'../escape':'x'})
    def test_repair_real_parser_diagnostics_and_fresh_workspace(self):
        # This contract test parses syntax; it does not claim an executed Docker validation.
        def validate(root,files):
            import ast
            try: ast.parse((root/'agent.py').read_text()); passed=True; error=''
            except SyntaxError as e: passed=False; error=str(e)
            return {'passed':passed,'kind':'trusted-fixed-template-tests','stdout':'actual AST parser test','stderr':error}
        with tempfile.TemporaryDirectory() as d:
            result=repair_loop({'agent.py':'def broken(:\n','test_agent.py':'# immutable\n'},Path(d)/'repairs',validate,
                               lambda f,e:{'agent.py':'answer = 42\n'},allowed_files=['agent.py'])
            self.assertEqual(result['status'],'passed'); self.assertEqual(result['calls'],1)
            self.assertIn('broken',(Path(d)/'repairs/attempt-00/agent.py').read_text())
            self.assertEqual(len(result['attempts']),2)
    def test_repair_preserves_test_and_budget(self):
        validator=lambda root,files:dict(passed=False,kind='trusted-fixed-template-tests',stdout='',stderr='seeded diagnostic')
        with tempfile.TemporaryDirectory() as d:
            result=repair_loop({'agent.py':'pass','test_agent.py':'assert False'},Path(d)/'repairs',validator,
                               lambda f,e:{'test_agent.py':'pass'},allowed_files=['agent.py'])
            self.assertEqual(result['status'],'unresolved'); self.assertEqual(result['calls'],1)
            self.assertEqual((Path(d)/'repairs/attempt-00/test_agent.py').read_text(),'assert False')
        with tempfile.TemporaryDirectory() as d:
            result=repair_loop({'agent.py':'pass'},Path(d)/'repairs',validator,lambda f,e:self.fail('no budget'),allowed_files=['agent.py'],max_calls=0)
            self.assertEqual(result['status'],'unresolved')
    def test_docker_planning_no_execution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'test_agent.py').write_text('pass')
            with self.assertRaises(ValueError): plan(root,'python:latest')
            p=plan(root,'python@sha256:'+'a'*64)
            self.assertEqual(p['status'],'PLANNED_NOT_EXECUTED')
            self.assertIn('--read-only',p['command']); self.assertIn('none',p['command'])
            self.assertIn('--pull',p['command']); self.assertNotIn('/var/run/docker.sock',' '.join(p['command']))
            with self.assertRaises(PermissionError): execute(root,p['image'],root/'evidence')
            (root/'bad').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError): plan(root,p['image'])
    def test_actual_trusted_generated_acceptance(self):
        approval=approve(self.spec,'human')
        files=render_trusted(self.spec,approval)
        result=test_trusted_template(self.spec,approval,files)
        self.assertTrue(result['passed'],result['stderr'])
        self.assertIn('Ran 5 tests',result['stderr'])
        files['agent.py']+='\nprint("untrusted")\n'
        with self.assertRaises(ValueError): test_trusted_template(self.spec,approval,files)
    def test_architecture_requires_current_approval(self):
        approval=approve(self.spec,'human'); req=requirements(self.spec,approval)
        design=architecture(self.spec,approval,req)
        decision={'architecture_sha256':sha(design),'reviewer':'human','decision':'approved'}
        with tempfile.TemporaryDirectory() as d:
            graph=scaffold_approved(self.spec,approval,req,design,decision,Path(d)/'new')
            self.assertEqual(graph['spec_sha256'],self.spec.digest)
            decision['architecture_sha256']='0'*64
            with self.assertRaises(ValueError): scaffold_approved(self.spec,approval,req,design,decision,Path(d)/'bad')
        req['unresolved']=['deployment ambiguous']
        with self.assertRaises(ValueError): architecture(self.spec,approval,req)
    def test_native_adapter_scaffolds_are_truthful(self):
        from adapters.frameworks import NativeFramework
        for name in ['agno','mastra']:
            value=example_spec(); value['framework']=name
            spec=TypedSpec.parse(value); adapter=NativeFramework(name)
            files=adapter.scaffold(spec,approve(spec,'human'))
            status=json.loads(files['ADAPTER-STATUS.json'])
            self.assertEqual(status['sdk_execution'],'NOT_EXECUTED')
            self.assertEqual(status['dependency_lock'],'REQUIRED_BEFORE_RELEASE')
            self.assertIn('artifact-graph.json',files)
            self.assertEqual(select_adapter({name:adapter},name,{'catalog_lookup'}),adapter)
            with self.assertRaises(ValueError): select_adapter({name:adapter},name,{'streaming'})
    def test_adapter_capabilities_fail_closed(self):
        with self.assertRaises(ValueError): select_adapter({},'agno',{'streaming'})

if __name__=='__main__': unittest.main()
