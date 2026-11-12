"""V3 selective recovery; v2 source and proofs remain immutable."""
import asyncio
from .pipeline_v2 import make_queries, evidence_for, template_report, _value, now
from .contracts_v2 import validate_plan, validate_source, validate_evidence, validate_analysis, validate_report
from .quality_v2 import assess_sources
from .recovery_v3 import RecoveryJournal
async def run_research(question,backend,planner,analyst,directory,*,input_manifest,workers=3,callback=None,cancel_event=None,recovery_authorizations=None,executor_identity=None):
    if not isinstance(question,str) or not 1<=len(question.strip())<=4000:raise ValueError('question must have 1..4000 characters')
    if not 1<=workers<=8:raise ValueError('workers must be 1..8')
    if not isinstance(input_manifest,dict) or not input_manifest.get('source_revision') or not isinstance(input_manifest.get('source_ids'),list):
        raise ValueError('exact source revision and explicit source_ids required')
    identity={'question':question.strip(),'backend':backend.identity,'input_manifest':input_manifest}
    journal=RecoveryJournal(directory,identity,authorizations=recovery_authorizations,executor_identity=executor_identity)
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
