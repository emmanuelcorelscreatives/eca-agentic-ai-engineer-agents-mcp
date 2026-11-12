# Project 1: Professional Digital Twin

Curriculum: Stage 5, lessons 1–13. This runnable **deterministic reference core** establishes grounding, typed tool boundaries and contact consent before adding a model/UI. Amara and Cedar Library are fictional; do not upload a real résumé to the public repository.

From repository root, with Python 3.10 or newer:

```sh
python3 projects/01-digital-twin/twin.py "What Python experience does Amara have?"
python3 projects/01-digital-twin/twin.py "Salary and private contact details"
python3 -m unittest discover -s tests -p 'test_projects_1_3.py' -v
```

Expected first result cites `profile-01`; the second refuses to establish private information. Retrieval returns **verbatim approved excerpts**, not generated paraphrases. It is lexical retrieval, not semantic search or a complete LLM agent. Citation identifiers remain stable. `run_tools` exposes only named retrieval/contact operations. Unknown tools and consent failures yield explicit rejected results. Contacts are stored locally; no notification is sent. Use a file SQLite database only when persistence is intentional; protect it from public serving. `delete_contact` supports practice retention/deletion.

## Build sequence and practical work

1. Describe the audience, source approval policy and success criteria in a project brief.
2. Use a **synthetic** résumé PDF to practise local text extraction. Optional `pypdf` may extract text, but review extraction order and approve the resulting sections before indexing; this core deliberately consumes reviewed JSON.
3. Draft system instructions: answer only from approved sections; express uncertainty; never infer availability, credentials or salary. Instructions complement tool restrictions, rather than replacing them.
4. Extend `retrieve` with paragraph indexing while preserving document IDs. Compare test outcomes before and after changes.
5. Call `run_tools` with one retrieval and one contact request. Observe that contact storage requires `consent=True`.
6. Add a configurable notification adapter with a dry-run default. Keep notification failure separate from saved-contact success.
7. Add visible status events such as `retrieving`, `ready`, `contact_saved`; do not display hidden reasoning.
8. Optional live/UI layer: install `gradio` and an approved model SDK in a separate environment; inject a model adapter, display cited sources and require an explicit contact-consent control. No live SDK/model, PDF parser, Gradio UI or hosted deployment is claimed by this core.
9. Deploy only after authentication/rate limits, privacy notice, secret management and contact retention have been designed for the chosen host.

## Exercises and solution notes

- **Unsupported award:** ask whether Amara won a national prize. Solution: `insufficient_evidence`, no invented award or citation.
- **Unapproved source:** add a matching section with `approved=false`. Solution: it never appears in retrieval or answers.
- **Contact consent:** try storage before and after opt-in. Solution: first call raises `PermissionError`; second returns `stored_locally` with `notification=not_sent`.
- **Multiple tools:** submit an unknown tool between valid calls. Solution: reject only the unknown operation, retaining explicit ordered per-call outcomes.
- **Deletion:** store then delete a fictional contact. Solution: first delete returns true, repeat returns false.

See `tests/test_projects_1_3.py` for executable acceptance examples. Authentication of the person granting consent and rate limiting belong to the eventual UI/service, not this local CLI.

## Implemented optional local interface

`app.py` builds an actual Gradio Blocks/ChatInterface around the approved-profile core. In a separate virtual environment install `requirements-optional.txt`, then run `python3 projects/01-digital-twin/app.py` from repository root. It binds loopback, disables public sharing and performs no model calls. The interface intentionally omits contact collection until service authentication/retention is configured. It was syntax-checked and build-tested with a component fake; an installed Gradio browser run remains required in the target environment. [Official ChatInterface documentation](https://gradio.app/docs/gradio/chatinterface).

## Additional implemented workflow components

`workflow.py` implements the explicit system-instruction contract, whole-section character budgeting, visible phase events and consented contact/notification composition. Notification adapters receive a record identifier; no external adapter is enabled by default, and failed notification does not erase successful local contact storage.

`make_pdf_fixture.py` creates a real synthetic PDF. After installing optional `pypdf`, run `python3 pdf_ingest.py fixtures/synthetic-resume.pdf` from this directory. Extracted text is **unapproved** until reviewed. Encrypted or image-only PDFs fail explicitly rather than inventing text. `evaluate.py` runs the transparent offline grounding scenarios.

`agents_adapter.py` is an implemented optional real SDK grounded-answer adapter. It passes only approved retrieved sections to a typed answer agent, rejects invented source identifiers and requires attribution for supported answers. Use `python3 agents_adapter.py 'Python experience' --live` with the same explicit environment configuration described in the other project adapters. It makes paid model requests; it has not been run against a provider. Citation validation is not an automatic claim-level truth guarantee.

The Dockerfile runs as a nonroot user. For a local-only deployment exercise: `docker build -t academy-twin .` followed by `docker run --rm -p 127.0.0.1:7860:7860 academy-twin`. Actual image build/run and authenticated hosted deployment remain to be validated on the chosen target. Never embed credentials, local contact databases or personal profile documents in the image.

## Actual local runtime validation (2026-11-12)

A finite resource-governed validation environment installed OpenAI Agents SDK 0.24.0, Pydantic 2.14.3, Gradio 6.31.0 and pypdf 6.21.4. Actual SDK agent configurations and both twin/sales Gradio interfaces built successfully; pypdf extracted the synthetic resume. This proves imports/configuration and text extraction, not live model behavior or browser interaction. No model requests or UI servers were started. Reproduce in an isolated environment; retain version resolution and rerun the tests before deployment.
