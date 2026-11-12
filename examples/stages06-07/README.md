# Stages 6–7: OpenAI Agents SDK and orchestration

Two layers are deliberately separate: `workflows.py` is a deterministic, standard-library application exercise; `sdk_adapter.py` constructs actual `openai-agents==0.24.0` agents, function tools, typed outputs, agent tools, handoffs, SQLite sessions, streaming and concurrent SDK runs. The local helpers never claim to implement the SDK itself.

## Offline

```sh
python3 -m unittest discover -s tests -p test_stages_06_07.py -v
python3 examples/stages06-07/workflows.py --stage 6
python3 examples/stages06-07/workflows.py --stage 7
python3 -m venv .venv-sdk
.venv-sdk/bin/pip install -r examples/stages06-07/requirements.txt
.venv-sdk/bin/python -m unittest discover -s tests -p test_stages_06_07.py -v
```

The optional tests invoke real function-tool objects locally and real SDK SQLiteSession persistence. The runner-entrypoint test uses a clearly labelled fake Runner. No offline test sends requests or uploads tracing data. Synthetic streaming events and LocalTrace are instructional fixtures rather than a provider execution record. Application session storage and actual SDK session storage use different internal schemas; do not point both at an existing learner database.

## Optional live execution — pending observed validation

Use only synthetic data and an explicit model available to your account. Supply your own credential through OPENAI_API_KEY without putting it in any capture or file. The following can incur provider charges:

```sh
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode catalogue --db academy-stage06.sqlite
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode catalogue --stream --db academy-stage06.sqlite 2>stream-events.jsonl
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode manager --db academy-stage07.sqlite
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode triage --db academy-stage07-shipping.sqlite
```

Tracing is disabled by default. Only add `--hosted-tracing` after deliberately authorizing hosted telemetry for the synthetic run; `trace_include_sensitive_data=False` remains set. Retain actual result, model identity, last_agent, emitted event types and actual trace identifier before making model or hosted-trace claims. The SDK run is bounded to eight turns, but that is not a dollar budget. `run_parallel_live` is an importable example of concurrent independent specialist calls, each capped at four turns.

## Interfaces checked against pinned package

The adapter uses `Agent`, `Runner.run`, `Runner.run_streamed`, `RunConfig`, `RunContextWrapper`, `SQLiteSession(session_id, db_path=...)`, `function_tool`, `handoff`, `Agent.as_tool(parameters=..., include_input_schema=True)`, `RunResult.final_output`, `last_agent` and `stream_events()`. Actual local tool invocation requires `agents.tool_context.ToolContext` in this release; a plain RunContextWrapper is insufficient for the tool invocation hook. Pydantic models set `extra='forbid'`; input IDs, result ownership and application tool permissions are validated separately.

## Official references

Verified on 2026-11-12 against official OpenAI documentation:

- https://developers.openai.com/api/docs/guides/agents/sdk
- https://developers.openai.com/api/docs/guides/agents/quickstart
- https://developers.openai.com/api/docs/guides/agents/running-agents
- https://developers.openai.com/api/docs/guides/agents/orchestration

The installed package is pinned rather than silently tracking latest. Live SDK/model execution, hosted tracing, quality and latency remain unverified here. Use genuine terminal/editor/SQLite captures; never build a mock provider trace UI.

## Semantic repair additions — authored, awaiting central QA

The authoritative Stage 6 decorator/validation exercise is the **course catalogue**
in `data/s06-catalogue.json`. The separate arithmetic framework companion is an
optional comparison, not the same dataset or acceptance contract. A catalogue
function tool now validates its **returned** value with `CatalogueToolResult` and
`CatalogueRecord`, then checks that the fact belongs to the requested current
fixture. `found=False, course=None` is the unknown variant. A valid-looking but
invented course title, mismatched ID, unexpected field, string Boolean or malformed
prerequisite list fails before being serialized to the model. This boundary is
different from the agent's final `CourseAnswer` schema.

### Streaming lifecycle

`stream_receipt.consume_sdk_stream` consumes the actual SDK stream iterator,
recognizes output-text deltas, counts unknown/empty events, and preserves partial
display text separately from a completed answer. A user cancellation calls
`result.cancel(mode='immediate')` and drains the **same** iterator for cleanup.
An error after partial output returns an explicit failed receipt; the CLI refuses
to print it as a completed final answer. Caller task cancellation propagates after
owned cleanup. No stream exception automatically starts a second provider call.

