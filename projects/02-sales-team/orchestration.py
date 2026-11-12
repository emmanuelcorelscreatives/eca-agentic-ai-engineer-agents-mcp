"""Explicit specialist handoff records, manager policies and evaluation."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Handoff:
    prospect_id:str
    campaign_id:str
    from_role:str
    to_role:str
    source_ids:tuple[str,...]
    revision_reason:str=''

    def __post_init__(self):
        roles={'research','strategy','writer','reviewer'}
        if self.from_role not in roles or self.to_role not in roles or not self.source_ids:
            raise ValueError('handoff must preserve source IDs and known specialist roles')
        if not self.prospect_id or not self.campaign_id:
            raise ValueError('prospect and campaign identity required')


def manager_next(state):
    if not state.get('research'):return {'next':'research','reason':'source evidence missing'}
    if not state.get('strategy'):return {'next':'strategy','reason':'value proposition missing'}
    if not state.get('draft'):return {'next':'writer','reason':'draft missing'}
    if state.get('review') is None:return {'next':'reviewer','reason':'draft needs review'}
    if not state['review']['passed']:return {'next':'writer','reason':'; '.join(state['review']['issues'])}
    return {'next':'human_approval','reason':'model review cannot authorize delivery'}


def build_sdk_manager(model):
    from agents_adapter import build_agents
    from agents import Agent
    specialists=build_agents(model)
    tools=[specialist.as_tool(tool_name=role,tool_description=f'Request the {role} specialist; preserve source attribution.') for role,specialist in specialists.items()]
    return Agent(name='Sales manager',model=model,instructions='Coordinate research, strategy, writing and review. Request revisions for factual issues. You have no delivery or human approval authority.',tools=tools)


def build_sdk_handoff(model):
    from agents_adapter import build_agents
    from agents import Agent
    specialists=build_agents(model)
    return Agent(name='Sales triage',model=model,instructions='Hand off to the appropriate specialist. Preserve prospect/source/campaign identifiers. Never send email.',handoffs=list(specialists.values()))


def score_draft(draft, prospect_name, company, verified_phrase):
    text=draft['body']
    checks={'personalized_name':prospect_name in text,'company_relevance':company in text or verified_phrase in text,'grounded_need':verified_phrase in text,'concise':len(text.split())<=120,'no_guarantee':'guaranteed' not in text.lower()}
    return {'checks':checks,'score':sum(checks.values())/len(checks),'scope':'transparent baseline rubric; not comprehensive truth verification'}


def build_context_handoff(model):
    """Actual typed SDK handoffs invoke the application context validator."""
    from agents import Agent, handoff
    from pydantic import BaseModel
    from agents_adapter import build_agents
    from context_wire import make_handoff_callback
    class HandoffIdentity(BaseModel):
        model_config = {'extra': 'forbid'}
        prospect_id: str
        company_id: str
        campaign_id: str
        evidence_ids: list[str]
        evidence_revision: str
    specialists = build_agents(model)
    targets = [handoff(agent, input_type=HandoffIdentity,
                       on_handoff=make_handoff_callback(role))
               for role, agent in specialists.items()]
    return Agent(name='Context-preserving sales triage', model=model,
                 instructions='Transfer to the requested specialist. Copy the exact supplied context identity into the handoff. Never approve or send.',
                 handoffs=targets)
