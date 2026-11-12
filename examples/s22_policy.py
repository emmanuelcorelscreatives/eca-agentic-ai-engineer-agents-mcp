"""Typed read-only domain boundaries shared by genuine framework adapters."""
from dataclasses import dataclass
from pathlib import Path
import json
import re
DATA = Path(__file__).resolve().parents[1] / 'data/s22_support.json'

@dataclass(frozen=True)
class PolicyService:
    path: Path = DATA
    def lookup(self, product_id: str) -> dict:
        if not isinstance(product_id, str) or not re.fullmatch(r'P-[A-Z]+', product_id):
            return {'ok':False, 'error':'invalid_product'}
        records = [p for p in json.loads(self.path.read_text())['policies'] if p['product_id'] == product_id]
        return {'ok':True,'policies':records} if records else {'ok':False,'error':'unknown_product'}
    def ticket(self, ticket_id):
        for ticket in json.loads(self.path.read_text())['tickets']:
            if ticket['id'] == ticket_id:
                return dict(ticket)
        raise ValueError('unknown_ticket')

@dataclass(frozen=True)
class RequestContext:
    request_id: str
    ticket_id: str
    policies: PolicyService
    role: str = 'triager'
    def __post_init__(self):
        if not self.request_id or not isinstance(self.policies, PolicyService):
            raise ValueError('Request context requires an ID and typed PolicyService')
        if self.role not in {'reader','triager'}:
            raise ValueError('Unknown application role')
        self.policies.ticket(self.ticket_id)

def validate_triage(value: dict, context: RequestContext) -> dict:
    required = {'ticket_id','category','rationale','policy_ids','confidence','unresolved'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('Invalid triage fields')
    if value['ticket_id'] != context.ticket_id or value['category'] not in {'damaged','delivery','unknown'}:
        raise ValueError('Wrong ticket or category')
    if not isinstance(value['rationale'], str) or not value['rationale'].strip():
        raise ValueError('Rationale required')
    if type(value['confidence']) not in (int, float) or not 0 <= value['confidence'] <= 1:
        raise ValueError('Confidence must be 0..1; this is not a truth guarantee')
    ticket = context.policies.ticket(context.ticket_id)
    allowed = {p['id'] for p in context.policies.lookup(ticket['product_id'])['policies']}
    if not isinstance(value['policy_ids'], list) or not set(value['policy_ids']) <= allowed:
        raise ValueError('Unverified policy citation')
    if not isinstance(value['unresolved'], list) or any(not isinstance(s,str) for s in value['unresolved']):
        raise ValueError('Unresolved must be a list of strings')
    return dict(value)

def escalation_draft(context: RequestContext, reason: str) -> dict:
    """Create a local value only: no sending, external mutation or automatic approval."""
    if context.role != 'triager':
        raise PermissionError('Reader role cannot prepare escalation drafts')
    if not reason.strip():
        raise ValueError('Reason required')
    return {'ticket_id':context.ticket_id,'reason':reason,'status':'draft_only','request_id':context.request_id}
