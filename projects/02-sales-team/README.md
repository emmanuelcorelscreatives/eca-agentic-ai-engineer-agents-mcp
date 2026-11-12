# Project 2: AI Sales Development Team

Curriculum: Stage 8, lessons 1–14. The local reference implements draft → review → human approval → **simulated** delivery. Cedar Library and Jordan Lee are invented; the fixture uses a reserved `.invalid` email domain. No email provider is called.

```sh
python3 projects/02-sales-team/sales.py
python3 projects/02-sales-team/sales.py --approve
```

The default prints a draft only. `--approve` records a named practice reviewer and writes a simulated outbox message. Every actual external send remains disabled, including an approved message when `live=True`. The approved hash binds subject and body. Editing resets approval, direct database payload tampering fails delivery, and each draft has one unique outbox entry. Rejection or revision can be represented by leaving a draft unapproved or editing it; there is no autonomous sender.

## Curriculum implementation path

- Prospect data is a typed dataclass. The fixture `source_id` attributes the stated need.
- `create_draft` is an intentionally deterministic baseline for research → strategy → writing. It must not be presented as an actual model-generated email or completed company investigation.
- `review` provides limited deterministic checks for selected unsupported superlatives; it is **not** a general factual correctness gate. The human reviewer checks every claim against sources.
- Practise code coordination by separating prospect research, strategy selection, drafting and review into named functions; add trace events containing inputs/output IDs rather than secrets.
- In a separate optional SDK adapter, implement OpenAI Agents SDK specialist agents, manager selection and handoffs. Return validated prospect/research/strategy/draft records (optional Pydantic) into this same local state machine. Install and pin actual framework versions only when that adapter is introduced. This reference has no hidden provider dependency and claims no live agent execution.
- A future delivery adapter needs explicit authenticated human approval, recipient binding, durable idempotency keys, provider receipts and error reconciliation. Do not replace `live=True` refusal with an unconditional API send.

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

`app.py` builds a real optional Gradio interface with create/edit/approve/reject/simulate controls. It uses an isolated local temporary SQLite database and fresh connections for callbacks. Edits must be saved before the exact displayed payload can be approved. Run `python3 app.py` with optional dependencies installed. The app binds loopback and disables public sharing. Its temporary database is practice state, not a permanent authenticated multi-user approval system. No external mail provider is implemented.

## Actual local runtime validation (2026-11-12)

A finite resource-governed validation environment installed OpenAI Agents SDK 0.24.0, Pydantic 2.14.3, Gradio 6.31.0 and pypdf 6.21.4. Actual SDK agent configurations and both twin/sales Gradio interfaces built successfully; pypdf extracted the synthetic resume. This proves imports/configuration and text extraction, not live model behavior or browser interaction. No model requests or UI servers were started. Reproduce in an isolated environment; retain version resolution and rerun the tests before deployment.
