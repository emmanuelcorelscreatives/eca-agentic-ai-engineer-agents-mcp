# Project 2: AI Sales Development Team

Curriculum: Stage 8, lessons 1–14. The reference implements generation → preview → review → exact human approval, with separate explicit simulation and actual owned-loopback SMTP submission. Cedar Library and Jordan Lee are invented; the fixture uses a reserved `.invalid` email domain. External email delivery is not enabled. New V2 source requires central runtime validation before release.

```sh
python3 projects/02-sales-team/sales.py
python3 projects/02-sales-team/sales.py --approve
```

The default prints a draft only. `--approve` records a named practice reviewer and writes a simulated outbox message. `live=True` remains rejected; actual owned-sink SMTP is a separate explicit operation described below. The approved hash binds recipient, subject, body and revision. Editing resets approval; rejection is explicit. No model can authorize sending.

## Curriculum implementation path

- Prospect data is a typed dataclass. The fixture `source_id` attributes the stated need.
- `create_draft` is an intentionally deterministic baseline for research → strategy → writing. It must not be presented as an actual model-generated email or completed company investigation.
- `review` provides limited deterministic checks for selected unsupported superlatives; it is **not** a general factual correctness gate. The human reviewer checks every claim against sources.
- Practise code coordination by separating prospect research, strategy selection, drafting and review into named functions; add trace events containing inputs/output IDs rather than secrets.
- The optional SDK adapter implements specialist agents, manager selection and context-preserving handoffs. It returns structured outputs into this same local state machine. This reference claims no live model execution merely from adapter construction.
- The new delivery adapter requires explicit owned-sink acknowledgement and exact approval, with durable claims and unknown-outcome holds. Production approver authentication is outside this private-local teaching app. `live=True` is never replaced with an unconditional send.

## Exercises and worked solutions

1. Attempt delivery immediately after draft creation. Expected: `PermissionError`, zero outbox messages.
2. Approve then edit the subject. Expected: status resets to `draft`, approval hash clears; another human approval is required.
3. Add “guaranteed” to a draft. Expected: the baseline reviewer reports an issue and approval refuses. Add a less obvious invented claim; discuss why deterministic word checks alone cannot establish truth.
4. Approve and simulate once, then attempt again. Expected: one outbox row, no duplicate simulated delivery.
5. Build a second fictional prospect with no source ID. Expected: reject rather than invent research evidence.
6. Design a typed manager handoff record carrying prospect ID, source IDs and revision reason. Keep human approval outside model authority.

All core SQLite mutations use transactions. Practice human identity is a CLI label, not authentication; a production service must authenticate its approvers separately.

## Implemented optional SDK adapter

`agents_adapter.py` implements actual `Agent`, `Runner.run`, typed Pydantic outputs and bounded turns. Install `requirements-optional.txt` in a separate virtual environment, then run `python3 agents_adapter.py --live` from this project directory after setting `OPENAI_API_KEY` and `ACADEMY_MODEL`. This makes paid requests. It was syntax-checked and exercised with a fake runner for orchestration, **not executed against a live provider**. The underlying SDK may retry transient requests according to its own settings; do not infer request-count guarantees from max_turns. No secrets are printed by this script, and tracing is disabled.

