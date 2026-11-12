# Microsoft agent ecosystem boundaries

AutoGen AgentChat 0.7.5 uses `AssistantAgent` plus a separate model client; the
application saves and loads agent state explicitly. It is not the older 0.2 API.
Semantic Kernel is a separate SDK for integrating models, plugins and agent
orchestration. No Semantic Kernel implementation is supplied by this stage;
its comparison is conceptual and must not be presented as an executed adapter.

## Implemented Microsoft Agent Framework path

`examples/s23_microsoft_native.py` implements the Microsoft Agent Framework
**1.16.1** practicals using the actual SDK interfaces:

- Strict `Ticket`, `Decision` and `Handoff` contracts, SDK `response_format`, and
  application checks binding each answer to the original ticket and category.
- Native decorated tools and the SDK function-invocation validation boundary.
- `AgentSession.to_dict` / `from_dict`, atomic application-owned persistence,
  cold-process restoration and explicit owner isolation.
- Native `Executor`, `handler`, `WorkflowContext` and `WorkflowBuilder` routing
  through category researchers and a shared review agent. Unknown requests yield
  a held clarification result without model calls. These agents share schemas,
  tools and policy components; this graph is not a renamed Python callback loop.
- Native agent, model and function middleware for correlated monotonic timings,
  error outcomes and allowlisted, redacted telemetry.
- Exact-payload human grants checked at the native function middleware boundary
  and consumed inside the sensitive tool. Declines, changed arguments and replay
  produce no local effect. The permitted effect is one synthetic local outbox
  append, explicitly **not** an email, external send or cloud deployment.

`examples/s23_framework_agents.py` retains the separate AutoGen constructor and
its state helpers, plus a basic Microsoft constructor. The earlier
`examples/s23_workflow.py` routing, approval and checkpoint examples remain
ordinary application Python. They are useful comparisons, not the implementation
of the native Microsoft workflow above.

## What has actually been verified

The central installed-SDK result
`stage21-25-central-current-runtime-result-v1.json` records **seven Stage 23
native SDK tests**, with **zero model-provider calls**. They exercise typed
validation and response identity; native tool validation and observed tool
results; exact approval/decline/change/replay; both workflow routes and held
ambiguity; native session continuation with a separate-process restart and owner
isolation; and middleware timings, correlation, failure reporting and dummy-secret
redaction. The underlying tests are in `tests/test_s23_native_semantics.py`.

Those tests use an explicitly scripted model client with genuine SDK function
invocation and middleware layers. The SDK agents, graph, tools, sessions and
middleware execute locally; the supplied model answers are fixtures. This proves
these scoped runtime mechanics, not model intelligence, real generated answers,
cloud availability or production readiness. Historical negative audits describe
the earlier source state and remain retained evidence; they do not override the
new scoped local runtime results.

Before claiming a genuine model demonstration, retain a separately authorized,
bounded run using an actual configured provider client, its raw terminal response
and observed specialist outputs. In particular, real generated decisions,
multi-turn reasoning and specialist contributions remain distinct evidence from
scripted tests. Matching current visuals and independent semantic/material review
are still required before lesson release. Credentials and cloud-specific
observability/deployment are optional extensions, not substitutes for the native
local practicals or permission to make unbudgeted calls.

## Migration boundaries

Instructions map to `instructions` / `system_message`; tools need their actual
registration schemas; model-client ownership and cleanup differ. Persisted
AutoGen state is not valid Microsoft `AgentSession` state. Recreate and verify
sessions against the target framework instead of relabelling serialized data.
Reuse typed domain contracts and policies, while testing each framework's
runtime, tool execution, approval and persistence behavior separately.

Official sources:

- [AutoGen AgentChat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html)
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)
- [Semantic Kernel overview](https://learn.microsoft.com/en-us/semantic-kernel/overview/)

Use the pinned installed 1.16.1 SDK source when current online examples differ.
