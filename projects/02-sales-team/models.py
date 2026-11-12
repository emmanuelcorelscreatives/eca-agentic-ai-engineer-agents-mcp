"""Shared records for campaign identity and attributable specialist outputs."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Company:
    id: str
    name: str
    industry: str
    source_id: str
    def __post_init__(self):
        if not all((self.id,self.name,self.industry,self.source_id)):
            raise ValueError('company record requires identity and evidence')

@dataclass(frozen=True)
class ResearchFinding:
    prospect_id: str
    company_id: str
    need: str
    source_ids: tuple[str,...]
    unknowns: tuple[str,...]=()
    def __post_init__(self):
        if not self.source_ids or not self.need:raise ValueError('research needs attributed evidence')

@dataclass(frozen=True)
class OutreachStrategy:
    campaign_id: str
    prospect_id: str
    value_proposition: str
    evidence_ids: tuple[str,...]
    tone: str='professional'
    def __post_init__(self):
        if not self.evidence_ids or not self.campaign_id:raise ValueError('strategy needs campaign and evidence')

@dataclass(frozen=True)
class EmailDraft:
    prospect_id: str
    campaign_id: str
    subject: str
    body: str
    evidence_ids: tuple[str,...]
    def __post_init__(self):
        if not all((self.prospect_id,self.campaign_id,self.subject,self.body,self.evidence_ids)):
            raise ValueError('complete attributable draft required')
