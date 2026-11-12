"""Persistent, approval-bound browser task core. Offline fixtures are the default."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Protocol
from urllib.parse import urlparse
from uuid import uuid4

SENSITIVE = {"submit", "download", "upload", "message", "save"}

@dataclass(frozen=True)
class Step:
    action: str
    target: str
    value: str = ""
    criterion: str = ""
    def validate(self):
        if self.action not in {"navigate", "extract", "save", *SENSITIVE}:
            raise ValueError("unsupported action")
        if not self.target or len(self.value) > 100_000:
            raise ValueError("invalid target or oversized value")
        if not self.criterion.strip():
            raise ValueError("a completion criterion is required")

    def digest(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

class Executor(Protocol):
    def execute(self, step: Step) -> str: ...

class FixtureBrowser:
    """Reads only bundled local HTML; deliberately cannot submit real forms."""
    def __init__(self, root: Path):
        self.root = root.resolve()
    def execute(self, step: Step) -> str:
        if step.action not in {"navigate", "extract"}:
            raise ValueError("fixture browser supports only read actions")
        path = (self.root / step.target).resolve()
        if not path.is_relative_to(self.root) or path.suffix != ".html":
            raise ValueError("outside fixture allowlist")
        from html.parser import HTMLParser
        class Text(HTMLParser):
            def __init__(self):
                super().__init__(); self.parts = []
            def handle_data(self, data): self.parts.append(data)
        parser = Text(); parser.feed(path.read_text())
        return " ".join(" ".join(parser.parts).split())

class ArtifactTools:
    """Wrap a read executor with exclusive writes inside a dedicated artifact root.

    The caller's TaskStore requires exact approval before every save. The root
    must be a dedicated, trusted directory, not shared with hostile writers.
    """
    def __init__(self, reader: Executor, root: Path):
        self.reader = reader
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
    def execute(self, step: Step) -> str:
        if step.action != 'save': return self.reader.execute(step)
        if Path(step.target).name != step.target or step.target in {'.', '..'}:
            raise ValueError('artifact target must be a simple filename')
        path = self.root / step.target
        with path.open('x', encoding='utf-8') as stream:
            stream.write(step.value)
        return 'Saved artifact: ' + path.name

class PlaywrightBrowser:
    """Optional real browser. A local HTTP origin must be explicitly allowlisted.

    Only navigate/extract are implemented; sensitive browser writes fail closed.
    The persistent approval lifecycle can be reused by a separately audited adapter.
    """
    def __init__(self, origin: str):
        parsed = urlparse(origin)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.path not in {"", "/"}:
            raise ValueError("use a dedicated loopback fixture origin")
        self.origin = origin.rstrip("/")
    def execute(self, step: Step) -> str:
        from playwright.sync_api import sync_playwright
        if step.action not in {"navigate", "extract"}:
            raise ValueError("sensitive browser interaction is not implemented")
        target = self.origin + "/" + step.target.lstrip("/")
        if ".." in step.target or urlparse(step.target).scheme:
            raise ValueError("unsafe relative URL")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(service_workers="block", accept_downloads=False)
                def route(request_route):
                    url = urlparse(request_route.request.url)
                    expected = urlparse(self.origin)
                    if (url.scheme, url.netloc) == (expected.scheme, expected.netloc) and request_route.request.method == "GET":
                        request_route.continue_()
                    else: request_route.abort()
                context.route("**/*", route)
                page = context.new_page(); page.goto(target, wait_until="domcontentloaded")
                return page.locator("body").inner_text()
            finally: browser.close()

class TaskStore:
    def __init__(self, database: Path):
        self.db = sqlite3.connect(database)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS task(id TEXT PRIMARY KEY, objective TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS step(task TEXT, number INTEGER, payload TEXT NOT NULL,
          state TEXT NOT NULL, approved_hash TEXT, result TEXT, PRIMARY KEY(task,number));
        CREATE TABLE IF NOT EXISTS trace(task TEXT, number INTEGER, event TEXT, detail TEXT,
          created TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
    def close(self): self.db.close()
    def create(self, objective: str, steps: list[Step]):
        if not objective.strip() or not steps: raise ValueError("objective and steps required")
        for step in steps: step.validate()
        task = str(uuid4())
        with self.db:
            self.db.execute("INSERT INTO task VALUES (?,?)", (task, objective))
            for number, step in enumerate(steps):
                self.db.execute("INSERT INTO step VALUES (?,?,?,'pending',NULL,NULL)", (task, number, json.dumps(asdict(step))))
        return task
    def checklist(self, task):
        return [dict(row) for row in self.db.execute("SELECT * FROM step WHERE task=? ORDER BY number", (task,))]
    def decide(self, task, number, decision, replacement: Step | None = None):
        if decision not in {"approve", "edit", "reject"}: raise ValueError("invalid decision")
        with self.db:
            row = self.db.execute("SELECT * FROM step WHERE task=? AND number=?", (task, number)).fetchone()
            if row is None or row['state'] not in {'pending', 'awaiting_approval'}: raise ValueError("step is not editable")
            step = replacement if replacement is not None else Step(**json.loads(row['payload']))
            step.validate()
            if decision == 'edit' and replacement is None: raise ValueError("replacement required")
            state = 'rejected' if decision == 'reject' else 'pending'
            approved = step.digest() if decision == 'approve' else None
            self.db.execute("UPDATE step SET payload=?,state=?,approved_hash=? WHERE task=? AND number=?", (json.dumps(asdict(step)),state,approved,task,number))
            self.db.execute("INSERT INTO trace(task,number,event,detail) VALUES (?,?,?,?)", (task,number,decision,step.digest()))
    def advance(self, task, executor: Executor):
        # Transaction serializes competing runners; a crash during execution leaves an
        # explicit unknown state requiring investigation, never an automatic replay.
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT * FROM step WHERE task=? AND state!='complete' ORDER BY number LIMIT 1", (task,)).fetchone()
            if row is None:
                self.db.commit(); return "complete"
            step = Step(**json.loads(row['payload'])); step.validate()
            if row['state'] in {'rejected','executing','failed'}:
                self.db.commit(); return row['state']
            if step.action in SENSITIVE and row['approved_hash'] != step.digest():
                self.db.execute("UPDATE step SET state='awaiting_approval' WHERE task=? AND number=?", (task,row['number']))
                self.db.commit(); return 'awaiting_approval'
            self.db.execute("UPDATE step SET state='executing' WHERE task=? AND number=?", (task,row['number']))
            self.db.commit()
        except BaseException:
            self.db.rollback(); raise
        try:
            result = executor.execute(step)
            if not isinstance(result, str) or not result.strip(): raise ValueError("empty result: completion criterion unmet")
        except Exception as error:
            with self.db:
                self.db.execute("UPDATE step SET state='failed', result=? WHERE task=? AND number=?", (str(error),task,row['number']))
            raise
        with self.db:
            self.db.execute("UPDATE step SET state='complete',result=? WHERE task=? AND number=?", (result,task,row['number']))
            self.db.execute("INSERT INTO trace(task,number,event,detail) VALUES (?,?,'complete',?)", (task,row['number'],step.digest()))
        return 'step_complete'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--database', default='sidekick.sqlite')
    args = parser.parse_args(); store = TaskStore(Path(args.database))
    try:
        task = store.create('Compare synthetic Academy workshop dates', [Step('extract','workshops.html',criterion='Return workshop dates and prices')])
        print('Task:',task); print(store.advance(task,FixtureBrowser(Path(__file__).parent/'fixtures')))
        print(json.dumps(store.checklist(task),indent=2))
    finally: store.close()
