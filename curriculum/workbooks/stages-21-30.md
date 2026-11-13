# Lesson practicals: stages 21–30

This workbook defines student tasks and acceptance evidence for the exact curriculum lesson IDs. These are assignments, not claims that live services, framework agents, browsers or deployments have already been verified. Save your new work and evidence under `student-work/<lesson-id>/` in your own checkout; do not commit credentials or private account captures. Existing repository paths below are starting points, not a guarantee that every lesson extension is already implemented.

Use the dependency manifests in `frameworks/requirements/` and each project’s optional requirements. Real model/provider, ADK dashboard, A2A, MCP inspector, Playwright browser, Qdrant, Docker and hosted deployment exercises require those actual runtimes and authorized access. Record a concrete blocker when unavailable. Deterministic fixtures and unit tests are useful foundations but do not substitute for a required real framework/MCP/model execution.

Project 7’s `projects/07-agent-factory/factory.py` remains the deterministic stdlib foundation. Its current `model_pipeline.py`, `model_schemas.py` and `MODEL-PIPELINE-AUTHORING.md` supply the additional typed generative pipeline: inspect these implementations before extending them. Labelled offline backend tests do not establish actual model-generated output, authenticated Docker acceptance or a launched generated agent. Project 8 now includes `agent_harness.py`, `capstone_agents.py`, `sdk_role_provider.py`, `mcp_lab/`, `retrieval_lab/`, `evaluation_lab/`, a revision/expiry-aware paper ledger, and separate operator/reviewer UI/API paths. Use the current implementations rather than recreating them as if absent. Actual local protocol, service and owned-UI observations remain scoped; real configured-model behavior, external search/semantic embedding, Inspector, Docker and hosted deployment evidence are separate requirements. No exercise authorizes real brokerage execution.


## Evidence boundary for the current source

Independent central observations on 2026-11-12 exercise native ADK persistence/MCP, A2A exchange, Pydantic role toolsets/MCP dispatch, Microsoft typed components with a scripted client, Agno MCP, Mastra workflows/MCP/LibSQL Memory and an owned Studio page. Project 8 observations exercise actual local MCP transports, service/Qdrant boundaries, application cases and owned React/Gradio interfaces. These are scoped observations, not blanket approval of these 134 lessons. A scripted model client or OfflineBackend is expressly not evidence of real provider reasoning. ADK dashboard startup still includes a first-run modal; Studio startup does not prove complete provider/run-history behavior.

Before narrating a result as observed, obtain the exact current-source evidence for that exercise. Required configured-model decisions and generative factory outputs, authenticated Docker execution, real search/semantic-embedding behavior, Inspector interactions, hosted deployment and final lesson-specific captures remain separate where not actually observed. Keep every original curriculum topic; recording an unresolved prerequisite does not remove it from the course.

## Stage 21: Google ADK and Agent-to-Agent Communication

**Current source starting points:** [`examples/s21_adk.py`](../../examples/s21_adk.py), [`examples/s21_inventory.py`](../../examples/s21_inventory.py), [`examples/s21_state.py`](../../examples/s21_state.py), [`examples/s21_mcp_inventory.py`](../../examples/s21_mcp_inventory.py), [`examples/s21_a2a_server.py`](../../examples/s21_a2a_server.py), [`examples/s21_a2a_client.py`](../../examples/s21_a2a_client.py), [`examples/s21_adk_dashboard/README.md`](../../examples/s21_adk_dashboard/README.md).

### s21-l01 — Introduction to Google Agent Development Kit

- **Task:** Map Agent, Runner, SessionService and tool responsibilities in examples/s21_adk.py and examples/s21_inventory.py; compare the introductory frameworks/google_adk_agent.py adapter.
- **Deliverable:** adk-component-map.md with the installed ADK version and a request sequence diagram.
- **Accept when:** Each diagram node maps to a real imported class; identify the model credential and runtime dependencies separately.

### s21-l02 — Build Your First Google ADK Agent

- **Task:** Run the supplied Google ADK adapter with a harmless course query and retain its actual response.
- **Deliverable:** first-adk-run.json containing sanitized request, output, model identifier and SDK version.
- **Accept when:** A real ADK Runner invocation completes; import success or an invented model reply does not count.

### s21-l03 — Add Tools to an ADK Agent

- **Task:** Inspect the supplied typed stock/delivery tools in examples/s21_inventory.py; add a bounded read-only lookup over data/s21_catalog.json without changing the inventory domain.
- **Deliverable:** lookup_tool.py and valid/invalid SKU input examples.
- **Accept when:** ADK discovers the declared schema, actually calls the tool and rejects an unknown SKU without a side effect.

### s21-l04 — Understand the ADK Agent Loop

- **Task:** Trace one ADK request requiring a tool, including a request that needs no tool.
- **Deliverable:** adk-loop-trace.json with ordered model and function events.
- **Accept when:** The trace separates model-selected actions from application code and pairs each tool result to its invocation.

### s21-l05 — Work with Sessions and Agent State

- **Task:** Use examples/s21_state.py to create shopping-a and shopping-b with actual DatabaseSessionService SQLite persistence; save the SKU and delivery preference only in shopping-a.
- **Deliverable:** session-isolation.py and a restart transcript.
- **Accept when:** The chosen session retains its preference after restart; the second session never receives it. Provider-free state_delta storage evidence is distinct from actual model-selected preference-tool usage.

### s21-l06 — Connect MCP Tools to Google ADK

- **Task:** Use examples/s21_mcp_inventory.py to attach its real inventory MCP server through the supported ADK MCP toolset; inspect the native binding and discovery before a model-selected call.
- **Deliverable:** adk-mcp-agent.py and the inventory tool discovery/call transcript.
- **Accept when:** The real stdio server exposes the selected stock/delivery reads and returns the synthetic catalog result; native discovery/read evidence does not itself prove a model chose the tool.

### s21-l07 — Use the ADK Development Dashboard

- **Task:** Follow examples/s21_adk_dashboard/README.md to open the actual ADK app, dismiss any first-run telemetry modal and inspect a real tool-using request.
- **Deliverable:** dashboard-observations.md plus screenshots of only the Academy test session.
- **Accept when:** The UI shows the actual run, tool arguments and result; record the launch command and installed version.

### s21-l08 — Introduction to the A2A Protocol

- **Task:** Draw separate A2A and MCP message paths for a research specialist and market-data tool.
- **Deliverable:** a2a-versus-mcp.md with one worked delegation scenario.
- **Accept when:** Agent delegation includes task lifecycle and capability discovery; a tool result is not mislabeled an autonomous agent response.

### s21-l09 — Agent Cards, Capabilities and Skills

- **Task:** Inspect examples/s21_a2a_server.py and publish its version-compatible Agent Card for the actual Academy inventory/delivery skill.
- **Deliverable:** agent-card.json plus a validator or discovery-client transcript.
- **Accept when:** The endpoint, identity, input/output modes and declared skill match the running service; unsupported authentication claims are absent.

### s21-l10 — Build an Agent-to-Agent Demonstration

- **Task:** Run examples/s21_a2a_server.py with examples/s21_a2a_client.py against an actual supported inventory/delivery request.
- **Deliverable:** a2a-research-server.py, client.py and sanitized request/status/result log.
- **Accept when:** The client discovers the card and receives a completed task or recorded real failure; an in-process Python function call alone is insufficient.

## Stage 22: AWS Strands and Pydantic AI

**Current source starting points:** [`examples/s22_agents.py`](../../examples/s22_agents.py), [`examples/s22_policy.py`](../../examples/s22_policy.py), [`examples/s22_toolsets.py`](../../examples/s22_toolsets.py), [`examples/s22_policy_mcp.py`](../../examples/s22_policy_mcp.py), [`frameworks/strands_bedrock.py`](../../frameworks/strands_bedrock.py).

