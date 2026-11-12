# Lesson practicals: stages 21–30

This workbook defines student tasks and acceptance evidence for the exact curriculum lesson IDs. These are assignments, not claims that live services, framework agents, browsers or deployments have already been verified. Save your new work and evidence under `student-work/<lesson-id>/` in your own checkout; do not commit credentials or private account captures. Existing repository paths below are starting points, not a guarantee that every lesson extension is already implemented.

Use the dependency manifests in `frameworks/requirements/` and each project’s optional requirements. Real model/provider, ADK dashboard, A2A, MCP inspector, Playwright browser, Qdrant, Docker and hosted deployment exercises require those actual runtimes and authorized access. Record a concrete blocker when unavailable. Deterministic fixtures and unit tests are useful foundations but do not substitute for a required real framework/MCP/model execution.

Project 7’s `projects/07-agent-factory/factory.py` initially generates a deterministic stdlib tool application. Stage 25 explicitly builds the additional model-driven factory agents and framework adapters. Project 8’s `projects/08-mcp-trading-floor/trading_floor.py` is a synthetic paper-trading engine; `mcp_server.py`, `api.py`, `gradio_app.py`, `approve_order.py` and `frontend/` are concrete integration starting points. Required search, memory, RAG, Qdrant, multi-agent and complete UI extensions must be implemented and verified separately. No exercise authorizes real brokerage execution.

## Stage 21: Google ADK and Agent-to-Agent Communication

### s21-l01 — Introduction to Google Agent Development Kit

- **Task:** Map Agent, Runner, SessionService and tool responsibilities in frameworks/google_adk_agent.py before running it.
- **Deliverable:** adk-component-map.md with the installed ADK version and a request sequence diagram.
- **Accept when:** Each diagram node maps to a real imported class; identify the model credential and runtime dependencies separately.

### s21-l02 — Build Your First Google ADK Agent

- **Task:** Run the supplied Google ADK adapter with a harmless course query and retain its actual response.
- **Deliverable:** first-adk-run.json containing sanitized request, output, model identifier and SDK version.
- **Accept when:** A real ADK Runner invocation completes; import success or an invented model reply does not count.

### s21-l03 — Add Tools to an ADK Agent

- **Task:** Add a read-only course-project lookup tool with typed stage and project arguments.
- **Deliverable:** lookup_tool.py and valid/invalid input examples.
- **Accept when:** ADK discovers the declared schema, actually calls the tool and rejects an out-of-range stage without a side effect.

### s21-l04 — Understand the ADK Agent Loop

- **Task:** Trace one ADK request requiring a tool, including a request that needs no tool.
- **Deliverable:** adk-loop-trace.json with ordered model and function events.
- **Accept when:** The trace separates model-selected actions from application code and pairs each tool result to its invocation.

### s21-l05 — Work with Sessions and Agent State

- **Task:** Create two ADK sessions and persist a selected project preference only in one.
- **Deliverable:** session-isolation.py and a restart transcript.
- **Accept when:** The chosen session retains its preference after restart; the second session never receives that state.

### s21-l06 — Connect MCP Tools to Google ADK

- **Task:** Attach the educational market MCP server to an ADK agent using the supported MCP toolset.
- **Deliverable:** adk-mcp-agent.py and discovery/call transcript.
- **Accept when:** The real stdio server exposes research_company and returns synthetic evidence; no approve or execute capability is available to the model.

### s21-l07 — Use the ADK Development Dashboard

- **Task:** Open the installed ADK development dashboard and inspect the tool-using request.
- **Deliverable:** dashboard-observations.md plus screenshots of only the Academy test session.
- **Accept when:** The UI shows the actual run, tool arguments and result; record the launch command and installed version.

### s21-l08 — Introduction to the A2A Protocol

- **Task:** Draw separate A2A and MCP message paths for a research specialist and market-data tool.
- **Deliverable:** a2a-versus-mcp.md with one worked delegation scenario.
- **Accept when:** Agent delegation includes task lifecycle and capability discovery; a tool result is not mislabeled an autonomous agent response.

### s21-l09 — Agent Cards, Capabilities and Skills

