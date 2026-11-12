"""Exact-message human approvals; simulation and real owned-sink SMTP are distinct."""
from dataclasses import dataclass
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip() or '\x00' in value:
        raise ValueError(label + ' required')
    return value


def email_address(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}', value):
        raise ValueError('valid single email address required; no display names/newlines')
    return value


def canonical_body(value):
    nonempty(value, 'body')
    text = value.replace('\r\n', '\n').replace('\r', '\n')
    return text if text.endswith('\n') else text + '\n'


@dataclass(frozen=True)
class Prospect:
    name: str
    company: str
    role: str
    verified_need: str
    source_id: str
    email: str
    prospect_id: str = 'prospect-cedar-001'
    company_id: str = 'company-cedar-001'
    campaign_id: str = 'campaign-cedar-001'

    def __post_init__(self):
        for key, value in self.__dict__.items():
            nonempty(value, key)
        email_address(self.email)


def digest(subject, body, recipient='', revision=0):
    return hashlib.sha256(json.dumps([recipient, subject, body, revision],
                                     ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


class SalesTeam:
    def __init__(self, database=':memory:'):
        self.db = sqlite3.connect(database)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS drafts(id INTEGER PRIMARY KEY,subject TEXT NOT NULL,body TEXT NOT NULL,source_id TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'draft',approved_hash TEXT,approver TEXT);
        CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY,draft_id INTEGER UNIQUE,subject TEXT,body TEXT,delivery TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS send_attempts(draft_id INTEGER PRIMARY KEY,payload_hash TEXT NOT NULL,message_id TEXT NOT NULL,status TEXT NOT NULL,receipt TEXT);
        CREATE TABLE IF NOT EXISTS approval_events(id INTEGER PRIMARY KEY,draft_id INTEGER NOT NULL,action TEXT NOT NULL,payload_hash TEXT,actor TEXT);
        """)
        columns = {x['name'] for x in self.db.execute('PRAGMA table_info(drafts)')}
        for key, declaration in {'recipient': "TEXT NOT NULL DEFAULT ''", 'revision': 'INTEGER NOT NULL DEFAULT 1',
                                 'prospect_id': "TEXT NOT NULL DEFAULT ''", 'company_id': "TEXT NOT NULL DEFAULT ''",
                                 'campaign_id': "TEXT NOT NULL DEFAULT ''"}.items():
            if key not in columns:
                self.db.execute(f'ALTER TABLE drafts ADD COLUMN {key} {declaration}')
        self.db.commit()

    def create_draft(self, prospect):
        subject = f'A practical workflow for {prospect.company}'
        body = f'Hello {prospect.name},\nYour practice brief identifies {prospect.verified_need}. We can demonstrate a small reporting prototype and review its fit with you. Would a walkthrough be useful?\nAcademy practice team\n'
        with self.db:
            row = self.db.execute('INSERT INTO drafts(subject,body,source_id,recipient,prospect_id,company_id,campaign_id) VALUES(?,?,?,?,?,?,?)',
                (subject, canonical_body(body), prospect.source_id, prospect.email, prospect.prospect_id, prospect.company_id, prospect.campaign_id))
        return row.lastrowid

    def draft(self, draft_id):
        row = self.db.execute('SELECT * FROM drafts WHERE id=?', (draft_id,)).fetchone()
        if row is None:
            raise KeyError(draft_id)
        return dict(row)

    def preview(self, draft_id):
        row = self.draft(draft_id)
        return {**row, 'payload_hash': digest(row['subject'], row['body'], row['recipient'], row['revision']),
                'notice': 'Preview only; no send and no automatic approval'}

    def edit(self, draft_id, subject, body, recipient=None, expected_revision=None):
        nonempty(subject, 'subject')
        if '\n' in subject or '\r' in subject:
            raise ValueError('subject header cannot contain newlines')
        body = canonical_body(body)
        with self.db:
            current = self.draft(draft_id)
            if expected_revision is not None and current['revision'] != expected_revision:
                raise ValueError('stale editor revision')
            if recipient is None:
                recipient = current['recipient']
            email_address(recipient)
            row = self.db.execute("UPDATE drafts SET subject=?,body=?,recipient=?,revision=revision+1,status='draft',approved_hash=NULL,approver=NULL WHERE id=? AND revision=? AND status IN ('draft','approved','rejected','revision_required')",
                                  (subject, body, recipient, draft_id, current['revision']))
            if row.rowcount != 1:
                raise ValueError('draft is missing, sending, unknown or already submitted')
            self.db.execute("INSERT INTO approval_events(draft_id,action) VALUES(?,'edit_revoked_approval')", (draft_id,))

    def reject(self, draft_id):
        with self.db:
            row = self.db.execute("UPDATE drafts SET status='rejected',approved_hash=NULL,approver=NULL WHERE id=? AND status IN ('draft','approved','rejected')", (draft_id,))
            if row.rowcount != 1:
                raise PermissionError('sending/unknown/submitted draft cannot be rejected retrospectively')
            self.db.execute("INSERT INTO approval_events(draft_id,action) VALUES(?,'reject')", (draft_id,))

    def review(self, draft_id):
        row = self.draft(draft_id)
        issues = [word for word in ('guaranteed', '100% roi', 'market leader') if word in row['body'].lower()]
        return {'passed': not issues, 'issues': issues, 'source_id': row['source_id'],
                'scope': 'Mechanical sample checks only; no factual/tone quality approval'}

    def approve(self, draft_id, approver, expected_hash=None):
        nonempty(approver, 'named local human approver')
        with self.db:
            row = self.preview(draft_id)
            email_address(row['recipient'])
            if expected_hash is not None and expected_hash != row['payload_hash']:
                raise PermissionError('displayed preview differs from current exact payload')
            if row['status'] != 'draft' or not self.review(draft_id)['passed']:
                raise ValueError('draft cannot be approved')
            self.db.execute("UPDATE drafts SET status='approved',approved_hash=?,approver=? WHERE id=?",
                            (row['payload_hash'], approver, draft_id))
            self.db.execute("INSERT INTO approval_events(draft_id,action,payload_hash,actor) VALUES(?,'approve',?,?)", (draft_id, row['payload_hash'], approver))

    def _approved(self, draft_id):
        row = self.preview(draft_id)
        if row['status'] != 'approved' or row['approved_hash'] != row['payload_hash']:
            raise PermissionError('current recipient/subject/body/revision requires exact human approval')
        return row

    def deliver(self, draft_id, live=False):
        """Legacy explicit simulation. Real SMTP uses submit_approved with owned sink config."""
        if live:
            raise PermissionError('Use explicit owned-sink SMTP submit_approved, not implicit live=True')
        with self.db:
            row = self._approved(draft_id)
            self.db.execute("INSERT INTO outbox(draft_id,subject,body,delivery) VALUES(?,?,?,'simulated_only')", (draft_id, row['subject'], row['body']))
            self.db.execute("UPDATE drafts SET status='simulated_delivery' WHERE id=?", (draft_id,))
        return {'draft_id': draft_id, 'delivery': 'simulated_only', 'external_messages_sent': 0}

    def submit_approved(self, draft_id, transport):
        """Claim durably BEFORE I/O. Any uncertain outcome stays held, never auto-retried."""
        from transport import OwnedSinkSMTP
        if not isinstance(transport, OwnedSinkSMTP):
            raise TypeError('Explicit OwnedSinkSMTP required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self._approved(draft_id)
            if not row['recipient'].endswith('.invalid'):
                raise PermissionError('Teaching sink accepts reserved .invalid recipients only')
            message_id = f'<academy-{draft_id}-{row["payload_hash"]}@example.invalid>'
            self.db.execute("INSERT INTO send_attempts VALUES(?,?,?,'sending',NULL)", (draft_id, row['payload_hash'], message_id))
            self.db.execute("UPDATE drafts SET status='sending' WHERE id=?", (draft_id,))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        try:
            receipt = transport.send(row, message_id)
        except BaseException as error:
            # Even a connection error is conservatively unknown. Preserve claim on crash.
            with self.db:
                self.db.execute("UPDATE send_attempts SET status='unknown_outcome',receipt=? WHERE draft_id=?", (json.dumps({'error_type': type(error).__name__, 'retry': 'held_for_manual_sink_reconciliation'}), draft_id))
                self.db.execute("UPDATE drafts SET status='unknown_outcome' WHERE id=?", (draft_id,))
            raise
        with self.db:
            self.db.execute("UPDATE send_attempts SET status='accepted_by_owned_sink',receipt=? WHERE draft_id=?", (json.dumps(receipt), draft_id))
            self.db.execute("UPDATE drafts SET status='accepted_by_owned_sink' WHERE id=?", (draft_id,))
        return {**receipt, 'draft_id': draft_id, 'approved_payload_hash': row['payload_hash']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--approve', action='store_true', help='Record local practice approval and simulate delivery')
    args = parser.parse_args()
    prospect = Prospect(**json.loads((Path(__file__).parent/'fixtures/prospect.json').read_text())['prospect'])
    team = SalesTeam()
    try:
        ident = team.create_draft(prospect)
        print(json.dumps(team.preview(ident), indent=2))
        if args.approve:
            team.approve(ident, 'CLI practice reviewer')
            print(json.dumps(team.deliver(ident), indent=2))
    finally:
        team.db.close()

if __name__ == '__main__':
    main()
