"""Exact excerpts with immutable provenance, unresolved conflicts and honest gaps."""
import hashlib
import json

class EvidenceStore:
    def __init__(self): self.records = {}
    def append(self, source, excerpt):
        if not excerpt or excerpt not in source["text"]:
            raise ValueError("excerpt must be an exact non-empty substring")
        payload = {"source_id": source["id"], "url": source["url"], "title": source["title"],
                   "published": source.get("published"), "retrieved": source.get("retrieved"),
                   "topic": source["topic"], "value": source["value"], "excerpt": excerpt,
                   "offset": source["text"].index(excerpt)}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        self.records.setdefault(digest, {"id": digest, **payload})
        return digest

def analyze(records):
    groups = {}
    for record in records:
        groups.setdefault(record["topic"], {}).setdefault(record["value"], []).append(record["id"])
    return [{"topic": topic, "status": "conflicting" if len(values)>1 else "supported_by_fixture",
             "alternatives": [{"value": value, "evidence_ids": sorted(refs)} for value, refs in sorted(values.items())]}
            for topic, values in sorted(groups.items())]

def validate_findings(findings, records):
    ids = {r["id"] for r in records}
    for finding in findings:
        for item in finding["alternatives"]:
            if not item["evidence_ids"] or not set(item["evidence_ids"]) <= ids:
                raise ValueError("unsupported evidence reference")
    return findings

def quality(findings, required=("accessibility", "cost", "operations")):
    covered = {f["topic"] for f in findings}
    return {"missing": sorted(set(required)-covered),
            "conflicts": [f["topic"] for f in findings if f["status"] == "conflicting"],
            "decision": "insufficient_evidence" if not findings or set(required)-covered else
                        "unresolved_conflicts" if any(f["status"] == "conflicting" for f in findings) else "fixture_evidence_complete"}