- **Task:** Publish a version-compatible A2A Agent Card for a synthetic-company research skill.
- **Deliverable:** agent-card.json plus a validator or discovery-client transcript.
- **Accept when:** The endpoint, identity, input/output modes and declared skill match the running service; unsupported authentication claims are absent.

### s21-l10 — Build an Agent-to-Agent Demonstration

- **Task:** Run a real A2A server and separate client that request research on ACA.
- **Deliverable:** a2a-research-server.py, client.py and sanitized request/status/result log.
- **Accept when:** The client discovers the card and receives a completed task or recorded real failure; an in-process Python function call alone is insufficient.

## Stage 22: AWS Strands and Pydantic AI

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

- **Task:** Run a Pydantic AI agent returning a typed project recommendation.
- **Deliverable:** typed-agent.py and validated response JSON.
- **Accept when:** The real SDK/model run produces the declared result type; malformed fixture responses are separately rejected by validation.

### s22-l07 — Add Dependency Injection

- **Task:** Inject a read-only course catalog repository through the framework's typed dependency mechanism.
- **Deliverable:** catalog_dependency.py and two independent test catalogs.
- **Accept when:** The same tool uses the injected catalog, not a global singleton; one test catalog cannot leak into the other run.

### s22-l08 — Create Structured Agent Outputs

- **Task:** Define a research result model with evidence IDs, summary and uncertainty fields.
- **Deliverable:** research_output.py and accepted/rejected output examples.
- **Accept when:** Required fields and types are enforced; missing evidence cannot be turned into a confident unsupported claim.

### s22-l09 — Add Tools and Toolsets

- **Task:** Separate catalog lookup and synthetic-market research into named toolsets.
- **Deliverable:** toolsets.py and a role-to-tool allowlist.
- **Accept when:** Only the selected toolset is visible to each agent; a disallowed operation cannot be reached through another generic tool.

### s22-l10 — Connect Pydantic AI to MCP

- **Task:** Consume the project's real MCP market server through Pydantic AI's supported MCP integration.
- **Deliverable:** pydantic-mcp.py and actual discovery/research transcript.
- **Accept when:** The MCP session starts, discovers tools and returns synthetic ACA evidence in a validated output; no broker calls occur.

### s22-l11 — Compare Strands and Pydantic AI Architectures

- **Task:** Run the same read-only research task through Strands and Pydantic AI.
- **Deliverable:** framework-comparison.md with commands, outputs and observed tradeoffs.
- **Accept when:** Compare actual typing, tools, provider setup and traces; identify untested features instead of inventing performance or quality scores.

## Stage 23: AutoGen and Microsoft Agent Framework

### s23-l01 — Introduction to AutoGen, Semantic Kernel and Microsoft Agent Framework

- **Task:** Inventory the installed AutoGen, Semantic Kernel and Microsoft Agent Framework packages and their distinct APIs.
- **Deliverable:** microsoft-ecosystem-map.md with pinned versions and migration boundaries.
- **Accept when:** The map does not assume package names or conversation classes are interchangeable; cite the actual imports used by supplied adapters.

### s23-l02 — Understand Microsoft’s Agent Architecture

- **Task:** Trace one Microsoft agent request through model, tool, conversation and persistence boundaries.
- **Deliverable:** microsoft-runtime-sequence.md and event glossary.
- **Accept when:** State ownership, orchestration and tool execution are assigned explicitly; no framework is credited with unimplemented persistence.

### s23-l03 — Build a Typed Microsoft Agent

- **Task:** Run frameworks/microsoft_agent.py and add a typed course-recommendation request/result boundary.
- **Deliverable:** typed-microsoft-agent.py and actual response record.
- **Accept when:** A real installed SDK call completes with validated data; incompatible versions are documented rather than bypassed with a mock model.

### s23-l04 — Add Tools and Structured Outputs

- **Task:** Add a read-only catalog tool and a structured research result to the Microsoft agent.
- **Deliverable:** tools_and_results.py plus invalid-result tests.
- **Accept when:** Only schema-valid results reach the consumer; record the actual tool invocation and keep provider/model identifiers in the run evidence.

### s23-l05 — Add Conversation State and Persistence

