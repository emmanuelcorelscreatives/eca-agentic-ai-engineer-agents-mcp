# Project 1: Professional Digital Twin Agent

Stage 5 implements a professional representative of **fictional Amara Okoye**. The résumé, portfolio and Cedar Library work are synthetic Academy teaching material, never a claim about a real person's employment. The project includes approved-source answers, an implemented grounded SDK adapter, typed contact/question tools, durable action receipts, a local notification outbox, conversation/tool context allocation, a real Gradio interface and deploy/privacy configuration.

## Start with the offline exercise

From the repository root, run the excerpt demo below, then the shared tests with `python3 scripts/run_tests.py`. No optional dependencies or model account are needed for this CLI exercise. Expect approved-source excerpts or an explicit abstention, not a generated model answer. See the [stage 1–10 workbook](../../curriculum/workbooks/stages-01-10.md) for the stage 5 exercises.

## Run the actual application

Use Python **3.10 or newer**. The CLI works directly from a checkout without third-party packages:

```sh
python3 projects/01-digital-twin/twin.py 'Python experience'
python3 projects/01-digital-twin/twin.py 'Has Amara won a national award?'
```

The first command should return `status: supported` and citation `profile-01`; the second should return `status: insufficient_evidence` and no citations. These are approved excerpts or abstention, not model-generated answers.

For the optional interface, create and activate an isolated environment. On macOS/Linux, from the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e ./projects/01-digital-twin -r projects/01-digital-twin/requirements-optional.txt
python3 projects/01-digital-twin/app.py
```

On Windows PowerShell, use the environment's interpreter directly; activation or execution-policy changes are not required:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ./projects/01-digital-twin -r projects/01-digital-twin/requirements-optional.txt
.\.venv\Scripts\python.exe projects/01-digital-twin/app.py
```

After installation, `eca-twin` and `eca-twin-ui` are the equivalent entry points. Keep the environment private; do not commit it. Settings read the launching process's environment; copying `.env.example` to `.env` does **not** load it automatically. Leave `TWIN_LIVE_MODEL_ENABLED` false for the offline exercise. `TWIN_PROFILE` optionally selects a private reviewed profile; see [loading reviewed sections](docs/ingestion.md#load-your-reviewed-sections).

The UI shows its exact mode. The default deterministic baseline returns approved excerpts, discloses the AI representation, cites sources and demonstrates contact flows with no model charge. For actual generated answers, deliberately configure `TWIN_LIVE_MODEL_ENABLED=true`, `ACADEMY_MODEL` and a private `OPENAI_API_KEY`; the same UI then invokes the real SDK adapter with bounded turns and explicit context allocation. This authorizes paid model use. The application never enables it merely because a key happens to exist. Model grounding, identity, tone and injection behaviour must be evaluated from genuine retained responses, not SDK object construction.

## Sources and ingestion

`make_pdf_fixture.py` can generate a matching résumé **and portfolio** from `fixtures/resume-source.txt` and `fixtures/portfolio-source.txt`, preserving Unicode and line structure with a real embedded TTF. It writes actual document/source/font/generator SHA values when executed and requires an explicit new `--output-dir`. See [ingestion](docs/ingestion.md). Matching PDFs already supplied in `fixtures/generated/` can be inspected without regeneration; review your own generated files separately if you perform that exercise. The older one-page synthetic resume fixture is retained as historical teaching evidence.

`pdf_ingest.py` records document SHA, exact raw page text and page text hashes, cleaned multiline text, page association, extraction warnings and exports. Extraction never grants factual approval. Scanned/corrupt/encrypted cases return actionable errors. Reviewed extraction sections can be approved individually before loading them into `DigitalTwin`; the `provenance` field is accepted and retained. The supplied `fixtures/profile.json` is the small preapproved starter dataset and is duplicated byte-for-byte as package data for installed CLI use.

## Agent and authority boundaries