### s22-l01 — Introduction to AWS Strands Agents

- **Task:** Map the Strands model provider, agent loop and tools using frameworks/strands_bedrock.py.
- **Deliverable:** strands-architecture.md with one model-to-tool sequence.
- **Accept when:** The selected provider and actual credential route are identified; distinguish SDK orchestration from the local tool implementation.

### s22-l02 — Build a Strands Agent

- **Task:** Run a Strands agent with a course-project explanation prompt.
- **Deliverable:** first-strands-run.json and runnable entry point.
- **Accept when:** The installed Strands SDK performs a real configured model request; record model/version and actual response or an explicit access blocker.

### s22-l03 — Add Tools and Model Providers

- **Task:** Add a typed synthetic-company lookup tool and configure an explicit model provider.
- **Deliverable:** strands-tools.py and tool contract tests.
- **Accept when:** A real agent run invokes lookup, invalid symbols are handled, and provider configuration is not silently replaced with a canned answer.

### s22-l04 — Connect Strands to AWS Bedrock

- **Task:** Configure a least-privilege AWS profile and execute one supported Bedrock model request.
- **Deliverable:** bedrock-run.md with region, model ID, request ID and sanitized response.
- **Accept when:** AWS returns a genuine authorized model result; denied model access is reported as a failed prerequisite, without exposing credentials.

### s22-l05 — Introduction to Pydantic AI

- **Task:** Inspect frameworks/pydantic_typed.py and separate dependencies, tools and output schema.
- **Deliverable:** pydantic-agent-contract.md containing a concrete typed data-flow diagram.
- **Accept when:** A type is assigned to every boundary and the model response is distinguished from validated application data.

### s22-l06 — Build a Typed Pydantic AI Agent

- **Task:** Run examples/s22_agents.py with the native typed policy/ticket request and result boundary; compare frameworks/pydantic_typed.py as an introductory adapter.
- **Deliverable:** typed-agent.py and validated response JSON.
- **Accept when:** The real SDK/model run produces the declared result type; malformed fixture responses are separately rejected by validation.

### s22-l07 — Add Dependency Injection

- **Task:** Use examples/s22_policy.py to inject RequestContext and distinct read-only policy repositories through the framework's typed dependency mechanism.
- **Deliverable:** policy_dependency.py and two independent policy repositories.
- **Accept when:** The same tool uses the injected policy repository, not a global singleton; one request context cannot leak into the other run.

### s22-l08 — Create Structured Agent Outputs

- **Task:** Define a research result model with evidence IDs, summary and uncertainty fields.
- **Deliverable:** research_output.py and accepted/rejected output examples.
- **Accept when:** Required fields and types are enforced; missing evidence cannot be turned into a confident unsupported claim.

### s22-l09 — Add Tools and Toolsets

- **Task:** Inspect examples/s22_toolsets.py and compare reader versus triager FunctionToolsets for policy lookup and an unsent escalation draft.
- **Deliverable:** toolsets.py and a role-to-tool allowlist.
- **Accept when:** Only the configured role's toolsets are visible; RequestContext.role must match that server-selected role, and guessed disallowed calls fail outside model instructions.

### s22-l10 — Connect Pydantic AI to MCP

- **Task:** Use examples/s22_policy_mcp.py to consume the policy MCP server through the actual filtered, prefixed Pydantic MCPToolset in a genuine Agent context.
- **Deliverable:** pydantic-mcp.py and actual discovery/research transcript.
- **Accept when:** The MCP session starts and the actual filtered/prefixed policy tool dispatches with typed dependencies; distinguish protocol-read evidence from a real model-produced final answer.

### s22-l11 — Compare Strands and Pydantic AI Architectures

- **Task:** Run the same read-only research task through Strands and Pydantic AI.
- **Deliverable:** framework-comparison.md with commands, outputs and observed tradeoffs.
- **Accept when:** Compare actual typing, tools, provider setup and traces; identify untested features instead of inventing performance or quality scores.

## Stage 23: AutoGen and Microsoft Agent Framework

**Current source starting points:** [`examples/s23_microsoft_native.py`](../../examples/s23_microsoft_native.py), [`examples/s23_framework_agents.py`](../../examples/s23_framework_agents.py), [`examples/s23_ecosystem.md`](../../examples/s23_ecosystem.md).

### s23-l01 — Introduction to AutoGen, Semantic Kernel and Microsoft Agent Framework

- **Task:** Inventory the installed AutoGen, Semantic Kernel and Microsoft Agent Framework packages and their distinct APIs.
- **Deliverable:** microsoft-ecosystem-map.md with pinned versions and migration boundaries.
- **Accept when:** The map does not assume package names or conversation classes are interchangeable; cite the actual imports used by supplied adapters.

### s23-l02 — Understand Microsoft’s Agent Architecture

- **Task:** Trace one Microsoft agent request through model, tool, conversation and persistence boundaries.
- **Deliverable:** microsoft-runtime-sequence.md and event glossary.
- **Accept when:** State ownership, orchestration and tool execution are assigned explicitly; no framework is credited with unimplemented persistence.

### s23-l03 — Build a Typed Microsoft Agent

- **Task:** Use examples/s23_microsoft_native.py for actual Microsoft Agent Framework typed Ticket/Decision data, SDK Agent, tools and sessions; keep the separate AutoGen example distinct.
- **Deliverable:** typed-microsoft-agent.py and actual response record.
- **Accept when:** A real installed SDK call completes with validated data; incompatible versions are documented rather than bypassed with a mock model.

### s23-l04 — Add Tools and Structured Outputs

- **Task:** Inspect the native Microsoft policy tools and strict Ticket/Decision schemas in examples/s23_microsoft_native.py, then exercise one valid and one invalid result.
- **Deliverable:** tools_and_results.py plus invalid-result tests.
- **Accept when:** Only schema-valid results reach the consumer; record the actual tool invocation and keep provider/model identifiers in the run evidence.

### s23-l05 — Add Conversation State and Persistence

- **Task:** Use the native Microsoft session save/load helpers to persist one conversation across processes; separately document AutoGen save_state/load_state as a different format.
- **Deliverable:** conversation_store.py and before/after sanitized transcript.
- **Accept when:** The restored run uses prior context, while a separate session remains isolated; an in-memory list alone does not satisfy persistence.

### s23-l06 — Build Multi-Agent Workflows

- **Task:** Inspect the supplied Microsoft WorkflowBuilder routing and typed Handoff, then run a researcher-to-reviewer workflow with explicit typed data.
- **Deliverable:** research_review_workflow.py and one complete execution trace.
- **Accept when:** Each specialist performs a real framework run and the reviewer receives the research evidence, not an invented transcript.

### s23-l07 — Add Routing and Delegation

- **Task:** Use the native Microsoft workflow to route delivery and damaged-product tickets to their proper specialists; retain an explicit unknown/held route.
- **Deliverable:** router.py with two route traces and one ambiguous-request case.
- **Accept when:** The chosen destination and decision reason are recorded; ambiguity produces clarification rather than an arbitrary tool mutation.

### s23-l08 — Add Middleware and Telemetry

- **Task:** Inspect native AgentMiddleware, ChatMiddleware and FunctionMiddleware in examples/s23_microsoft_native.py; verify policy/error handling and sanitized telemetry with a dummy secret.
- **Deliverable:** middleware.py and a sanitized telemetry sample.
- **Accept when:** The dummy secret is absent from every retained log and errors preserve correlation IDs without claiming a successful request.

### s23-l09 — Add Human Approval

