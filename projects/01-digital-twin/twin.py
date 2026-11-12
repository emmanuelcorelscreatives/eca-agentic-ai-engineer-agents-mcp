"""Deterministic teaching core. No language model or notification network calls."""
from dataclasses import dataclass, asdict
import argparse
import json
from pathlib import Path
import re
import sqlite3

@dataclass(frozen=True)
class Section:
    id: str
    title: str
    text: str
    approved: bool
    provenance: dict | None = None


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower())) - {"a", "an", "the", "what", "is", "has", "does", "and", "of", "in"}


class DigitalTwin:
    def __init__(self, sections, database=":memory:"):
        self.sections = [Section(**s) for s in sections]
        if any(type(s.approved) is not bool or not s.id or not s.text.strip() for s in self.sections):
            raise ValueError("section requires an identifier, text and explicit boolean approval")
        if len({s.id for s in self.sections}) != len(self.sections):
            raise ValueError("duplicate section identifiers")
        self.db = sqlite3.connect(database)
        self.db.execute("CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT, consent INTEGER CHECK(consent=1))")

    def retrieve(self, question, limit=3):
        if not 1 <= limit <= 10:
            raise ValueError("limit must be 1..10")
        query = tokens(question)
        ranked = [(len(query & tokens(s.title + " " + s.text)), s) for s in self.sections if s.approved]
        return [s for score, s in sorted(ranked, key=lambda x: (-x[0], x[1].id)) if score > 0][:limit]

    def answer(self, question):
        evidence = self.retrieve(question)
        return {"answer": "\n".join(s.text for s in evidence) if evidence else "The approved profile does not establish that information.",
                "citations": [s.id for s in evidence], "status": "supported" if evidence else "insufficient_evidence"}

    def record_contact(self, name, email, message, consent=False):
        if consent is not True:
            raise PermissionError("explicit contact-storage consent is required")
        if not name.strip() or not message.strip() or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("name, valid email and message are required")
        if len(message) > 2000:
            raise ValueError("message exceeds 2000 characters")
        with self.db:
            row = self.db.execute("INSERT INTO contacts(name,email,message,consent) VALUES(?,?,?,1)", (name.strip(), email, message))
        return {"contact_id": row.lastrowid, "notification": "not_sent", "status": "stored_locally"}

    def delete_contact(self, contact_id):
        with self.db:
            return self.db.execute("DELETE FROM contacts WHERE id=?", (contact_id,)).rowcount == 1

    def run_tools(self, calls):
        registry = {"retrieve": lambda **kw: [asdict(s) for s in self.retrieve(**kw)], "record_contact": self.record_contact}
        results = []
        for call in calls:
            name = call.get("name")
            if name not in registry:
                results.append({"status": "rejected", "error": "unknown tool"})
                continue
            try:
                results.append({"status": "ok", "result": registry[name](**call.get("arguments", {}))})
            except (TypeError, ValueError, PermissionError) as error:
                results.append({"status": "rejected", "error": str(error)})
        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default="What Python experience does Amara have?")
    args = parser.parse_args()
    from config import profile_path
    sections = json.loads(profile_path().read_text())["sections"]
    print(json.dumps(DigitalTwin(sections).answer(args.question), indent=2))

if __name__ == "__main__":
    main()