- `prompts.py`: explicit AI representation identity, professional tone, grounded citations and untrusted document/history/tool boundaries.
- `context.py`: whole evidence, recent conversation and tool receipts with an output reserve and allocation report. An injectable counter can measure actual tokenizer units. Default character counts are labelled characters, never tokens.
- `twin.py`: deterministic approved-section retrieval and the legacy introductory API. Unsupported questions abstain; this is lexical retrieval, not semantic truth verification.
- `tools.py`, `storage.py`: typed `Lead`, `Question`, `ToolCall`; explicit registry, eight-call turn bound, transactional call-ID fingerprint ledger, persistent resume/replay dedupe and retained source of each local action.
- `notifications.py`: default local dry run and an explicitly configured notification adapter. SQLite outbox payloads are structured JSON record IDs. Lead creation and outbox insertion are atomic; notification execution is separately recorded. Unknown external outcomes never become automatically retryable.
- `status.py`, `service.py`, `app.py`: stable action IDs, consent/validation/storage/notification checklist, no premature success, real contact/opportunity/question controls, private local state and per-session request limits.

Repeated submission of the same call ID and payload returns the same receipt. A changed email/message with the old call ID is refused. A retired action ID cannot recreate personal information after retention cleanup. The UI's “Start another” controls deliberately create a new action identity; this is separate from replaying an old action.

## Exercises and evidence

[Project charter](docs/project-charter.md) defines the users, approved sources, boundaries and ten classified scenarios. [Architecture](docs/architecture.md) explains import-safe module authority. `data/evaluation/professional-questions.jsonl` contains 24 versioned professional, privacy, identity, consent, replay, notification and context cases. `evaluate.py --output ACTUAL_REPORT.json` writes actual observations, failures and explicit model-quality limitations when executed.

Tests are in repository `tests/test_stage05_semantic_repairs_application.py`, `tests/test_stage05_semantic_repairs_tools.py` and `tests/test_stage05_semantic_repairs_ingest.py`. They are included by the shared test runner. Optional dependencies may cause explicit skips. A static prompt assertion or fake runner is not observed model behaviour; test the optional interface and configured model separately before claiming those outcomes.

### Stage 5 exercise and reference map