- **Task:** Use the native Microsoft ApprovalLedger to require explicit confirmation for an exact unsent synthetic escalation payload before its local outbox append.
- **Deliverable:** approval_gate.py and declined/approved execution records.
- **Accept when:** Declining results in zero mutation; an approval bound to the exact payload permits only one local outbox append. This is not an email/network delivery result.

### s23-l10 — Understand AutoGen Migration Patterns

- **Task:** Map an existing AutoGen AgentChat example to the Microsoft adapter's supported abstractions.
- **Deliverable:** autogen-migration.md with before/after runnable files.
- **Accept when:** Both versions' real APIs are identified; document semantic differences and test equivalent task behavior rather than renaming imports.

### s23-l11 — Build Reusable Agent Components

- **Task:** Extract the actual policy tools, strict ticket/decision schemas and approval middleware into reusable components.
- **Deliverable:** components/ package and two small consuming agents.
- **Accept when:** Both agents import shared components without copied implementations; version/configuration differences remain explicit.

## Stage 24: Agno and Mastra

**Current source starting points:** [`examples/s24_agno.py`](../../examples/s24_agno.py), [`examples/s24_mcp_articles.py`](../../examples/s24_mcp_articles.py), [`examples/s24_mastra/triage.ts`](../../examples/s24_mastra/triage.ts), [`examples/s24_mastra/mcp.ts`](../../examples/s24_mastra/mcp.ts), [`examples/s24_mastra/memory.ts`](../../examples/s24_mastra/memory.ts), [`examples/s24_mastra/studio-runbook.md`](../../examples/s24_mastra/studio-runbook.md).

### s24-l01 — Introduction to Agno

- **Task:** Map Agno model, agent, team, memory and workflow responsibilities using the supplied adapter.
- **Deliverable:** agno-design-notes.md with an actual single-agent execution path.
- **Accept when:** Identify which capabilities the starter implements and which require new code or external services.

### s24-l02 — Build a Lightweight Agno Agent

- **Task:** Use examples/s24_triage.py build_agno(model) with an explicitly configured real model and a synthetic ticket from data/s24_articles.json; request evidence-grounded triage through lookup_ticket and search_articles.
- **Deliverable:** agno-first-run.json containing the actual ticket ID, sanitized request/response, cited article IDs, unresolved fields and configured model/package versions.
- **Accept when:** A real Agno/model execution returns the declared Triage fields (ticket_id, summary, article_ids, unresolved), citing actual retrieved articles without sending a message. Record real provider evidence separately; dependency construction, scripted responses and discovery alone do not satisfy this lesson.

### s24-l03 — Add Tools and Structured Outputs

- **Task:** Inspect and exercise the actual typed lookup_ticket(ticket_id) and search_articles(product_id) tools plus the Triage output_schema in examples/s24_triage.py; add one bounded validation case without changing the ticket/article domain.
- **Deliverable:** agno-ticket-tools.md and validation cases covering a known ticket, an unknown ticket, a product with no matching articles and malformed Triage output.
- **Validation:** Shared `triage_schema()` binds article IDs to the returned ticket/product fixture; `validate_triage_response(..., requested_ticket_id=...)` binds the original request. Unsupported, cross-product, duplicate and absent evidence IDs fail. There is no priority field; fixture membership does not prove model retrieval or free-text factuality.
- **Accept when:** The real model/tool run grounds article_ids in the returned ticket/product evidence and reports unresolved facts. Unknown tickets remain explicit errors, empty article matches are not invented, and malformed structured output is rejected; provider-free contract checks remain separately labelled.

### s24-l04 — Connect Agno to MCP

- **Task:** Use examples/s24_mcp_articles.py to connect actual Agno MCPTools to the course article server and inspect configuration, discovery, read and cleanup.
- **Deliverable:** agno_mcp.py and tool-discovery transcript.
- **Accept when:** Actual article reads work through MCP with the configured tool restrictions and cleanup; record model-selected usage separately from provider-free protocol checks.

### s24-l05 — Build an Agno Team

- **Task:** Coordinate a research specialist and review specialist as an Agno team.
- **Deliverable:** agno_team.py and both agents' observed contributions.
- **Native result handling:** Inspect `specialist_completion_summary(result)` and retained member responses. Team `COMPLETED` and delegation `tool_call_error=False` do not prove member success; missing/error/empty specialist records remain explicitly incomplete without rewriting native status. Recorded completion is separate from evidence quality.
- **Accept when:** A final answer attributes evidence to each actual contribution, while unavailable tools or failed members remain visible.

### s24-l06 — Introduction to Mastra

- **Task:** Inspect examples/s24_mastra/triage.ts, mcp.ts and memory.ts for current native tools, workflow, MCPClient and LibSQL-backed Agent Memory; compare the introductory frameworks/mastra adapter.
- **Deliverable:** mastra-component-map.md with the Node/package versions used.
- **Accept when:** TypeScript schema validation and model orchestration are distinguished; document whether memory and observability are actually enabled.

### s24-l07 — Set Up a TypeScript Agent Project

- **Task:** Use examples/s24_mastra/package.json and studio-runbook.md in a clean workspace; configure secrets through environment variables and preserve its exact fixture-server settings.
- **Deliverable:** setup-log.md with install/typecheck/start commands and a redacted .env.example.
- **Accept when:** The actual TypeScript build succeeds and the running process sees required variable names without printing their secret values.

### s24-l08 — Build Mastra Tools and Workflows

- **Task:** Use the native Mastra triage workflow and typed policy/article tools; add a bounded review branch while preserving schema validation.
- **Deliverable:** triage-workflow.ts and success/failure run evidence.
- **Accept when:** The real workflow enforces the tool schema and stops or handles invalid tool output at a documented boundary.

### s24-l09 — Connect Mastra to MCP

- **Task:** Inspect examples/s24_mastra/mcp.ts and connect the actual course article MCP server through Mastra MCPClient.
- **Deliverable:** mcp-client.ts and actual discovery/research record.
- **Accept when:** The TypeScript process communicates with the real MCP server; protocol errors are reported instead of replaced by local fixture calls.

### s24-l10 — Add Memory and Structured Results

- **Task:** Use examples/s24_mastra/memory.ts to persist a thread-specific synthetic triage preference with real LibSQL Agent Memory; return a schema-checked triage result.
- **Deliverable:** memory-workflow.ts and two-session restart checks.
- **Accept when:** State survives restart only for its intended thread/resource, and malformed results fail the output contract. Agent Memory persistence does not establish durable global Studio run history.

### s24-l11 — Inspect Agents with Mastra Studio

- **Task:** Follow examples/s24_mastra/studio-runbook.md to launch the actual Studio app and inspect a real workflow with a failed tool and a separately observed successful attempt.
- **Deliverable:** studio-observations.md plus Academy-only screenshots.
- **Accept when:** Actual UI steps identify tool, arguments, error and later result. The observed local agents page with Academy triage and two tools proves startup, not provider interaction or complete run-history persistence.

### s24-l12 — Compare Python and TypeScript Agent Development

- **Task:** Compare equivalent Python and TypeScript read-only research agents built in this stage.
- **Deliverable:** language-choice.md with measured setup/run evidence.
- **Accept when:** Choose based on actual deployment constraints, typing, team skills and ecosystem; mark absent benchmarks and unsupported capabilities.

## Stage 25: Project 7: Agent Application Factory

