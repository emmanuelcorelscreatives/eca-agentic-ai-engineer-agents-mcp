"""Native Stage 17 graphs; synthetic Academy fixture data, zero provider calls.

Run with the tested Stage 16/17 SDK environment:
    python -m examples.s17.native_graph_features

The deterministic message producer demonstrates orchestration, not model quality.
All branching, tool execution, supersteps and recovery below use LangGraph.
"""
from __future__ import annotations

from operator import add
from threading import Barrier
from typing import Annotated, TypedDict
import json
import os

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from examples.s17.graph_workflow import lookup_product, merge_evidence


class EvidenceState(TypedDict, total=False):
    evidence: Annotated[list[dict], merge_evidence]
    audit: Annotated[list[str], add]
    answer: str


def build_parallel_graph(*, conflict=False, duplicate=False, checkpointer=None):
    """Two native sibling nodes meet a thread barrier; a graph join follows both.

    The barrier makes sequential execution fail rather than claiming concurrency
    from elapsed time. Each invocation should use a newly built graph, because
    this deliberately simple teaching barrier is scoped to a single run.
    """
    gate = Barrier(2)

    def collect(source):
        def node(state):
            # Both siblings read the previous superstep, not each other's write.
            if state.get('evidence'):
                raise ValueError('demo requires empty initial evidence')
            gate.wait(timeout=5)
            record = {'id': source, 'source': 'academy://' + source,
                      'text': 'Synthetic Academy ' + source + ' policy'}
            if source == 'course' and (conflict or duplicate):
                record = {'id': 'privacy', 'source': 'academy://privacy',
                          'text': 'Synthetic Academy privacy policy'}
                if conflict:
                    record['text'] = 'conflicting synthetic policy'
            return {'evidence': [record], 'audit': ['collected:' + source]}
        return node

    def compose(state):
        return {'answer': ' | '.join(row['text'] for row in state['evidence']),
                'audit': ['joined:' + str(len(state['evidence']))]}

    graph = StateGraph(EvidenceState)
    graph.add_node('privacy', collect('privacy'))
    graph.add_node('course', collect('course'))
    graph.add_node('compose', compose)
    graph.add_edge(START, 'privacy')
    graph.add_edge(START, 'course')
    # A list edge is an AND join: compose waits for BOTH predecessors.
    graph.add_edge(['privacy', 'course'], 'compose')
    graph.add_edge('compose', END)
    return graph.compile(checkpointer=checkpointer)


@tool
def academy_product(product_id: str) -> dict:
    """Read a synthetic Academy course-fixture product; never place an order."""
    return lookup_product(product_id)


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    rounds: int
    status: str
    audit: Annotated[list[str], add]


def build_tool_loop(*, max_rounds=2, never_finish=False, checkpointer=None):
    """Real AIMessage -> ToolNode -> ToolMessage -> conditional graph loop.

    'reason' is an explicitly deterministic SDK test-message producer. It never
    contacts a provider or pretends its messages are observed model responses.
    max_rounds bounds TOOL cycles, independent of the SDK recursion limit.
    """
    if type(max_rounds) is not int or not 1 <= max_rounds <= 8:
        raise ValueError('max_rounds must be 1..8')

    def reason(state):
        rounds = state.get('rounds', 0)
        messages = state.get('messages', [])
        if messages and isinstance(messages[-1], ToolMessage) and not never_finish:
            return {'messages': [AIMessage(content='Synthetic result: ' + messages[-1].content)],
                    'status': 'complete', 'audit': ['reason:complete']}
        if rounds >= max_rounds:
            return {'messages': [AIMessage(content='Stopped at the explicit tool-cycle budget.')],
                    'status': 'budget-exhausted', 'audit': ['reason:budget-exhausted']}
        call_id = 'academy-call-' + str(rounds + 1)
        return {'messages': [AIMessage(content='', tool_calls=[{
                    'name': 'academy_product', 'args': {'product_id': 'sidekick'},
                    'id': call_id, 'type': 'tool_call'}])],
                'rounds': rounds + 1, 'status': 'tool-requested',
                'audit': ['reason:tool-requested:' + call_id]}

    def route(state):
        return 'tools' if state['messages'][-1].tool_calls else 'stop'

    graph = StateGraph(AgentState)
    graph.add_node('reason', reason)
    graph.add_node('tools', ToolNode([academy_product]))
    graph.add_edge(START, 'reason')
    graph.add_conditional_edges('reason', route, {'tools': 'tools', 'stop': END})
    graph.add_edge('tools', 'reason')
    return graph.compile(checkpointer=checkpointer)


class RecoveryState(TypedDict, total=False):
    attempts: int
    outcome: str
    error: str
    answer: str
    audit: Annotated[list[str], add]