Use the [stage 5 workbook](../../curriculum/workbooks/stages-01-10.md#stage-5) for the authored deliverables and acceptance criteria. The files below are reference solutions to inspect and extend, not proof that you completed a live integration. Keep your actual observations private and distinguish expected results from observed ones.

| Lesson | Reference solution | Your task and expected check |
|---|---|---|
| s05-l01 — plan | [Project charter](docs/project-charter.md) | Write your own brief and classify supported, absent and consent-required cases. |
| s05-l02 — PDFs | [Ingestion guide](docs/ingestion.md), `pdf_ingest.py` | Inspect supplied PDFs or generate to a fresh directory; compare extraction and leave unreviewed sections unapproved. |
| s05-l03 — prompt | `prompts.py`, [evaluation rubric](docs/evaluation-rubric.md) | Version a prompt change; separately observe grounded, unsupported and private-information responses from an explicitly enabled model. |
| s05-l04 — context | `context.py:assemble_context` | Add long history; inspect dropped whole items and retained source IDs/output reserve. Default units are characters, not tokens. |
| s05-l05 — retrieval | `twin.py:DigitalTwin`, [reviewed-source handoff](docs/ingestion.md#load-your-reviewed-sections) | Run the two CLI checks above, then load reviewed synthetic sections; unrelated/unapproved content must not support answers. |
| s05-l06 — tools | `tools.py:ToolsService`, `storage.py` | Inspect typed lead/question contracts; absent consent must reject without a partial contact record. |
| s05-l07 — ordered calls | `twin.py:DigitalTwin.run_tools`, worked example below | Submit retrieval, unknown operation and consented contact in order; expect `ok`, `rejected`, `ok` and one local contact. |
| s05-l08 — notifications | `notifications.py`, `tools.py:dispatch_once` | Record a local dry run; a real destination adapter and genuine provider receipt are a separate opt-in exercise. |
| s05-l09 — checklist | `status.py`, `service.py:contact_events` | Compare no-consent and consented event streams; local completion must not claim external delivery. |
| s05-l10 — Gradio | `app.py`, `agents_adapter.py` | Launch locally and inspect Q&A and unticked consent controls in a browser. Observe configured-model answers separately from the default excerpt baseline. |
| s05-l11 — modules | [Architecture](docs/architecture.md) | Draw the import/authority map and run regressions after your refactor; importing must not launch UI or send requests. |
| s05-l12 — evaluation | `evaluate.py`, `data/evaluation/professional-questions.jsonl` | From the root run `python projects/01-digital-twin/evaluate.py`; inspect all 24 local cases and failures. Model quality remains `NOT_EVALUATED`. |
| s05-l13 — deploy | [Deployment runbook](docs/deploy.md) | Follow its declared project directory and verify a visitor flow. Source/configuration and a health response alone are not deployment success. |

### Worked solution: ordered local calls and durable replay

Run this Python example from the repository root. It uses synthetic data and in-memory SQLite only:

```python
import sys
sys.path.insert(0, 'projects/01-digital-twin')
from config import load_profile_sections
from twin import DigitalTwin
from tools import ToolsService

core = DigitalTwin(load_profile_sections())
try:
    results = core.run_tools([
        {'name': 'retrieve', 'arguments': {'question': 'Python experience'}},
        {'name': 'unknown_operation', 'arguments': {}},
        {'name': 'record_contact', 'arguments': {
            'name': 'Practice Visitor', 'email': 'visitor@example.invalid',
            'message': 'Synthetic project inquiry', 'consent': True}},
    ])
    print([result['status'] for result in results])
    print(core.db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0])
finally:
    core.db.close()

with ToolsService() as tools:
    first = tools.record_lead('practice-01', 'Practice Visitor',
                              'visitor@example.invalid', 'Synthetic inquiry', True)
    replay = tools.record_lead('practice-01', 'Practice Visitor',
                               'visitor@example.invalid', 'Synthetic inquiry', True)
    print(first == replay, first['status'], first['notification'])
```

Expected outputs are `['ok', 'rejected', 'ok']`, `1`, and `True stored_locally pending`. The first block is the introductory legacy API; it does not provide persistent replay deduplication. The second uses the typed idempotent service used by the UI; select a private database path to retain it between runs. `ToolsService.run` supports lead/question writes, not retrieval. Never rerun the legacy write expecting deduplication.

The answering SDK agent has **no registered write tools**. UI contact/question buttons explicitly call the consent-enforcing application service. This separates model wording from write authority; neither a manual button nor the deterministic example is a model-selected tool request. The stage 4 genuine-model tool-round-trip exercise remains separate.

## Deploy and retain data

Read [deployment](docs/deploy.md) before any external exposure. The Dockerfile runs nonroot, private state belongs on an owned `/data` volume and default public sharing is disabled. Public binding requires configured authentication; HTTPS and network-wide rate controls belong at the approved proxy. A readiness probe is not an authenticated visitor test. `maintenance.py purge` applies configured retention; `outbox` and `dry-run-one` are private operator actions. Never put credentials, real résumés, contact databases or private receipts in a public repository or screenshot.

### Validation scope

Earlier reference validation reported **48 semantic repair tests, with zero skips**, plus generation, extraction/source comparison and rendered-page inspection of both Unicode PDFs. This historical result does not certify your environment or later changes. Run the relevant local tests yourself, including `python -m unittest discover -s tests -p test_student_project_01.py -v`. Extracted sections still require explicit human factual approval. Local checks do not establish actual model behaviour, browser interaction or deployed visitor readiness.
