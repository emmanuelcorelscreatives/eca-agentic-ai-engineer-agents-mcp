import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {openAcademyMemory,saveSyntheticContext} from './memory.js';
import {evidence} from './triage.js';
test('actual native Memory persists on restart and isolates resources',async()=>{
  const directory=await mkdtemp(join(tmpdir(),'academy-s24-'));
  const url=`file:${join(directory,'memory.db')}`;
  try {
    let handle=await openAcademyMemory(url);
    try {
      await saveSyntheticContext(handle.memory,'academy-alice','academy-ticket-a','Synthetic T-001 missing key');
      await saveSyntheticContext(handle.memory,'academy-bob','academy-ticket-b','Synthetic T-002 delivery');
    } finally {await handle.close();}
    // Reconstruct SDK objects and reopen the same physical DB, rather than
    // reading a retained JS object or manufacturing expected messages.
    handle=await openAcademyMemory(url);
    try {
      const a=await handle.memory.recall({threadId:'academy-ticket-a',resourceId:'academy-alice'});
      const b=await handle.memory.recall({threadId:'academy-ticket-b',resourceId:'academy-bob'});
      assert.match(JSON.stringify(a.messages),/T-001/);
      assert.doesNotMatch(JSON.stringify(a.messages),/T-002/);
      assert.match(JSON.stringify(b.messages),/T-002/);
      assert.doesNotMatch(JSON.stringify(b.messages),/T-001/);
      // Storage ownership checks may reject cross-resource access or return
      // an empty result; neither path is allowed to reveal Alice's content.
      try {
        const wrong=await handle.memory.recall({threadId:'academy-ticket-a',resourceId:'academy-bob'});
        assert.equal(wrong.messages.length,0);
      } catch(error) {
        assert.match(String(error),/resource|belong|own|access|thread/i);
      }
    } finally {await handle.close();}
  } finally {await rm(directory,{recursive:true,force:true});}
});
test('structured-result runtime validation is distinct from generation',()=>{
  assert.equal(evidence.safeParse({ticketId:'T-001',summary:'Draft',articleIds:['A-001'],unresolved:[]}).success,true);
  assert.equal(evidence.safeParse({ticketId:'T-001',articleIds:['A-001']}).success,false);
});
