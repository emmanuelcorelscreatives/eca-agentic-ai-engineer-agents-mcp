"""Transparent fixture metrics; clarity heuristic is not a human quality verdict."""
from collections import defaultdict

def evidence_quality(claims, evidence):
    known = {row['id']: row for row in evidence}
    supported = 0; citations = 0; conflicts = 0
    for claim in claims:
        refs = claim.get('evidence_ids', [])
        citations += bool(refs)
        matches = [known[x] for x in refs if x in known]
        # Every fact is a typed key/value, not substring-based grounding.
        fact = claim.get('fact')
        values = [row.get('facts', {}).get(fact) for row in matches]
        if values and all(value == claim.get('value') for value in values): supported += 1
        if len({repr(value) for value in values}) > 1: conflicts += 1
    total = len(claims)
    return {'claims':total, 'supported_claims':supported, 'cited_claims':citations,
            'conflicting_claims':conflicts, 'support_fraction':supported/total if total else None}


def decision_consistency(runs):
    """Compare pairs only within exact scenario/input hash; don't assume determinism."""
    buckets = defaultdict(list)
    for row in runs:
        buckets[(row['scenario_id'],row['input_sha256'])].append(row.get('decision'))
    pairs = agreeing = unavailable = 0
    for decisions in buckets.values():
        for index, first in enumerate(decisions):
            for second in decisions[index+1:]:
                if first is None or second is None: unavailable += 1
                else: pairs += 1; agreeing += first == second
    return {'comparable_pairs':pairs,'agreeing_pairs':agreeing,'unavailable_pairs':unavailable,
            'agreement':agreeing/pairs if pairs else None}


def explanation_clarity(text):
    # Explicit structural heuristic; human/model rubric must assess actual quality.
    words = text.split(); sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    return {'word_count':len(words),'sentence_count':len(sentences),
            'mean_words_per_sentence':len(words)/len(sentences) if sentences else None,
            'has_evidence_section':'Evidence:' in text,
            'has_limitations_section':'Limitations:' in text,
            'interpretation':'structural measurements only, not a quality pass'}
