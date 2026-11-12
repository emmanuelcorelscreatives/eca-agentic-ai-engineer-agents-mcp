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