- **Task:** Persist one conversation, terminate the application and restore it in a new process.
- **Deliverable:** conversation_store.py and before/after sanitized transcript.
- **Accept when:** The restored run uses prior context, while a separate session remains isolated; an in-memory list alone does not satisfy persistence.

### s23-l06 — Build Multi-Agent Workflows

- **Task:** Build researcher-to-reviewer workflow with explicit typed handoff data.
- **Deliverable:** research_review_workflow.py and one complete execution trace.
- **Accept when:** Each specialist performs a real framework run and the reviewer receives the research evidence, not an invented transcript.

### s23-l07 — Add Routing and Delegation

- **Task:** Route catalog questions to a catalog specialist and risk questions to a risk specialist.
- **Deliverable:** router.py with two route traces and one ambiguous-request case.
- **Accept when:** The chosen destination and decision reason are recorded; ambiguity produces clarification rather than an arbitrary tool mutation.

### s23-l08 — Add Middleware and Telemetry

- **Task:** Add middleware that redacts a dummy secret and telemetry for each model/tool step.
- **Deliverable:** middleware.py and a sanitized telemetry sample.
- **Accept when:** The dummy secret is absent from every retained log and errors preserve correlation IDs without claiming a successful request.

### s23-l09 — Add Human Approval

- **Task:** Require an explicit human confirmation before an educational state-changing tool.
- **Deliverable:** approval_gate.py and declined/approved execution records.
- **Accept when:** Declining results in zero mutation; approval is bound to the exact arguments and cannot authorize a changed request.

### s23-l10 — Understand AutoGen Migration Patterns

- **Task:** Map an existing AutoGen AgentChat example to the Microsoft adapter's supported abstractions.
- **Deliverable:** autogen-migration.md with before/after runnable files.
- **Accept when:** Both versions' real APIs are identified; document semantic differences and test equivalent task behavior rather than renaming imports.

### s23-l11 — Build Reusable Agent Components

- **Task:** Extract catalog tools, output schemas and approval middleware into reusable components.
- **Deliverable:** components/ package and two small consuming agents.
- **Accept when:** Both agents import shared components without copied implementations; version/configuration differences remain explicit.

## Stage 24: Agno and Mastra

### s24-l01 — Introduction to Agno

- **Task:** Map Agno model, agent, team, memory and workflow responsibilities using the supplied adapter.
- **Deliverable:** agno-design-notes.md with an actual single-agent execution path.
- **Accept when:** Identify which capabilities the starter implements and which require new code or external services.

### s24-l02 — Build a Lightweight Agno Agent

- **Task:** Run frameworks/agno_agent.py against a configured model with a harmless catalog query.
- **Deliverable:** agno-first-run.json with model and package version.
- **Accept when:** The response comes from a real Agno/model execution; a dependency import alone is not an agent demonstration.

### s24-l03 — Add Tools and Structured Outputs

- **Task:** Add a synthetic-company tool and a validated response model to the Agno agent.
- **Deliverable:** agno_tools.py with valid and invalid examples.
- **Accept when:** A real tool call supplies evidence to a schema-valid result; invalid data is rejected rather than silently coerced into a claim.

### s24-l04 — Connect Agno to MCP

- **Task:** Connect Agno to the actual educational market MCP server.
- **Deliverable:** agno_mcp.py and tool-discovery transcript.
- **Accept when:** Research and portfolio reads work through MCP; the tool list excludes human approval and execution.

### s24-l05 — Build an Agno Team

- **Task:** Coordinate a research specialist and review specialist as an Agno team.
- **Deliverable:** agno_team.py and both agents' observed contributions.
- **Accept when:** A final answer attributes evidence to each actual contribution, while unavailable tools or failed members remain visible.

### s24-l06 — Introduction to Mastra

- **Task:** Inspect frameworks/mastra/order-agent.ts and map its tools, workflow and model configuration.
- **Deliverable:** mastra-component-map.md with the Node/package versions used.
- **Accept when:** TypeScript schema validation and model orchestration are distinguished; document whether memory and observability are actually enabled.

### s24-l07 — Set Up a TypeScript Agent Project