**Current source starting points:** [`projects/07-agent-factory/model_pipeline.py`](../../projects/07-agent-factory/model_pipeline.py), [`projects/07-agent-factory/model_schemas.py`](../../projects/07-agent-factory/model_schemas.py), [`projects/07-agent-factory/MODEL-PIPELINE-AUTHORING.md`](../../projects/07-agent-factory/MODEL-PIPELINE-AUTHORING.md), [`projects/07-agent-factory/adapters/frameworks.py`](../../projects/07-agent-factory/adapters/frameworks.py), [`projects/07-agent-factory/docker_validate.py`](../../projects/07-agent-factory/docker_validate.py).

### s25-l01 — Design the Agent Application Factory

- **Task:** Define the application factory's approved inputs, stage gates and generated artifact contract, starting from projects/07-agent-factory/factory.py.
- **Deliverable:** factory-design.md distinguishing the deterministic foundation from model-driven extensions.
- **Accept when:** The design includes requirements, architecture, generation, review and validation; do not describe the starter's templates as LLM agents.

### s25-l02 — Define the Typed Agent Specification

- **Task:** Validate examples/text_helper.json and add one accepted and three rejected specifications.
- **Deliverable:** spec-validation-tests.py and an annotated AgentSpec schema.
- **Accept when:** Unknown fields, unsafe names and unsupported frameworks fail; new supported features require deliberate schema/adapter changes.

### s25-l03 — Build the Requirements Analysis Agent

- **Task:** Inspect Pipeline.analyze and AutoGenBackend in model_pipeline.py, then create the supported catalog specification with advanced.example_spec() and validate it using TypedSpec.parse before an admitted real requirements-specialist call with an explicitly configured model client. The legacy examples/text_helper.json schema cannot be passed unchanged to Pipeline.analyze.
- **Deliverable:** requirements_agent.py, the canonical catalog TypedSpec and its digest, actual retained requirements-specialist response, and a structured requirement-to-field/acceptance-test mapping.
- **Accept when:** A real model response satisfies RequirementsProposal, binds spec_sha256 to the exact catalog TypedSpec and links every mandatory specification field to an observable acceptance test. Preserve genuine raw output and unresolved requirements; offline fixtures or parser success alone do not establish model execution.

### s25-l04 — Build the Architecture Planning Agent

- **Task:** Use Pipeline.design after exact external approval of the requirements; inspect its typed architecture schema and actual specialist response.
- **Deliverable:** architecture_agent.py and a component/dependency plan.
- **Accept when:** The real planner identifies entry points, data boundaries and framework prerequisites without contradicting the approved requirements.

### s25-l05 — Build the Agent Scaffolding Agent

- **Task:** Inspect the scaffolder stage in Pipeline.generate and propose a bounded file manifest in a fresh evidence/output workspace before any application write.
- **Deliverable:** scaffolding_agent.py and proposed/applied manifests.
- **Accept when:** Generation cannot escape the new output directory, overwrite an existing project or silently add unapproved files.

### s25-l06 — Build the Tool Generation Agent

- **Task:** Use the model pipeline's distinct tools specialist with the approved catalog TypedSpec, requirements, architecture and current artifact hashes. Generate the supported catalog_lookup and draft_notification tools using their exact input/output schemas from advanced.TOOL_SCHEMAS; do not substitute the legacy word_count/uppercase contracts.
- **Deliverable:** tool_generation_agent.py, the actual model-generated catalog_lookup and draft_notification modules, typed schema/contract checks, and retained source/specification/architecture identity links.
- **Accept when:** Actual generated tools satisfy the approved TypedSpec schemas, reject malformed and unauthorized arguments, and keep draft_notification unsent with delivered=false. The supported catalog_lookup returns fixture-grounded matches; unavailable external integrations fail explicitly rather than fabricating results. Retain the genuine specialist response separately from offline contract evidence; provider execution remains required before claiming an observed generation.

### s25-l07 — Build the Prompt and Instruction Generator

- **Task:** Use the instructions specialist in model_pipeline.py to generate role, permitted tools, policy clauses and escalation instructions from the approved typed specification.
- **Deliverable:** instruction_agent.py and generated instructions.md.
- **Accept when:** The actual model output preserves every required policy, does not grant extra tools and contains no embedded credentials.

### s25-l08 — Build the Test Generation Agent

- **Task:** Use the tests specialist to propose additional tests from approved requirements; supply the independent immutable acceptance/ suite before generation.
- **Deliverable:** test_generation_agent.py and requirement-to-test mapping.
- **Accept when:** Generated tests run against generated code; include a failing implementation mutant so passing tests are not merely tautological.

### s25-l09 — Build the Code Review Agent

- **Task:** Use Pipeline.inspect to combine static diagnostics with typed reviewer findings over exact generated files and approved requirements; keep reviewer ownership independent of the generator.
- **Deliverable:** review_agent.py and issue records with exact file/line references.
- **Accept when:** The reviewer reports actual inspected code; at least one seeded defect is detected and no patch is accepted solely because the author approved it.

### s25-l10 — Add Framework Selection and Adapters

- **Task:** Inspect adapters/frameworks.py and FRAMEWORKS.md; select an explicit supported adapter and extend it only when its actual required framework behavior is missing.
- **Deliverable:** adapters/ package and framework-selection decision tests.
- **Accept when:** Unsupported frameworks fail explicitly; a selected LLM framework genuinely runs its SDK rather than falling back to the deterministic starter.

### s25-l11 — Generate Complete Agent Project Structures

- **Task:** Assemble the approved generated modules, prompts, schemas, tools, tests and configuration in a new destination.
- **Deliverable:** generated-project/ and SHA-256 inventory.
- **Accept when:** Every declared artifact exists, references resolve and tests execute; preserve the starter's no-overwrite and path-boundary protections.

### s25-l12 — Create README and Environment Templates

- **Task:** Generate a README and .env.example from the selected adapter's actual dependencies.
- **Deliverable:** generated README.md and .env.example reviewed against a clean install.
- **Accept when:** A new user can follow the commands, identify required keys and run the project; no credential or unsupported feature claim enters the files.

### s25-l13 — Validate Generated Projects Inside Docker

- **Task:** Use docker_validate.py and the model pipeline's trusted orchestrator Docker boundary to execute the exact generated artifact and independently supplied acceptance suite in a separately approved digest-pinned image.
- **Deliverable:** docker-validation.json with image ID, commands and real exit codes.
- **Accept when:** The actual container runs non-root under the approved resource/network policy; verify authenticated central receipts, not merely their SHA. Docker execution remains pending where the daemon/image is unavailable; Python isolated mode is not a substitute.

### s25-l14 — Build an Automated Repair Loop

- **Task:** Use Pipeline.repair with actual retained Docker failure diagnostics, the exact allowed non-test file set and the configured at-most-two-patch limit.
- **Deliverable:** repair_loop.py and before/after diff, test output and attempt counter.
- **Accept when:** Only approved non-test files change, the failing case passes and independent acceptance remains immutable. A reserved UNKNOWN model submission is reconciled, never automatically retried.

### s25-l15 — Launch the Generated Agent

- **Task:** Use run_factory with exact requirements/architecture approvals, independent authenticated acceptance, fresh workspace and final human release approval; then launch the validated generated agent.
- **Deliverable:** launch-transcript.json and service startup instructions.
- **Accept when:** The actual generated agent uses its selected framework and validated tools; a deterministic text dispatcher is labeled only the foundation.

### s25-l16 — Complete the Agent Application Factory

- **Task:** Package the full factory evidence, generated application and limitations for an independent reviewer.
- **Deliverable:** factory-portfolio.md linking requirements, plans, code, review, Docker and launch evidence.
- **Accept when:** Every required stage has traceable real execution evidence or an explicit unresolved blocker; no claim that template tests prove model-agent completion.

## Stage 26: MCP Foundations

