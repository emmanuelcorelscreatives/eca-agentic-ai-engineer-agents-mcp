/** Actual native Memory/LibSQL lifecycle, no model or simulated conversation. */
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';
import type { MastraDBMessage } from '@mastra/core/agent';
export async function openAcademyMemory(databaseUrl:string) {
  if(!databaseUrl.startsWith('file:')) throw new Error('Use a local Academy file database');
  const storage=new LibSQLStore({id:'academy-session-store',url:databaseUrl});
  await storage.init();
  const memory=new Memory({storage,options:{lastMessages:10,semanticRecall:false}});
  return {memory,storage,close:async()=>{await memory.settled();await storage.close();}};
}
export async function saveSyntheticContext(memory:Memory, resourceId:string, threadId:string, text:string) {
  if(!/^academy-[a-z0-9-]+$/.test(resourceId)||!/^academy-[a-z0-9-]+$/.test(threadId))
    throw new Error('Academy synthetic resource/thread IDs required');
  const existing=await memory.getThreadById({threadId,resourceId});
  if(!existing) await memory.createThread({threadId,resourceId,title:'Synthetic support-ticket exercise'});
  const message:MastraDBMessage={id:crypto.randomUUID(),role:'user',createdAt:new Date(),
    resourceId,threadId,content:{format:2,parts:[{type:'text',text}]}};
  await memory.saveMessages({messages:[message]});
}
