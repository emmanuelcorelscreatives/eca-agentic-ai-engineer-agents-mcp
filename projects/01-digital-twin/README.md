# Project 1: Professional Digital Twin Agent

Stage 5 implements a professional representative of **fictional Amara Okoye**. The résumé, portfolio and Cedar Library work are synthetic Academy teaching material, never a claim about a real person's employment. The project includes approved-source answers, an implemented grounded SDK adapter, typed contact/question tools, durable action receipts, a local notification outbox, conversation/tool context allocation, a real Gradio interface and deploy/privacy configuration.

## Current validation status

The earlier baseline had actual dependency-construction/PDF extraction checks. This semantic-repair revision adds required features beyond that baseline. Its new source and tests are **authored and awaiting central guarded execution**. Do not reuse old passing totals to certify new code. No live model response, new generated portfolio PDF, browser interaction or deployment success is claimed here until its actual run is recorded.

## Run the actual application

Use a separate environment and install the project plus `requirements-optional.txt`. The executable entry points are `eca-twin` for approved-excerpt answers and `eca-twin-ui` for Gradio. From a checkout, the equivalent commands are:

```sh
python3 projects/01-digital-twin/twin.py 'Python experience'
python3 projects/01-digital-twin/app.py
```

The UI shows its exact mode. The default deterministic baseline returns approved excerpts, discloses the AI representation, cites sources and demonstrates contact flows with no model charge. For actual generated answers, deliberately configure `TWIN_LIVE_MODEL_ENABLED=true`, `ACADEMY_MODEL` and a private `OPENAI_API_KEY`; the same UI then invokes the real SDK adapter with bounded turns and explicit context allocation. This authorizes paid model use. The application never enables it merely because a key happens to exist. Model grounding, identity, tone and injection behaviour must be evaluated from genuine retained responses, not SDK object construction.

## Sources and ingestion

`make_pdf_fixture.py` can generate a matching résumé **and portfolio** from `fixtures/resume-source.txt` and `fixtures/portfolio-source.txt`, preserving Unicode and line structure with a real embedded TTF. It writes actual document/source/font/generator SHA values when executed. See [ingestion](docs/ingestion.md). New document generation and independent visual inspection are pending central QA. The older one-page synthetic resume fixture is retained as historical teaching evidence.

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

Tests are authored in repository `tests/test_stage05_semantic_repairs_application.py`, `tests/test_stage05_semantic_repairs_tools.py` and `tests/test_stage05_semantic_repairs_ingest.py`. The parent QA service owns execution under the shared resource governor. Live model cases and browser captures must be separately admitted; a static prompt assertion or fake runner is never reported as observed model behaviour.

## Deploy and retain data

Read [deployment](docs/deploy.md) before any external exposure. The Dockerfile runs nonroot, private state belongs on an owned `/data` volume and default public sharing is disabled. Public binding requires configured authentication; HTTPS and network-wide rate controls belong at the approved proxy. A readiness probe is not an authenticated visitor test. `maintenance.py purge` applies configured retention; `outbox` and `dry-run-one` are private operator actions. Never put credentials, real résumés, contact databases or private receipts in a public repository or screenshot.

### Subsequent central QA evidence

The central guarded QA owner subsequently executed all **48 semantic repair tests, with zero skips**, and actually generated both Unicode résumé/portfolio PDFs, extracted each document and compared raw Unicode lines with the authored sources. Both pages were rendered and inspected. These observations establish the scoped local behaviour and document production; source sections remain unapproved until explicit human factual approval. They do not establish actual model behaviour, browser interaction or deployed visitor readiness.
