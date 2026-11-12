"""Context budgeting, visible status and consent-gated notification composition."""
from dataclasses import dataclass, asdict
from typing import Callable

SYSTEM_INSTRUCTIONS = "Answer only from approved profile evidence. Cite stable section IDs. Say when information is absent. Never invent credentials or reveal private data. Contact storage needs explicit consent."

@dataclass(frozen=True)
class Status:
    phase: str
    detail: str


def context_for(question, sections, max_chars=4000):
    if max_chars < len(SYSTEM_INSTRUCTIONS) + len(question):
        raise ValueError('question and instructions exceed context budget')
    chosen=[]
    used=len(SYSTEM_INSTRUCTIONS)+len(question)
    for section in sections:
        if not section.approved:
            continue
        text=f'[{section.id}] {section.title}: {section.text}'
        if used+len(text) <= max_chars:
            chosen.append(text)
            used+=len(text)
    return {'instructions':SYSTEM_INSTRUCTIONS,'question':question,'evidence':chosen,'character_budget':max_chars,'characters_used':used}


def answer_with_status(twin, question):
    yield {'status':asdict(Status('retrieving','Finding approved profile sections'))}
    result=twin.answer(question)
    yield {'status':asdict(Status('ready','Approved evidence processed')),'result':result}


def contact_and_notify(twin, name, email, message, consent=False, notifier:Callable|None=None):
    result=twin.record_contact(name,email,message,consent)
    if notifier is None:
        return result
    try:
        # External adapter receives only the local record identifier; explicit
        # deployment configuration decides what, if anything, leaves the service.
        notifier({'contact_id':result['contact_id']})
        return {**result,'notification':'adapter_completed'}
    except Exception as error:
        return {**result,'notification':'adapter_failed','error_type':type(error).__name__}
