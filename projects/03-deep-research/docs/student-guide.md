# Stages 9–10 student guide

Use the [workbook](../../../curriculum/workbooks/stages-01-10.md#stage-9) for each
lesson's practical, deliverable and acceptance criteria. This guide supplies the
project-specific setup and a local practice route; it does not replace live deliverables
with fixtures. Commands here assume the **repository root** on Linux/macOS. On Windows,
use Python 3.11+ through `py -3` and activate `.venv\Scripts\Activate.ps1` in PowerShell.

## Offline setup and expected result

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 examples/stages09-10/run_research.py
python3 -m unittest discover -s projects/03-deep-research/tests -v
```

No package installation, API key, account, email or web access is needed for these
commands. Optional Gradio-dependent tests may skip and must be reported as skipped.

The default workshop report uses four Academy-authored records from
[`s09-workshop-sources.json`](../data/s09-workshop-sources.json). It should show
accessibility and operations findings, **30 versus 45 credits** as unresolved cost
alternatives, source citations, `human_review_required: true` and `tokens: null`.
`example.invalid` URLs identify practice records, not visited pages. This deterministic
route supports only `Community workshop scheduling` (case/spacing variations allowed).
Changing the question to an unrelated topic raises an explicit scope error before
any retrieval. It does not produce findings for that topic.

Create a private export directory outside the checkout:

```sh
python3 examples/stages09-10/run_research.py --export "$HOME/eca-workshop-report"
```

Inspect `report.md`, `research.json`, `sha256.json` and `checkpoint.json` there. The
manifest hashes the Markdown and JSON bytes; the checkpoint preserves the same
question-bound fixture bundle. These are not the four v3 live-application exports.
Do not publish raw reports/state containing private data from a future live run.

## Lesson practice and reference checks

| Workbook lessons | Concrete practice | Expected check / deliverable |
|---|---|---|
| s09-l01–l02 | Write the workshop brief and diagram `planning.ROLES`, search, evidence, quality and reporting. | Brief separates fixture scope from real research and states what missing evidence means. |
| s09-l03–l04 | Inspect `planning.py` and `sdk_v2.py`; map query IDs to task IDs in the exported JSON. | Fixed fixture tasks are not claimed to be a generated plan. A live-plan deliverable requires actual SDK output from the optional route below. |
| s09-l05–l06 | Inspect `brave_search.py`, `contracts_v2.py` and the exact-excerpt tests. Change an excerpt in an isolated copy of a test record. | The changed excerpt is rejected; snippets are not independently fetched full pages. Real search receipts remain a separate live deliverable. |
| s09-l07–l09 | Follow one cost alternative from source text to evidence ID and report; inspect malformed-plan/report tests. | Both 30/45-credit alternatives remain cited; invalid structures cannot advance. |
| s09-l10–l13 | Run `test_stage09_semantic_repairs.py` through unittest discovery and read its dependency, cancellation and quality cases. | Diagram phase order; list one completed-reuse case and one held UNKNOWN case. Fake backends test behavior, not real provider success. |
| s10-l01–l04 | Map `pipeline_v2.py`, `interface_v2.py` and `interface_v3.py`; compare their event allowlists with the offline UI. | Public status is operational metadata, not secret/private reasoning; fixture UI observations do not establish live UI behavior. |
| s10-l05 | Export the offline bundle, then inspect `exports_v2.py` and its simulated-delivery tests. | Report citations survive export. Email remains disabled unless separately configured and recipient/report approval is exact; fake delivery is not an SMTP receipt. |
| s10-l06–l08 | Add two cases to an isolated copy of `data/s10-evaluation-v2.json`; draft a rubric sheet using `quality_v2.py`. | Preserve held-out split and uncertainty criteria. Human judgments cite evidence; missing tokens stay null; summed concurrent spans are not wall time. |
| s10-l09 | Inspect `tests/test_stage10_recovery_export_v3.py` and the [recovery contract](selective-recovery-and-owned-export-v3.md). | The failed known branch alone may resume with exact authorization; completed siblings and raw history are retained; UNKNOWN never replays. |
| s10-l10–l11 | Follow [v3 deployment](../deployment/research-v3/README.md) only after choosing live accounts/budget. | Record actual health, report and own-session download results separately; unobserved live/module deliverables remain incomplete. |

The [Cedar comparison](../README.md#legacy-cedar-comparison-exercise) has a separate
45/70-minute corpus and an unrelated-question insufficient-evidence exercise. Never
mix those records into workshop results. Keep source trust, consent, bounded recovery
and private-session checks when extending either route.

## Optional offline UI

Use a separate virtual environment for the UI rather than installing every course
framework together. From the repository root:

```sh
python3 -m venv .venv-research-ui
. .venv-research-ui/bin/activate
python3 -m pip install -r projects/03-deep-research/requirements-ui-stages09-10.txt
python3 examples/stages09-10/run_research.py --ui
```

Open the localhost URL printed by Gradio. This is the synthetic workshop UI, not the
v3 application: it uses no model/search service, supports the same fixed question and
does not establish live deployment or owned-session downloads. It binds localhost
with sharing disabled. The UI requirements are not a frozen deployment lock; actual
browser compatibility must be checked in the environment where you install them.

## Optional live SDK and search

This route makes real, potentially paid model and Brave Search requests. Do not run
it as part of offline tests. Choose your own accounts, access permissions, model and
finite spending budget first. No internal production approval actor is required.

For the current application use **Python 3.12** in an isolated environment and the
supplied v3 transitive hash lock, not the legacy `requirements-optional.txt`:

```sh
python3.12 -m venv .venv-research-live
. .venv-research-live/bin/activate
python3 -m pip install --require-hashes -r projects/03-deep-research/deployment/research-v3/requirements.lock
```

Configure `OPENAI_API_KEY`, `BRAVE_SEARCH_API_KEY` and `ACADEMY_MODEL` through your local
secret manager or private environment outside this repository; never paste credentials
into command arguments, reports or commits. Dependency installation is not a live-call
test. Replace the source-revision placeholder with the reviewed source version you
actually use. Choose new private state/output paths for a genuinely new run; preserve
and reconcile the original paths for any existing or interrupted run.

```sh
python3 projects/03-deep-research/capstone_v2.py --live \
  --question 'Compare evidence for an accessible community workshop scheduling pilot.' \
  --source-revision YOUR_REVIEWED_SOURCE_REVISION --workers 3 \
  --state "$HOME/eca-research/run-01/state" --output "$HOME/eca-research/run-01/output"
```

Retain exact plan/source/response attribution, observed spans and uncertainty. Search
snippets are not full pages and unknown dates stay unknown. A timeout or IN_FLIGHT/
UNKNOWN journal entry is not permission to delete state and repeat a paid operation.
The CLI uses the v2 journal; selective known-failure recovery is the separate
[v3 contract](selective-recovery-and-owned-export-v3.md), not automatic CLI retry.
See the [architecture](semantic-repair-stages09-10-v2.md) for contracts and the
[deployment exercise](../deployment/research-v3/README.md) for the current UI.
