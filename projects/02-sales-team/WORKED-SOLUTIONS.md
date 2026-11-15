# Sales team: worked exercises and capstone

Run commands from the repository root except where the README explicitly changes directory. [Setup and optional SDK/UI instructions](README.md) and [Stage 8 workbook](../../curriculum/workbooks/stages-01-10.md#stage-8).

## Six worked exercises

```sh
python3 projects/02-sales-team/exercises.py
```

Read [exercises.py](exercises.py) alongside this explanation. It uses an in-memory `SalesTeam`, not a model or SMTP listener. A successful run prints `exercises_checked: 6`, a `simulated_only` receipt with zero external messages, and a reviewer-to-writer handoff.

1. `create_draft` followed by `deliver` raises `PermissionError`; the outbox count assertion remains zero. Draft generation does not grant approval.
2. `approve`, then `edit` changes revision and clears approval. The script asserts `status == 'draft'` and `approved_hash is None`. Recipient/body changes have the same approval-revocation rule.
3. Appending `Guaranteed savings.` produces a failed mechanical review; `approve` raises `ValueError`. Replacing that with invented annual revenue passes the word filter. This is a deliberate false-positive demonstration, not a true revenue assertion. The script removes it before approval. A human compares every claim with `fixtures/prospect.json`; schema/word checks cannot establish factual accuracy.
4. Approve the corrected draft and simulate once. The script asserts one outbox row and a refused second simulation. No external message is sent.
5. `dataclasses.replace(prospect, source_id='')` raises `ValueError`. Do not guess a source ID to bypass missing evidence. Use a separately identified brief, such as `fixtures/prospect-sparse.json`, for a second valid prospect.
6. `Handoff(prospect_id, campaign_id, 'reviewer', 'writer', (source_id,), revision_reason)` expresses the intended transfer and returns the unsupported-claim repair reason. This is an application contract, not observed delegation. `context_wire.SalesContext` additionally binds company, evidence revision and exact immutable identity in the actual SDK callback.

The provider-free regression file [test_student_project_02.py](../../tests/test_student_project_02.py) tests identity rejection, failed-review rejection, capstone simulation, observations and scoring. Tests with fake runners do not demonstrate actual model success.

## Draft-to-simulation capstone

Follow the README's local interface setup. First practise using `deterministic`; later, with an explicit private model configuration and billing opt-in, use `sdk-sequential`.

1. Generate and inspect each research/strategy/writer/reviewer output in the operational JSON. Deterministic mode has a template event instead, not four agent calls.
2. Compare every factual claim to its identified fictional brief. Treat unknown budget/revenue/purchase intent as unknown. A model's reviewer result is not human approval.
3. If review failed, choose Reject or save a correction. Any saved edit creates a new revision and clears approval. After edits, manually review the new text; saving is not evidence that the model re-reviewed it.
4. Refresh the exact recipient/subject/body/revision/hash. Approve only the displayed saved preview, then select **Simulate approved delivery; no email**.
5. Expect `delivery: simulated_only`, `external_messages_sent: 0`; another simulation must fail. Export the draft report, inspect approval history/current status and distinguish generation observations from the subsequent human-edited draft. A simulated outbox is not an SMTP receipt.

For an SDK run, retain the actual model/version and run configuration separately without credentials. No successful model run or UI interaction is supplied by these instructions; record your actual outcome, including errors or missing stages.

## Manager versus handoff

The paid `sdk-manager` mode exposes specialists as tools; the manager retains coordination ownership. The paid `sdk-handoff` mode transfers control to the requested specialist. Neither result is silently converted into a draft or send approval.

After each separately opted-in run, select **Export selected manager/handoff observation**. Compare actual tool names, arguments/outputs and agent-transfer events. For the handoff, inspect the validated identity callback and receiving agent. Annotate any selected specialist, explicit revision request/reason and bounded termination observed in that run. If the model did not request a revision, the correct annotation is “no revision observed,” not a fabricated revision trace. Item type names alone do not prove a successful specialist call.

The export contains operational observations, not private model reasoning or proof of hosted tracing. Draft-only actions refuse when a coordination observation is selected. Generate a separate deterministic/sequential draft to enter approval and simulation.

## Score two prospects

This walkthrough needs no model calls. The sample below produces **fixture outputs**, not observed agent output. From the project directory (`cd projects/02-sales-team`), run this script in a Python session, or place it in your own untracked practice file:

```python
import json
from pathlib import Path
from evaluations import DIMENSIONS, score_observations
from sales import Prospect, SalesTeam

records = []
for filename in ('prospect.json', 'prospect-sparse.json'):
    prospect = Prospect(**json.loads((Path('fixtures') / filename).read_text())['prospect'])
    team = SalesTeam()
    try:
        draft = team.draft(team.create_draft(prospect))
        body = draft['body']
        scores = dict.fromkeys(DIMENSIONS, 2)
        rationale = 'Offer addresses the supplied need; no observed customer result or send is claimed.'
        if filename == 'prospect-sparse.json':
            body += 'Your annual budget is one million dollars.'
            scores['factual_accuracy'] = 0
            rationale = 'Seeded failure: budget is unknown in the sparse brief.'
        records.append({
            'run_id': 'fixture-' + prospect.prospect_id,
            'output_origin': 'fixture-output',
            'prospect': prospect.__dict__, 'prospect_id': prospect.prospect_id,
            'source_id': prospect.source_id, 'subject': draft['subject'], 'body': body,
            'reviewer': 'Fictional practice reviewer', 'scores': scores, 'rationale': rationale,
        })
    finally:
        team.db.close()
print(json.dumps(score_observations(records), indent=2))
```

Expected: two fixture cases, zero agent-output cases, one failure under the exercise policy “any rubric score below 2 fails.” The sparse invented-budget case can still pass mechanical phrase checks. These are illustrative manual annotations, not general factual verification or model scoring.

For the actual-output exercise, replace subject/body with the exact retained writer output from each separately authorized run; set `run_id` to its retained operational record identity, `output_origin` to `retained-agent-output`, and manually rescore every dimension with a named reviewer and source-based rationale. Preserve failures and missing facts rather than silently replacing outputs. The source label is a declaration, not automatic provenance verification. Save your observations outside tracked source/private credentials, then run:

```sh
python3 evaluations.py --observations /path/to/your/private-observations.json
```

Retain reference-corpus labels separately from these actual-output ratings and failure counts. Do not claim complete model quality evaluation from one passing draft or the static reference corpus.
