"""One application controller for SDK generation, review, approval and owned-sink send."""
import json
from pathlib import Path
from sales import SalesTeam, Prospect
from evaluations import evaluation_report, mechanical_checks
from context_wire import context_for


class SalesApplication:
    def __init__(self, database, *, allow_sdk=False, model=None, sink=None, export_directory=None):
        self.database = database
        self.allow_sdk = allow_sdk
        self.model = model
        self.sink = sink
        self.export_directory = Path(export_directory) if export_directory else None
        self.runs = {}

    async def create(self, prospect: Prospect, mode='deterministic'):
        result = {'mode': 'deterministic-application-draft', 'status': 'human_approval_required',
                  'operational_events': [{'event': 'local_template_generation', 'model_call': False}],
                  'identity': context_for(prospect).identity()}
        if mode != 'deterministic':
            if not self.allow_sdk or not self.model:
                raise PermissionError('SDK execution requires application opt-in and explicit model')
            if mode in {'sdk-sequential', 'sdk-manager'}:
                from agents_adapter import run_integrated_pipeline
                result = await run_integrated_pipeline(prospect, self.model, manager=mode == 'sdk-manager')
            elif mode == 'sdk-handoff':
                from agents_adapter import run_context_handoff
                result = await run_context_handoff(prospect, self.model)
            else:
                raise ValueError('unknown generation mode')
        if mode in {'sdk-manager', 'sdk-handoff'}:
            return {'draft_id': None, 'observation': result,
                    'notice': 'Observed agent coordination only; no free text silently promoted to a sendable draft'}
        team = SalesTeam(self.database)
        try:
            ident = team.create_draft(prospect)
            if mode == 'sdk-sequential':
                team.edit(ident, result['draft']['subject'], result['draft']['body'])
                if result['status'] == 'revision_required':
                    with team.db:
                        team.db.execute("UPDATE drafts SET status='revision_required' WHERE id=?", (ident,))
            self.runs[ident] = result
            return {'draft_id': ident, 'preview': team.preview(ident), 'generation': result,
                    'evaluation': mechanical_checks(team.draft(ident)['subject'], team.draft(ident)['body'], prospect)}
        finally:
            team.db.close()

    def action(self, ident, action, *, subject=None, body=None, recipient=None, expected_revision=None, expected_hash=None):
        if ident is None:
            raise ValueError('no selected draft')
        team = SalesTeam(self.database)
        try:
            if action == 'edit':
                team.edit(ident, subject, body, recipient, expected_revision)
            elif action == 'approve':
                if expected_hash is None:
                    raise PermissionError('Displayed exact preview hash required')
                team.approve(ident, 'Local UI practice human; not production authentication', expected_hash)
            elif action == 'reject':
                team.reject(ident)
            elif action == 'submit-owned-sink':
                if self.sink is None:
                    raise PermissionError('Owned sink not configured')
                if expected_hash is None or expected_hash != team.preview(ident)['payload_hash']:
                    raise PermissionError('Current displayed exact preview hash required before send')
                return team.submit_approved(ident, self.sink)
            elif action != 'preview':
                raise ValueError('unknown action')
            return team.preview(ident)
        finally:
            team.db.close()

    def export(self, ident, prospect):
        """Operational events and reference evaluation; never private reasoning traces."""
        if self.export_directory is None:
            raise PermissionError('Private export directory not configured')
        self.export_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        team = SalesTeam(self.database)
        try:
            report = {'draft': team.preview(ident), 'generation_observation': self.runs.get(ident),
                      'reference_evaluation_corpus': evaluation_report(prospect),
                      'current_draft_mechanical': mechanical_checks(team.draft(ident)['subject'], team.draft(ident)['body'], prospect),
                      'approval_history': [dict(x) for x in team.db.execute('SELECT * FROM approval_events WHERE draft_id=? ORDER BY id', (ident,))],
                      'transport_history': [dict(x) for x in team.db.execute('SELECT * FROM send_attempts WHERE draft_id=?', (ident,))],
                      'scope': 'Local operational evidence and author labels, not hosted traces or model quality scores'}
            path = self.export_directory / f'sales-draft-{int(ident)}-report.json'
            # A UI user must never supply a pathname; only selected numeric ID enters filename.
            with path.open('w', encoding='utf-8') as handle:
                json.dump(report, handle, ensure_ascii=False, indent=2)
            path.chmod(0o600)
            return str(path)
        finally:
            team.db.close()
