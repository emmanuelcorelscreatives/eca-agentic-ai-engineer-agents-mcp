import { readFileSync } from 'node:fs';
import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { z } from 'zod';
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';
const data = JSON.parse(readFileSync(new URL('../../data/s24_articles.json', import.meta.url), 'utf8')) as {
  tickets: { id:string; product_id:string; summary:string; category:string }[];
  articles: { id:string; product_id:string; title:string; text:string }[];
};
export const input = z.object({ ticketId:z.string().regex(/^T-\d{3}$/) });
export const evidence = z.object({ ticketId:z.string(), summary:z.string(), articleIds:z.array(z.string()), unresolved:z.array(z.string()) });
export const lookupTicket = createTool({ id:'academy-ticket', description:'Read one exact synthetic ticket',
  inputSchema:input, outputSchema:z.object({ ticket:z.object({id:z.string(),product_id:z.string(),summary:z.string(),category:z.string()}) }),
  execute:async ({ ticketId }) => { const ticket=data.tickets.find(t=>t.id===ticketId); if(!ticket) throw new Error('unknown_ticket'); return {ticket}; } });
export const findArticles = createTool({ id:'academy-articles', description:'Find product-scoped fixture articles',
  inputSchema:z.object({productId:z.string()}), outputSchema:z.object({articles:z.array(z.object({id:z.string(),text:z.string()}))}),
  execute:async ({productId}) => ({articles:data.articles.filter(a=>a.product_id===productId).map(a=>({id:a.id,text:a.text}))}) });
export function localEvidence(ticketId:string) {
  const ticket=data.tickets.find(t=>t.id===ticketId); if(!ticket) throw new Error('unknown_ticket');
  const articles=data.articles.filter(a=>a.product_id===ticket.product_id);
  return evidence.parse({ticketId,summary:ticket.summary,articleIds:articles.map(a=>a.id),unresolved:articles.length?[]:['No supporting article']});
}
const gather=createStep({id:'gather-fixture-evidence',inputSchema:input,outputSchema:evidence,
  execute:async ({inputData})=>localEvidence(inputData.ticketId)});
export const workflow=createWorkflow({id:'academy-triage-evidence',inputSchema:input,outputSchema:evidence}).then(gather).commit();
export function buildAgent(model:string, databaseUrl:string = 'file:./academy-triage.db') {
  if(!model) throw new Error('Explicit provider/model required');
  return new Agent({id:'academy-triage',name:'Academy triage',model,
    instructions:'Use the ticket and article tools; cite only retrieved IDs. Draft only; report unknowns.',
    memory:new Memory({storage:new LibSQLStore({id:'academy-triage-store',url:databaseUrl}),options:{lastMessages:10}}),
    tools:{lookupTicket,findArticles}});
}
