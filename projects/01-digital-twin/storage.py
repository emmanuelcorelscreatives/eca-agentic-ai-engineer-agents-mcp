"""Durable local tools state; importing this module opens no database.

A service owns one connection. A reentrant transaction uses SQLite savepoints,
so a nested operation never accidentally commits its caller's transaction.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import threading
import time


class SQLiteStore:
    def __init__(self, database=":memory:", *, clock=time.time):
        self.database = str(database)
        self.clock = clock
        self._lock = threading.RLock()
        self._depth = 0
        self.db = sqlite3.connect(self.database, isolation_level=None, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS twin_leads (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
                message TEXT NOT NULL, consent INTEGER NOT NULL CHECK(consent=1),
                opportunity TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS twin_questions (
                id INTEGER PRIMARY KEY, question TEXT NOT NULL,
                consent INTEGER NOT NULL CHECK(consent=1), created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS twin_calls (
                call_id TEXT PRIMARY KEY, tool TEXT NOT NULL, fingerprint TEXT NOT NULL,
                result TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS twin_outbox (
                id INTEGER PRIMARY KEY, call_id TEXT NOT NULL UNIQUE REFERENCES twin_calls(call_id),
                payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
                adapter TEXT, external INTEGER NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0, receipt TEXT, error TEXT,
                created_at REAL NOT NULL, updated_at REAL NOT NULL);
        """)

    @contextmanager
    def transaction(self):
        with self._lock:
            depth = self._depth
            savepoint = f"twin_nested_{depth}"
            self.db.execute("BEGIN IMMEDIATE" if depth == 0 else f"SAVEPOINT {savepoint}")
            self._depth += 1
            try:
                yield self.db
            except BaseException:
                if depth == 0:
                    self.db.execute("ROLLBACK")
                else:
                    self.db.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                    self.db.execute(f"RELEASE SAVEPOINT {savepoint}")
                raise
            else:
                self.db.execute("COMMIT" if depth == 0 else f"RELEASE SAVEPOINT {savepoint}")
            finally:
                self._depth -= 1

    def pending_outbox(self):
        """Include held/failure states for operator visibility; never auto-retry them."""
        with self._lock:
            rows = self.db.execute("SELECT * FROM twin_outbox WHERE status NOT IN ('dry_run','delivered') ORDER BY id").fetchall()
            return [self.decode_outbox(row) for row in rows]

    @staticmethod
    def decode_outbox(row):
        result = dict(row)
        result['payload'] = json.loads(result['payload'])
        if result['receipt'] is not None:
            result['receipt'] = json.loads(result['receipt'])
        result['external'] = bool(result['external'])
        return result

    def purge_retention(self, before_timestamp):
        """Erase expired personal data but retain non-PII dedupe tombstones.

        Delivery payloads contain only local IDs. UNKNOWN/dispatching receipts stay
        visible and blocked even after contact erasure, never becoming retryable.
        A retired call ID cannot recreate erased personal data through replay.
        """
        if isinstance(before_timestamp, bool) or not isinstance(before_timestamp, (int, float)):
            raise ValueError('retention cutoff must be a numeric Unix timestamp')
        counts = {}
        with self.transaction() as db:
            for table in ('twin_leads', 'twin_questions'):
                counts[table] = db.execute(f'DELETE FROM {table} WHERE created_at < ?', (before_timestamp,)).rowcount
            counts['calls_retired'] = db.execute(
                "UPDATE twin_calls SET result=? WHERE created_at < ? AND result != ?",
                ('{"status":"expired","notification":"not_sent"}', before_timestamp,
                 '{"status":"expired","notification":"not_sent"}')).rowcount
            counts['outbox_removed'] = db.execute(
                "DELETE FROM twin_outbox WHERE created_at < ? AND status NOT IN ('dispatching','unknown')",
                (before_timestamp,)).rowcount
        return counts

    def close(self):
        with self._lock:
            self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
