"""Local sales workflow with immutable approved payloads and a simulated outbox."""
from dataclasses import dataclass
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

@dataclass(frozen=True)
class Prospect:
    name: str
    company: str
    role: str
    verified_need: str
    source_id: str
    email: str


def digest(subject, body):
    return hashlib.sha256(json.dumps([subject, body], separators=(",", ":")).encode()).hexdigest()


class SalesTeam:
    def __init__(self, database=":memory:"):
        self.db = sqlite3.connect(database)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS drafts(id INTEGER PRIMARY KEY, subject TEXT NOT NULL, body TEXT NOT NULL, source_id TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', approved_hash TEXT, approver TEXT);
        CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY, draft_id INTEGER UNIQUE, subject TEXT, body TEXT, delivery TEXT NOT NULL);
        """)

    def create_draft(self, prospect):
        if not prospect.source_id or not prospect.verified_need:
            raise ValueError("verified need and source attribution are required")
        subject = f"A practical workflow for {prospect.company}"
        body = f"Hello {prospect.name},\nYour practice brief identifies {prospect.verified_need}. We can demonstrate a small reporting prototype and review its fit with you. Would a walkthrough be useful?\nAcademy practice team"
        with self.db:
            row = self.db.execute("INSERT INTO drafts(subject,body,source_id) VALUES(?,?,?)", (subject, body, prospect.source_id))
        return row.lastrowid

    def draft(self, draft_id):
        row = self.db.execute("SELECT * FROM drafts WHERE id=?", (draft_id,)).fetchone()
        if row is None:
            raise KeyError(draft_id)
        return dict(row)

    def edit(self, draft_id, subject, body):
        if not subject.strip() or not body.strip():
            raise ValueError("empty draft")
        with self.db:
            row = self.db.execute("UPDATE drafts SET subject=?,body=?,status='draft',approved_hash=NULL,approver=NULL WHERE id=? AND status!='simulated_delivery'", (subject, body, draft_id))
            if row.rowcount != 1:
                raise ValueError("missing draft or delivery already completed")

    def review(self, draft_id):
        row = self.draft(draft_id)
        text = row['body'].lower()
        issues = [word for word in ('guaranteed', '100% roi', 'market leader') if word in text]
        return {"passed": not issues, "issues": issues, "source_id": row['source_id'], "scope": "deterministic sample checks; human factual review still required"}

    def approve(self, draft_id, approver):
        if not approver.strip():
            raise ValueError("named human approver required")
        with self.db:
            row = self.draft(draft_id)
            if row['status'] != 'draft' or not self.review(draft_id)['passed']:
                raise ValueError("draft cannot be approved")
            self.db.execute("UPDATE drafts SET status='approved',approved_hash=?,approver=? WHERE id=?", (digest(row['subject'], row['body']), approver, draft_id))

    def deliver(self, draft_id, live=False):
        if live:
            raise PermissionError("live delivery is not implemented in this practice core")
        with self.db:
            row = self.draft(draft_id)
            if row['status'] != 'approved' or row['approved_hash'] != digest(row['subject'], row['body']):
                raise PermissionError("current exact payload requires human approval")
            self.db.execute("INSERT INTO outbox(draft_id,subject,body,delivery) VALUES(?,?,?,'simulated_only')", (draft_id, row['subject'], row['body']))
            self.db.execute("UPDATE drafts SET status='simulated_delivery' WHERE id=?", (draft_id,))
        return {"draft_id": draft_id, "delivery": "simulated_only", "external_messages_sent": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve", action="store_true", help="record a practice human approval and simulate delivery")
    args = parser.parse_args()
    prospect = Prospect(**json.loads((Path(__file__).parent / "fixtures/prospect.json").read_text())["prospect"])
    team = SalesTeam()
    ident = team.create_draft(prospect)
    print(json.dumps(team.draft(ident), indent=2))
    if args.approve:
        team.approve(ident, "CLI practice reviewer")
        print(json.dumps(team.deliver(ident), indent=2))

if __name__ == "__main__":
    main()