def build_recovery_graph(*, failure='transient', max_attempts=2,
                         exhausted_action='fallback', checkpointer=None):
    """Catch expected domain errors in one node, then route through native edges.

    Synthetic transient/permanent failures are injected for a repeatable lab.
    Unexpected programming errors are deliberately not swallowed. A successful
    fallback is labelled cached synthetic data, never a successful live lookup.
    """
    if failure not in ('none', 'transient', 'permanent', 'invalid'):
        raise ValueError('unsupported synthetic failure')
    if type(max_attempts) is not int or not 1 <= max_attempts <= 8:
        raise ValueError('max_attempts must be 1..8')
    if exhausted_action not in ('fallback', 'intervention'):
        raise ValueError('unsupported exhausted action')

    def attempt(state):
        number = state.get('attempts', 0) + 1
        try:
            if failure == 'permanent' or (failure == 'transient' and number == 1):
                raise TimeoutError('synthetic product read timeout')
            if failure == 'invalid':
                raise ValueError('synthetic invalid product data')
            product = lookup_product('sidekick')
            return {'attempts': number, 'outcome': 'success', 'error': '',
                    'answer': product['id'] + ' costs ' + product['price'],
                    'audit': ['attempt:' + str(number) + ':success']}
        except TimeoutError as exc:
            return {'attempts': number, 'outcome': 'retryable', 'error': str(exc),
                    'audit': ['attempt:' + str(number) + ':retryable']}
        except ValueError as exc:
            return {'attempts': number, 'outcome': 'invalid', 'error': str(exc),
                    'audit': ['attempt:' + str(number) + ':invalid']}

    def route(state):
        if state['outcome'] == 'success':
            return 'finish'
        if state['outcome'] == 'invalid':
            return 'intervention'
        return 'retry' if state['attempts'] < max_attempts else exhausted_action

    graph = StateGraph(RecoveryState)
    graph.add_node('attempt', attempt)
    graph.add_node('retry', lambda _: {'audit': ['retry:scheduled']})
    graph.add_node('finish', lambda _: {'audit': ['finish:success']})
    graph.add_node('fallback', lambda _: {
        'outcome': 'fallback', 'answer': 'Cached synthetic Academy product: sidekick.',
        'audit': ['fallback:cached-not-live']})
    graph.add_node('intervention', lambda _: {
        'outcome': 'intervention', 'answer': 'Ask the user to verify the product data.',
        'audit': ['intervention:required']})
    graph.add_edge(START, 'attempt')
    graph.add_conditional_edges('attempt', route, {
        name: name for name in ('retry', 'finish', 'fallback', 'intervention')})
    graph.add_edge('retry', 'attempt')
    for name in ('finish', 'fallback', 'intervention'):
        graph.add_edge(name, END)
    return graph.compile(checkpointer=checkpointer)


def demo_result():
    return {
        'fixture_notice': 'Synthetic Academy data; deterministic message producer; no provider calls.',
        'parallel': build_parallel_graph().invoke({'evidence': [], 'audit': []}),
        'tool_loop': build_tool_loop().invoke({'messages': [], 'rounds': 0, 'audit': []}),
        'recovery': build_recovery_graph().invoke({'attempts': 0, 'audit': []}),
    }


def run_demo(*, langsmith=False):
    """Explicit opt-in hosted tracing; the default forcibly disables telemetry.

    Hosted tracing is a separate external operation, not exercised by the local
    tests. Inputs/outputs of ALL child runs are hidden at the client boundary;
    node names, transitions, timing and tool run identity remain inspectable.
    The run URL is an actual SDK URL, not proof that upload/hosting succeeded.
    Inspect that URL in LangSmith before claiming a retained hosted observation.
    Never supply private documents, real customer data or secrets to this demo.
    """
    from langsmith import Client, traceable, tracing_context
    from langsmith.run_helpers import get_current_run_tree

    if not langsmith:
        with tracing_context(enabled=False):
            return {'result': demo_result(), 'trace': {'status': 'disabled'}}
    api_key = os.environ.get('LANGSMITH_API_KEY')
    if not api_key:
        raise ValueError('Explicit LangSmith run requires LANGSMITH_API_KEY')
    # The key stays in memory and is never included in printed results.
    client = Client(api_key=api_key, hide_inputs=True, hide_outputs=True)
    trace_reference = {}

    @traceable(name='academy-stage17-native-graphs', run_type='chain')
    def traced_demo():
        run = get_current_run_tree()
        if run is not None:
            trace_reference.update({'run_id': str(run.id), 'run_url': run.get_url()})
        return demo_result()

    with tracing_context(enabled=True, client=client,
                         project_name='academy-stage17-synthetic',
                         tags=['synthetic-fixture', 'zero-model-provider-calls']):
        result = traced_demo()
    client.flush(timeout=15)
    return {'result': result, 'trace': {
        **trace_reference, 'status': 'upload-attempted-inspect-hosted-run',
        'redaction': 'all child-run inputs and outputs hidden'}}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--langsmith', action='store_true',
                        help='Explicitly opt in to hosted synthetic traces; needs LANGSMITH_API_KEY.')
    options = parser.parse_args()
    print(json.dumps(run_demo(langsmith=options.langsmith), indent=2,
                     default=lambda value: value.model_dump()))
