"""Run-bound, authenticated feedback; corrections never modify historical outputs."""
import hashlib
import hmac
import json
import sqlite3
from datetime import datetime, timezone

class BoundFeedbackStore:
    def __init__(self, path):
        self.db=sqlite3.connect(path)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS review_outputs(run_id TEXT NOT NULL, output_sha256 TEXT NOT NULL,
          PRIMARY KEY(run_id,output_sha256));
        CREATE TABLE IF NOT EXISTS review_feedback(submission_id TEXT PRIMARY KEY, run_id TEXT NOT NULL,
          output_sha256 TEXT NOT NULL, reviewer TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(run_id,output_sha256) REFERENCES review_outputs(run_id,output_sha256));
        ''')

    def register_output(self,run_id,output):
        if not isinstance(run_id,str) or not run_id.strip(): raise ValueError('run required')
        sha=hashlib.sha256(output.encode()).hexdigest()
        with self.db:
            # Lock the writer before reading so two callers cannot register
            # different outputs for one immutable run identity concurrently.
            self.db.execute('BEGIN IMMEDIATE')
            old=self.db.execute('SELECT output_sha256 FROM review_outputs WHERE run_id=?',(run_id,)).fetchone()
            if old and old[0]!=sha: raise ValueError('run ID already binds a different output')
            self.db.execute('INSERT OR IGNORE INTO review_outputs VALUES (?,?)',(run_id,sha))
        return sha

    def submit(self, *, submission_id, run_id, output_sha256, reviewer, token,
               reviewer_tokens, rating, comment, correction=None):
        expected=reviewer_tokens.get(reviewer)
        if not isinstance(expected,str) or not isinstance(token,str) or not hmac.compare_digest(token,expected):
            raise PermissionError('authenticated practice reviewer required')
        if type(rating) is not int or not 1 <= rating <= 5: raise ValueError('rating must be 1..5')
        if not isinstance(comment,str) or not 1 <= len(comment) <= 4000: raise ValueError('comment required, max 4000')
        if correction is not None and (not isinstance(correction,str) or len(correction)>4000):
            raise ValueError('correction must be text max 4000')
        if not isinstance(submission_id,str) or not submission_id.strip(): raise ValueError('submission ID required')
        payload=json.dumps({'rating':rating,'comment':comment,'correction':correction},sort_keys=True)
        with self.db:
            if not self.db.execute('SELECT 1 FROM review_outputs WHERE run_id=? AND output_sha256=?',(run_id,output_sha256)).fetchone():
                raise ValueError('unknown exact run/output')
            old=self.db.execute('SELECT run_id,output_sha256,reviewer,payload FROM review_feedback WHERE submission_id=?',(submission_id,)).fetchone()
            if old and tuple(old)!=(run_id,output_sha256,reviewer,payload): raise ValueError('changed submission under same ID')
            self.db.execute('INSERT OR IGNORE INTO review_feedback VALUES (?,?,?,?,?,?)',
                (submission_id,run_id,output_sha256,reviewer,payload,datetime.now(timezone.utc).isoformat()))
        return {'submission_id':submission_id,'execution_approval':False}

    def report(self):
        rows=[{'submission_id':r[0],'run_id':r[1],'output_sha256':r[2],'reviewer':r[3],**json.loads(r[4]),'created_at':r[5]}
              for r in self.db.execute('SELECT * FROM review_feedback ORDER BY submission_id')]
        return {'reviews':rows,'count':len(rows), 'mean_rating':sum(r['rating'] for r in rows)/len(rows) if rows else None,
                'corrections':sum(bool(r['correction']) for r in rows)}

    def close(self): self.db.close()
