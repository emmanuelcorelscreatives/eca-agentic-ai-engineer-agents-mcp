"""AUTHOR-ONLY: central QA must execute. Deterministic probes are not provider evidence."""
import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from advanced import TypedSpec,example_spec,sha
HAS_PYDANTIC = importlib.util.find_spec('pydantic') is not None
if HAS_PYDANTIC:
    # An installed but incompatible/broken SDK must fail visibly; only absence skips.
    from model_schemas import RequirementsProposal,ArchitectureProposal,ReviewProposal
    from model_pipeline import Pipeline,validate_requirements,validate_architecture,prepare_workspace,release_decision,review

class OfflineBackend:
    def __init__(self,content=None,fail=False):self.content=content;self.fail=fail;self.calls=0
    async def invoke(self,*args):
        self.calls+=1
        if self.fail:raise TimeoutError('seeded UNKNOWN provider outcome')
        return self.content,{'source':'explicit-offline-test-fixture','content':self.content}

def req(spec):
    paths=['/purpose','/users','/datasets','/expected_output','/policies','/deployment','/framework','/tools/0','/tools/1']
    return RequirementsProposal(spec_sha256=spec.digest,requirements=[dict(id='REQ-'+str(i),source=p,criterion='Measured criterion',acceptance_test='test_'+str(i)) for i,p in enumerate(paths)],unresolved=[])

@unittest.skipUnless(HAS_PYDANTIC, 'Optional Pydantic absent; typed pipeline semantics NOT verified')
class Semantics(unittest.TestCase):
    def test_required_environment_template_is_safe_and_not_rejected_as_dot_path(self):
        files={'agent.py':'pass','.env.example':'# Example only\nAPI_KEY=<your-key>\n'}
        self.assertEqual(review(files)['artifact_sha256'],sha(files))
        with self.assertRaises(ValueError):review({'agent.py':'pass','.env.example':'API_KEY=actual-secret-value'})
    def test_actual_specialist_schema_handoff(self):
        spec=TypedSpec.parse(example_spec());r=req(spec)
        with tempfile.TemporaryDirectory() as d:
            backend=OfflineBackend(r.model_dump(mode='json'));p=Pipeline(Path(d),backend)
            result=asyncio.run(p.analyze(spec));self.assertEqual(result,r)
            self.assertTrue((Path(d)/'requirements/raw-response.json').is_file())
            with self.assertRaises(RuntimeError):asyncio.run(p.analyze(spec))
            self.assertEqual(backend.calls,1)
    def test_unknown_is_never_replayed(self):
        with tempfile.TemporaryDirectory() as d:
            backend=OfflineBackend(fail=True);p=Pipeline(Path(d),backend)
            with self.assertRaises(TimeoutError):asyncio.run(p.propose('requirements',{}))
            with self.assertRaises(RuntimeError):asyncio.run(p.propose('requirements',{}))
            self.assertEqual(backend.calls,1)
            self.assertTrue((Path(d)/'requirements/SUBMISSION-UNKNOWN.json').is_file())
    def test_missing_required_field_blocks_handoff(self):
        spec=TypedSpec.parse(example_spec());r=req(spec);r.requirements.pop()
        with self.assertRaises(ValueError):validate_requirements(spec,r)
    def test_framework_and_requirement_changes_block(self):
        spec=TypedSpec.parse(example_spec());r=req(spec)
        design=ArchitectureProposal(requirements_sha256=sha(r.model_dump(mode='json')),framework='agno',entry_point='agent.py',components=[dict(path='agent.py',requirement_ids=[x.id for x in r.requirements],purpose='app')],unresolved=[])
        with self.assertRaises(ValueError):validate_architecture(spec,r,design)
    def test_independent_suite_is_disjoint_and_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            result=prepare_workspace(Path(d)/'new',{'agent.py':'raise RuntimeError("not executed")'},{'acceptance/test_contract.py':'assert False'})
            self.assertEqual(result['acceptance_sha256'],sha({'acceptance/test_contract.py':'assert False'}))
            self.assertTrue((Path(d)/'new/agent.py').exists())
            with self.assertRaises(ValueError):prepare_workspace(Path(d)/'bad',{'acceptance/a.py':'x'},{'acceptance/a.py':'y'})
    def test_model_clean_review_alone_cannot_release(self):
        spec=TypedSpec.parse(example_spec());r=req(spec);files={'agent.py':'pass'}
        reviewed=ReviewProposal(artifact_sha256=sha(files),findings=[],covered_requirement_ids=[x.id for x in r.requirements],limitations=['Model opinion only'])
        with self.assertRaises(ValueError):release_decision(files,r,reviewed,{},sha({'suite':'immutable'}),{'artifact_sha256':sha(files),'decision':'approved'})

if __name__=='__main__':unittest.main()
