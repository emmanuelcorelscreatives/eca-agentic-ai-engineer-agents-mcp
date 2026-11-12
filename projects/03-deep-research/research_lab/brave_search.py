"""Concrete Brave Web Search adapter. Required live lesson observation is separate.

Primary API contract checked 2026-11-12:
https://api-dashboard.search.brave.com/api-reference/web/search/get
https://api-dashboard.search.brave.com/app/documentation/web-search
GET /res/v1/web/search?q=...&count=..., X-Subscription-Token header,
web.results[].{title,url,description}; description is a search snippet, not a page.
"""
import asyncio
from datetime import datetime, timezone
import hashlib
import html
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, build_opener
from .transports import NoRedirect
from .contracts_v2 import validate_source

class BraveSearch:
    identity='brave-web-search-v1'
    def __init__(self, token, *, enabled=False, opener=None):
        if not enabled or not isinstance(token,str) or not token or '\r' in token or '\n' in token:
            raise ValueError('explicit live-search consent and separate credential required')
        self.token=token;self.opener=opener or build_opener(NoRedirect())
    def request(self, query):
        if not 1<=len(query['text'])<=600 or len(query['text'].split())>75:
            raise ValueError('Brave query exceeds documented limits')
        request=Request('https://api.search.brave.com/res/v1/web/search?'+urlencode({'q':query['text'],'count':5}),headers={'Accept':'application/json','X-Subscription-Token':self.token})
        with self.opener.open(request,timeout=15) as response:
            raw=response.read(2_000_001)
        if len(raw)>2_000_000:raise ValueError('oversized provider response')
        body=json.loads(raw); results=body.get('web',{}).get('results',[])
        if not isinstance(results,list):raise ValueError('invalid Brave web.results')
        retrieved=datetime.now(timezone.utc).isoformat(); sources=[]
        for row in results[:5]:
            # Keep excerpt as returned text; HTML is removed for textual display only.
            description=html.unescape(re.sub('<[^>]*>','',row.get('description','')))
            if not description:continue
            source={'schema_version':2,'id':'brave-'+hashlib.sha256(row['url'].encode()).hexdigest(),
                    'query_id':query['id'],'task_id':query['task_id'],'provider':self.identity,
                    'title':row['title'],'url':row['url'],'published':None,'retrieved':retrieved,
                    'text':description,'scope':'search-result snippet only; page not retrieved',
                    'content_kind':'search_snippet','link_status':'not_checked'}
            sources.append(validate_source(source))
        return {'sources':sources,'raw_response':body,'raw_sha256':hashlib.sha256(raw).hexdigest(),
                'retrieved':retrieved,'query_id':query['id'],'provider':self.identity}
    async def search(self, query):
        # No automatic retries. An interrupted or timed-out call has unknown outcome.
        return await asyncio.to_thread(self.request,query)
