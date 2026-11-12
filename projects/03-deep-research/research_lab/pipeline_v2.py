"""Durable per-phase/per-query orchestration. No automatic UNKNOWN replay.

Callers supply an explicit planner, search backend and analyst. SDK implementations
live in sdk_v2; fixture callbacks in tests are not represented as AI observations.
"""
import asyncio
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError
from .contracts_v2 import validate_plan, validate_query, validate_source, validate_evidence, validate_analysis, validate_report
from .quality_v2 import assess_sources

class UnknownOutcome(RuntimeError):pass
class RecordedFailure(RuntimeError):pass

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()

def make_queries(plan):
    rows=[];seen=set()
    for task in plan['tasks']:
        for intent,suffix in (('support','evidence'),('counterevidence','limitations alternatives')):
            query={'schema_version':2,'id':task['id']+'-'+intent,'task_id':task['id'],
                   'intent':intent,'text':f"{plan['question']} {task['objective']} {suffix}"}
            normalized=' '.join(query['text'].lower().split())
            if normalized not in seen:rows.append(validate_query(query,plan));seen.add(normalized)
    return rows

class Journal:
    def __init__(self,directory,identity):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.path=self.directory/'state-v2.json'; self.identity=identity
        self.state=None
    @contextmanager
    def lock(self):
        descriptor=os.open(self.directory/'owner.lock',os.O_CREAT|os.O_RDWR,0o600)
        try:
            try:fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise RecordedFailure('another owner holds this exact run')
            if self.path.exists():
                self.state=json.loads(self.path.read_text())
                if self.state.get('schema_version')!=2 or self.state.get('identity')!=self.identity:
                    raise ValueError('checkpoint question/config/source identity mismatch')
            else:self.state={'schema_version':2,'identity':self.identity,'steps':{},'events':[]}
            yield self
        finally:os.close(descriptor)
    def save(self):
        temporary=self.directory/'state-v2.json.tmp'
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w') as handle:
            json.dump(self.state,handle,sort_keys=True);handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,self.path)
        fd=os.open(self.directory,os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    async def step(self,name,inputs,operation,validate,callback=None):
        expected=digest(inputs);existing=self.state['steps'].get(name)
        if existing:
            if existing['input_sha256']!=expected:raise ValueError('step input changed: '+name)
            if existing['status']=='COMPLETE':
                if digest(existing['result'])!=existing['result_sha256']:raise ValueError('checkpoint result was changed: '+name)
                return validate(existing['result'])
            if existing['status'] in ('IN_FLIGHT','UNKNOWN'):raise UnknownOutcome(name+': recover original response; never replay')
            raise RecordedFailure(name+': known failed/invalid result retained; revise explicitly under a new run identity')
        started=time.monotonic();stamp=now();span='span-'+str(len(self.state['events']))+'-'+name
        entry={'status':'IN_FLIGHT','input_sha256':expected,'started_at':stamp,'span_id':span}
        self.state['steps'][name]=entry;self.save()
        if callback:callback({'phase':name,'status':'STARTED','span_id':span,'started_at':stamp})
        try:
            result=await operation()
            # Persist actual returned bytes/value before parsing/validation can fail.
            entry['raw_result']=result;self.save()
            validated=validate(result)
            entry.update(status='COMPLETE',result=validated,result_sha256=digest(validated))
        except BaseException as error:
            if isinstance(error,HTTPError):status='FAILED' # known HTTP response, not a guessed replay permission
            elif isinstance(error,ConnectionRefusedError):status='FAILED'
            elif 'raw_result' in entry:status='INVALID'
            else:status='UNKNOWN' # cancellation/timeout/process interruption can leave a charged request
            entry.update(status=status,error_type=type(error).__name__)
            raise
        finally:
            entry['ended_at']=now();entry['duration_seconds']=time.monotonic()-started
            event={'phase':name,'span_id':span,'parent_id':'research-run','status':entry['status'],
                   'started_at':stamp,'ended_at':entry['ended_at'],'duration_seconds':entry['duration_seconds'],
                   'tokens':None,'measurement':'observed local monotonic duration; provider usage not supplied'}
            self.state['events'].append(event);self.save()
            if callback:callback(event)
        return validated

async def _value(value):return value

def evidence_for(sources):
    evidence=[];seen=set()
    for source in sources:
        identity=digest({'source_id':source['id'],'text':source['text']})
        if identity in seen:continue
        seen.add(identity)
        record={'schema_version':2,'id':identity,'source_id':source['id'],
                'excerpt':source['text'],'start':0,'end':len(source['text'])}
        evidence.append(validate_evidence(record,sources))
    return evidence

def template_report(plan,evidence,analysis,quality):
    refs=[e['id'] for e in evidence]
    section=lambda kind,content,ids=[]:{'kind':kind,'text':content,'evidence_ids':list(ids)}
    return validate_report({'schema_version':2,'title':'Evidence-attributed research: '+plan['question'],
        'sections':[section('question',plan['question']),section('method','Bounded planner/search/analysis pipeline. Search snippets are not full documents.'),
                    section('findings',json.dumps(analysis['findings']) or 'No supported findings',refs),
                    section('limitations',json.dumps({'uncertainties':analysis['uncertainties'],'source_quality':quality})),
                    section('recommendation','Resolve outstanding uncertainty before making a real-world decision.'),
                    section('references',json.dumps(evidence) if evidence else 'No evidence available',refs)]},evidence)

async def run_research(question,backend,planner,analyst,directory,*,input_manifest,workers=3,callback=None,cancel_event=None):
    if not isinstance(question,str) or not 1<=len(question.strip())<=4000:raise ValueError('question must have 1..4000 characters')
    if not 1<=workers<=8:raise ValueError('workers must be 1..8')
    if not isinstance(input_manifest,dict) or not input_manifest.get('source_revision') or not isinstance(input_manifest.get('source_ids'),list):
        raise ValueError('exact source revision and explicit source_ids required')
    identity={'question':question.strip(),'backend':backend.identity,'input_manifest':input_manifest}
    journal=Journal(directory,identity)
    with journal.lock():
        def checked_plan(value):
            validate_plan(value)
            if value['question']!=question.strip():raise ValueError('planner changed the research question')
            return value
        plan=await journal.step('planning',identity,lambda:planner(question.strip()),checked_plan,callback)
        queries=make_queries(plan);sem=asyncio.Semaphore(workers)
        async def search(query):
            async with sem:
                if cancel_event is not None and cancel_event.is_set():raise asyncio.CancelledError()
                def validate(result):
                    if not isinstance(result,dict) or not isinstance(result.get('sources'),list):raise ValueError('search response requires sources')
                    for source in result['sources']:
                        validate_source(source)
                        if source['query_id']!=query['id'] or source['task_id']!=query['task_id']:raise ValueError('source/query/task attribution mismatch')
                    return result
                return await journal.step('search/'+query['id'],query,lambda:backend.search(query),validate,callback)
        completed_tasks=set();branch_map={}
        while len(completed_tasks)<len(plan['tasks']):
            ready={task['id'] for task in plan['tasks'] if task['id'] not in completed_tasks
                   and set(task['dependencies'])<=completed_tasks}
            if not ready:raise ValueError('no dependency-ready tasks')
            wave=[query for query in queries if query['task_id'] in ready]
            tasks=[asyncio.create_task(search(query)) for query in wave]
            try:results=await asyncio.gather(*tasks,return_exceptions=True)
            except BaseException:
                for task in tasks:task.cancel()
                await asyncio.gather(*tasks,return_exceptions=True)
                raise
            # Completed siblings stay committed; dependent tasks do not start after failure.
            for result in results:
                if isinstance(result,BaseException):raise result
            branch_map.update((query['id'],result) for query,result in zip(wave,results))
            completed_tasks.update(ready)
        branches=[branch_map[query['id']] for query in queries]
        sources=[];versions={}
        for branch in branches:
            for source in branch['sources']:
                old=versions.setdefault(source['id'],source['text'])
                if old!=source['text']:raise ValueError('one source id has conflicting bytes; version the source explicitly')
                sources.append(source)
        evidence=await journal.step('evidence',sources,lambda:_value(evidence_for(sources)),lambda rows:[validate_evidence(e,sources) for e in rows],callback)
        quality=assess_sources(sources,as_of=now())
        # Untrusted source text is passed as data, never used as model instructions.
        def checked_analysis(value):
            validate_analysis(value,evidence)
            unusable={row['source_id'] for row in quality if not row['usable_as_evidence']}
            denied={row['id'] for row in evidence if row['source_id'] in unusable}
            for finding in value['findings']:
                if finding['status']=='supported' and set(finding['evidence_ids']) & denied:
                    raise ValueError('supported finding cites excluded/injected/broken source')
            return value
        analysis=await journal.step('analysis',{'plan':plan,'evidence':evidence,'quality':quality},
            lambda:analyst(plan,evidence,quality),checked_analysis,callback)
        report=await journal.step('writing',{'plan':plan,'evidence':evidence,'analysis':analysis,'quality':quality},
            lambda:_value(template_report(plan,evidence,analysis,quality)),lambda value:validate_report(value,evidence),callback)
        return {'schema_version':2,'identity':identity,'plan':plan,'queries':queries,'sources':sources,
                'evidence':evidence,'analysis':analysis,'source_quality':quality,'report':report,'events':journal.state['events']}