**Current source starting points:** [`projects/08-mcp-trading-floor/architecture.md`](../../projects/08-mcp-trading-floor/architecture.md), [`projects/08-mcp-trading-floor/mcp_lab/server.py`](../../projects/08-mcp-trading-floor/mcp_lab/server.py), [`projects/08-mcp-trading-floor/mcp_lab/README.md`](../../projects/08-mcp-trading-floor/mcp_lab/README.md).

### s26-l01 — Welcome to Model Context Protocol

- **Task:** Trace how the capstone agent will use the supplied MCP market server instead of a custom tool wrapper.
- **Deliverable:** mcp-introduction.md with one concrete research_company request path.
- **Accept when:** The explanation identifies the reusable protocol boundary and does not conflate MCP with model inference.

### s26-l02 — What Is MCP?

- **Task:** Compare a bespoke market API integration with the same capability exposed through MCP.
- **Deliverable:** integration-comparison.md listing discovery, schemas and transport differences.
- **Accept when:** Both approaches answer the same concrete use case; distinguish protocol benefits from unimplemented authentication or reliability features.

### s26-l03 — MCP Hosts, Clients and Servers

- **Task:** Identify the host, client and server processes for the educational market integration.
- **Deliverable:** mcp-process-map.md with launch commands and trust boundaries.
- **Accept when:** Each role corresponds to a real process/component, and the model itself is not labeled the MCP transport client.

### s26-l04 — Tools, Resources and Prompts

- **Task:** Classify a company lookup, a market-fixture document and a research template as tool, resource and prompt.
- **Deliverable:** capability-contracts.md with example names and schemas.
- **Accept when:** The three classes have distinct invocation/discovery behavior; use mcp_lab/server.py for actual tool, resource and prompt capabilities, rather than claiming all servers expose all three.

### s26-l05 — Capability Discovery and Negotiation

- **Task:** Capture initialization and capability negotiation using a real MCP client and server.
- **Deliverable:** initialize-transcript.json with protocol/package versions and negotiated capabilities.
- **Accept when:** Only advertised supported capabilities are claimed; unavailable resources/prompts are not invented.

### s26-l06 — Local vs Remote MCP Servers

- **Task:** Use mcp_lab/server.py to inspect real stdio and Streamable HTTP variants; then design a separately hosted remote deployment.
- **Deliverable:** local-remote-comparison.md plus a verified local session and remote deployment checklist.
- **Accept when:** Process lifetime, credentials, network exposure and authorization differences are explicit; remote connectivity remains unverified until tested.

### s26-l07 — MCP Connection and Transport Models

- **Task:** Observe initialization, one tool request, response and shutdown over a supported transport.
- **Deliverable:** transport-lifecycle.md and actual protocol trace.
- **Accept when:** Request/response IDs pair correctly and cleanup closes the real process/session; do not substitute arbitrary HTTP JSON for MCP.

### s26-l08 — Working with Node-Based MCP Servers

- **Task:** Install a supported Node-based filesystem MCP server restricted to a fresh Academy practice directory.
- **Deliverable:** node-server-setup.md and sanitized startup/discovery log.
- **Accept when:** The real server starts with the pinned package version and cannot read a test file outside its allowed directory.

### s26-l09 — Inspect MCP Server Capabilities

- **Task:** Use an MCP inspector to inspect market tool names, schemas and a research result.
- **Deliverable:** inspector-observations.md plus Academy-only screenshots.
- **Accept when:** The inspector shows actual server capabilities, validates bad arguments and reports that approval/execution are absent.

### s26-l10 — Understand the Agent Harness and MCP Relationship

- **Task:** Follow one real agent decision that invokes a discovered MCP research tool.
- **Deliverable:** agent-harness-trace.json with model decision, MCP request/result and final answer.
- **Accept when:** The agent runtime owns planning while MCP carries the tool call; final evidence IDs match the actual returned synthetic data.

## Stage 27: Connecting Agents to MCP Servers

**Current source starting points:** [`projects/08-mcp-trading-floor/agent_harness.py`](../../projects/08-mcp-trading-floor/agent_harness.py), [`projects/08-mcp-trading-floor/retrieval_lab/workflow.py`](../../projects/08-mcp-trading-floor/retrieval_lab/workflow.py), [`projects/08-mcp-trading-floor/retrieval_lab/solutions.py`](../../projects/08-mcp-trading-floor/retrieval_lab/solutions.py), [`projects/08-mcp-trading-floor/retrieval_lab/README.md`](../../projects/08-mcp-trading-floor/retrieval_lab/README.md).

### s27-l01 — Connect to a Filesystem MCP Server

- **Task:** Connect a filesystem MCP server to a temporary directory containing course notes.
- **Deliverable:** filesystem-agent.py and allowed/denied path test transcript.
- **Accept when:** The real server reads the allowed note and rejects traversal or access outside the approved root; use no personal files.

### s27-l02 — Connect to a Web Fetch MCP Server

- **Task:** Connect a genuine web-fetch MCP server and request a harmless public documentation page.
- **Deliverable:** fetch-agent.py and URL/status/content record.
- **Accept when:** The result came from the server at the recorded time; retain failures and do not represent fixture text as a live fetch.

### s27-l03 — Connect to a Playwright MCP Server

- **Task:** Start a real Playwright MCP server with a fresh browser profile and open a course-only local page.
- **Deliverable:** playwright-session.md and actual navigation/extraction output.
- **Accept when:** The MCP client drives a real browser, extracts the expected page text and closes its temporary context without touching personal sessions.

### s27-l04 — Call MCP Tools from an AI Agent

- **Task:** Discover the educational market tools and let an actual model select research_company.
- **Deliverable:** agent-tool-loop.py and sanitized model/MCP events.
- **Accept when:** Validate arguments before the call and return the real tool result to the model; no automatic approval or trade is exposed.

### s27-l05 — Read MCP Resources

- **Task:** Use mcp_lab/server.py to discover and read its actual stable handbook resource URI through the resources API.
- **Deliverable:** resource-client.py and resource list/read results.
- **Accept when:** Discovery advertises the resource and read returns the documented MIME type and content; a similarly named tool call is not substituted.

### s27-l06 — Work with MCP Prompts

- **Task:** Use mcp_lab/server.py to discover and retrieve the supplied parameterized prompt through the prompts API.
- **Deliverable:** prompt-client.py and list/get transcript.
- **Accept when:** The real prompts API validates required arguments and returns reusable messages; local string formatting alone does not prove MCP prompt support.

### s27-l07 — Build a Web-Browsing MCP Agent

- **Task:** Use retrieval_lab/workflow.py and solutions.compare_products with the pinned genuine Fetch and Playwright servers on the exact Academy static/dynamic fixture pages.
- **Deliverable:** browsing-agent.py and cited navigation/research record.
- **Accept when:** The real agent selects actual fetch/browser actions and cites exact observed source quotations; URL/tool facades reject file:, metadata hosts, unapproved URLs and mutation tools. A private network namespace alone does not confine browser filesystem reads.

### s27-l08 — Trace MCP Tool Calls

- **Task:** Instrument each MCP operation with correlation ID, server, tool, sanitized arguments and latency.
- **Deliverable:** mcp_trace.py and JSONL from a successful and failed call.
- **Accept when:** Every result/error maps to its actual request, secrets are redacted and duration is measured rather than estimated.

### s27-l09 — Handle Tool Failures and Invalid Results

- **Task:** Inject a stopped server, invalid tool input and malformed result into separate client tests.
- **Deliverable:** mcp-failure-tests.py and observed recovery outcomes.
- **Accept when:** The client reports distinct errors and applies bounded recovery; uncertain state-changing requests are never blindly replayed.

### s27-l10 — Filter and Organize MCP Tools

