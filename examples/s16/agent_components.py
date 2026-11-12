"""Stage 16 offline component contracts. These fixtures are NOT model observations."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from uuid import uuid4

PAGES = {
    'course': {'title': 'Academy Browser Sidekick', 'body': 'The sidekick reads synthetic Academy documentation.'},
    'privacy': {'title': 'Privacy', 'body': 'Use an isolated profile. Never use personal account data.'},
    'checkpoint': {'title': 'Checkpoints', 'body': 'A checkpoint stores resumable application state.'},
}

def lookup_section(page_id: str) -> dict:
    """Read a synthetic Academy page by its exact allowlisted identifier."""
    if type(page_id) is not str or page_id not in PAGES:
        raise ValueError('unknown page_id')
    return {'page_id': page_id, **PAGES[page_id]}


def dispatch(call: dict, *, allowed=frozenset({'lookup_section'})) -> dict:
    if set(call) != {'id', 'name', 'args'} or not isinstance(call['id'], str) or not call['id']:
        raise ValueError('malformed tool call')
    if call['name'] not in allowed or call['name'] != 'lookup_section':
        raise ValueError('tool not allowed')
    if type(call['args']) is not dict or set(call['args']) != {'page_id'}:
        raise ValueError('malformed tool arguments')
    return {'role': 'tool', 'tool_call_id': call['id'], 'content': lookup_section(**call['args'])}


def aggregate_stream(events):
    """A terminal event is required. Never report a truncated stream as complete."""
    text, complete = [], False
    for event in events:
        if complete:
            raise ValueError('event after completion')
        if set(event) - {'content', 'done'} or type(event.get('content', '')) is not str:
            raise ValueError('invalid stream event')
        text.append(event.get('content', ''))
        complete = event.get('done') is True
    if not complete:
        raise InterruptedError('stream ended without terminal event')
    return ''.join(text)


def validate_answer(value: dict) -> dict:
    if type(value) is not dict or set(value) != {'answer', 'citations'}:
        raise ValueError('strict answer schema')
    if type(value['answer']) is not str or not value['answer'].strip():
        raise ValueError('answer required')
    citations = value['citations']
    if type(citations) is not list or not citations or any(type(c) is not str or c not in PAGES for c in citations):
        raise ValueError('unsupported citation')
    # This deterministic fixture has exact answers; arbitrary answers require a real grounding evaluation.
    if value['answer'] not in [PAGES[c]['body'] for c in citations]:
        raise ValueError('answer not supported by cited fixture')
    return value


class Memory:
    def __init__(self, max_messages=4):
        if type(max_messages) is not int or max_messages < 1:
            raise ValueError('positive history budget required')
        self.max_messages, self.threads = max_messages, {}

    def append(self, thread: str, message: dict):
        if not thread or message.get('role') not in {'user', 'assistant', 'tool'}:
            raise ValueError('trusted thread and role required')
        self.threads[thread] = [*self.threads.get(thread, []), dict(message)][-self.max_messages:]
        return [dict(m) for m in self.threads[thread]]


def fixture_agent(page_id='privacy', *, tool_budget=1, call_name='lookup_section'):
    """Scripted control-flow fixture; does not impersonate a live model."""
    if tool_budget < 1:
        raise RuntimeError('tool budget exhausted')
    trace_id = str(uuid4())
    call = {'id': 'fixture-call-1', 'name': call_name, 'args': {'page_id': page_id}}
    events = [{'id': trace_id, 'parent': None, 'kind': 'agent', 'origin': 'scripted-fixture'}]
    try:
        result = dispatch(call)
        events.append({'id': call['id'], 'parent': trace_id, 'kind': 'tool', 'status': 'ok', 'result': result})
        answer = validate_answer({'answer': result['content']['body'], 'citations': [page_id]})
        return {'answer': answer, 'events': events}
    except (ValueError, RuntimeError) as exc:
        events.append({'id': call['id'], 'parent': trace_id, 'kind': 'tool', 'status': 'error', 'error': str(exc)})
        return {'answer': None, 'events': events}


def create_live_agent(model):
    """Genuine LangChain API. Caller supplies configured model; this function sends no request."""
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langchain.agents.middleware import wrap_tool_call
    from langchain_core.messages import ToolMessage

    @wrap_tool_call
    def validate_tool(request, handler):
        call = request.tool_call
        # Validate without running the tool; actual execution belongs to the handler.
        args = call.get('args', {})
        if call.get('name') != 'lookup_section' or set(args) != {'page_id'} or args.get('page_id') not in PAGES:
            return ToolMessage(content='Rejected: unsupported tool or page', tool_call_id=call['id'])
        return handler(request)

    return create_agent(model=model, tools=[tool(lookup_section)], middleware=[validate_tool],
                        system_prompt='Use only supplied Academy pages. Cite page identifiers; say when information is unavailable.')


if __name__ == '__main__':
    print(json.dumps(fixture_agent(), indent=2))
