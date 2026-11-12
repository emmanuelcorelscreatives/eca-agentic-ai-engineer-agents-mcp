"""Explicit HTTP chat-completions protocol adapter; zero requests on import."""
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

class HTTPJudgeProvider:
    def __init__(self, *, endpoint, token, envelope_path, timeout=30, trace=None):
        parsed = urlsplit(endpoint)
        if parsed.scheme != 'https' or parsed.username or parsed.password or not parsed.hostname:
            raise ValueError('explicit HTTPS endpoint without embedded credentials required')
        if not token or not 0 < timeout <= 120: raise ValueError('token and bounded timeout required')
        self.endpoint=endpoint; self.token=token; self.envelope_path=Path(envelope_path)
        self.timeout=timeout; self.trace=trace

    def __call__(self, *, model, rubric, output):
        request_body={'model':model, 'messages':[
            {'role':'system','content':'Evaluate only the supplied text. Return JSON with exactly the rubric dimensions, each containing integer score 0..2 and evidence_quote copied from the text. No tool use. Rubric: '+json.dumps(rubric,sort_keys=True)},
            {'role':'user','content':output}], 'response_format':{'type':'json_object'}}
        # Exclusive intent also preserves unknown outcomes if the outer caller is interrupted.
        with os.fdopen(os.open(self.envelope_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as stream:
            json.dump({'status':'dispatch_intent','model':model},stream); stream.flush(); os.fsync(stream.fileno())
        def invoke(*,model,payload):
            request=Request(self.endpoint,data=json.dumps(payload).encode(),method='POST',
                            headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json'})
            # No retry/fallback/redirect: redirect could leak credentials or create a duplicate.
            from urllib.request import HTTPRedirectHandler, build_opener
            class NoRedirect(HTTPRedirectHandler):
                def redirect_request(self,*args,**kwargs): return None
            with build_opener(NoRedirect()).open(request,timeout=self.timeout) as response:
                raw=response.read(2_000_001)
            if len(raw)>2_000_000: raise ValueError('provider response too large')
            body=json.loads(raw)
            with self.envelope_path.open('w') as stream:
                json.dump({'status':'received','model':model,'raw_response':body},stream)
                stream.flush(); os.fsync(stream.fileno())
            return body
        if self.trace is None: response=invoke(model=model,payload=request_body)
        else:
            from .tracing import dispatch_model
            response=dispatch_model(self.trace,invoke,model=model,payload=request_body)
        return response['choices'][0]['message']['content']