- **Task:** Build a role-specific tool registry separating research reads from administrative functions.
- **Deliverable:** tool-filter.py and discovery allowlist tests.
- **Accept when:** An unapproved tool is absent from the model-visible list and denied even if its name is requested directly.

### s27-l11 — Apply Least-Privilege Tool Access

- **Task:** Restrict a research agent to read-only company data and its own scratch directory.
- **Deliverable:** least-privilege.md and attempted unauthorized-operation transcript.
- **Accept when:** Access controls are enforced outside model instructions, with a real denied cross-directory read or write.

### s27-l12 — Secure Secrets and Sensitive Data

- **Task:** Use a dummy credential to test environment loading, redaction and untrusted-server prompt injection.
- **Deliverable:** secret-handling-tests.py and sanitized logs.
- **Accept when:** The dummy secret never appears in retained prompts, errors or generated files; malicious returned instructions cannot expand permissions.

### s27-l13 — Add Human Approval to MCP Tools

- **Task:** Add an application-side approval gate before a harmless MCP write to a temporary note.
- **Deliverable:** approval-client.py and declined, approved and changed-argument tests.
- **Accept when:** No write happens before explicit human confirmation; approval binds exact arguments and cannot be reused for another operation.

## Stage 28: Building Custom MCP Servers

**Current source starting points:** [`projects/08-mcp-trading-floor/mcp_lab/server.py`](../../projects/08-mcp-trading-floor/mcp_lab/server.py), [`projects/08-mcp-trading-floor/retrieval_lab/research_server.py`](../../projects/08-mcp-trading-floor/retrieval_lab/research_server.py), [`projects/08-mcp-trading-floor/retrieval_lab/rag.py`](../../projects/08-mcp-trading-floor/retrieval_lab/rag.py), [`projects/08-mcp-trading-floor/retrieval_lab/search.py`](../../projects/08-mcp-trading-floor/retrieval_lab/search.py), [`projects/08-mcp-trading-floor/retrieval_lab/progressive.py`](../../projects/08-mcp-trading-floor/retrieval_lab/progressive.py).

### s28-l01 — When to Build a Custom MCP Server

- **Task:** Assess three capabilities: portfolio read, internal arithmetic and external search.
- **Deliverable:** mcp-boundary-decisions.md with consumers, reuse need and alternatives.
- **Accept when:** Each choice explains why MCP, a native function or an API is appropriate rather than putting every function behind a server.

### s28-l02 — Design an MCP Server Contract

- **Task:** Write a contract for synthetic-company research, including permissions and error cases.
- **Deliverable:** market-server-contract.json and versioning notes.
- **Accept when:** Names, input/output types, synthetic labels, limits and errors are specified before implementation and agree with starter market fixtures.

### s28-l03 — Introduction to FastMCP

- **Task:** Inspect the FastMCP imports and decorators in projects/08-mcp-trading-floor/mcp_server.py.
- **Deliverable:** fastmcp-component-map.md with installed MCP/FastMCP versions.
- **Accept when:** Identify server construction, typed tools and stdio startup; do not mix incompatible standalone FastMCP and bundled SDK APIs.

### s28-l04 — Build Your First FastMCP Server

- **Task:** Launch the supplied market MCP server and connect a real client.
- **Deliverable:** first-fastmcp-run.json with initialization, list_tools and research_company result.
- **Accept when:** The real client receives ACA fixture evidence and closes the session; importing mcp_server.py alone does not count.

### s28-l05 — Create Typed MCP Tools

- **Task:** Add a documented typed research filter or portfolio-summary tool with bounded inputs.
- **Deliverable:** typed_market_tool.py and valid/invalid client-call results.
- **Accept when:** Schemas reject invalid arguments and output remains serializable, read-only and explicitly synthetic.

### s28-l06 — Add MCP Resources

- **Task:** Expose the fixture catalog through a stable read-only MCP resource URI.
- **Deliverable:** market_resources.py and list/read transcript.
- **Accept when:** A real client lists and reads the resource using the resources API with the correct MIME type and synthetic-data description.

### s28-l07 — Add Reusable MCP Prompts

- **Task:** Expose a parameterized research-summary prompt with evidence requirements.
- **Deliverable:** market_prompts.py and list/get transcript.
- **Accept when:** The prompts API advertises arguments and returns messages that require evidence IDs and uncertainty rather than fabricated prices.

### s28-l08 — Run and Inspect the Server

- **Task:** Launch an MCP inspector against the extended server and test each exposed capability.
- **Deliverable:** server-inspection.md plus actual tool/resource/prompt observations.
- **Accept when:** All documented schemas agree with actual discovery, and invalid calls produce observed errors without mutating the portfolio.

### s28-l09 — Connect the Server to an AI Agent

- **Task:** Attach the extended server to an actual framework agent and request a company summary.
- **Deliverable:** custom-mcp-agent.py and full model/tool/final-answer trace.
- **Accept when:** The answer uses returned evidence and identifies the fictional company; local direct calls are not presented as protocol integration.

### s28-l10 — Test MCP Tools and Error Handling

- **Task:** Test valid input, schema failure, denied access, timeout and terminated server scenarios.
- **Deliverable:** mcp_server_tests.py and real client/server test log.
- **Accept when:** Each failure has an explicit expected outcome; a server timeout does not become an invented successful response.

### s28-l11 — Build a Long-Term Memory MCP Server

- **Task:** Inspect the existing namespaced persistent memory service and retrieval_lab resource controls; demonstrate storage, retrieval and update without inventing a second incompatible persistence layer.
- **Deliverable:** memory_server.py, temporary SQLite fixture and restart/isolation tests.
- **Accept when:** Memories survive process restart, one owner cannot access another's records and all mutation boundaries are tested.

### s28-l12 — Build a Web Search MCP Server

- **Task:** Configure retrieval_lab/search.py with an authorized SearxNG-compatible origin and invoke the revealed search_web capability, preserving normalized query/results and actual provider metadata.
- **Deliverable:** search_server.py and sanitized actual provider response.
- **Accept when:** Retain original URLs and retrieval time, distinguish provider failure from empty results and never label fixture search as live.

### s28-l13 — Connect an Agentic RAG Service

- **Task:** Use retrieval_lab/research_server.py, solutions.ingest_course_documents and solutions.answer_with_rag with a write-authorized preparation session and a separate read-only model session.
- **Deliverable:** rag_server.py, small Academy corpus and retrieval/evidence tests.
- **Accept when:** Real ingestion and retrieval return owner-bound chunk IDs, source URIs, offsets and hashes; final quotations must match actual observations. Empty evidence produces abstention, not invented citations.

### s28-l14 — Connect Vector Search with Qdrant

- **Task:** Use retrieval_lab/rag.py DocumentRAG.service with a real Qdrant service, then insert/query/delete Academy document chunks through the MCP research server.
- **Deliverable:** qdrant_server.py with collection schema and real insert/search transcript.
- **Accept when:** A real Qdrant service returns stored IDs with verified persistence and owner isolation. Label the default 64-dimensional token-hash encoder honestly; a SentenceTransformerEncoder needs an immutable model revision and its own actual semantic-embedding evidence.

### s28-l15 — Build a Market Data MCP Service

- **Task:** Extend the supplied synthetic market server with normalized quote metadata and permission checks.
- **Deliverable:** market-service-tests.py and contract-to-tool mapping.
- **Accept when:** Fixture prices retain synthetic/as-of/evidence labels and invalid symbols fail; live market sourcing is a distinct unclaimed integration.

### s28-l16 — Apply Progressive Tool Discovery

