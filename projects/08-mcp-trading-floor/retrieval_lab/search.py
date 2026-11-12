"""Normalized bounded real search provider; no fixture-as-live fallback."""
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from hashlib import sha256
from urllib.parse import urlencode
from urllib.error import HTTPError
import json
import socket
import unicodedata
from .core import ControlledFetch,RetrievalError

class SearchFailure(RetrievalError):
    def __init__(self,code): self.code=code; super().__init__(code)

class BoundedSearch:
    def __init__(self,endpoint,fetcher:ControlledFetch):
        if fetcher.origin(endpoint) not in fetcher.origins: raise SearchFailure('ENDPOINT_DENIED')
        self.endpoint=endpoint;self.fetcher=fetcher
    def search(self,query,limit=5):
        if not isinstance(query,str) or type(limit) is not int or not 1<=limit<=10: raise SearchFailure('INVALID_ARGUMENT')
        query=' '.join(unicodedata.normalize('NFKC',query).split())
        if not query or len(query)>500: raise SearchFailure('INVALID_ARGUMENT')
        separator='&' if '?' in self.endpoint else '?'
        try:
            body,kind=self.fetcher.read(self.endpoint+separator+urlencode({'q':query,'format':'json'}))
        except Exception as error:
            cause=error.__cause__ if isinstance(error,RetrievalError) else error
            if isinstance(cause,HTTPError): raise SearchFailure('RATE_LIMIT' if cause.code==429 else 'HTTP_FAILURE') from None
            if isinstance(cause,(TimeoutError,socket.timeout)): raise SearchFailure('TIMEOUT') from None
            raise SearchFailure('PROVIDER_UNAVAILABLE') from None
        try:
            payload=json.loads(body)
            if kind!='application/json' or not isinstance(payload,dict) or not isinstance(payload.get('results'),list): raise ValueError()
            results=[]
            for item in payload['results'][:limit]:
                if not isinstance(item,dict) or not all(isinstance(item.get(k),str) for k in ('title','url','content')): raise ValueError()
                ControlledFetch.origin(item['url'])
                if len(item['title'])>500 or len(item['url'])>2000 or len(item['content'])>5000: raise ValueError()
                results.append({key:item[key] for key in ('title','url','content')})
        except (ValueError,TypeError) as error: raise SearchFailure('INVALID_RESPONSE') from error
        return {'query':query,'results':results,'empty':not results,'retrieved_at':datetime.now(timezone.utc).isoformat(),
                'provider':self.endpoint,'response_sha256':sha256(body.encode()).hexdigest(),
                'provenance':'observed configured provider HTTP response; fixture providers must be labeled by operator'}
