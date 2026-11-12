"""Strict judge boundary and persistent feedback, separate from order approval."""
import hashlib
import json
import os
import tempfile
import sqlite3
from datetime import datetime, timezone

RUBRIC = {'evidence': '0 unsupported; 1 partial; 2 all claims grounded',
          'clarity': '0 unclear; 1 understandable; 2 clear and concise'}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def parse_judgment(raw, output):
    data = json.loads(raw)
    if not isinstance(data, dict) or set(data) != set(RUBRIC):
        raise ValueError('exact rubric dimensions required')
    for dimension, item in data.items():
        if not isinstance(item, dict) or set(item) != {'score', 'evidence_quote'}:
            raise ValueError('invalid dimension')
        if type(item['score']) is not int or not 0 <= item['score'] <= 2:
            raise ValueError('score outside rubric')
        quote = item['evidence_quote']
        if not isinstance(quote, str) or not quote.strip() or quote not in output:
            raise ValueError('evidence must quote evaluated output')
    return data


def judge(output, *, provider, model, run_id, artifact_path):
    """provider(model=..., rubric=..., output=...) -> raw JSON string.

    No provider is defaulted; timeout/unknown results are retained as failures and
    never retried here. Artifact deliberately omits raw prompt/output content;
    hashes bind original input and raw response while limiting disclosure.
    """
    if not callable(provider) or not model or not run_id:
        raise ValueError('explicit provider/model/run required')
    # Reserve durable intent BEFORE dispatch. Existing/unknown artifacts forbid replay.
    with os.fdopen(os.open(artifact_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as stream:
        json.dump({'status': 'dispatch_intent', 'model': model, 'run_id': run_id}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    record = {'run_id': run_id, 'model': model, 'input_sha256': digest(output),
              'rubric_sha256': digest(RUBRIC), 'evaluated_at': datetime.now(timezone.utc).isoformat(),
              'can_override_risk': False}
    try:
        raw = provider(model=model, rubric=RUBRIC.copy(), output=output)
        record['response_sha256'] = digest(raw)
        record['raw_response'] = raw  # private artifact: exact response, including invalid JSON
        record['judgment'] = parse_judgment(raw, output)
        record['status'] = 'scored'
    except Exception as exc:
        record['status'] = 'evaluator_failure'
        record['error_type'] = type(exc).__name__
    # Exclusive creation prevents silently overwriting a prior paid/unknown result.
    fd, temporary = tempfile.mkstemp(dir=artifact_path.parent, prefix='.judge-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(record, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, artifact_path)
        directory = os.open(artifact_path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)
    return record


class FeedbackStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS feedback (key TEXT PRIMARY KEY, payload TEXT NOT NULL)')

    def submit(self, *, key, run_id, output_sha256, reviewer, rating, comment):
        if type(rating) is not int or not 1 <= rating <= 5:
            raise ValueError('rating must be integer 1..5')
        if not all(isinstance(x, str) and x.strip() for x in (key, run_id, reviewer, comment)):
            raise ValueError('identity and comment required')
        if len(output_sha256) != 64 or any(x not in '0123456789abcdef' for x in output_sha256):
            raise ValueError('exact output SHA256 required')
        if len(comment) > 4000: raise ValueError('comment too long')
        value = {'run_id': run_id, 'output_sha256': output_sha256, 'reviewer': reviewer,
                 'rating': rating, 'comment': comment}
        payload = json.dumps(value, sort_keys=True)
        with self.db:
            old = self.db.execute('SELECT payload FROM feedback WHERE key=?', (key,)).fetchone()
            if old and old[0] != payload: raise ValueError('feedback key reused for changed submission')
            self.db.execute('INSERT OR IGNORE INTO feedback VALUES (?,?)', (key, payload))
        return value

    def list(self):
        return [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM feedback ORDER BY key')]

    def close(self): self.db.close()