- **Task:** Inspect retrieval_lab/progressive.py and research_server.py; demonstrate hidden-then-revealed specialist capabilities with session-specific exposure and fresh authorization at dispatch.
- **Deliverable:** progressive_discovery.py and before/after tool lists.
- **Accept when:** Only task-relevant capabilities become visible after a documented selection step; permission enforcement persists even when a hidden name is guessed.

## Stage 29: Project 8: MCP-Powered AI Trading Floor

**Current source starting points:** [`projects/08-mcp-trading-floor/trading_floor.py`](../../projects/08-mcp-trading-floor/trading_floor.py), [`projects/08-mcp-trading-floor/capstone_agents.py`](../../projects/08-mcp-trading-floor/capstone_agents.py), [`projects/08-mcp-trading-floor/sdk_role_provider.py`](../../projects/08-mcp-trading-floor/sdk_role_provider.py), [`projects/08-mcp-trading-floor/portfolio_mcp_server.py`](../../projects/08-mcp-trading-floor/portfolio_mcp_server.py), [`projects/08-mcp-trading-floor/gradio_app.py`](../../projects/08-mcp-trading-floor/gradio_app.py).

### s29-l01 — Design the MCP Trading Floor

- **Task:** Define the paper-trading learning goals, intended users and non-broker boundaries.
- **Deliverable:** trading-floor-scope.md based on projects/08-mcp-trading-floor.
- **Accept when:** All data is identified as synthetic, execution remains simulated and required multi-agent/MCP/UI work is separated from the deterministic starter.

### s29-l02 — Define the Capstone Architecture

- **Task:** Map agents, MCP services, TradingFloor state, human approval, API and dashboards.
- **Deliverable:** capstone-architecture.md with component ownership and trust boundaries.
- **Accept when:** The map identifies actual starter files versus extensions, persistent DB locations and the separate human approval path.

### s29-l03 — Define the Market Research Agent

- **Task:** Use capstone_agents.py TradingAgents and sdk_role_provider.py SDKRoleProvider to run the actual researcher role against MCP-supplied evidence with an explicitly configured model client.
- **Deliverable:** research_agent.py and a structured synthetic-company report.
- **Accept when:** A real agent/MCP run produces evidence-linked claims and uncertainty; TradingFloor.research alone is only the deterministic data foundation.

### s29-l04 — Define the Trading Strategy Agent

- **Task:** Use the strategist role in TradingAgents with the typed research handoff and explicit configured-model provider; inspect proposal rationale, uncertainty and whole-share quantity.
- **Deliverable:** strategy_agent.py and accepted/rejected structured proposals.
- **Accept when:** A real model output explains quantity/side using evidence, while deterministic validation remains authoritative before further processing.

### s29-l05 — Define the Risk Management Agent

- **Task:** Wrap TradingFloor.risk as the deterministic authority for the risk specialist.
- **Deliverable:** risk_agent.py and boundary-case test table.
- **Accept when:** Insufficient cash, order limit, position limit and unsupported short sale are rejected regardless of the model's recommendation.

### s29-l06 — Define the Portfolio and Paper-Execution Agent

- **Task:** Inspect TradingAgents execution boundaries, portfolio_mcp_server.py and the application-only reviewer/execute paths; run the specialist with exact account and proposal identities.
- **Deliverable:** execution_agent.py and approval-to-paper-fill trace.
- **Accept when:** No model role grants approval. A paper fill requires the exact proposal/account/revision-bound, unexpired approval and stable request ID; account changes invalidate stale approval.

### s29-l07 — Build the Market Data MCP Integration

- **Task:** Use the genuine market MCP server to obtain research and normalized fixture prices.
- **Deliverable:** market-integration.json with discovery and actual tool results.
- **Accept when:** Symbols, evidence IDs and as-of values match fixtures/market.json and are labeled fictional rather than represented as current market quotes.

### s29-l08 — Build the Research MCP Integration

- **Task:** Use the existing services.py corpus/retrieval tools for synthetic research and retrieval_lab/search.py for an explicitly configured real search provider; preserve the distinction.
- **Deliverable:** research_mcp.py and source attribution tests.
- **Accept when:** The agent receives source IDs/URLs and retrieval metadata; unavailable live search is stated explicitly instead of synthesized.

### s29-l09 — Build the Memory MCP Integration

- **Task:** Use ToolServices namespaced persistent memory and MCP memory tools to reconnect across application sessions; record the actual database and trusted owner identity.
- **Deliverable:** memory_integration.py and two-session isolation/restart transcript.
- **Accept when:** Prior analysis is recoverable for the correct user, rejected proposals remain auditable and another session's data is inaccessible.

### s29-l10 — Build the Portfolio MCP Service

- **Task:** Expose read-only portfolio/valuation and controlled paper-order operations through explicit service contracts.
- **Deliverable:** portfolio_service.py and cash/positions/order tests.
- **Accept when:** Approval remains outside model authority; expose controlled paper execution only through its explicit service/allowlist boundary. Unauthorized or stale operations fail, and an exact duplicate execution returns its prior receipt.

### s29-l11 — Use the Researcher-as-a-Tool Pattern

- **Task:** Expose the researcher as a callable specialist used by strategy rather than duplicating its logic.
- **Deliverable:** researcher_tool.py and a strategy-to-research handoff trace.
- **Accept when:** The actual requesting agent receives a validated research artifact with evidence IDs; trace attribution identifies the specialist call.

### s29-l12 — Pass Structured Information Between Agents

- **Task:** Inspect capstone_agents.py Handoff and TradingAgents role-output validation; exercise typed research, strategy, risk and execution boundaries without bypassing account revision checks.
- **Deliverable:** handoff_schemas.py with valid/invalid examples for each boundary.
- **Accept when:** A malformed report or mismatched proposal digest stops the workflow before approval or execution.

### s29-l13 — Apply Risk and Portfolio Rules

- **Task:** Test portfolio limits at, below and above each configured boundary.
- **Deliverable:** risk_boundary_tests.py referencing TradingFloor.risk.
- **Accept when:** Assertions verify exact cash/order/concentration/short-sale behavior and no rejected transaction changes stored state.

### s29-l14 — Execute Controlled Paper Trades

- **Task:** Review the exact proposal through approve_order.py or the separate reviewer-token /reviews endpoint, then execute with the operator capability and a stable request ID.
- **Deliverable:** paper-trade-receipt.json with before/after state and trace.
- **Accept when:** The fill occurs once; exact replay returns its receipt and a changed order/key pairing fails. Verify approval expiry and account-revision invalidation before execution, not just at proposal creation.

### s29-l15 — Orchestrate the Complete Trading Floor

- **Task:** Run TradingAgents with the genuine MCP registry and explicitly configured SDKRoleProvider through research→strategy→deterministic-risk→human-review→paper execution.
- **Deliverable:** orchestrator.py and complete actual trace.
- **Accept when:** Each required agent/MCP boundary is exercised, human approval is real and refusal/error paths do not mutate the account.

### s29-l16 — Build the Gradio Trading Dashboard

- **Task:** Launch the current gradio_app.py and exercise its actual research, proposal, distinct reviewer approval/rejection, execution, portfolio, trace and feedback paths.
- **Deliverable:** gradio-observations.md and implemented dashboard changes.
- **Accept when:** Actual browser output shows the expected current states and preserves rejection/error messages. Genuine local UI behavior does not prove real model-agent contributions or hosted deployment.

## Stage 30: Evaluation, Deployment and Course Completion

