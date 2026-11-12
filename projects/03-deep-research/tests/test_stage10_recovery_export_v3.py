"""NEW selective-recovery/export regressions; central QA owns actual execution."""
import asyncio
from copy import deepcopy
import io
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from test_stage09_semantic_repairs import Backend,planner,analyst,MANIFEST
from research_lab.pipeline_v2 import digest,UnknownOutcome,RecordedFailure
from research_lab.pipeline_v3 import run_research
from research_lab.recovery_v3 import RecoveryJournal
from research_lab.contracts_v2 import ContractError
from research_lab.run_exports_v3 import RunExports
from research_lab.interface_v3 import build_ui,stream_owned

def permit_for(entry,step,attempt='recovery-2'):
    malformed=entry['status']=='INVALID'
    kind='known_malformed_response' if malformed else 'known_http_response'
    return {'step_name':step,'old_attempt_sha256':digest(entry),'input_sha256':entry['input_sha256'],
        'failure_kind':kind,'evidence_sha256':digest(entry['raw_result'] if malformed else entry['known_failure_evidence']),
        'reviewer_identity':'independent-test-reader','executor_identity':'test-executor',
        'reason':'Positively returned synthetic response retained; one targeted same-input retry.',
        'new_attempt_id':attempt}

class SelectiveRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_malformed_search_only_failed_branch_retried_completed_sibling_reused(self):
        class OnceMalformed(Backend):
            bad=True
            async def search(self,query):
                if query['intent']=='counterevidence' and self.bad:
                    self.bad=False;self.calls.append(query['id']);return {'sources':[{'malformed':'retained actual synthetic response'}]}
                return await super().search(query)
        backend=OnceMalformed()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ContractError):
                await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1)
            before=json.loads((Path(directory)/'state-v2.json').read_text())
            step='search/task-a-counterevidence';old=deepcopy(before['steps'][step]);permit=permit_for(old,step)
            bundle=await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1,
                recovery_authorizations={step:permit},executor_identity='test-executor')
            after=json.loads((Path(directory)/'state-v2.json').read_text())
            self.assertEqual(1,backend.calls.count('task-a-support'))
            self.assertEqual(2,backend.calls.count('task-a-counterevidence'))
            self.assertEqual(old,after['attempt_history'][step][0]['attempt'])
            self.assertEqual(permit,after['attempt_history'][step][0]['authorization'])
            self.assertEqual('recovery-2',after['steps'][step]['attempt_id'])
            self.assertEqual(before['steps']['search/task-a-support'],after['steps']['search/task-a-support'])
            self.assertTrue(bundle['report']['sections'])
    async def test_known_http_error_body_retained_and_selectively_recovered(self):
        class OnceHTTP(Backend):
            bad=True
            async def search(self,query):
                if query['intent']=='counterevidence' and self.bad:
                    self.bad=False;self.calls.append(query['id'])
                    raise HTTPError('https://provider.example.invalid',503,'unavailable',{},io.BytesIO(b'known synthetic HTTP response'))
                return await super().search(query)
        backend=OnceHTTP()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(HTTPError):await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1)
            state=json.loads((Path(directory)/'state-v2.json').read_text());step='search/task-a-counterevidence'
            entry=state['steps'][step]
            self.assertEqual(503,entry['known_failure_evidence']['status'])
            self.assertEqual(b'known synthetic HTTP response'.hex(),entry['known_failure_evidence']['response_body_hex'])
            await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1,
                recovery_authorizations={step:permit_for(entry,step)},executor_identity='test-executor')
            self.assertEqual(1,backend.calls.count('task-a-support'));self.assertEqual(2,backend.calls.count('task-a-counterevidence'))
    async def test_known_malformed_analysis_recovery_does_not_repeat_searches(self):
        calls=[]
        async def once_bad(plan,evidence,quality):
            calls.append(1)
            if len(calls)==1:return {'malformed':'known synthetic model output'}
            return await analyst(plan,evidence,quality)
        backend=Backend()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ContractError):await run_research('q',backend,planner,once_bad,directory,input_manifest=MANIFEST)
            state=json.loads((Path(directory)/'state-v2.json').read_text());count=len(backend.calls)
            await run_research('q',backend,planner,once_bad,directory,input_manifest=MANIFEST,
                recovery_authorizations={'analysis':permit_for(state['steps']['analysis'],'analysis')},executor_identity='test-executor')
            self.assertEqual(count,len(backend.calls));self.assertEqual(2,len(calls))
    async def test_three_total_attempt_ceiling_retains_each_known_failure(self):
        class AlwaysBad(Backend):
            async def search(self,query):self.calls.append(query['id']);return {'sources':[{'malformed':'known output'}]}
        backend=AlwaysBad()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ContractError):await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1)
            for attempt in (2,3):
                state=json.loads((Path(directory)/'state-v2.json').read_text())
                permits={name:permit_for(entry,name,'recovery-'+str(attempt)+'-'+name) for name,entry in state['steps'].items() if name.startswith('search/')}
                with self.assertRaises(ContractError):await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1,recovery_authorizations=permits,executor_identity='test-executor')
            state=json.loads((Path(directory)/'state-v2.json').read_text());before=len(backend.calls)
            permits={name:permit_for(entry,name,'attempt-4-'+name) for name,entry in state['steps'].items() if name.startswith('search/')}
            with self.assertRaises(RecordedFailure):await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,workers=1,recovery_authorizations=permits,executor_identity='test-executor')
            self.assertEqual(before,len(backend.calls));self.assertEqual(2,len(state['attempt_history']['search/task-a-support']))
    async def test_unknown_timeout_never_replayed_even_with_permit(self):
        class Timeout(Backend):
            async def search(self,query):self.calls.append(query['id']);raise TimeoutError('unknown synthetic request')
        backend=Timeout()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(TimeoutError):await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST)
            before=list(backend.calls)
            with self.assertRaises(UnknownOutcome):await run_research('q',backend,planner,analyst,directory,input_manifest=MANIFEST,
                recovery_authorizations={'search/task-a-support':{'forged':'not a positive receipt'}},executor_identity='test-executor')
            self.assertEqual(before,backend.calls)
    def test_stale_forged_self_review_and_unknown_history_refused(self):
        entry={'status':'INVALID','input_sha256':'a'*64,'error_type':'ValueError','raw_result':{'bad':'payload'}}
        with tempfile.TemporaryDirectory() as directory:
            journal=RecoveryJournal(directory,{},executor_identity='test-executor')
            journal.state={'attempt_history':{}}
            good=permit_for(entry,'analysis')
            for field,value in (('old_attempt_sha256','b'*64),('evidence_sha256','c'*64),('reviewer_identity','test-executor')):
                changed={**good,field:value}
                with self.assertRaises(ValueError):journal.authorize_recovery('analysis',entry,changed)
            journal.state={'attempt_history':{'analysis':[{'attempt':{'status':'UNKNOWN'},'authorization':{'new_attempt_id':'old'}}]}}
            with self.assertRaises(UnknownOutcome):journal.authorize_recovery('analysis',entry,good)