- **Task:** Install the supplied Mastra project in a clean workspace and configure secrets through environment variables.
- **Deliverable:** setup-log.md with install/typecheck/start commands and a redacted .env.example.
- **Accept when:** The actual TypeScript build succeeds and the running process sees required variable names without printing their secret values.

### s24-l08 — Build Mastra Tools and Workflows

- **Task:** Extend the Mastra example with a typed catalog lookup and review workflow.
- **Deliverable:** catalog-workflow.ts and success/failure run evidence.
- **Accept when:** The real workflow enforces the tool schema and stops or handles invalid tool output at a documented boundary.

### s24-l09 — Connect Mastra to MCP

- **Task:** Attach the educational MCP market server to the Mastra agent.
- **Deliverable:** mcp-client.ts and actual discovery/research record.
- **Accept when:** The TypeScript process communicates with the real MCP server; protocol errors are reported instead of replaced by local fixture calls.

### s24-l10 — Add Memory and Structured Results

- **Task:** Persist a selected course-project preference and return a schema-checked recommendation.
- **Deliverable:** memory-workflow.ts and two-session restart checks.
- **Accept when:** State survives restart only for its intended session, and malformed recommendations fail the configured output contract.

### s24-l11 — Inspect Agents with Mastra Studio

- **Task:** Launch Mastra Studio and inspect a real workflow with a failed tool and a successful retry.
- **Deliverable:** studio-observations.md plus Academy-only screenshots.
- **Accept when:** Actual UI steps identify the tool, arguments, error and later result; do not fabricate a trace from a design diagram.

### s24-l12 — Compare Python and TypeScript Agent Development

- **Task:** Compare equivalent Python and TypeScript read-only research agents built in this stage.
- **Deliverable:** language-choice.md with measured setup/run evidence.
- **Accept when:** Choose based on actual deployment constraints, typing, team skills and ecosystem; mark absent benchmarks and unsupported capabilities.

## Stage 25: Project 7: Agent Application Factory

### s25-l01 — Design the Agent Application Factory

- **Task:** Define the application factory's approved inputs, stage gates and generated artifact contract, starting from projects/07-agent-factory/factory.py.
- **Deliverable:** factory-design.md distinguishing the deterministic foundation from model-driven extensions.
- **Accept when:** The design includes requirements, architecture, generation, review and validation; do not describe the starter's templates as LLM agents.

### s25-l02 — Define the Typed Agent Specification

- **Task:** Validate examples/text_helper.json and add one accepted and three rejected specifications.
- **Deliverable:** spec-validation-tests.py and an annotated AgentSpec schema.
- **Accept when:** Unknown fields, unsafe names and unsupported frameworks fail; new supported features require deliberate schema/adapter changes.

### s25-l03 — Build the Requirements Analysis Agent

- **Task:** Implement a model-backed requirements analysis agent that consumes a validated AgentSpec.
- **Deliverable:** requirements_agent.py and structured requirements for text_helper.
- **Accept when:** A real model execution links each requirement to a specification field and an observable acceptance test; preserve its actual response.

### s25-l04 — Build the Architecture Planning Agent

- **Task:** Implement an architecture planning agent that consumes approved requirements.
- **Deliverable:** architecture_agent.py and a component/dependency plan.
- **Accept when:** The real planner identifies entry points, data boundaries and framework prerequisites without contradicting the approved requirements.

### s25-l05 — Build the Agent Scaffolding Agent

- **Task:** Build a scaffolding agent that proposes a bounded file manifest before any write.
- **Deliverable:** scaffolding_agent.py and proposed/applied manifests.
- **Accept when:** Generation cannot escape the new output directory, overwrite an existing project or silently add unapproved files.

### s25-l06 — Build the Tool Generation Agent

- **Task:** Add a tool generation agent using the allowed word_count and uppercase contracts first.
- **Deliverable:** tool_generation_agent.py, generated tools and contract tests.
- **Accept when:** Generated code passes input/output tests and rejects unsupported shell/network tools; label any integration stub as unimplemented.

### s25-l07 — Build the Prompt and Instruction Generator

- **Task:** Generate instructions from purpose, permitted tools, policies and escalation rules.
- **Deliverable:** instruction_agent.py and generated instructions.md.
- **Accept when:** The actual model output preserves every required policy, does not grant extra tools and contains no embedded credentials.