**Current source starting points:** [`projects/08-mcp-trading-floor/evaluation_lab/README.md`](../../projects/08-mcp-trading-floor/evaluation_lab/README.md), [`projects/08-mcp-trading-floor/evaluation_lab/WORKED-SOLUTIONS.md`](../../projects/08-mcp-trading-floor/evaluation_lab/WORKED-SOLUTIONS.md), [`projects/08-mcp-trading-floor/api.py`](../../projects/08-mcp-trading-floor/api.py), [`projects/08-mcp-trading-floor/frontend/src/main.jsx`](../../projects/08-mcp-trading-floor/frontend/src/main.jsx), [`projects/08-mcp-trading-floor/deployment/DEPLOY.md`](../../projects/08-mcp-trading-floor/deployment/DEPLOY.md).

### s30-l01 — Add Tracing and Observability to the Trading Floor

- **Task:** Instrument real capstone model, MCP, transition, approval and error events alongside TradingFloor.trace.
- **Deliverable:** observability.py and correlated JSONL for one complete run.
- **Accept when:** Events have timestamps and parent/run IDs; retain actual failures and separate local deterministic events from model/provider telemetry.

### s30-l02 — Build Capstone Evaluation Datasets

- **Task:** Create deterministic scenario fixtures for insufficient cash, concentration, stale quote and missing evidence.
- **Deliverable:** evaluation-cases.json with expected constraints and provenance.
- **Accept when:** Each case has explicit expected checks, uses fictional companies and avoids assuming one model's exact wording is the ground truth.

### s30-l03 — Evaluate Research and Trading Decisions

- **Task:** Evaluate real saved research and strategy outputs against evidence and rule-compliance criteria.
- **Deliverable:** evaluation-report.json with per-case scores and citations.
- **Accept when:** Scores can be traced to inspected outputs and actual assertions; missing data is unresolved rather than scored as successful.

### s30-l04 — Add Deterministic Risk Checks

- **Task:** Expand risk tests for numeric edge cases, changed proposal evidence and duplicate request IDs.
- **Deliverable:** deterministic_risk_tests.py and actual test output.
- **Accept when:** Invalid quantities/prices and mismatched evidence fail, approved fills remain idempotent and rejected calls leave balances unchanged.

### s30-l05 — Add Model-Based Quality Evaluators

- **Task:** Run an independent model evaluator with an explicit evidence, clarity and uncertainty rubric.
- **Deliverable:** model_evaluator.py plus actual structured judgments and model IDs.
- **Accept when:** Retain input/output and uncertainty; model judgments never override deterministic risk or fabricate an observed human rating.

### s30-l06 — Collect Human Feedback

- **Task:** Use evaluation_lab/feedback.py BoundFeedbackStore and the existing UI/API form to bind feedback to the exact registered run/output SHA, then collect an actual reviewer comment.
- **Deliverable:** feedback_schema.py and one actual reviewer submission.
- **Accept when:** Feedback attribution, timestamp and exact output binding are preserved; altered/unregistered output is rejected. Fixture reviewer comments are not represented as real human feedback or trading approval.

### s30-l07 — Test Tool and Agent Failure Scenarios

- **Task:** Simulate MCP outage, malformed research, model failure and a stopped orchestration step.
- **Deliverable:** failure_matrix.md and actual injected-failure logs.
- **Accept when:** The workflow exposes the failing boundary and preserves state, without reporting a paper fill for an incomplete run.

### s30-l08 — Add Retry and Recovery Strategies

- **Task:** Implement bounded retries for read-only work and resume/idempotency rules for execution.
- **Deliverable:** recovery_policy.py and interrupted-run/replay tests.
- **Accept when:** Attempts are capped; uncertain writes are checked by request ID before replay and risk/approval are revalidated after changes.

### s30-l09 — Monitor Token Usage, Latency and Cost

- **Task:** Collect genuine provider usage, measured latency and configured price-version calculations.
- **Deliverable:** usage_report.json per model/agent/tool/run.
- **Accept when:** Missing usage is unknown rather than zero; the starter's zero-call metrics are labeled deterministic-only and not used as LLM cost evidence.

### s30-l10 — Build the FastAPI Backend

- **Task:** Launch api.py and exercise /health, /state, /research/{symbol}, /proposals, /reviews, /execute and feedback routes with the appropriate distinct operator/reviewer capabilities.
- **Deliverable:** api-tests.py and actual HTTP status/body records.
- **Accept when:** Unauthenticated mutations fail, reviewer and operator tokens differ, strict schemas validate and exact approval/revision/expiry checks hold. Document read-only research/state exposure and localhost-only identity limitations.

### s30-l11 — Build the React Front End

- **Task:** Install and run the current frontend/ against the real API; exercise research, proposals, reviewer approval/rejection, execution, portfolio/trace and bound feedback, including actual error responses.
- **Deliverable:** frontend-observations.md and React changes for required workflow states.
- **Accept when:** Actual browser requests display current API data and preserve a rejected execution/error rather than immediately overwriting it with a successful refresh; tokens remain masked and absent from captures.

### s30-l12 — Package the Application with Docker

- **Task:** Inspect deployment/compose.yaml and its backend/frontend Dockerfiles, nginx.conf and .env.example; build the actual stack and test persistent paper state.
- **Deliverable:** compose.yaml and actual build/start/restart logs.
- **Accept when:** Containers run with documented ports/secrets/volumes and state persists after restart; unavailable Docker access is reported, not replaced by import tests.

### s30-l13 — Deploy the MCP-Powered Trading Floor

- **Task:** Deploy the educational stack to an authorized test host and run a complete non-broker workflow.
- **Deliverable:** deployment-receipt.md with commit/image IDs, health checks and rollback procedure.
- **Accept when:** Actual reachable services and persisted paper state are verified; local-only execution is clearly distinguished from hosted deployment.

### s30-l14 — Inspect Complete Capstone Traces

- **Task:** Inspect one accepted and one rejected capstone run end to end.
- **Deliverable:** trace-walkthrough.md linking research, strategy, risk, approval and state evidence.
- **Accept when:** Every claimed outcome is supported by matching run IDs/proposal digests, with no missing tool results hidden by the summary.

### s30-l15 — Present the Final Capstone Project

- **Task:** Present a recorded or live capstone walkthrough with architecture, evidence and limitations.
- **Deliverable:** capstone-presentation.md and demonstration links/files.
- **Accept when:** Demonstrate a genuine model/MCP workflow, deterministic rejection and approved paper fill; disclose incomplete external integrations.

### s30-l16 — Choosing the Right Agent Framework

- **Task:** Compare the course's real framework implementations against a single task and deployment requirement.
- **Deliverable:** framework-decision-record.md with measured/observed evidence and alternatives.
- **Accept when:** Explain tradeoffs in control, state, interoperability and operations without inventing unrun benchmarks or declaring a universal winner.

### s30-l17 — Ten Principles of Effective Agentic AI Engineering

- **Task:** Audit the capstone against ten explicit engineering principles with concrete code/evidence links.
- **Deliverable:** engineering-principles-audit.md with one finding/action per principle.
- **Accept when:** Each principle has an inspected implementation or honest gap, including typed boundaries, least privilege, observability, approval and recovery.

### s30-l18 — Your Agentic AI Engineering Career Roadmap

- **Task:** Choose an engineering role and map three completed projects to demonstrated skills and remaining gaps.
- **Deliverable:** career-roadmap.md with portfolio links, a rehearsal plan and next learning milestones.
- **Accept when:** Every portfolio claim links to actual code/run evidence; do not claim hypothetical deployments, customers or employment outcomes.

### s30-l19 — Course Completion and Next Steps

- **Task:** Create the final portfolio index and choose one justified specialization extension.
- **Deliverable:** completion-checklist.md linking eight projects, evaluations, repos and unresolved prerequisites.
- **Accept when:** Completion claims match verified artifacts and real runs; pending SDK/service/browser checks remain clearly open rather than silently waived.
