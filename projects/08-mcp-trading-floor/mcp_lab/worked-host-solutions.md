# Worked host-policy solutions

These are concrete solutions for the new `agent_harness.py` implementation.
The new tests have been authored, **not executed by the author**. The existing
four-test protocol proof remains historical evidence for its exact earlier
revision. Neither this document nor a deterministic provider proves a genuine
model decision, current capture approval or whole-course readiness.

## Namespaces, discovery and permissions — Stage 27 lessons 4, 10 and 11

Give already-connected, owned MCP sessions distinct aliases. Never combine
native tool names in an unqualified dictionary:

```python
from pathlib import Path
from agent_harness import MCPRegistry, ToolPolicy, ReadPathPolicy

reviewer = MCPRegistry(
    {"files": filesystem_session, "fetch": fetch_session},
    {"files::read_text_file"},
    tool_policies={
        "files::read_text_file": ToolPolicy(
            argument_check=ReadPathPolicy(
                Path(course_fixture_root),
                permitted_files=frozenset({"final/report.txt"}),
            )
        )
    },
)
await reviewer.discover()
observed = await reviewer.dispatch(
    "files::read_text_file", {"path": str(Path(course_fixture_root) / "final/report.txt")}
)
```

The reviewer sees only the server-qualified read tool. `drafts/report.txt`, a
symlink outside the fixture root, `files::write_file`, and guessed newly added
tools are denied before dispatch. A researcher gets a **different registry**
whose `ReadPathPolicy` permits the two explicit `sources` and `drafts`
directories. The underlying filesystem server must still enforce its own
course-only root; the host policy does not replace the server boundary.

If two servers both advertise `lookup`, keep `files::lookup` and
`fetch::lookup`. The test `test_cross_server_collision_and_exact_routing`
demonstrates the intended dispatch using labeled doubles; it is not evidence
that either named real server implements a tool called `lookup`.

Malformed discovered argument schemas fail validation before the real call.
`test_real_json_schema_validation_before_dispatch` uses the actual JSON Schema
validator when installed. External schema references are refused rather than
fetched. Tool descriptions are omitted from the provider catalogue because
server text is not host policy.

## Resource note and prompt inspection — Stage 27 lessons 5 and 6

```python
registry = MCPRegistry(
    {"lab": laboratory_session}, {"lab::quote"},
    allowed_resources={("lab", "academy://handbook")},
    allowed_prompts={("lab", "research_brief")},
)
await registry.discover()
guide = await registry.read_resource("lab", "academy://handbook")
note = {"citation": "academy://handbook", "excerpt": guide}
messages = await registry.get_prompt("lab", "research_brief", {"symbol": "ACME"})
```

The note cites the actual read identifier and returned text. No mutation tool
is called to read it. `messages` is the retrieved template, not an executed
model answer. Unknown identifiers, unsupported server capabilities and binary
resources produce distinct host errors; missing prompt arguments fail before
`get_prompt`. Retrieving a template never changes `descriptors()` or permits a
write. Do not promote a template into a privileged system message.

## Bounded agent integration — Stage 27 lessons 4, 7 and 9; Stage 28 lesson 9

Connect the concrete JSON action adapter to the separately configured model:

```python
from agent_harness import JSONAgentProvider

async def complete_research_action(payload):
    # configured_model is the application's explicit provider adapter with
    # finite output-token/request-cost settings; it is not an environment read.
    return await configured_model.complete(role="mcp_researcher", payload=payload)

provider = JSONAgentProvider(complete_research_action, max_response_bytes=16384)
```

The adapter accepts only an exact JSON tool action or final-answer envelope;
extra fields such as a model-invented `approval_token` are rejected. This is an
integration boundary, not a pretend model. The module does not read credentials
or make provider calls on import. A real authorized run and its observed trace
are still required for model-driven lesson demonstrations.

Pass the configured provider to `AgentHarness(registry, provider,
RunBudget(iterations=6, tool_calls=4, total_seconds=30, per_call_seconds=5))`.
The provider sees only allowed descriptors and explicitly untrusted tool
observations. Time, iteration and call budgets stop loops. The harness never
retries a timeout automatically. A possible mutation timeout is recorded as
`unknown`, consumes its one-use approval and requires reconciliation.
That exact mutation is also blocked for the lifetime of the registry, even
with a fresh token. The application must persist the returned unknown outcome
and trace before closing the run; this in-memory teaching registry is not a
durable job controller. Do not restart it to clear an unresolved mutation.

`SequenceProvider` in the test file is clearly a deterministic control-flow
fixture. It proves that an observation returns to the next provider step;
it does not prove a genuine agent selected a server or grounded its final
answer. The separate research workflow validates citations against observed
evidence and enforces its own allowed destinations.

## Secret-safe diagnostics — Stage 27 lessons 8 and 12

The unsafe pattern is logging raw arguments/results or exception messages.
The fixed registry records only correlation ID, known server-qualified tool,
terminal classification and measured latency. Concurrent calls have separate
IDs. The tests deliberately raise an exception containing a synthetic canary;
the trace must not contain it.

For a host that holds runtime credentials, construct
`SecretBoundary((runtime_secret_value,))` and pass it as `secret_boundary`.
Known credential values are rejected in input arguments, prompt arguments and
user questions; nested result strings are redacted before the provider sees
them. Sensitive dictionary keys are masked too. This does not discover unknown
personal data: least-privilege files, owned fixtures and isolated browser
profiles remain required. Never paste a live credential into an exercise.

## Exact report-write human approval — Stage 27 lesson 13

Use a separate registry for the sandbox writer and a trusted human-facing
integration. The research registry must not expose the writer:

```python
from agent_harness import HumanApprovalGate

gate = HumanApprovalGate({"authenticated-course-reviewer"})
writer = MCPRegistry(
    {"sandbox": sandbox_filesystem_session}, {"sandbox::write_file"},
    approval_gate=gate,
    tool_policies={"sandbox::write_file": ToolPolicy(mutation=True,
        argument_check=ReadPathPolicy(Path(course_fixture_root),
            permitted_files=frozenset({"approved-report.txt"})))},
)
```

Without approval, `dispatch` raises `ApprovalRequired` containing a proposal.
Its digest binds the **server-qualified tool and complete canonical arguments**,
including exact path and content. A trusted UI must authenticate its reviewer
outside the harness, show the full proposal and call `deny` or `approve`.
The resulting opaque token is supplied by the host as the keyword-only
`approval_token`; a model `ToolCall` has no such field. Merely returning the
text “approved” grants nothing.

Approvals expire within fifteen minutes and are single-use. Changing path or
content invalidates the token. A second approval of the same proposal is
rejected. The optional genuine Node test writes an original report only after
approval, compares the exact filesystem bytes, then verifies a consumed token
cannot overwrite a later independent edit. This is a test source awaiting
central QA execution, not a claim that the new write already ran.

This generic sandbox gate is **not** the paper-trading approval mechanism.
The trusted portfolio service has a distinct server alias, exact proposal and
account revision checks, and its own human approval. Never reuse a report-write
token to authorize a trade.

## Central QA commands

The designated QA owner executes the following through the current finite
resource wrapper and captures the actual log. The author has not run them:

```sh
python -m unittest discover -s tests -p test_project8_agent_harness.py -v
python -m unittest discover -s tests -p test_project8_mcp_protocol.py -v
```

Use the already prepared SDK runtime and official filesystem lockfile for the
optional genuine sessions. Missing dependencies must remain explicit skips;
the full SDK acceptance run must report those actual sessions executed rather
than treating a skipped integration as a pass.
