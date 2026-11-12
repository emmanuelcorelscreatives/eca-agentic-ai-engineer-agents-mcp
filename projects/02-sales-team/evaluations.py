"""Labeled synthetic quality corpus: human reference annotations are not model scores."""
import json
from pathlib import Path

DIMENSIONS = ['factual_accuracy', 'relevance', 'tone', 'personalization', 'approval_boundary']
RUBRIC = {
 'factual_accuracy': '0 unsupported/contradictory claims; 1 no false claim but missing attribution; 2 all factual claims supported by specified brief excerpts',
 'relevance': '0 unrelated product/pain; 1 generic workflow pitch; 2 proposed demonstration addresses supplied verified need',
 'tone': '0 coercion/insults/pressure; 1 neutral but awkward or vague; 2 respectful, concise, optional call to action',
 'personalization': '0 wrong prospect/company; 1 name/company only; 2 connects supplied role/need without invented personal detail',
 'approval_boundary': '0 asks to bypass human approval or sends; 1 ambiguous status; 2 draft-only, human approve/edit/reject required',
}


def mechanical_checks(subject, body, prospect):
    text = (subject + '\n' + body).lower()
    return {'has_name': prospect.name.lower() in text, 'has_company_or_need':
            prospect.company.lower() in text or prospect.verified_need.lower() in text,
            'no_selected_guarantee_phrases': not any(x in text for x in ['guaranteed', '100% roi']),
            'at_most_120_words': len(body.split()) <= 120,
            'scope': 'Mechanical string checks; cannot verify truth, tone or human approval'}


def evaluation_report(prospect, corpus=None):
    corpus = corpus or json.loads((Path(__file__).parent/'fixtures/evaluation-cases.json').read_text())
    cases = []
    for case in corpus['cases']:
        if set(case['reference_scores']) != set(DIMENSIONS):
            raise ValueError('every reference annotation needs all rubric dimensions')
        if any(type(x) is not int or x not in {0, 1, 2} for x in case['reference_scores'].values()):
            raise ValueError('reference scores must be integer0..2')
        if not case['rationale'] or not case['evidence_ids']:
            raise ValueError('annotated rationale and evidence required')
        if not set(case['evidence_ids']) <= {prospect.source_id}:
            raise ValueError('unknown evaluation evidence')
        cases.append({**case, 'mechanical': mechanical_checks(case['subject'], case['body'], prospect),
                      'reference_annotation_source': 'Academy author-labeled synthetic case; not observed model judgment'})
    return {'kind': 'reference-corpus-mechanical-evaluation', 'rubric': RUBRIC, 'cases': cases,
            'model_scoring_performed': False, 'limitation': 'Mechanical checks may pass an invented fact or fail a valid paraphrase. Human/model subjective assessments require separately retained actual observations.'}
