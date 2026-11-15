"""Worked state-machine exercises, entirely local and in-memory; no SDK or SMTP."""
from dataclasses import asdict, replace
import json
from pathlib import Path
from sales import Prospect, SalesTeam
from orchestration import Handoff


def expect_error(error_type, operation):
    try:
        operation()
    except error_type:
        return
    raise AssertionError(f'Expected {error_type.__name__}')


def worked_solutions():
    prospect = Prospect(**json.loads((Path(__file__).parent/'fixtures/prospect.json').read_text())['prospect'])
    team = SalesTeam()
    try:
        ident = team.create_draft(prospect)
        expect_error(PermissionError, lambda: team.deliver(ident))
        assert team.db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0] == 0
        team.approve(ident, 'Fictional practice reviewer')
        team.edit(ident, 'Changed subject', team.draft(ident)['body'])
        edited = team.draft(ident)
        assert edited['status'] == 'draft' and edited['approved_hash'] is None
        team.edit(ident, edited['subject'], edited['body'] + 'Guaranteed savings.')
        assert not team.review(ident)['passed']
        expect_error(ValueError, lambda: team.approve(ident, 'Fictional practice reviewer'))
        team.edit(ident, edited['subject'], edited['body'] + 'Annual revenue is ten million dollars.')
        assert team.review(ident)['passed']
        team.edit(ident, edited['subject'], edited['body'])
        team.approve(ident, 'Fictional practice reviewer')
        receipt = team.deliver(ident)
        expect_error(PermissionError, lambda: team.deliver(ident))
        assert team.db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0] == 1
        expect_error(ValueError, lambda: replace(prospect, source_id=''))
        handoff = Handoff(prospect.prospect_id, prospect.campaign_id, 'reviewer', 'writer',
                          (prospect.source_id,), 'Remove the unsupported revenue assertion')
        return {'exercises_checked': 6, 'receipt': receipt, 'handoff': asdict(handoff),
                'limitation': 'Mechanical checks missed the invented revenue; a human must compare every factual claim to the source.'}
    finally:
        team.db.close()


if __name__ == '__main__':
    print(json.dumps(worked_solutions(), indent=2))
