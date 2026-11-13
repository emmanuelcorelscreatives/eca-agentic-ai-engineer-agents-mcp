"""Shared deterministic article tools; real agent execution is opt-in."""
import json
from pathlib import Path
DATA = Path(__file__).resolve().parents[1] / 'data/s24_articles.json'

def lookup_ticket(ticket_id: str) -> dict:
    """Return one exact synthetic ticket."""
    for ticket in json.loads(DATA.read_text())['tickets']:
        if ticket['id'] == ticket_id:
            return {'ok':True,'ticket':ticket}
    return {'ok':False,'error':'unknown_ticket'}

def search_articles(product_id: str) -> dict:
    """Read only articles matching a product; unknown products have no evidence."""
    articles=[a for a in json.loads(DATA.read_text())['articles'] if a['product_id']==product_id]
    return {'articles':articles}

def triage_schema():
    """Typed response with fixture-bound citation validation, not prose approval.

    Kept lazy so importing deterministic tools does not require optional SDKs.
    The returned ticket is checked here; callers also bind the original request
    with validate_triage_response before presenting a provider-generated draft.
    """
    from pydantic import BaseModel, model_validator
    class Triage(BaseModel):
        ticket_id: str
        summary: str
        article_ids: list[str]
        unresolved: list[str]

        @model_validator(mode='after')
        def fixture_bound_citations(self):
            found = lookup_ticket(self.ticket_id)
            if not found['ok']:
                raise ValueError('unknown_ticket')
            allowed = {article['id'] for article in search_articles(
                found['ticket']['product_id'])['articles']}
            if len(set(self.article_ids)) != len(self.article_ids):
                raise ValueError('duplicate_citation')
            if any(article_id not in allowed for article_id in self.article_ids):
                raise ValueError('unsupported_citation_for_ticket')
            if allowed and not self.article_ids:
                raise ValueError('missing_evidence_ids')
            if not allowed and not self.unresolved:
                raise ValueError('missing_evidence_must_be_unresolved')
            return self

    return Triage


def validate_triage_response(candidate, *, requested_ticket_id):
    """Bind schema-validated output to the actual caller request; no model call."""
    if hasattr(candidate, 'model_dump'):
        candidate = candidate.model_dump()
    result = triage_schema().model_validate(candidate)
    if result.ticket_id != requested_ticket_id:
        raise ValueError('requested_ticket_mismatch')
    return result


def build_agno(model):
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    if not model:
        raise ValueError('Explicit model ID required')
    return Agent(name='Academy triage', model=OpenAIChat(id=model),
        tools=[lookup_ticket,search_articles], output_schema=triage_schema(),
        instructions='Use only the synthetic ticket and article tools. Cite article IDs; do not send messages.')

def build_team(model):
    from agno.agent import Agent
    from agno.team import Team
    from agno.models.openai import OpenAIChat
    researcher=Agent(name='Article researcher',model=OpenAIChat(id=model),tools=[lookup_ticket,search_articles],
        role='Find fixture-supported article evidence only')
    reviewer=Agent(name='Evidence reviewer',model=OpenAIChat(id=model),tools=[search_articles],
        role='Check cited article IDs and list unresolved facts')
    return Team(name='Academy ticket team',model=OpenAIChat(id=model),members=[researcher,reviewer],
        instructions='Coordinate evidence lookup and independent review. Produce a draft, never send it.')


def specialist_completion_summary(result):
    """Expose missing/error member runs without rewriting native Team status.

    Native Team COMPLETED means the coordinator finished, not that all required
    specialists succeeded. This checks recorded statuses/content only; neither
    a completed member nor this summary proves citations or review quality.
    Call on the retained TeamRunOutput (or its to_dict() JSON), never infer
    member success from the delegation tool_call_error flag alone.
    """
    if not isinstance(result, dict):
        result = result.to_dict()
    required = ('article-researcher', 'evidence-reviewer')
    records = []
    missing = []
    for member_id in required:
        responses = [response for response in result.get('member_responses', [])
                     if response.get('agent_id') == member_id]
        if not responses:
            missing.append(member_id)
        for response in responses:
            native_status = response.get('status')
            status = getattr(native_status, 'value', native_status)
            content = response.get('content')
            records.append({'member_id': member_id, 'run_id': response.get('run_id'),
                'native_status': status, 'reported_content': content,
                'complete_record': status == 'COMPLETED' and bool(content)})
    native_status = result.get('status')
    native_status = getattr(native_status, 'value', native_status)
    complete = native_status == 'COMPLETED' and not missing and all(
        record['complete_record'] for record in records)
    return {'native_team_status': native_status,
        'specialist_records': records, 'missing_specialists': missing,
        'outcome': 'specialist-records-complete' if complete else 'incomplete',
        'limitation': 'Recorded completion only; not evidence citation validation or factual review approval'}

def build_mcp_agent(model, **kwargs):
    """Return the genuine Agent context; use ``async with`` before execution."""
    from examples.s24_agno import build_mcp_agent as context
    return context(model, **kwargs)
