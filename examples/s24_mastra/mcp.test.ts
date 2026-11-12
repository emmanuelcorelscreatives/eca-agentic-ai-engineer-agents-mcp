// Actual MCP SDK subprocess tests. No model.generate / provider calls.
import assert from 'node:assert/strict';
import test from 'node:test';
import { Agent } from '@mastra/core/agent';
import { ARTICLE_TOOL_NAMES,makeMcpClient,selectArticleTools,withArticleTools,withMcpAgent } from './mcp.js';
const python=process.env.COURSE_MCP_PYTHON;
test('allowlist rejects missing discovery',()=>assert.throws(()=>selectArticleTools({}),/Missing required/));
test('genuine MCP read tools wired into genuine Agent', {skip:!python}, async()=>{
  await withMcpAgent(python!, 'openai/gpt-4.1-mini',async(agent,tools)=>{
    assert.ok(agent instanceof Agent);
    assert.deepEqual(Object.keys(await agent.listTools()).sort(),[...ARTICLE_TOOL_NAMES].sort());
    const ticket=await tools.articles_lookup_ticket.execute!({ticket_id:'T-001'},{});
    const article=await tools.articles_search_articles.execute!({product_id:'P-KEY'},{});
    assert.match(JSON.stringify(ticket),/T-001/);
    assert.match(JSON.stringify(article),/A-001/);
    const unknown=await tools.articles_lookup_ticket.execute!({ticket_id:'T-999'},{});
    assert.match(JSON.stringify(unknown),/unknown_ticket/);
  });
});
test('extra discovery tools never cross source allowlist',{skip:!python}, async()=>{
  await withArticleTools(python!,async tools=>{
    const selected=selectArticleTools({...tools, forbidden_mutation:tools.articles_lookup_ticket});
    assert.deepEqual(Object.keys(selected).sort(),[...ARTICLE_TOOL_NAMES].sort());
  });
});
test('real client disconnect is idempotent after a real session',{skip:!python},async()=>{
  const client=makeMcpClient(python!);
  try { assert.equal(Object.keys(selectArticleTools(await client.listTools())).length,2); }
  finally { await client.disconnect(); await client.disconnect(); }
});
test('consumer exception is preserved through cleanup',{skip:!python},async()=>{
  await assert.rejects(withArticleTools(python!,async()=>{throw new Error('consumer_failure')}),/consumer_failure/);
});
