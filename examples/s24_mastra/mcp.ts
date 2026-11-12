import { MCPClient } from '@mastra/mcp';
// Start repo root as cwd; use the Python interpreter containing the pinned MCP SDK.
export function makeMcpClient(python:string) {
  if (!python || !python.startsWith('/')) throw new Error('Supply an absolute Python interpreter');
  return new MCPClient({ id:'academy-articles', servers:{ articles:{ command:python,args:['-m','examples.s24_mcp_articles'] } } });
}
export async function withArticleTools<T>(python:string, run:(tools:unknown)=>Promise<T>) {
  const client=makeMcpClient(python);
  try { return await run(await client.listTools()); } finally { await client.disconnect(); }
}
