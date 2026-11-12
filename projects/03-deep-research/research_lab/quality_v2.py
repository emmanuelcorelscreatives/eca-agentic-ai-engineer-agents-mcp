"""Source-quality observations and human-annotated report rubric; no fake link checks."""
from datetime import datetime
from urllib.parse import urlparse
import re

INJECTION=re.compile(r'ignore (?:all |previous |prior )?instructions|reveal (?:your |the )?(?:secret|system prompt)|send .*api.?key',re.I)

def assess_sources(sources, *, as_of, max_age_days=365):
    now=datetime.fromisoformat(as_of.replace('Z','+00:00')); rows=[]
    for source in sources:
        issues=[]
        if source['published'] is None:issues.append('publication_date_unknown')
        else:
            published=datetime.fromisoformat(source['published'].replace('Z','+00:00'))
            age=(now.date()-published.date()).days
            if age<0:issues.append('future_publication_date')
            if age>max_age_days:issues.append('stale_for_requested_freshness')
        if source['link_status']=='observed_broken':issues.append('observed_broken_link')
        elif source['link_status']=='not_checked':issues.append('link_not_checked')
        if INJECTION.search(source['text']):issues.append('untrusted_instruction_in_source')
        if source['content_kind']=='search_snippet':issues.append('snippet_not_full_document')
        rows.append({'source_id':source['id'],'issues':issues,'usable_as_instruction':False,
                     'usable_as_evidence':not any(i in issues for i in ('observed_broken_link','untrusted_instruction_in_source','future_publication_date'))})
    return rows

def scope_comparison(left,right):
    """Do not equate a monthly pilot estimate with annual production spend."""
    if left['scope']!=right['scope']:
        return {'status':'incomparable','reason':'measurement scope differs; normalize with attributed evidence before comparison'}
    return {'status':'comparable_scope','reason':'matching stated scope does not prove matching methods or truth'}

def annotated_rubric(bundle, annotation):
    """Human scores must include evidence-linked rationales, not inferred count scores."""
    dimensions=('relevance','source_diversity','coverage','organization','factual_support')
    if annotation.get('kind')!='human_rubric' or not annotation.get('reviewer'):
        raise ValueError('attributed human annotation required')
    allowed={e['id'] for e in bundle['evidence']};out={}
    for dimension in dimensions:
        row=annotation['scores'][dimension]
        if type(row['score']) is not int or not 0<=row['score']<=4 or not row['reason'].strip():
            raise ValueError('score 0..4 and reason required: '+dimension)
        if not set(row['evidence_ids'])<=allowed:raise ValueError('annotation has unknown evidence id')
        if dimension=='factual_support' and row['score']>0 and not row['evidence_ids']:
            raise ValueError('positive support score needs evidence')
        out[dimension]=row
    return {'kind':'human_rubric','reviewer':annotation['reviewer'],'scores':out,
            'independent_truth_verified':False,'limitations':'A human rubric judgment is attributable interpretation, not an automated truth certificate.'}

def trace_summary(events):
    spans=[e for e in events if e.get('status') in ('COMPLETE','FAILED','UNKNOWN','INVALID')]
    measured=[e['duration_seconds'] for e in spans if e.get('duration_seconds') is not None]
    tokens=[e.get('tokens') for e in spans]
    return {'completed_span_count':len(spans),'measured_span_seconds_sum':sum(measured),
            'wall_clock_note':'Parallel span sums can exceed wall-clock run duration.',
            'slowest_span':max(spans,key=lambda e:e.get('duration_seconds') or 0,default=None),
            'provider_tokens':sum(tokens) if tokens and all(type(t) is int for t in tokens) else None,
            'unknown_usage_span_count':sum(t is None for t in tokens)}