### s25-l08 — Build the Test Generation Agent

- **Task:** Generate unit, integration and behavior tests from the approved acceptance requirements.
- **Deliverable:** test_generation_agent.py and requirement-to-test mapping.
- **Accept when:** Generated tests run against generated code; include a failing implementation mutant so passing tests are not merely tautological.

### s25-l09 — Build the Code Review Agent

- **Task:** Run an independent code review agent over generated files and requirements.
- **Deliverable:** review_agent.py and issue records with exact file/line references.
- **Accept when:** The reviewer reports actual inspected code; at least one seeded defect is detected and no patch is accepted solely because the author approved it.

### s25-l10 — Add Framework Selection and Adapters

- **Task:** Define adapter interfaces and implement an explicit real-agent framework adapter alongside the existing stdlib adapter.
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

- **Task:** Build the generated application's Dockerfile and execute its tests in an isolated container.
- **Deliverable:** docker-validation.json with image ID, commands and real exit codes.
- **Accept when:** The actual container runs non-root with bounded resources and appropriate network policy; Python isolated mode alone is not a Docker result.

### s25-l14 — Build an Automated Repair Loop

- **Task:** Implement one bounded repair cycle from a saved genuine failing test.
- **Deliverable:** repair_loop.py and before/after diff, test output and attempt counter.
- **Accept when:** Only approved files change, the failing test passes afterward, unrelated tests stay green and the configured repair budget stops further attempts.

### s25-l15 — Launch the Generated Agent

- **Task:** Start the validated generated agent and complete a user-to-model-to-tool interaction.
- **Deliverable:** launch-transcript.json and service startup instructions.
- **Accept when:** The actual generated agent uses its selected framework and validated tools; a deterministic text dispatcher is labeled only the foundation.

### s25-l16 — Complete the Agent Application Factory

- **Task:** Package the full factory evidence, generated application and limitations for an independent reviewer.
- **Deliverable:** factory-portfolio.md linking requirements, plans, code, review, Docker and launch evidence.
- **Accept when:** Every required stage has traceable real execution evidence or an explicit unresolved blocker; no claim that template tests prove model-agent completion.

## Stage 26: MCP Foundations

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
- **Accept when:** The three classes have different invocation/discovery behavior; document that the starter currently supplies tools only.

### s26-l05 — Capability Discovery and Negotiation

- **Task:** Capture initialization and capability negotiation using a real MCP client and server.
- **Deliverable:** initialize-transcript.json with protocol/package versions and negotiated capabilities.
- **Accept when:** Only advertised supported capabilities are claimed; unavailable resources/prompts are not invented.

### s26-l06 — Local vs Remote MCP Servers

- **Task:** Run the stdio market server and design a separately hosted remote MCP version.
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

- **Task:** Implement or use a resource-capable MCP server and read a stable course-document URI.
- **Deliverable:** resource-client.py and resource list/read results.
- **Accept when:** Discovery advertises the resource and read returns the documented MIME type and content; a similarly named tool call is not substituted.

### s27-l06 — Work with MCP Prompts

- **Task:** Implement or use a prompt-capable server exposing a parameterized research template.
- **Deliverable:** prompt-client.py and list/get transcript.
- **Accept when:** The real prompts API validates required arguments and returns reusable messages; local string formatting alone does not prove MCP prompt support.

### s27-l07 — Build a Web-Browsing MCP Agent

- **Task:** Combine genuine fetch and browser MCP servers in a controlled research workflow.
- **Deliverable:** browsing-agent.py and cited navigation/research record.
- **Accept when:** The real agent selects appropriate servers, observes actual pages and avoids submitting forms or accessing personal account data.

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

- **Task:** Implement persistent memories with scoped ownership and search/update semantics.
- **Deliverable:** memory_server.py, temporary SQLite fixture and restart/isolation tests.
- **Accept when:** Memories survive process restart, one owner cannot access another's records and all mutation boundaries are tested.

### s28-l12 — Build a Web Search MCP Server

