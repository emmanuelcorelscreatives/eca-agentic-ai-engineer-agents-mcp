"""Application-owned context and actual SDK handoff payload validation."""
from dataclasses import dataclass, field
import hashlib
import json


@dataclass
class SalesContext:
    prospect_id: str
    company_id: str
    campaign_id: str
    evidence_ids: tuple[str, ...]
    evidence_revision: str
    operational_events: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not all([self.prospect_id, self.company_id, self.campaign_id, self.evidence_ids, self.evidence_revision]):
            raise ValueError('complete campaign context required')
        self._identity = self.identity()

    def identity(self):
        return {'prospect_id': self.prospect_id, 'company_id': self.company_id,
                'campaign_id': self.campaign_id, 'evidence_ids': list(self.evidence_ids),
                'evidence_revision': self.evidence_revision}

    def validate(self, payload):
        # Detect mutation of context as well as model-provided handoff metadata.
        if self.identity() != self._identity:
            raise ValueError('application context mutated')
        raw = payload.model_dump() if hasattr(payload, 'model_dump') else payload
        if raw != self._identity:
            raise ValueError('handoff changed prospect/company/campaign/evidence/revision')
        return raw


def context_for(prospect):
    raw = json.dumps(prospect.__dict__, sort_keys=True, separators=(',', ':'))
    return SalesContext(prospect.prospect_id, prospect.company_id, prospect.campaign_id,
                        (prospect.source_id,), hashlib.sha256(raw.encode()).hexdigest())


def make_handoff_callback(destination):
    async def on_handoff(wrapper, payload):
        exact = wrapper.context.validate(payload)
        wrapper.context.operational_events.append({'event': 'sdk_handoff_validated',
                                                   'destination': destination, 'context': exact})
    return on_handoff
