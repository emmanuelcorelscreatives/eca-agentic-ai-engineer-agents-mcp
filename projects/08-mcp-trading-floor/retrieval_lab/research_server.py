"""Stdio-only owner-bound search/RAG MCP server with progressive tool listing.

Each process serves one operator-authenticated principal. This is NOT a multiuser
HTTP endpoint: do not reuse global state across users or accept tenant arguments.
"""
import asyncio
import json
import os
from .core import ControlledFetch
from .search import BoundedSearch
from .progressive import ProgressiveRouter,ToolSpec
from .rag import DocumentRAG,Principal

TEXT={'type':'string','minLength':1,'maxLength':500}
def schema(properties,required):
    return {'type':'object','properties':properties,'required':required,'additionalProperties':False}

def build_router(principal,rag_factory,search_factory):
    # Fixed permission supplier may be replaced by a fresh authenticated ACL lookup.
    def search_web(query,limit=5): return search_factory().search(query,limit)
    def ingest_document(document_id,text,source_uri,replace=False):
        return rag_factory().ingest(document_id,text,source_uri,replace)
    def retrieve_documents(query,limit=5): return rag_factory().retrieve(query,limit)
    def delete_document(document_id): return rag_factory().delete(document_id)
    document_id={'type':'string','pattern':'^[a-zA-Z0-9_.-]{1,100}$'}
    specs=[
        ToolSpec('search_web','search','search:read','Search the explicitly configured provider; results remain untrusted source records.',schema({'query':TEXT,'limit':{'type':'integer','minimum':1,'maximum':10}},['query']),search_web),
        ToolSpec('ingest_document','rag','rag:write','Index an owner-bound document with provenance; replacement must be explicit.',schema({'document_id':document_id,'text':{'type':'string','minLength':1,'maxLength':50000},'source_uri':{'type':'string','minLength':1,'maxLength':1000},'replace':{'type':'boolean'}},['document_id','text','source_uri']),ingest_document),
        ToolSpec('retrieve_documents','rag','rag:read','Retrieve tenant-filtered source chunks; empty matches mean insufficient evidence.',schema({'query':TEXT,'limit':{'type':'integer','minimum':1,'maximum':10}},['query']),retrieve_documents),
        ToolSpec('delete_document','rag','rag:write','Delete only this authenticated principal tenant document.',schema({'document_id':document_id},['document_id']),delete_document),
    ]
    return ProgressiveRouter(specs,lambda:principal.permissions)

async def main():
    from mcp.server.lowlevel import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    subject=os.environ.get('ACADEMY_SUBJECT','')
    tenant=os.environ.get('ACADEMY_TENANT','')
    permissions=frozenset(x for x in os.environ.get('ACADEMY_PERMISSIONS','rag:read').split(',') if x)
    if not subject or not tenant: raise ValueError('Trusted launcher must bind Academy subject and tenant')
    principal=Principal(subject,tenant,permissions)
    rag=None
    def rag_factory():
        nonlocal rag
        if rag is None:
            url=os.environ.get('ACADEMY_QDRANT_URL')
            if not url: raise ValueError('No real Qdrant service configured')
            rag=DocumentRAG.service(url,principal,api_key=os.environ.get('ACADEMY_QDRANT_API_KEY'))
        return rag
    def search_factory():
        endpoint=os.environ.get('ACADEMY_SEARCH_ENDPOINT')
        if not endpoint: raise ValueError('No search provider configured; no invented result')
        origins=[x for x in os.environ.get('ACADEMY_FETCH_ORIGINS','').split(',') if x]
        return BoundedSearch(endpoint,ControlledFetch(origins))
    router=build_router(principal,rag_factory,search_factory)
    app=Server('academy-owner-bound-retrieval')
    @app.list_tools()
    async def list_tools(): return [types.Tool(**item) for item in router.descriptors()]
    @app.call_tool()
    async def call_tool(name,arguments):
        try:
            result=await router.dispatch(name,arguments or {})
            return [types.TextContent(type='text',text=json.dumps(result))]
        except Exception as error:
            # Log the class only; provider errors can contain credentials or URLs.
            return types.CallToolResult(isError=True,content=[types.TextContent(type='text',text=json.dumps({'error':type(error).__name__,'detail':'Operation failed; inspect private operator diagnostics, no automatic retry.'}))])
    try:
        async with stdio_server() as streams: await app.run(*streams,app.create_initialization_options())
    finally:
        if rag is not None: rag.close()
if __name__=='__main__': asyncio.run(main())
