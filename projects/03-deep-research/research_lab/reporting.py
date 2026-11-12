"""Inspectable bundle export, digest-bound approval and simulated delivery."""
import hashlib
import json
from pathlib import Path

def markdown(bundle):
    lines = ["# Academy research report", bundle["plan"]["question"], "", "## Method",
             bundle["scope"], "", "## Findings"]
    for finding in bundle["findings"]:
        lines.append(f'### {finding["topic"]}: {finding["status"]}')
        for alternative in finding["alternatives"]:
            lines.append(f'- {alternative["value"]} [{", ".join(alternative["evidence_ids"])}]')
    lines += ["", "## Limitations", json.dumps(bundle["quality"], sort_keys=True),
              "Dates may be unknown. Fixture agreement is not independent verification of real-world truth.",
              "", "## Recommendation", "Resolve gaps and conflicts before choosing a real scheduling product.",
              "", "## References"]
    for evidence in bundle["evidence"]:
        lines.append(f'- [{evidence["id"]}] {evidence["title"]}; {evidence["url"]}; exact excerpt: {evidence["excerpt"]}')
    return "\n".join(lines)

def export_bundle(bundle, directory):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    files = {"report.md": markdown(bundle), "research.json": json.dumps(bundle, indent=2, sort_keys=True)}
    for name, content in files.items(): (directory/name).write_text(content)
    manifest = {name: hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in files}
    (directory/"sha256.json").write_text(json.dumps(manifest, indent=2))
    return manifest

def delivery_digest(recipient, report):
    if "@" not in recipient or "\n" in recipient or "\r" in recipient:
        raise ValueError("invalid recipient")
    return hashlib.sha256((recipient + "\0" + report).encode()).hexdigest()

def deliver_approved(recipient, report, approved_digest, adapter):
    if approved_digest != delivery_digest(recipient, report):
        raise ValueError("recipient and exact report require approval")
    return adapter(recipient, report)

class SimulatedOutbox:
    def __init__(self): self.messages = []
    def __call__(self, recipient, report):
        self.messages.append({"recipient": recipient, "report": report})
        return {"status": "simulated_only", "message_count": len(self.messages)}