- **Task:** Wrap a real search provider with normalized query/result schemas and rate/timeout handling.
- **Deliverable:** search_server.py and sanitized actual provider response.
- **Accept when:** Retain original URLs and retrieval time, distinguish provider failure from empty results and never label fixture search as live.

### s28-l13 — Connect an Agentic RAG Service

- **Task:** Expose document ingestion and evidence-grounded retrieval through MCP.
- **Deliverable:** rag_server.py, small Academy corpus and retrieval/evidence tests.
- **Accept when:** Real ingestion creates searchable records and returned passages carry document IDs; the answering agent cites retrieved rather than invented text.

### s28-l14 — Connect Vector Search with Qdrant

- **Task:** Run Qdrant, insert embeddings for the Academy corpus and query through MCP.
- **Deliverable:** qdrant_server.py with collection schema and real insert/search transcript.
- **Accept when:** A real Qdrant service returns stored record IDs; record embedding model/dimension and do not substitute an in-memory list as Qdrant.

### s28-l15 — Build a Market Data MCP Service

- **Task:** Extend the supplied synthetic market server with normalized quote metadata and permission checks.
- **Deliverable:** market-service-tests.py and contract-to-tool mapping.
- **Accept when:** Fixture prices retain synthetic/as-of/evidence labels and invalid symbols fail; live market sourcing is a distinct unclaimed integration.

### s28-l16 — Apply Progressive Tool Discovery

- **Task:** Implement staged tool discovery for research, memory and portfolio specialists.
- **Deliverable:** progressive_discovery.py and before/after tool lists.
- **Accept when:** Only task-relevant capabilities become visible after a documented selection step; permission enforcement persists even when a hidden name is guessed.

## Stage 29: Project 8: MCP-Powered AI Trading Floor

### s29-l01 — Design the MCP Trading Floor

- **Task:** Define the paper-trading learning goals, intended users and non-broker boundaries.
- **Deliverable:** trading-floor-scope.md based on projects/08-mcp-trading-floor.
- **Accept when:** All data is identified as synthetic, execution remains simulated and required multi-agent/MCP/UI work is separated from the deterministic starter.

### s29-l02 — Define the Capstone Architecture

- **Task:** Map agents, MCP services, TradingFloor state, human approval, API and dashboards.
- **Deliverable:** capstone-architecture.md with component ownership and trust boundaries.
- **Accept when:** The map identifies actual starter files versus extensions, persistent DB locations and the separate human approval path.

### s29-l03 — Define the Market Research Agent

- **Task:** Implement a model-backed researcher that consumes company and source evidence through MCP.
- **Deliverable:** research_agent.py and a structured synthetic-company report.
- **Accept when:** A real agent/MCP run produces evidence-linked claims and uncertainty; TradingFloor.research alone is only the deterministic data foundation.

### s29-l04 — Define the Trading Strategy Agent

- **Task:** Implement a strategy agent that consumes a research report and proposes a paper order.
- **Deliverable:** strategy_agent.py and accepted/rejected structured proposals.
- **Accept when:** A real model output explains quantity/side using evidence, while deterministic validation remains authoritative before further processing.

### s29-l05 — Define the Risk Management Agent

- **Task:** Wrap TradingFloor.risk as the deterministic authority for the risk specialist.
- **Deliverable:** risk_agent.py and boundary-case test table.
- **Accept when:** Insufficient cash, order limit, position limit and unsupported short sale are rejected regardless of the model's recommendation.

### s29-l06 — Define the Portfolio and Paper-Execution Agent

- **Task:** Implement a portfolio/execution specialist that delegates actual mutation only to the approved application path.
- **Deliverable:** execution_agent.py and approval-to-paper-fill trace.
- **Accept when:** No model tool grants itself approval; state changes follow exact proposal approval and request-id idempotency rules.

### s29-l07 — Build the Market Data MCP Integration

- **Task:** Use the genuine market MCP server to obtain research and normalized fixture prices.
- **Deliverable:** market-integration.json with discovery and actual tool results.
- **Accept when:** Symbols, evidence IDs and as-of values match fixtures/market.json and are labeled fictional rather than represented as current market quotes.

### s29-l08 — Build the Research MCP Integration

