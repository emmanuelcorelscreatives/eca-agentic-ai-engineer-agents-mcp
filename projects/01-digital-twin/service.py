"""Application boundary composing truthful answer/contact/status workflows."""
from collections import defaultdict,deque
from pathlib import Path
import threading
import time
from prompts import IDENTITY
from status import Checklist
from tools import ToolsService
from twin import DigitalTwin

class RateLimiter:
    def __init__(self,limit,clock=time.monotonic):
        self.limit=limit;self.clock=clock;self.events=defaultdict(deque);self.lock=threading.Lock()
    def check(self,session):
        with self.lock:
            now=self.clock()
            for key in list(self.events):
                if not self.events[key] or self.events[key][-1]<=now-60:del self.events[key]
            if session not in self.events and len(self.events)>=10000:raise PermissionError('service session capacity reached')
            events=self.events[session]
            while events and events[0]<=now-60:events.popleft()
            if len(events)>=self.limit:raise PermissionError('request limit reached; wait before trying again')
            events.append(now)

class TwinService:
    def __init__(self,sections,settings):
        self.sections=sections;self.settings=settings
        self.limiter=RateLimiter(settings.request_limit_per_minute)
    def _tools(self):
        path=Path(self.settings.database)
        if self.settings.database!=':memory:':path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        tools=ToolsService(self.settings.database)
        if self.settings.database!=':memory:':path.chmod(0o600)
        return tools
    def answer(self,session,question):
        self.limiter.check(session)
        core=DigitalTwin(self.sections)
        try:
            if question.strip().lower() in ('who are you?','who are you','are you amara?','are you amara'):
                return {'answer':IDENTITY,'citations':[],'status':'identity_disclosure'}
            result=core.answer(question)
            return {**result,'identity':IDENTITY}
        finally:core.db.close()
    async def answer_with_model(self,session,question,history=()):
        if not self.settings.live_model_enabled:raise PermissionError('live model has not been explicitly enabled')
        self.limiter.check(session)
        from agents_adapter import answer
        return await answer(question,self.settings.model,history=history)
    def contact_events(self,session,call_id,name,email,message,consent,opportunity=''):
        self.limiter.check(session)
        checklist=Checklist(task_id=call_id)
        yield checklist.visible()
        if consent is not True:
            checklist.update('consent','failed');checklist.finish('consent_required');yield checklist.visible();return
        checklist.update('consent','passed');yield checklist.visible()
        tools=None
        try:
            tools=self._tools()
            result=tools.record_lead(call_id,name,email,message,consent,opportunity)
            if result.get('status')!='stored_locally':raise ValueError('This action ID is retired; use an explicitly new request after reviewing consent.')
            checklist.update('validation','passed');checklist.update('storage','passed')
            notification_receipt=None
            if self.settings.notification_mode=='dry_run':
                notification_receipt=tools.dispatch_once(result['outbox_id'])
                checklist.update('notification','passed' if notification_receipt['status']=='dry_run' else 'unknown')
                notice='Stored with consent. Notification was simulated locally; no external send is claimed.'
            else:
                checklist.update('notification','queued')
                notice='Stored with consent. Owner notification is queued locally; no external send is claimed.'
            checklist.finish('complete')
            yield {**checklist.visible(),'receipt':result,'notification_receipt':notification_receipt,'notice':notice}
        except (ValueError,TypeError,PermissionError) as error:
            checklist.update('validation','failed');checklist.finish('failed');yield {**checklist.visible(),'error':str(error)}
        except Exception as error:
            checklist.update('storage','unknown');checklist.finish('unknown');yield {**checklist.visible(),'error_type':type(error).__name__,'notice':'Action outcome is unresolved; inspect the exact call receipt before retrying.'}
        finally:
            if tools is not None:tools.close()
    def capture_question(self,session,call_id,question,consent):
        self.limiter.check(session);tools=self._tools()
        try:return tools.capture_question(call_id,question,consent)
        finally:tools.close()
    def health(self):
        return {'status':'ok','service':'academy-fictional-twin','external_notifications_enabled':False,'retention_days':self.settings.retention_days,'model_enabled':self.settings.live_model_enabled}
