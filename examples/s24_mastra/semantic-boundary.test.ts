/** Real tools/workflow plus pure response-validation unit cases. These candidate
 * objects are labelled validator inputs, never represented as model responses. */
import assert from 'node:assert/strict';
import test from 'node:test';
import {gatherUsingTools,validateGroundedTriage,workflow,generateValidatedTriage,reviewGatheredEvidence,parseRequestedTicketResponse,lookupTicket} from './triage.js';
import {Agent} from '@mastra/core/agent';
import {writeFile} from 'node:fs/promises';
import {isAbsolute,join} from 'node:path';
async function retainWorkflowTrace(name:string,run:object,result:unknown) {
  const directory=process.env.COURSE_QA_TRACE_DIR;
  if(!directory) return;
  if(!isAbsolute(directory)) throw new Error('COURSE_QA_TRACE_DIR must be an absolute fresh Academy output directory');
  const record={scope:'Actual deterministic SDK workflow; no model claim',
    runId:Reflect.get(run,'runId'),result};
  await writeFile(join(directory,`${name}.json`),JSON.stringify(record,(_key,value)=>
    value instanceof Error?{name:value.name,message:value.message,stack:value.stack}:value,2)+'\n',
    {flag:'wx',mode:0o600});
}
test('genuine typed lookup and article tools return exact shared fixture',async()=>{
  const facts=await gatherUsingTools('T-001');
  assert.equal(facts.ticket.product_id,'P-KEY');
  assert.deepEqual(facts.articles.map(a=>a.id),['A-001']);
});
test('genuine tool failure cannot become a valid summary',async()=>{
  await assert.rejects(gatherUsingTools('T-999'),/unknown_ticket/);
  await assert.rejects(gatherUsingTools('not-a-ticket'));
});
test('actual workflow tool steps complete with grounded output',async()=>{
  const run=await workflow.createRun();
  const result=await run.start({inputData:{ticketId:'T-002'}});
  await retainWorkflowTrace('s24-workflow-success',run,result);
  assert.equal(result.status,'success');
  if(result.status!=='success') throw new Error('workflow failed');
  assert.equal(result.result.ticketId,'T-002');
  assert.deepEqual(result.result.articleIds,['A-002']);
});
test('schema-valid but wrong ticket or unsupported citation is rejected',async()=>{
  const facts=await gatherUsingTools('T-001');
  const candidate={ticketId:'T-001',summary:'Validator fixture',articleIds:['A-001'],unresolved:[]};
  assert.equal(validateGroundedTriage(candidate,facts).ticketId,'T-001');
  assert.throws(()=>validateGroundedTriage({...candidate,ticketId:'T-002'},facts),/ticket_mismatch/);
  assert.throws(()=>validateGroundedTriage({...candidate,articleIds:['A-002']},facts),/unsupported_citation/);
  assert.throws(()=>validateGroundedTriage({...candidate,articleIds:[]},facts),/missing_grounded_citation/);
  assert.throws(()=>validateGroundedTriage({...candidate,articleIds:['A-001','A-001']},facts),/duplicate_citation/);
  assert.throws(()=>validateGroundedTriage({ticketId:'T-001'},facts));
});
test('empty evidence remains explicitly unresolved',async()=>{
  const facts=await gatherUsingTools('T-001');
  const empty={...facts,articles:[]};
  assert.throws(()=>validateGroundedTriage({ticketId:'T-001',summary:'Validator fixture',articleIds:[],unresolved:[]},empty),/must_be_unresolved/);
  assert.equal(validateGroundedTriage({ticketId:'T-001',summary:'Validator fixture',articleIds:[],unresolved:['No evidence']},empty).unresolved.length,1);
});
test('real model invocation boundary refuses unapproved call before SDK generation',async()=>{
  const agent=new Agent({id:'approval-boundary',name:'No-call construction',model:'openai/gpt-4.1-mini',instructions:'Synthetic fixture only'});
  await assert.rejects(generateValidatedTriage(agent,{ticketId:'T-001',resourceId:'academy-a',threadId:'academy-a',providerCallApproved:false}),/approval required/);
});

test('bounded review takes explicit human branch and rejects source-substitution',async()=>{
  const facts=await gatherUsingTools('T-001');
  assert.equal(reviewGatheredEvidence(facts).reviewStatus,'grounded-draft');
  assert.equal(reviewGatheredEvidence({...facts,articles:[]}).reviewStatus,'human-review-required');
  assert.throws(()=>reviewGatheredEvidence({...facts,ticket:{...facts.ticket,summary:'Invented ticket text'}}),/source_mismatch/);
  assert.throws(()=>reviewGatheredEvidence({...facts,articles:[{id:'A-002',text:'Other product'}]}),/source_mismatch/);
});

test('actual unknown-ticket workflow failure preserves a failed step record',async()=>{
  const run=await workflow.createRun();
  const result=await run.start({inputData:{ticketId:'T-999'}});
  await retainWorkflowTrace('s24-workflow-failure',run,result);
  assert.equal(result.status,'failed');
  assert.match(JSON.stringify(result),/unknown_ticket/);
});

test('actual valid tool response for another ticket fails original-request binding',async()=>{
  // This is a genuine lookup result, deliberately paired with the wrong request,
  // not a fabricated provider answer or monkey-patched tool implementation.
  const other=await lookupTicket.execute!({ticketId:'T-002'},{});
  assert.throws(()=>parseRequestedTicketResponse('T-001',other),/requested_ticket_mismatch/);
  assert.equal(parseRequestedTicketResponse('T-002',other).ticket.id,'T-002');
});