The application-consumer tests feed clearly labelled synthetic events to test
empty, unknown, partial-error and cancellation boundaries. These tests do not
prove model streaming was observed. An optional authorized real streaming run can
add `--cancel-after-deltas 1` to the existing `--stream` invocation; preserve its
actual receipt and any cleanup uncertainty.

### Conversation continuity and real process restart

The live dialogue entrypoint makes **one** actual SDK Runner call per invocation.
The SDK's `SQLiteSession` carries history; the application never manually replays
the first answer or inserts conversation items. With an explicitly authorized
model budget, use a new course-owned database and invoke these separately:

```sh
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode dialogue --dialogue-step seed --db academy-dialogue-new.sqlite
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode dialogue --dialogue-step followup --db academy-dialogue-new.sqlite
.venv-sdk/bin/python examples/stages06-07/sdk_adapter.py --live --model YOUR_AVAILABLE_MODEL --mode dialogue --dialogue-step control --db academy-dialogue-new.sqlite
```

Seed chooses ECA-101. The follow-up in the second process asks what was selected
without repeating the ID. The control asks the same question in an unrelated
session. These are **three separately budgeted real calls**, not permission to
run them during authoring. Record the actual answer, `session_items_before` and
`session_items_after`, and whether the control admits missing information. No
answer is assumed in advance. Keep generated SQLite files out of publication.

`session_contract_probe.py` offers a provider-free **real SDK Runner** history
contract test using its explicitly synthetic `HistoryObservationModel`. Separate
processes prove that SDK-delivered input contains the persisted marker only in the
matching session. That verifies persistence/SDK wiring, not learned recall or
provider reasoning. The scripted output and zero-provider status remain labelled.

### Usage, latency and actual local SDK span export

`ObservationHooks` records actual SDK lifecycle callbacks, each model call's
monotonic elapsed time, available SDK usage counters, optional response ID,
tool-call IDs and handoffs. Missing usage is `null`, not an invented zero; the
SDK may itself normalize provider omissions, so these counters are not raw billing
proof. An unfinished call stays `started` with missing duration/usage. Inputs,
arbitrary tool output and user text are not copied into the diagnostics.

For an authorized run, `--trace-file NEW_PRIVATE_FILE.json` installs a local
`LocalSDKTraceProcessor` and enables genuine SDK spans while replacing the hosted
HTTP exporter. It exports actual span/trace IDs, parent IDs, start/end times,
span kinds and error-presence flags, omitting private input/output/error text.
Existing files are never overwritten. The local export explicitly says
`hosted_upload_proven=False`. Adding `--hosted-tracing` is a **separate telemetry
opt-in**; even then requesting an upload is not proof of hosted acceptance.

### Connected complete orchestration

`--mode complete` builds a real SDK manager with inventory/policy agents as tools,
then a handoff to a delivery synthesizer. That receiving agent reads the shipping
tool and owns the combined answer using the prior tool results and typed request
context. All phases remain inside one root SDK trace when local tracing is enabled.
The resulting `complete_lineage_observed` is computed from actual callbacks:
inventory and policy tool completion, then handoff, then shipping tool completion,
then the receiving agent's final output. If the model omits or reorders a required
phase, it is **False**; instructions are never reported as an observed trace.

`connected_application_run` supplies a separate deterministic connected lineage
for understanding parent IDs without a model call. It is labelled
`deterministic-application-lineage-not-sdk`; do not present it as model delegation.
`--mode parallel` exposes the actual two-call `asyncio.gather` route and retains
each healthy/failed-or-unknown result with role attribution. It does not retry an
uncertain provider request. CLI provider-client retries are explicitly disabled.

### Explicit fallback

`specialists_with_fallback` retains healthy facts, original failed role/reason and
`unresolved`, and separately produces `draft_manual_review`. Its source is
`application-failure-policy-v1`, not a cached or invented product policy.
`facts_recovered=False`, `sent=False` and `requires_human_review=True` describe the
alternative recovery action honestly. A timeout, exhausted classified transient
read or permanent schema error may reach this fallback; no fallback fabricates
stock, returns or delivery facts or sends an external message.

New semantic tests: `tests/test_stage06_07_semantic_repairs.py`. They are **authored
and not executed by this author**. Central QA must retain actual results, distinguish
SDK skips, and independently review the changed source before publication or use
as approved teaching material. The older logs retain their historical source scope.
