import { MCPClient } from '@mastra/mcp';
import { Agent } from '@mastra/core/agent';
import { fileURLToPath } from 'node:url';
export const ARTICLE_TOOL_NAMES = ['articles_lookup_ticket','articles_search_articles'] as const;
// The server is Academy-owned, read-only and receives no model credentials.
export function makeMcpClient(python:string) {
  if (!python || !python.startsWith('/')) throw new Error('Supply an absolute Python interpreter');
  const root=fileURLToPath(new URL('../../',import.meta.url));
  return new MCPClient({ id:'academy-articles', registerProcessHooks:false, servers:{
    articles:{ command:python,args:['-m','examples.s24_mcp_articles'],
      cwd:root, env:{PYTHONPATH:root}, inheritDefaultEnv:false }
  } });
}
export type ArticleTools = Awaited<ReturnType<MCPClient['listTools']>>;
export function selectArticleTools(discovered:ArticleTools):ArticleTools {
  const selected:ArticleTools={};
  for (const key of ARTICLE_TOOL_NAMES) {
    if (!Object.hasOwn(discovered,key)) throw new Error(`Missing required MCP tool: ${key}`);
    selected[key]=discovered[key];
  }
  // Extra server tools, including future mutations, never reach the Agent.
  return selected;
}
export async function withArticleTools<T>(python:string, run:(tools:ArticleTools)=>Promise<T>) {
  const client=makeMcpClient(python);
  try { return await run(selectArticleTools(await client.listTools())); }
  finally { await client.disconnect(); }
}
export async function withMcpAgent<T>(python:string, model:string,
    run:(agent:Agent, tools:ArticleTools)=>Promise<T>) {
  if(!model) throw new Error('Explicit provider/model required');
  return withArticleTools(python, async tools=>{
    const agent=new Agent({id:'academy-mcp-triage',name:'Academy MCP triage',model,
      instructions:'Use only retrieved synthetic ticket/article evidence. Cite actual IDs; draft only. Report unknowns.',tools});
    return run(agent,tools);
  });
}