class OwnedExportTests(unittest.IsolatedAsyncioTestCase):
    async def complete(self,registry,session='session-A'):
        token,directory=registry.create(session)
        bundle=await run_research('q',Backend(),planner,analyst,directory,input_manifest=MANIFEST)
        registry.finish(token,session,bundle)
        return token,directory,bundle
    async def test_exact_own_completed_run_calls_existing_export_and_downloads_four_files(self):
        with tempfile.TemporaryDirectory() as root:
            registry=RunExports(root);token,directory,bundle=await self.complete(registry)
            files=registry.download_paths(token,'session-A')
            self.assertEqual({'report.md','report.html','research.json','sha256.json'},{Path(p).name for p in files})
            self.assertEqual(bundle,json.loads((directory/'exports/research.json').read_text()))
            self.assertTrue(all(Path(p).parent==directory/'exports' for p in files))
    async def test_foreign_session_and_arbitrary_path_token_refused(self):
        with tempfile.TemporaryDirectory() as root:
            registry=RunExports(root);token,_,_=await self.complete(registry)
            with self.assertRaises(PermissionError):registry.download_paths(token,'session-B')
            with self.assertRaises(PermissionError):registry.download_paths('../../etc/passwd','session-A')
    async def test_incomplete_and_foreign_bundle_refused(self):
        with tempfile.TemporaryDirectory() as root:
            registry=RunExports(root);token,directory=registry.create('session-A')
            with self.assertRaises(ValueError):registry.download_paths(token,'session-A')
            bundle=await run_research('q',Backend(),planner,analyst,directory,input_manifest=MANIFEST)
            bundle['identity']['question']='foreign question'
            with self.assertRaises(ValueError):registry.finish(token,'session-A',bundle)
    async def test_export_tamper_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as root:
            registry=RunExports(root);token,directory,_=await self.complete(registry)
            markdown=directory/'exports/report.md';markdown.write_text('changed report')
            with self.assertRaises(ValueError):registry.download_paths(token,'session-A')
        with tempfile.TemporaryDirectory() as root:
            registry=RunExports(root);token,directory,_=await self.complete(registry)
            path=directory/'exports/report.md';path.unlink();path.symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):registry.download_paths(token,'session-A')
    async def test_completed_state_change_refused(self):
        with tempfile.TemporaryDirectory() as root:
            registry=RunExports(root);token,directory,_=await self.complete(registry)
            state=directory/'state-v2.json';state.write_text(state.read_text()+' ')
            with self.assertRaises(ValueError):registry.download_paths(token,'session-A')
    @unittest.skipUnless(importlib.util.find_spec('gradio'), 'Optional Gradio absent; genuine UI callback NOT verified in this environment')
    async def test_real_gradio_constructor_and_actual_download_callback_session_check(self):
        # No fake Gradio, browser or server. Requires the actual centrally admitted UI dependency.
        import gradio as gr
        with tempfile.TemporaryDirectory() as root:
            demo=build_ui(Backend(),planner,analyst,root,MANIFEST)
            config=demo.get_config_file()
            self.assertTrue(any(component['type']=='file' and component['props'].get('file_count')=='multiple' for component in config['components']))
            registry=demo.academy_registry;token,_,_=await self.complete(registry)
            files=demo.academy_downloads(token,gr.Request(session_hash='session-A'))
            self.assertEqual(4,len(files))
            with self.assertRaises(PermissionError):demo.academy_downloads(token,gr.Request(session_hash='session-B'))
    @unittest.skipUnless(importlib.util.find_spec('gradio'), 'Optional Gradio absent; genuine UI callback NOT verified in this environment')
    async def test_actual_async_ui_callback_finishes_owned_export_from_actual_fixture_run(self):
        import gradio as gr
        with tempfile.TemporaryDirectory() as root:
            demo=build_ui(Backend(),planner,analyst,root,MANIFEST)
            output=[row async for row in demo.academy_submit('q',gr.Request(session_hash='session-A'))]
            self.assertTrue(output[-1][1]);token=output[-1][3]
            self.assertEqual(4,len(demo.academy_downloads(token,gr.Request(session_hash='session-A'))))

if __name__=='__main__':unittest.main()
