import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { isAbsolute, resolve } from 'node:path';
import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { z } from 'zod';
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';
// Mastra bundles this module into .mastra/output/index.mjs. Asset lookup must
// therefore use the explicit repository/cwd contract, never import.meta.url.
// npm run check/test/dev must start in examples/s24_mastra; an alternate launcher
// supplies an absolute COURSE_REPOSITORY_ROOT. The SHA rejects stale/wrong copies.
const configuredRoot=process.env.COURSE_REPOSITORY_ROOT;
if(configuredRoot && !isAbsolute(configuredRoot))
  throw new Error('COURSE_REPOSITORY_ROOT must be an absolute Academy repository path');
export const fixturePath=resolve(configuredRoot ?? resolve(process.cwd(),'../..'),'data/s24_articles.json');
const fixtureBytes=readFileSync(fixturePath);
export const fixtureSha256=createHash('sha256').update(fixtureBytes).digest('hex');
if(fixtureSha256!=='3e2f8e8bb583e9855112adda091f3189009928967dd22787c607d1769ef4d645')
  throw new Error('Academy Stage 24 fixture SHA mismatch; use the pinned repository dataset');
const data = JSON.parse(fixtureBytes.toString('utf8')) as {
  tickets: { id:string; product_id:string; summary:string; category:string }[];
  articles: { id:string; product_id:string; title:string; text:string }[];
};
export const input = z.object({ ticketId:z.string().regex(/^T-\d{3}$/) });
export const evidence = z.object({
  ticketId:z.string().regex(/^T-\d{3}$/), summary:z.string().min(1),
  articleIds:z.array(z.string().regex(/^A-\d{3}$/)), unresolved:z.array(z.string())
}).strict();
const ticketSchema=z.object({id:z.string(),product_id:z.string(),summary:z.string(),category:z.string()});
const ticketResponse=z.object({ticket:ticketSchema});
const articleSchema=z.object({id:z.string(),text:z.string()});
const articleResponse=z.object({articles:z.array(articleSchema)});
export const gatheredEvidence=z.object({ticket:ticketSchema,articles:z.array(articleSchema)});
export type GatheredEvidence=z.infer<typeof gatheredEvidence>;
export const lookupTicket = createTool({ id:'academy-ticket', description:'Read one exact synthetic ticket',
  inputSchema:input, outputSchema:ticketResponse,
  execute:async ({ ticketId }) => { const ticket=data.tickets.find(t=>t.id===ticketId); if(!ticket) throw new Error('unknown_ticket'); return {ticket}; } });
export const findArticles = createTool({ id:'academy-articles', description:'Find product-scoped fixture articles',
  inputSchema:z.object({productId:z.string()}), outputSchema:articleResponse,
  execute:async ({productId}) => ({articles:data.articles.filter(a=>a.product_id===productId).map(a=>({id:a.id,text:a.text}))}) });

/** Bind tool-returned records to this exact pinned source, not just ID shape. */
export function validateRetrievedFacts(retrieved:GatheredEvidence) {
  const facts=gatheredEvidence.parse(retrieved);
  const original=data.tickets.find(ticket=>ticket.id===facts.ticket.id);
  if(!original || original.product_id!==facts.ticket.product_id || original.summary!==facts.ticket.summary
      || original.category!==facts.ticket.category) throw new Error('retrieved_ticket_source_mismatch');
  for(const article of facts.articles) {
    const originalArticle=data.articles.find(item=>item.id===article.id && item.product_id===original.product_id);
    if(!originalArticle || originalArticle.text!==article.text) throw new Error('retrieved_article_source_mismatch');
  }
  return facts;
}
export const reviewedEvidence=gatheredEvidence.extend({
  reviewStatus:z.enum(['grounded-draft','human-review-required']),reviewReasons:z.array(z.string())
});
/** Bounded deterministic review, not a simulated model reviewer. Empty evidence
 * takes the explicit human-review branch; wrong source records throw. */
export function reviewGatheredEvidence(retrieved:GatheredEvidence) {
  const facts=validateRetrievedFacts(retrieved);
  return reviewedEvidence.parse({...facts,
    reviewStatus:facts.articles.length?'grounded-draft':'human-review-required',
    reviewReasons:facts.articles.length?[]:['No supporting article; human review required']});
}

/** Validate schema AND the exact retrieved ticket/citations. This does not prove
 * every free-text statement is factual: independent review is still required. */
export function validateGroundedTriage(candidate:unknown, retrieved:GatheredEvidence) {
  const facts=validateRetrievedFacts(retrieved);
  const parsed=evidence.parse(candidate);
  if(parsed.ticketId!==facts.ticket.id) throw new Error('ticket_mismatch');
  const allowed=new Set(facts.articles.map(article=>article.id));
  if(new Set(parsed.articleIds).size!==parsed.articleIds.length) throw new Error('duplicate_citation');
  if(parsed.articleIds.some(id=>!allowed.has(id))) throw new Error('unsupported_citation');
  if(allowed.size && !parsed.articleIds.length) throw new Error('missing_grounded_citation');
  if(!allowed.size && !parsed.unresolved.length) throw new Error('missing_evidence_must_be_unresolved');
  return parsed;
}

