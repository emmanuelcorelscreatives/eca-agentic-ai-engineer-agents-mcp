"""Public operational events and request-bound durable recovery."""
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path
from .planning import make_plan, queries_for
from .search import parallel_search
from .evidence import EvidenceStore, analyze, validate_findings, quality

async def run(question, backend, workers=3, event_callback=None):
    started = time.monotonic(); plan = make_plan(question)
    events = []
    def emit(event):
        events.append(event)
        if event_callback is not None: event_callback(event)
    emit({"phase": "planned", "task_count": len(plan["tasks"])})
    branches = await parallel_search(queries_for(plan), backend, workers)
    store = EvidenceStore()
    for branch in branches:
        for source in branch["sources"]: store.append(source, source["text"])
        emit({"phase": "searched", "query_id": branch["query"]["id"],
                       "source_count": len(branch["sources"]), "error": branch["error"]})
    evidence = list(store.records.values()); findings = analyze(evidence)
    validate_findings(findings, evidence)
    emit({"phase": "completed", "duration_seconds": time.monotonic()-started,
                   "tokens": None, "token_measurement": "not supplied by fixture backend"})
    return {"schema_version": 1, "plan": plan, "evidence": evidence, "findings": findings,
            "quality": quality(findings), "events": events,
            "scope": ("Academy-authored synthetic offline corpus; no live web observations"
                      if backend.__class__.__name__ == "FixtureSearch" else
                      "Configured search adapter results; independently review sources and provenance")}

def save_checkpoint(bundle, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as handle:
        json.dump(bundle, handle, sort_keys=True); handle.flush(); os.fsync(handle.fileno())
    temporary.replace(path)

def resume_checkpoint(question, path):
    bundle = json.loads(Path(path).read_text())
    if bundle.get("schema_version") != 1 or bundle.get("plan", {}).get("question") != question.strip():
        raise ValueError("checkpoint request mismatch")
    validate_findings(bundle["findings"], bundle["evidence"])
    return bundle

async def bounded_retry(operation, max_attempts=2):
    """Only explicit retryable read failures. Never retry unknown paid outcomes."""
    if not 1 <= max_attempts <= 3: raise ValueError("attempts must be 1..3")
    for attempt in range(max_attempts):
        try: return await operation()
        except ConnectionRefusedError:
            if attempt+1 == max_attempts: raise
            await asyncio.sleep(0)
