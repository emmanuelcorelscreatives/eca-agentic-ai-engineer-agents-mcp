import assert from 'node:assert/strict';
import test from 'node:test';
import {localEvidence,input,evidence,workflow} from './triage.js';
test('exact fixture-backed article IDs',()=>assert.deepEqual(localEvidence('T-001').articleIds,['A-001']));
test('unknown ticket cannot become a summary',()=>assert.throws(()=>localEvidence('T-999'),/unknown_ticket/));
test('runtime schema rejects invalid args and missing fields',()=>{assert.equal(input.safeParse({ticketId:3}).success,false);assert.equal(evidence.safeParse({ticketId:'T-001'}).success,false)});
test('real workflow executes deterministic evidence step',async()=>{const run=await workflow.createRun(); const result=await run.start({inputData:{ticketId:'T-001'}});assert.equal(result.status,'success')});
