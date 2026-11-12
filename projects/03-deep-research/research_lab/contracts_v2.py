"""Version-two boundary schemas. Validation failures retain an exact field path."""
from urllib.parse import urlparse

VERSION = 2
class ContractError(ValueError): pass

def version(value,path):
    _check(type(value) is int and value==VERSION,path,'unsupported version')

def references(value,path):
    _check(isinstance(value,list),path,'list of unique string identifiers required')
    for item in value:text(item,path)
    _check(len(set(value))==len(value),path,'duplicate identifier')
    return value

def _check(test, path, detail):
    if not test: raise ContractError(f'{path}: {detail}')
def text(value, path, maximum=10000):
    _check(isinstance(value,str) and bool(value.strip()) and len(value)<=maximum,path,'nonempty bounded string required')
    return value

def object_keys(value, fields, path):
    _check(isinstance(value,dict),path,'object required')
    _check(set(value)==set(fields),path,f'exact fields required: {sorted(fields)}')

def validate_plan(plan):
    object_keys(plan,('schema_version','question','scope','acceptance','tasks'), 'plan')
    version(plan['schema_version'],'plan.schema_version')
    text(plan['question'],'plan.question',4000); text(plan['scope'],'plan.scope')
    _check(isinstance(plan['acceptance'],list) and 1<=len(plan['acceptance'])<=10,'plan.acceptance','1..10 criteria required')
    for i,value in enumerate(plan['acceptance']): text(value,f'plan.acceptance[{i}]')
    _check(isinstance(plan['tasks'],list) and 1<=len(plan['tasks'])<=8,'plan.tasks','1..8 tasks required')
    ids=[]; edges={}
    for i,task in enumerate(plan['tasks']):
        path=f'plan.tasks[{i}]';object_keys(task,('id','objective','dependencies','completion'),path)
        for field in ('id','objective','completion'): text(task[field],path+'.'+field)
        references(task['dependencies'],path+'.dependencies')
        ids.append(task['id']); edges[task['id']]=task['dependencies']
    _check(len(set(ids))==len(ids),'plan.tasks','duplicate task id')
    visiting=set(); done=set()
    def visit(key):
        _check(key in edges,'plan.tasks.dependencies','unknown dependency')
        _check(key not in visiting,'plan.tasks.dependencies','cycle')
        if key in done:return
        visiting.add(key)
        for item in edges[key]:visit(item)
        visiting.remove(key);done.add(key)
    for key in ids:visit(key)
    return plan

def validate_query(query, plan):
    object_keys(query,('schema_version','id','task_id','intent','text'),'query')
    version(query['schema_version'],'query.schema_version')
    for field in ('id','task_id','text'):text(query[field],'query.'+field,4000)
    _check(query['task_id'] in {t['id'] for t in plan['tasks']},'query.task_id','unknown task')
    _check(query['intent'] in ('support','counterevidence'),'query.intent','invalid enum')
    return query

def validate_source(source):
    fields=('schema_version','id','query_id','task_id','provider','title','url','published','retrieved','text','scope','content_kind','link_status')
    object_keys(source,fields,'source')
    version(source['schema_version'],'source.schema_version')
    for field in ('id','query_id','task_id','provider','title','text','scope'):text(source[field],'source.'+field)
    text(source['url'],'source.url');url=urlparse(source['url'])
    _check(url.scheme in ('http','https') and bool(url.hostname) and not url.username and not url.password,'source.url','public web location required')
    for field in ('published','retrieved'):
        if source[field] is not None:
            from datetime import datetime
            try: datetime.fromisoformat(source[field].replace('Z','+00:00'))
            except (TypeError,ValueError): raise ContractError('source.'+field+': ISO date/time or null required')
    _check(source['content_kind'] in ('synthetic_document','search_snippet','retrieved_document'),'source.content_kind','invalid enum')
    _check(source['link_status'] in ('not_checked','observed_ok','observed_broken'),'source.link_status','invalid enum')
    return source

def validate_evidence(evidence, sources):
    object_keys(evidence,('schema_version','id','source_id','excerpt','start','end'),'evidence')
    version(evidence['schema_version'],'evidence.schema_version')
    text(evidence['source_id'],'evidence.source_id')
    source=next((s for s in sources if s['id']==evidence['source_id']),None)
    _check(source is not None,'evidence.source_id','dangling source reference')
    start,end=evidence['start'],evidence['end']
    _check(type(start) is int and type(end) is int and 0<=start<end<=len(source['text']),'evidence.offsets','invalid substring range')
    text(evidence['id'],'evidence.id');text(evidence['excerpt'],'evidence.excerpt')
    _check(source['text'][start:end]==evidence['excerpt'],'evidence.excerpt','not an exact source substring')
    return evidence

def validate_analysis(analysis, evidence):
    object_keys(analysis,('schema_version','findings','uncertainties'),'analysis')
    version(analysis['schema_version'],'analysis.schema_version')
    _check(isinstance(analysis['findings'],list),'analysis.findings','list required')
    _check(isinstance(analysis['uncertainties'],list),'analysis.uncertainties','list required')
    ids={e['id'] for e in evidence}
    for i, finding in enumerate(analysis['findings']):
        p=f'analysis.findings[{i}]';object_keys(finding,('claim','status','evidence_ids','measurement_scope'),p)
        text(finding['claim'],p+'.claim'); text(finding['measurement_scope'],p+'.measurement_scope')
        _check(finding['status'] in ('supported','conflicting','insufficient','incomparable'),p+'.status','invalid enum')
        references(finding['evidence_ids'],p+'.evidence_ids')
        _check(set(finding['evidence_ids'])<=ids,p+'.evidence_ids','dangling evidence reference')
        if finding['status'] in ('supported','conflicting','incomparable'):
            _check(bool(finding['evidence_ids']),p+'.evidence_ids','attribution required')
    for uncertainty in analysis['uncertainties']:text(uncertainty,'analysis.uncertainties')
    return analysis

def validate_report(report, evidence):
    object_keys(report,('schema_version','title','sections'),'report')
    version(report['schema_version'],'report.schema_version')
    text(report['title'],'report.title');required={'question','method','findings','limitations','recommendation','references'}
    _check(isinstance(report['sections'],list),'report.sections','list required')
    for section in report['sections']:
        _check(isinstance(section,dict),'report.sections','section object required')
    _check({s.get('kind') for s in report['sections']}==required and len(report['sections'])==6,'report.sections','exactly six required section kinds')
    ids={e['id'] for e in evidence}
    for section in report['sections']:
        object_keys(section,('kind','text','evidence_ids'),'report.section')
        text(section['text'],'report.section.text',2_000_000)
        references(section['evidence_ids'],'report.section.evidence_ids')
        _check(set(section['evidence_ids'])<=ids,'report.section.evidence_ids','dangling evidence reference')
    return report
