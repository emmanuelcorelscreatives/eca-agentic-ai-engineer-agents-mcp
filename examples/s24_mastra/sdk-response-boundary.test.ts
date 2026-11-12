/** Genuine Agent.generate SDK boundary with explicitly SCRIPTED SDK test model.
 * This tests integration and rejection behavior, never provider intelligence or
 * actual model recall. No network provider/model response is claimed. */
import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {Agent} from '@mastra/core/agent';
import {createMockModel} from '@mastra/core/test-utils/llm-mock';
import {openAcademyMemory} from './memory.js';
import {generateValidatedTriage,lookupTicket,findArticles} from './triage.js';

async function withScriptedAgent<T>(scripted:Record<string,unknown>,
    action:(agent:Agent,invocations:()=>number)=>Promise<T>) {
  const directory=await mkdtemp(join(tmpdir(),'academy-s24-scripted-'));
  const handle=await openAcademyMemory(`file:${join(directory,'sessions.db')}`);
  let calls=0;
  const model=createMockModel({version:'v2',objectGenerationMode:'json',mockText:scripted,
    spyGenerate:()=>{calls++},spyStream:()=>{calls++}});
  const agent=new Agent({id:'scripted-boundary-test',name:'Explicitly scripted SDK test model',
    model,instructions:'Synthetic integration test; output is scripted, not a real inference.',
    memory:handle.memory,tools:{lookupTicket,findArticles}});
  try {return await action(agent,()=>calls);}
  finally {await handle.close();await rm(directory,{recursive:true,force:true});}
}
const validScript={ticketId:'T-001',summary:'Keyboard arrived with a missing key',articleIds:['A-001'],unresolved:[]};
const options={ticketId:'T-001',resourceId:'academy-scripted-user',threadId:'academy-scripted-thread',providerCallApproved:true};
test('genuine Agent.generate scripted SDK response reaches validation and native Memory',async()=>{
  await withScriptedAgent(validScript,async(agent,calls)=>{
    const result=await generateValidatedTriage(agent,options);
    assert.equal(result.validated.ticketId,'T-001');
    assert.deepEqual(result.validated.articleIds,['A-001']);
    assert.ok(calls()>0,'must exercise actual SDK model path, not a direct dictionary validator');
    assert.ok(result.rawResponse);
  });
});
test('genuine generated scripted response with other-product citation is rejected',async()=>{
  await withScriptedAgent({...validScript,articleIds:['A-002']},async(agent,calls)=>{
    await assert.rejects(generateValidatedTriage(agent,options),/unsupported_citation/);
    assert.ok(calls()>0);
  });
});
test('genuine generated scripted response for the wrong ticket is rejected',async()=>{
  await withScriptedAgent({...validScript,ticketId:'T-002'},async(agent,calls)=>{
    await assert.rejects(generateValidatedTriage(agent,options),/ticket_mismatch/);
    assert.ok(calls()>0);
  });
});

test('genuine SDK scripted malformed generated result fails runtime schema',async()=>{
  await withScriptedAgent({summary:'Explicit malformed SDK model fixture'},async(agent,calls)=>{
    await assert.rejects(generateValidatedTriage(agent,options));
    assert.ok(calls()>0);
  });
});
