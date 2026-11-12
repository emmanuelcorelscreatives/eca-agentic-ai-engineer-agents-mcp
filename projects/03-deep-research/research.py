"""Source-attributed research over a synthetic local corpus, not live web search."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import argparse
import json
from pathlib import Path
import re

@dataclass(frozen=True)
class Evidence:
    source_id: str
    title: str
    location: str
    published: str
    claim: str
    value: str
    excerpt: str


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def search(query, corpus):
    terms = words(query) - {"what", "the", "is", "for", "of", "and"}
    scored = [(len(terms & words(e.title + ' ' + e.claim + ' ' + e.excerpt)), e) for e in corpus]
    return [e for score, e in sorted(scored, key=lambda pair: (-pair[0], pair[1].source_id)) if score]


def plan(question):
    if not question.strip():
        raise ValueError("research question is required")
    return {"question": question, "queries": [question, question + " limitations", question + " conflicting findings"],
            "completion": "every conclusion has local source references; contradictions and gaps are explicit"}


def investigate(question, corpus, max_workers=3):
    if not 1 <= max_workers <= 8:
        raise ValueError("max_workers must be 1..8")
    if len({e.source_id for e in corpus}) != len(corpus):
        raise ValueError("duplicate source identifiers")
    research_plan = plan(question)
    # Expansion terms must not manufacture relevance to an unrelated question.
    relevant = search(question, corpus)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        branches = list(executor.map(lambda q: search(q, relevant), research_plan['queries']))
    collected = {e.source_id: e for branch in branches for e in branch}
    claims = {}
    for e in collected.values():
        claims.setdefault(e.claim, {}).setdefault(e.value, []).append(e.source_id)
    findings = []
    for claim, values in sorted(claims.items()):
        findings.append({"claim": claim, "status": "conflicting" if len(values) > 1 else "supported_by_local_corpus", "alternatives": [{"value": value, "citations": sorted(refs)} for value, refs in sorted(values.items())]})
    return {"plan": research_plan, "scope": "synthetic local corpus only; no live search or independent truth verification", "findings": findings,
            "status": "insufficient_evidence" if not findings else "conflicts_present" if any(f['status']=='conflicting' for f in findings) else "local_evidence_found",
            "sources": [e.__dict__ for e in sorted(collected.values(), key=lambda e:e.source_id)]}


def markdown(report):
    lines = ['# Research report', report['plan']['question'], '', report['scope'], '']
    for finding in report['findings']:
        lines.append(f"## {finding['claim']} — {finding['status']}")
        for value in finding['alternatives']:
            lines.append(f"- {value['value']} [{', '.join(value['citations'])}]")
    if not report['findings']:
        lines.append('No matching evidence. No conclusion can be established.')
    lines.append('\n## Sources')
    for e in report['sources']:
        lines.append(f"- [{e['source_id']}] {e['title']} ({e['published']}), {e['location']}. Excerpt: {e['excerpt']}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('question', nargs='?', default='Cedar Library weekly reporting time')
    args = parser.parse_args()
    data = json.loads((Path(__file__).parent/'fixtures/evidence.json').read_text())
    print(markdown(investigate(args.question, [Evidence(**e) for e in data['evidence']])))

if __name__ == '__main__':
    main()
