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

def build_agno(model):
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from pydantic import BaseModel
    class Triage(BaseModel):
        ticket_id: str
        summary: str
        article_ids: list[str]
        unresolved: list[str]
    if not model:
        raise ValueError('Explicit model ID required')
    return Agent(name='Academy triage', model=OpenAIChat(id=model),
        tools=[lookup_ticket,search_articles], output_schema=Triage,
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

def build_mcp_agent(model, **kwargs):
    """Return the genuine Agent context; use ``async with`` before execution."""
    from examples.s24_agno import build_mcp_agent as context
    return context(model, **kwargs)