- **Task:** Add an MCP research service exposing a controlled evidence corpus and optional real search provider.
- **Deliverable:** research_mcp.py and source attribution tests.
- **Accept when:** The agent receives source IDs/URLs and retrieval metadata; unavailable live search is stated explicitly instead of synthesized.

### s29-l09 — Build the Memory MCP Integration

- **Task:** Add scoped persistent analysis/decision memory and reconnect across application sessions.
- **Deliverable:** memory_integration.py and two-session isolation/restart transcript.
- **Accept when:** Prior analysis is recoverable for the correct user, rejected proposals remain auditable and another session's data is inaccessible.

### s29-l10 — Build the Portfolio MCP Service

- **Task:** Expose read-only portfolio/valuation and controlled paper-order operations through explicit service contracts.
- **Deliverable:** portfolio_service.py and cash/positions/order tests.
- **Accept when:** Approval and execution remain outside model-visible starter MCP tools; unauthorized or duplicate mutation fails or returns the exact prior result.

### s29-l11 — Use the Researcher-as-a-Tool Pattern

- **Task:** Expose the researcher as a callable specialist used by strategy rather than duplicating its logic.
- **Deliverable:** researcher_tool.py and a strategy-to-research handoff trace.
- **Accept when:** The actual requesting agent receives a validated research artifact with evidence IDs; trace attribution identifies the specialist call.

### s29-l12 — Pass Structured Information Between Agents

- **Task:** Validate typed handoffs for research, strategy, risk and execution outcomes.
- **Deliverable:** handoff_schemas.py with valid/invalid examples for each boundary.
- **Accept when:** A malformed report or mismatched proposal digest stops the workflow before approval or execution.

### s29-l13 — Apply Risk and Portfolio Rules

- **Task:** Test portfolio limits at, below and above each configured boundary.
- **Deliverable:** risk_boundary_tests.py referencing TradingFloor.risk.
- **Accept when:** Assertions verify exact cash/order/concentration/short-sale behavior and no rejected transaction changes stored state.

### s29-l14 — Execute Controlled Paper Trades

- **Task:** Approve one exact proposal through approve_order.py and execute it with a stable request ID.
- **Deliverable:** paper-trade-receipt.json with before/after state and trace.
- **Accept when:** The real paper fill occurs once; replay returns the same receipt and a changed order with the same key is rejected.

### s29-l15 — Orchestrate the Complete Trading Floor

- **Task:** Run the full model-driven research→strategy→deterministic-risk→human-approval→paper-execution workflow.
- **Deliverable:** orchestrator.py and complete actual trace.
- **Accept when:** Each required agent/MCP boundary is exercised, human approval is real and refusal/error paths do not mutate the account.

### s29-l16 — Build the Gradio Trading Dashboard

- **Task:** Launch gradio_app.py, inspect available views and extend the UI to expose missing required capstone states.
- **Deliverable:** gradio-observations.md and implemented dashboard changes.
- **Accept when:** Actual browser output shows research, proposals, approval state, positions and agent activity; do not claim the starter already implements every view.

## Stage 30: Evaluation, Deployment and Course Completion

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

- **Task:** Add a feedback form bound to run/proposal IDs and record real reviewer comments.
- **Deliverable:** feedback_schema.py and one actual reviewer submission.
- **Accept when:** Feedback attribution and timestamps are preserved; generated sample feedback is labeled fixture and not claimed as human approval.

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

- **Task:** Launch api.py and exercise /state, /proposals and /execute with valid and invalid token/input cases.
- **Deliverable:** api-tests.py and actual HTTP status/body records.
- **Accept when:** Unauthenticated mutations fail, input schemas validate and execution still requires separate exact human approval; document read-only /state exposure.

### s30-l11 — Build the React Front End

- **Task:** Install and run frontend/ against the real FastAPI service, then add missing capstone views.
- **Deliverable:** frontend-observations.md and React changes for required workflow states.
- **Accept when:** Actual browser requests display real API data and errors; the starter's proposal/state buttons are not claimed as a complete approval/execution UI.

### s30-l12 — Package the Application with Docker

- **Task:** Build the provided Dockerfile, add required service wiring and test persistent paper state.
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