/** Bind the actual returned ticket to the original caller's requested ID. */
export function parseRequestedTicketResponse(requestedTicketId:string,response:unknown) {
  const requested=input.parse({ticketId:requestedTicketId});
  const parsed=ticketResponse.parse(response);
  if(parsed.ticket.id!==requested.ticketId) throw new Error('requested_ticket_mismatch');
  return parsed;
}

/** Genuine typed Tool execution, not localEvidence masquerading as a tool run. */
export async function gatherUsingTools(ticketId:string):Promise<GatheredEvidence> {
  const args=input.parse({ticketId});
  const ticket=parseRequestedTicketResponse(args.ticketId,await lookupTicket.execute!(args,{})).ticket;
  const articles=articleResponse.parse(await findArticles.execute!({productId:ticket.product_id},{})).articles;
  return gatheredEvidence.parse({ticket,articles});
}

/** Retained direct fixture reference for comparison tests only; workflow uses tools. */
export function localEvidence(ticketId:string) {
  const ticket=data.tickets.find(t=>t.id===ticketId); if(!ticket) throw new Error('unknown_ticket');
  const articles=data.articles.filter(a=>a.product_id===ticket.product_id);
  return validateGroundedTriage({ticketId,summary:ticket.summary,articleIds:articles.map(a=>a.id),
    unresolved:articles.length?[]:['No supporting article']},{ticket,articles});
}
const lookup=createStep({id:'lookup-ticket-tool',inputSchema:input,outputSchema:ticketResponse,
  execute:async ({inputData})=>{
    const args=input.parse(inputData);
    return parseRequestedTicketResponse(args.ticketId,await lookupTicket.execute!(args,{}));
  }});
const articles=createStep({id:'find-articles-tool',inputSchema:ticketResponse,outputSchema:gatheredEvidence,
  execute:async ({inputData})=>{
    const {ticket}=ticketResponse.parse(inputData);
    const result=articleResponse.parse(await findArticles.execute!({productId:ticket.product_id},{}));
    return gatheredEvidence.parse({ticket,articles:result.articles});
  }});
const review=createStep({id:'bounded-source-review',inputSchema:gatheredEvidence,outputSchema:reviewedEvidence,
  execute:async({inputData})=>reviewGatheredEvidence(inputData)});
const compose=createStep({id:'validate-evidence-draft',inputSchema:reviewedEvidence,outputSchema:evidence,
  execute:async ({inputData})=>{
    const facts=reviewedEvidence.parse(inputData);
    return validateGroundedTriage({ticketId:facts.ticket.id,summary:facts.ticket.summary,
      articleIds:facts.articles.map(article=>article.id),
      unresolved:facts.reviewReasons},facts);
  }});
export const workflow=createWorkflow({id:'academy-triage-evidence',inputSchema:input,outputSchema:evidence})
  .then(lookup).then(articles).then(review).then(compose).commit();

/** Actual SDK model invocation boundary. Offline SDK tests use ONLY the
 * explicitly scripted SDK test model; no real provider answer is implied.
 * Caller must have separate provider authorization; one invocation, no app retry.
 * Return raw terminal SDK response for real evidence, never manufacture a result.
 */
export async function generateValidatedTriage(agent:Agent, options:{
  ticketId:string;resourceId:string;threadId:string;providerCallApproved:boolean
}) {
  if(options.providerCallApproved!==true) throw new Error('Explicit provider-call approval required');
  if(!/^academy-[a-z0-9-]+$/.test(options.resourceId)||!/^academy-[a-z0-9-]+$/.test(options.threadId))
    throw new Error('Academy synthetic resource/thread IDs required');
  const facts=await gatherUsingTools(options.ticketId);
  const response=await agent.generate(
    'Draft triage for this synthetic ticket using only the retrieved evidence. '
      +'Cite only the supplied article IDs and report unresolved facts. '+JSON.stringify(facts),
    {memory:{thread:options.threadId,resource:options.resourceId},structuredOutput:{schema:evidence}});
  const validated=validateGroundedTriage(await response.object,facts);
  return {validated,retrieved:facts,rawResponse:response};
}
export function buildAgent(model:string, databaseUrl:string = 'file:./academy-triage.db') {
  if(!model) throw new Error('Explicit provider/model required');
  return new Agent({id:'academy-triage',name:'Academy triage',model,
    instructions:'Use the ticket and article tools; cite only retrieved IDs. Draft only; report unknowns.',
    memory:new Memory({storage:new LibSQLStore({id:'academy-triage-store',url:databaseUrl}),options:{lastMessages:10}}),
    tools:{lookupTicket,findArticles}});
}
