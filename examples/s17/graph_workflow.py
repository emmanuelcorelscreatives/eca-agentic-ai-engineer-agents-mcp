"""Stage 17 deterministic graph contracts and a genuine optional LangGraph builder."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import TypedDict, Annotated
from operator import add
import json

PRODUCTS = {'sidekick': {'id': 'sidekick', 'price': '0.00', 'category': 'course-fixture'}}


def merge_evidence(left, right):
    combined = {}
    for record in [*left, *right]:
        if set(record) != {'id', 'source', 'text'} or any(type(v) is not str for v in record.values()):
            raise ValueError('invalid evidence record')
        if record['id'] in combined and combined[record['id']] != record:
            raise ValueError('conflicting evidence identity')
        combined[record['id']] = dict(record)
    return [combined[k] for k in sorted(combined)]


def route_request(state):
    if not isinstance(state.get('request'), str) or not state['request'].strip():
        return 'clarify'
    return 'lookup' if state['request'].strip().lower() in PRODUCTS else 'finish'


def lookup_product(product_id):
    if type(product_id) is not str or product_id not in PRODUCTS:
        raise ValueError('unsupported product')
    return dict(PRODUCTS[product_id])


def workflow(request, *, failure=None, attempt_budget=2):
    if type(attempt_budget) is not int or not 1 <= attempt_budget <= 8:
        raise ValueError('attempt budget must be 1..8')
    state = {'request': request, 'route': route_request({'request': request}), 'audit': [], 'attempts': 0}
    if state['route'] != 'lookup':
        state['answer'] = 'Please specify a product.' if state['route'] == 'clarify' else 'No supported fixture product.'
        return state
    while state['attempts'] < attempt_budget:
        state['attempts'] += 1
        try:
            if failure == 'permanent':
                raise ValueError('synthetic invalid product data')
            if failure == 'transient' and state['attempts'] == 1:
                raise TimeoutError('synthetic read timeout')
            state['product'] = lookup_product(request.strip().lower())
            state['audit'].append({'node': 'lookup', 'outcome': 'ok', 'attempt': state['attempts']})
            state['answer'] = state['product']['id'] + ' costs ' + state['product']['price']
            return state
        except TimeoutError as exc:
            state['audit'].append({'node': 'lookup', 'outcome': 'retryable', 'error': str(exc)})
        except ValueError as exc:
            state['audit'].append({'node': 'lookup', 'outcome': 'terminal', 'error': str(exc)})
            state['answer'] = None
            return state
    state['answer'] = None
    state['audit'].append({'node': 'lookup', 'outcome': 'budget-exhausted'})
    return state


def superstep():
    """Both collectors see the same input; a barrier separates collection from reduction."""
    gate = Barrier(2)
    def collect(source):
        gate.wait(timeout=3)
        return [{'id': source, 'source': 'academy://' + source, 'text': 'fixture ' + source}]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(collect, name) for name in ['privacy', 'course']]
        return merge_evidence(futures[0].result(), futures[1].result())


class GraphState(TypedDict, total=False):
    request: str
    route: str
    product: dict
    answer: str
    audit: Annotated[list, add]


def build_graph(checkpointer=None):
    from langgraph.graph import StateGraph, START, END
    builder = StateGraph(GraphState)
    builder.add_node('classify', lambda s: {'route': route_request(s), 'audit': ['classified']})
    builder.add_node('lookup', lambda s: {'product': lookup_product(s['request'].strip().lower()), 'audit': ['looked-up']})
    builder.add_node('compose', lambda s: {'answer': s['product']['id'] + ' costs ' + s['product']['price']})
    builder.add_node('clarify', lambda s: {'answer': 'Please specify a product.'})
    builder.add_node('finish', lambda s: {'answer': 'No supported fixture product.'})
    builder.add_edge(START, 'classify')
    builder.add_conditional_edges('classify', lambda s: s['route'], {'lookup': 'lookup', 'clarify': 'clarify', 'finish': 'finish'})
    builder.add_edge('lookup', 'compose')
    for name in ['compose', 'clarify', 'finish']:
        builder.add_edge(name, END)
    return builder.compile(checkpointer=checkpointer)


if __name__ == '__main__':
    print(json.dumps({'workflow': workflow('sidekick', failure='transient'), 'superstep': superstep()}, indent=2))
