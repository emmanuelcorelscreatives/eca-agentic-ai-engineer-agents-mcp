# Stage 25 model-driven factory: authored, central QA pending

The original PDF requires a genuinely generative factory: requirements, architecture, scaffolding, tools, instructions, tests, review, Docker validation and bounded repairs. Maintained deterministic templates alone do not satisfy those lessons.

`model_schemas.py` defines closed Pydantic handoffs. `model_pipeline.py` implements actual optional AutoGen `AssistantAgent(output_content_type=...)` specialists with no execution tools. `AutoGenBackend` receives an explicitly configured model client; importing either module makes no call. Each proposal reserves a durable once key and call budget before submission; raw responses are fsynced before local validation. Failure, timeout or a missing receipt leaves UNKNOWN, never an automatic retry. Central QA must configure the real model transport with retries disabled and record its actual provider/model/version.

`Pipeline.analyze(spec)` → externally approved requirements → `design(...)` → externally approved architecture → `generate(...)` runs five distinct specialist proposals, preserving hashes and preventing overwrite between specialists. `inspect(...)` combines actual static diagnostics with typed review findings. `repair(...)` accepts actual failed Docker diagnostics and at most two patches to explicitly allowed non-test files. `run_factory(...)` composes these steps, fresh workspaces, independent immutable acceptance, externally authenticated central Docker receipts and final human release approval. Its callbacks are trusted orchestrator integration boundaries, never model-supplied tools. SHA identity alone is not receipt authentication. No generated code is imported or executed on the host.

The independent acceptance suite is supplied before generation under `acceptance/`; the model's generated tests are additional evidence only. Central QA must independently author/inspect that suite. A clean model review cannot release an application without actual Docker execution and independent acceptance. The existing Docker wrapper requires a separately approved digest-pinned image; image build, dependency locking and genuine launch still require actual central execution.

## Central QA commands (not executed by this author)

From `projects/07-agent-factory`, using the project-specific admitted helper:

```sh
python -m unittest discover -s tests -p test_s25_pipeline_semantics.py -v
python -m unittest -v test_advanced.py
```

Use the pinned repository virtual environment with Pydantic and AutoGen installed. The first command uses explicitly labeled offline fixture responses to test handoff and UNKNOWN/budget behavior; it does not claim real model quality. Add central independent cases for stale approvals, generated path traversal, altered policy/tool scope, immutable acceptance tampering, false Docker receipts, unchanged-code rerun and budget exhaustion before production use. Execute actual bounded AutoGen proposal and Docker workflows only under central owner admission. Retain actual raw messages and container receipts separately.

Primary API source inspected: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html (AssistantAgent structured output / `output_content_type`; 2026-11-12). SDK/compiler/provider/Docker execution is not certified by this documentation reference.

PDF essentials remain required. Agno/Mastra selection is a Stage 24/expanded workbook detail rather than a requirement for those named frameworks in the original Stage 25 PDF. Native framework adapters still require real dependency locks and genuine observed behavior before presenting them as completed integrations. No lesson is approved by this author-only handoff.
