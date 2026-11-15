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

## Verify the native behavior

Run the native Stage 23 tests in the framework-specific environment and retain actual output. They exercise typed validation/response identity, tool validation, approval/checkpoint boundaries and middleware with scripted responses. These are local framework mechanics, not evidence of provider intelligence, model-generated decisions or cloud deployment. A skipped SDK case is not a verified integration.

For a real-model comparison, explicitly choose the configured provider account and budget, then retain the actual terminal response and specialist outputs. Keep genuine multi-turn reasoning and model-selected tool behavior distinct from scripted test results. Store credentials privately and configure hosted observability or deployment only when the corresponding exercise requires it.
