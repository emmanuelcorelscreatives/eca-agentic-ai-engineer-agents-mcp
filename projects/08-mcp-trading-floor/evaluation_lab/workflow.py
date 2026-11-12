"""Instrument the existing deterministic paper ledger without a model/broker call."""
from .observability import Trace


def run_paper_workflow(floor, *, symbol, quantity, request_id, reviewer=None):
    trace = Trace()
    before = floor.state()
    with trace.span('paper_workflow', 'workflow'):
        with trace.span('research', 'agent', symbol=symbol):
            research = floor.research(symbol)
        with trace.span('proposal', 'agent', symbol=symbol, quantity=quantity):
            proposal = floor.propose(symbol, quantity)
        with trace.span('risk', 'tool', evidence_id=research['evidence_id']) as span:
            risk = floor.risk(proposal)
            span['fields']['allowed'] = risk['allowed']
        if not risk['allowed']:
            state = 'RISK_REJECTED'; execution = None
        elif reviewer is None:
            state = 'AWAITING_HUMAN_APPROVAL'; execution = None
        else:
            # Transport caller must authenticate reviewer. Tests use a labelled test identity.
            with trace.span('human_approval', 'approval'):
                floor.approve(proposal, reviewer)
            with trace.span('paper_execution', 'order', order_id=request_id):
                execution = floor.execute(proposal, request_id)
            state = 'EXECUTED'
    return {'run_id': trace.run_id, 'state': state, 'before': before,
            'after': floor.state(), 'execution': execution, 'trace': trace}