Official API references checked 2026-11-12: [SDK overview](https://developers.openai.com/api/docs/guides/agents/sdk), [quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart?lang=python), [agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents). Version ranges are compatibility constraints, not a verified frozen deployment lock; resolve/pin in your environment and rerun tests before live use.

## Implemented manager, handoffs, evaluation and interface

`orchestration.py` contains typed prospect/campaign/source handoff records, a deterministic manager decision policy, real SDK manager `as_tool` configuration, real SDK specialist handoffs and a transparent five-check evaluation rubric. No manager or specialist can authorize delivery.

`app.py` builds the optional integrated Gradio interface described in V2 below. It uses an isolated local temporary SQLite database and fresh connections for callbacks. Edits must be saved before the exact displayed payload can be approved or submitted. The app binds loopback and disables public sharing. Its temporary database is practice state, not a permanent authenticated multi-user approval system. Owned-sink SMTP is explicit; external mail providers remain disabled.

## Historical baseline runtime validation (2026-11-12; not V2 evidence)

A finite resource-governed validation environment installed OpenAI Agents SDK 0.24.0, Pydantic 2.14.3, Gradio 6.31.0 and pypdf 6.21.4. Actual SDK agent configurations and both twin/sales Gradio interfaces built successfully; pypdf extracted the synthetic resume. This proves imports/configuration and text extraction, not live model behavior or browser interaction. No model requests or UI servers were started. Reproduce in an isolated environment; retain version resolution and rerun the tests before deployment.

## Stage 8 semantic repair V2 — source authored, central runtime validation pending

The earlier implementation only simulated delivery and constructed agents/UI objects. That baseline does not establish actual SMTP, context-preserving SDK handoffs or integrated browser interaction. The new code below closes implementation gaps; no new runtime result is claimed in this authoring change.

### Typed identities and evidence

`Prospect` validates fields and a single email address, with explicit prospect/company/campaign IDs. `fixtures/company.json` shares `company-cedar-001`; the brief/evaluation records use `synthetic-brief-cedar-001`. `models.validate_identity_graph` checks research, strategy and draft foreign IDs and evidence subsets. Unknown revenue, budget and purchase intent remain unknown. SDK specialist output schemas additionally require exact prospect/company/campaign/evidence/revision identity. Structural validation never proves model factual accuracy.

### Draft, preview, approval, actual owned-sink send

`SalesTeam.create_draft`, `preview`, `edit`, `reject`, `approve`, and `submit_approved` are separate application operations. The preview hash binds **recipient, subject, body and revision**. Text is normalized to LF with a final newline before preview/approval so decoded SMTP text has an exact canonical comparison. Changing recipient or text increments revision and clears approval. Approving a stale preview or sending an edited/unapproved/rejected draft fails.

`submit_approved` accepts only an explicit `OwnedSinkSMTP` instance configured for literal loopback and an acknowledged unprivileged sink port. Reserved `.invalid` recipient addresses cannot escape to real recipients. The transport performs actual SMTP and records acceptance by the sink; it does not claim mailbox delivery or external mail. A durable unique send claim is committed **before** network I/O. Success is `accepted_by_owned_sink`. Any transport exception becomes `unknown_outcome` and remains held; a crash after claiming leaves `sending`, also held. Neither status is auto-retried or made editable. Reconcile the captured sink Message-ID/payload hash manually; never erase uncertain history and replay.

Legacy `deliver()` remains labelled simulation; `deliver(live=True)` is intentionally rejected. It is not the new SMTP path.

### Context-preserving handoffs

`orchestration.build_context_handoff` constructs actual SDK `handoff(..., input_type=HandoffIdentity, on_handoff=...)` objects. `context_wire.SalesContext` retains prospect, company, campaign, evidence IDs and source revision. The actual handoff callback rejects any identity mismatch or mutated application context before recording a validated transfer. `agents_adapter.run_context_handoff` executes the handoff with `Runner.run(..., context=context)`. Its model execution remains unobserved until an authorized run. Local callback checks are not model-delegation evidence.

### Integrated UI and operational reports

`SalesApplication` and `app.build_app` support explicit `deterministic`, `sdk-sequential`, `sdk-manager` and `sdk-handoff` modes. SDK execution requires server-side `allow_sdk=True` plus an explicit model; CLI opt-in also requires `OPENAI_API_KEY`. The sequential SDK path retains each actual typed stage output, validates context/source identity and creates an unapproved draft in the same persistent approval database. Model review is never human send approval. Manager/handoff free text is displayed as an observation and is not silently promoted into an email.

The UI provides recipient/subject/body editing, revision/hash preview, approval, rejection, owned-sink submission and a downloadable operational/evaluation report. The report contains actual local events, retained structured outputs, approval events and transport history. It is **not** a hosted model trace or hidden chain-of-thought export. Hosted tracing stays disabled. Local UI reviewer labels are practice identities, not production authentication.

### Quality evaluations

`fixtures/evaluation-cases.json` contains six synthetic author-labeled cases with source excerpts and per-dimension rationales: grounded, invented revenue, irrelevant offer, coercive guarantee, approval bypass and a grounded paraphrase. `evaluations.py` exposes factual-accuracy, relevance, tone, personalization and approval-boundary rubrics. Mechanical checks are reported separately from reference annotations. The invented-revenue case demonstrates a mechanical false positive; the paraphrase demonstrates a false negative. No model scoring or observed quality result is fabricated.

### Commands for the central guarded validator (not executed by the author)

```sh
python3 -m unittest discover -s tests -p test_stage08_semantic_repairs.py -v
python3 -m unittest discover -s tests -p test_projects_1_3.py -v
python3 -m unittest discover -s tests -p test_stages_05_08.py -v
```

With the already authorized optional SDK/Gradio runtime installed, the new suite constructs real SDK handoffs and the actual Gradio app without model calls, and starts a temporary **owned loopback SMTP sink** for an actual received-message comparison. It shuts the sink down before returning. Separate genuine browser interactions are still required for UI proof. Do not infer browser success from Blocks construction.

For an actual local UI after central approval, start a newly owned sink first, then:

```sh
python3 projects/02-sales-team/app.py --owned-sink-port YOUR_OWNED_LOOPBACK_PORT --acknowledge-owned-sink
```

SDK modes require the additional deliberate `--allow-sdk` switch and environment configuration. These modes can incur provider charges and must not be exercised by offline QA. No external SMTP host, real recipient account, publication action or course setting is touched by these changes.

### Subsequent central QA evidence

The initial central semantic suite executed 11 cases: ten passed and the owned-loopback SMTP case exposed surrounding RFC header-folding whitespace in the test's digest comparison. The updated digest validator strips only surrounding whitespace and retains exact hex validation, internal-whitespace and duplicate-header negatives. The single corrected SMTP case subsequently passed in central guarded QA. Coverage is the composition of the ten retained historical passes and this one targeted pass, not a claim that the whole updated suite was rerun. No external mailbox delivery or actual model behaviour was observed.
