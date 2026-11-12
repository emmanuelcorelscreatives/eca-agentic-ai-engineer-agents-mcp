"""Validated local records and evidence foreign identities."""
from dataclasses import dataclass


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('nonempty string required')


def evidence(values):
    if not isinstance(values, tuple) or not values or len(set(values)) != len(values):
        raise ValueError('nonempty unique evidence tuple required')
    for value in values:
        text(value)


@dataclass(frozen=True)
class Company:
    id: str
    name: str
    industry: str
    source_id: str
    def __post_init__(self):
        for value in self.__dict__.values():
            text(value)


@dataclass(frozen=True)
class ResearchFinding:
    prospect_id: str
    company_id: str
    need: str
    source_ids: tuple[str, ...]
    unknowns: tuple[str, ...] = ()
    def __post_init__(self):
        for value in (self.prospect_id, self.company_id, self.need):
            text(value)
        evidence(self.source_ids)
        if not isinstance(self.unknowns, tuple):
            raise ValueError('unknowns must be an explicit tuple')
        for item in self.unknowns:
            text(item)


@dataclass(frozen=True)
class OutreachStrategy:
    campaign_id: str
    prospect_id: str
    value_proposition: str
    evidence_ids: tuple[str, ...]
    tone: str = 'professional'
    def __post_init__(self):
        for value in (self.campaign_id, self.prospect_id, self.value_proposition, self.tone):
            text(value)
        evidence(self.evidence_ids)


@dataclass(frozen=True)
class EmailDraft:
    prospect_id: str
    campaign_id: str
    subject: str
    body: str
    evidence_ids: tuple[str, ...]
    def __post_init__(self):
        for value in (self.prospect_id, self.campaign_id, self.subject, self.body):
            text(value)
        evidence(self.evidence_ids)


def validate_identity_graph(prospect, company, finding, strategy=None, draft=None):
    if prospect.company_id != company.id or prospect.company != company.name:
        raise ValueError('prospect company foreign identity mismatch')
    if finding.prospect_id != prospect.prospect_id or finding.company_id != company.id:
        raise ValueError('research foreign identity mismatch')
    known = {company.source_id, prospect.source_id}
    if not set(finding.source_ids) <= known or prospect.source_id not in finding.source_ids:
        raise ValueError('research contains unknown or missing prospect evidence')
    if finding.need != prospect.verified_need:
        raise ValueError('finding differs from synthetic verified need')
    for item in (strategy, draft):
        if item is None:
            continue
        if item.prospect_id != prospect.prospect_id or item.campaign_id != prospect.campaign_id:
            raise ValueError('strategy/draft identity mismatch')
        if not set(item.evidence_ids) <= set(finding.source_ids):
            raise ValueError('strategy/draft evidence not in validated research')
    return {'valid': True, 'prospect_id': prospect.prospect_id, 'company_id': company.id,
            'campaign_id': prospect.campaign_id, 'validated_evidence_ids': sorted(finding.source_ids)}
