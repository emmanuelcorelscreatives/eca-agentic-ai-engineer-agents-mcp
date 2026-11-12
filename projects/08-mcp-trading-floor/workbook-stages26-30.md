# MCP and trading-floor practical workbook

Each section retains the PDF objective. Files below are real reusable implementation components; a path mapping is not proof that every acceptance criterion has passed. Named-application and model-dependent gaps remain explicit.

## s26-l01 — Welcome to Model Context Protocol

**Objective:** Introduce MCP and explain how it standardizes connections between AI applications, tools and data services.

**Implementation:** `projects/08-mcp-trading-floor/architecture.md`

**Exercise:**
- Draw the architecture boundary and identify which component owns the model.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- The role map distinguishes protocol integration from model execution and application policy.

## s26-l02 — What Is MCP?

**Objective:** Explain the problems MCP addresses and the benefits of reusable, discoverable integrations.

**Implementation:** `projects/08-mcp-trading-floor/architecture.md`

**Exercise:**
- Classify which repeated adapter responsibilities MCP standardizes and which remain application specific.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- The comparison correctly separates structured invocation, discovery and transport from authorization.

## s26-l03 — MCP Hosts, Clients and Servers

**Objective:** Define each architectural role and follow a request from an agent to an MCP capability.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Annotate a captured initialization, discovery and invocation trace with owner roles and matching request IDs.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- A real SDK-backed local session supplies the trace; tests validate IDs, role boundaries and one invocation.

## s26-l04 — Tools, Resources and Prompts

**Objective:** Differentiate executable actions, readable context and reusable prompt templates.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Classify three needs, discover the matching capabilities, and call or retrieve them.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Tests exercise actual tool validation/output, exact resource bytes and prompt arguments; retrieving a prompt is distinguished from executing it.

## s26-l05 — Capability Discovery and Negotiation

**Objective:** Explain how participants advertise and agree on the capabilities available during a connection.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Inspect both initialization messages and explain an unavailable feature and a supported feature.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Real SDK integration tests cover initialization and unavailable-feature handling; document the actual negotiated version rather than an unverified latest version. Capability support is not user permission.

## s26-l06 — Local vs Remote MCP Servers

**Objective:** Compare local process integrations with network-accessible services and their operational implications.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Choose a deployment for three scenarios and compare configuration, lifecycle, trust boundary and failure handling.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Both real SDK-backed variants return the same fixture record; test clean shutdown and unavailable endpoint. Public hosting and its authorization are not implied by a loopback demo.

## s26-l07 — MCP Connection and Transport Models

**Objective:** Introduce the supported communication patterns and how clients establish and maintain sessions.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Trace initialization, request, error and shutdown behavior on both transports.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Real SDK tests cover ordered lifecycle, disconnect, timeout and structured errors. Verify supported transport and session rules in official documentation during implementation; historical transports are clearly marked and HTTP is not falsely described as always requiring a persistent session.

## s26-l08 — Working with Node-Based MCP Servers

**Objective:** Install and run an existing Node-based server and inspect its exposed capabilities.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/node-filesystem/package.json`, `projects/08-mcp-trading-floor/mcp_lab/client_policy.py`

**Exercise:**
- Recreate installation, launch the existing server and inspect its capabilities without touching personal files.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Clean-environment tests launch the actual third-party server, retrieve exact fixture bytes through a real client, and reject out-of-root/traversal access. Record actual Node/package versions and commands. An Academy-written replacement does not satisfy this lesson.

**Outstanding evidence:**
- Actual official Node filesystem-server integration test pending exact installed runtime receipt.

## s26-l09 — Inspect MCP Server Capabilities

**Objective:** Use inspection tools to review available tools, schemas, resources and prompts before integration.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/README.md`

**Exercise:**
- Inspect discovery, submit valid and invalid lookup arguments and explain why listed capability does not imply permission.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Capture actual Inspector attached to the tested server and compare discovery with the client. The filesystem server may lack resources/prompts; demonstrate those categories with the Academy teaching server rather than inventing support.

**Outstanding evidence:**
- Interactive MCP Inspector session not captured; client protocol tests do not substitute for Inspector.

## s26-l10 — Understand the Agent Harness and MCP Relationship

**Objective:** Explain how an agent runtime decides when and how to invoke capabilities supplied through MCP.

**Implementation:** `projects/08-mcp-trading-floor/architecture.md`, `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Compare the protocol trace with the harness decision trace and locate action choice, validation and denial/error handling.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Deterministic tests use a clearly labeled model stub for control flow and deny/malformed/error cases. A separate finite authorized real-model run must precede the filmed demonstration and retain actual request, selected tool and response; never present a stub as a real model result.

## s27-l01 — Connect to a Filesystem MCP Server

**Objective:** Give an agent restricted access to approved files and directories through an MCP client.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/client_policy.py`

**Exercise:**
- Add a second approved subdirectory without widening access to the fixture parent.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/01-restricted-filesystem/tests/test_restricted_filesystem.py: Approved read returns exact fixture bytes; relative traversal, absolute outside paths and symlink escape fail without disclosing outside bytes.
- projects/08-mcp-trading-floor/stage27/01-restricted-filesystem/tests/test_restricted_filesystem.py: Record the real selected server launch command, allowed-root arguments and tool discovery; test platform-specific path behavior in the actual execution environment.

## s27-l02 — Connect to a Web Fetch MCP Server

**Objective:** Retrieve web content through a standardized MCP tool and return structured results.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`, `projects/08-mcp-trading-floor/retrieval_lab/server.py`

**Exercise:**
- Extract the fixture product name and policy excerpt; preserve source provenance and handle a missing page.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/02-structured-fetch/tests/test_structured_fetch.py: Actual server retrieves the owned fixture page; exact expected excerpt is present and records validate against schema.
- projects/08-mcp-trading-floor/stage27/02-structured-fetch/tests/test_structured_fetch.py: 404, denied destinations and invalid response shapes return explicit failures rather than invented content; external network policy is enforced by the application or sandbox when the server lacks it.

**Outstanding evidence:**
- Controlled owned HTTP fetch tested; existing third-party fetch-server integration remains separate.

## s27-l03 — Connect to a Playwright MCP Server

**Objective:** Make browser navigation and extraction capabilities available to an agent through MCP.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/mcp_adapter.py`

**Exercise:**
- Read the dynamically rendered article heading and visible table; leave the demonstration form unsubmitted.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/03-playwright-session/tests/test_playwright_session.py: Actual browser tool discovery and render/extraction succeeds against the owned local site; raw tool output matches the visible page.
- projects/08-mcp-trading-floor/stage27/03-playwright-session/tests/test_playwright_session.py: Browser is isolated from personal profiles, remote navigation is restricted, submit actions are unavailable, and all owned processes close at teardown.

**Outstanding evidence:**
- Playwright MCP named existing-server browser run not yet executed.

## s27-l04 — Call MCP Tools from an AI Agent

**Objective:** Discover tools, supply validated arguments and return tool results to the agent loop.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/mcp_adapter.py`

**Exercise:**
- Route a file-read request and a fetch request to their intended servers; reject an unknown tool and malformed arguments.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/04-agent-tool-dispatch/tests/test_agent_tool_dispatch.py: Discovered argument schemas are validated before invoking a real server; invalid arguments make zero tool dispatches.
- projects/08-mcp-trading-floor/stage27/04-agent-tool-dispatch/tests/test_agent_tool_dispatch.py: Namespaced duplicate tool names cannot collide; agent iteration/tool budgets stop loops, and observed tool results are returned without becoming trusted instructions.

**Outstanding evidence:**
- Real bounded model/agent tool-loop run not performed; no paid provider call authorized in this task.

## s27-l05 — Read MCP Resources

**Objective:** Access server-provided documents and data without treating every operation as an executable tool.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Select the provided course guide by discovered identifier and include a cited excerpt in a research note.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/05-resource-reader/tests/test_resource_reader.py: List/read resources through the actual MCP client APIs on a capable server, and compare returned bytes with the fixture.
- projects/08-mcp-trading-floor/stage27/05-resource-reader/tests/test_resource_reader.py: Unknown identifiers, unsupported capabilities and non-text resource payloads are handled explicitly; reading a resource never silently invokes a mutation tool.

## s27-l06 — Work with MCP Prompts

**Objective:** Discover and use reusable prompt templates supplied by an MCP server.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Retrieve a research-brief template with a topic argument and inspect the returned messages before invoking an agent.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/06-prompt-loader/tests/test_prompt_loader.py: The chosen real server advertises prompts; list/get calls return observed messages and expected supplied arguments.
- projects/08-mcp-trading-floor/stage27/06-prompt-loader/tests/test_prompt_loader.py: Missing arguments and unknown prompt names produce clear errors; template content cannot override application tool permissions or approval rules.

## s27-l07 — Build a Web-Browsing MCP Agent

**Objective:** Combine fetch and browser servers into a controlled research and navigation workflow.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/mcp_adapter.py`

**Exercise:**
- Compare two fictional course products using cited page excerpts, using rendered extraction only where needed.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/07-controlled-browser-agent/tests/test_controlled_browser_agent.py: Two owned fixture pages yield schema-valid records with citations resolved to actual content, not guessed facts.
- projects/08-mcp-trading-floor/stage27/07-controlled-browser-agent/tests/test_controlled_browser_agent.py: A controlled genuine model integration demonstrates observed server selection; deterministic dispatch tests remain explicitly separate from model behavior.
- projects/08-mcp-trading-floor/stage27/07-controlled-browser-agent/tests/test_controlled_browser_agent.py: Tool and time budgets are enforced; page prompt injection cannot enable denied tools, submit forms, or expand network destinations.

**Outstanding evidence:**
- Real model-driven browsing run not performed; browser adapter alone is not evidence.

## s27-l08 — Trace MCP Tool Calls

**Objective:** Record server selection, arguments, responses, latency, failures and agent decisions.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/observability.py`, `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Follow one research request across two servers and reconstruct its ordering from correlation IDs.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/08-trace-events/tests/test_trace_events.py: Actual MCP tool calls emit a validated start/end trace with correlation IDs, server/tool identifiers, measured latency and terminal status.
- projects/08-mcp-trading-floor/stage27/08-trace-events/tests/test_trace_events.py: Concurrent requests remain distinguishable; failure events retain error classifications and redacted argument/result summaries without exposing secret fixture values.

## s27-l09 — Handle Tool Failures and Invalid Results

**Objective:** Recover from unavailable servers, invalid arguments, timeouts and malformed responses.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`, `projects/08-mcp-trading-floor/evaluation_lab/recovery.py`

**Exercise:**
- Repair a malformed result adapter and configure a finite retry policy for a documented safe read.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/09-failure-recovery/tests/test_failure_recovery.py: Stopped server, invalid schema, timeout and malformed payload cases each terminate predictably with trace evidence.
- projects/08-mcp-trading-floor/stage27/09-failure-recovery/tests/test_failure_recovery.py: Invalid arguments are not retried unchanged; retries have deadlines/backoff limits, and timeout on a possible side effect remains uncertain rather than blindly replayed.
- projects/08-mcp-trading-floor/stage27/09-failure-recovery/tests/test_failure_recovery.py: Exercise uses genuine server failure for at least one case; explicitly labeled test servers cover otherwise hard-to-trigger malformed responses.

## s27-l10 — Filter and Organize MCP Tools

**Objective:** Present only relevant capabilities to an agent and group tools by task or permission level.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`, `projects/08-mcp-trading-floor/mcp_lab/client_policy.py`

**Exercise:**
- Give the researcher read-only file/fetch tools and remove browser form actions from its view.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/10-tool-filtering/tests/test_tool_filtering.py: Each task sees exactly its authorized tools; equivalent calls against a hidden tool are also rejected by the dispatcher.
- projects/08-mcp-trading-floor/stage27/10-tool-filtering/tests/test_tool_filtering.py: Unknown new tools default to unavailable; duplicate tool names remain server-qualified and logged.

## s27-l11 — Apply Least-Privilege Tool Access

**Objective:** Restrict each agent to the minimum tools, data and actions required for its role.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/client_policy.py`, `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Add a reviewer role that can read a final report but cannot access drafts or write files.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/11-least-privilege/tests/test_least_privilege.py: Role/action/path matrix passes allow and deny cases through the real dispatcher and relevant actual server.
- projects/08-mcp-trading-floor/stage27/11-least-privilege/tests/test_least_privilege.py: Traversal, symlink escape, unauthorized destinations and direct hidden-tool dispatch remain denied; each policy denial is auditable and does not disclose denied data.

## s27-l12 — Secure Secrets and Sensitive Data

**Objective:** Keep credentials outside prompts, logs, generated files and untrusted server content.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/observability.py`, `projects/08-mcp-trading-floor/mcp_lab/README.md`

**Exercise:**
- Locate and remove an intentionally unsafe fake-token log path; verify the replacement retains useful diagnostic context.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/12-secret-hygiene/tests/test_secret_hygiene.py: Fake secret canaries appear only in approved runtime input, never prompts, traces, report artifacts, screenshots or checked-in files.
- projects/08-mcp-trading-floor/stage27/12-secret-hygiene/tests/test_secret_hygiene.py: Redaction handles nested argument/result fields and common error paths; untrusted server content cannot request or retrieve runtime credentials.
- projects/08-mcp-trading-floor/stage27/12-secret-hygiene/tests/test_secret_hygiene.py: Environment examples contain placeholders only; actual integration credentials, when required, are not stored or captured.

## s27-l13 — Add Human Approval to MCP Tools

**Objective:** Require confirmation before high-impact MCP operations are executed.

**Implementation:** `projects/08-mcp-trading-floor/approve_order.py`, `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Inspect a report-write proposal, deny it once, then explicitly approve the exact sandbox destination and content digest.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage27/13-approval-gate/tests/test_approval_gate.py: Denied, missing, expired and mismatched approval cause zero mutation dispatches; matching approval permits exactly the intended sandbox write.
- projects/08-mcp-trading-floor/stage27/13-approval-gate/tests/test_approval_gate.py: Changed path, arguments or content digest invalidates prior approval; a model-generated approval string is rejected.
- projects/08-mcp-trading-floor/stage27/13-approval-gate/tests/test_approval_gate.py: Actual approved write is verified on the filesystem; timeout/unknown mutation outcome is retained and not silently replayed.

## s28-l01 — When to Build a Custom MCP Server

**Objective:** Decide whether a capability belongs in MCP, a native application function or a conventional API.

**Implementation:** `projects/08-mcp-trading-floor/architecture.md`

**Exercise:**
- Classify memory lookup, application formatting and partner HTTP access; justify each choice against the actual consumers.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Reject a decision matrix with missing consumer, permissions or operational owner; verify examples exercise all three placements.

## s28-l02 — Design an MCP Server Contract

**Objective:** Define capability names, schemas, outputs, errors, permissions and operational boundaries before implementation.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Design a bounded memory.search tool and a read-only document resource; reject unconstrained query sizes and ambiguous errors.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Validate example requests and responses against schemas; detect duplicate names, missing bounds, undocumented errors and write permissions assigned to read-only roles.

## s28-l03 — Introduction to FastMCP

**Objective:** Introduce the Python development model for creating servers, clients and reusable capabilities.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Identify where a Python function becomes a discovered MCP capability and explain transport versus application logic.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Import the pinned real package; verify a real minimal server exposes the expected capability through its supported client API. Mock-only success does not satisfy this check.

## s28-l04 — Build Your First FastMCP Server

**Objective:** Create and run a minimal server and verify that a client can connect to it.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Start the server, discover its capabilities and invoke a known catalogue lookup from a separate real session.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Exercise actual session initialization, list_tools and a successful tool call; verify clean shutdown and unknown-item behavior.

## s28-l05 — Create Typed MCP Tools

**Objective:** Expose Python functions as documented tools with validated parameters and results.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Add a typed catalogue price lookup and demonstrate rejected malformed IDs and out-of-range result limits.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Use a real MCP session to verify discovered input schemas, accepted inputs, invalid-type rejection and documented structured outputs without relying on a framework-specific error shape until inspected.

## s28-l06 — Add MCP Resources

**Objective:** Publish readable data and documents through stable resource identifiers.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Discover resources and read one exact document and one parameterized catalogue resource.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Verify actual list/read operations and stable URI mapping; reject traversal, nonexistent records and unintended files outside the course data directory.

## s28-l07 — Add Reusable MCP Prompts

**Objective:** Provide parameterized prompt templates that clients can discover and reuse.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Discover and render a prompt with supplied arguments, then explain why rendering a prompt is not equivalent to executing its instructions.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Verify real prompt discovery and retrieval, required-argument errors, deterministic fixture rendering and preservation of quoted untrusted content.

## s28-l08 — Run and Inspect the Server

**Objective:** Launch the server and examine its capabilities, schemas and responses with an inspector.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/README.md`

**Exercise:**
- Inspect the same contract implemented in earlier lessons and compare observed schemas with the saved specification.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Record actual Inspector and server versions, connection transcript and screenshots; verify one discovery/read/prompt/tool success and one invalid request. Do not substitute a drawn inspector UI.

## s28-l09 — Connect the Server to an AI Agent

**Objective:** Configure a client session and make the custom capabilities available to an agent.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/mcp_adapter.py`

**Exercise:**
- Have the agent discover and invoke the catalogue tool, and produce an answer traceable to the returned record.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Run a bounded genuine agent/provider integration when configured; assert tool trace and returned record attribution. Offline adapters test dispatch but are labeled and cannot stand in for observed agent behavior.

**Outstanding evidence:**
- Live agent/model integration not executed.

## s28-l10 — Test MCP Tools and Error Handling

**Objective:** Verify valid calls, invalid inputs, permission errors, timeouts and server failures.

**Implementation:** `projects/08-mcp-trading-floor/mcp_lab/server.py`

**Exercise:**
- Introduce a controlled delayed operation and unauthorized write; show bounded failure and successful later reconnection.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Assert actual invalid input handling, no write on denial, configured timeout termination, controlled server crash behavior and subsequent clean new session. No flaky reliance on wall-clock sleeps alone.

## s28-l11 — Build a Long-Term Memory MCP Server

**Objective:** Store, retrieve, update and search persistent memories through controlled operations.

**Implementation:** `projects/08-mcp-trading-floor/services.py`, `projects/08-mcp-trading-floor/mcp_server.py`

**Exercise:**
- Store a fictional learner preference, restart the server, retrieve it, update it and search within the same tenant scope.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Verify persistence across actual process restart, deterministic seed setup, cross-tenant read/write denial, validation, versioned update conflict and bounded search results.

## s28-l12 — Build a Web Search MCP Server

**Objective:** Wrap a search provider behind normalized queries, results, limits and error handling.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`, `projects/08-mcp-trading-floor/retrieval_lab/server.py`

**Exercise:**
- Compare explicitly labeled recorded fixture results with a bounded live provider query, recording result URLs, timestamps and provenance.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Offline tests cover schema normalization, empty results, quota and timeout errors; a separately bounded genuine provider run verifies actual response and provenance. Missing credentials must be reported as skipped, not replaced by invented live results.

**Outstanding evidence:**
- Actual public search endpoint not called; owned response fixture is labeled.

## s28-l13 — Connect an Agentic RAG Service

**Objective:** Expose document ingestion and retrieval capabilities for evidence-grounded agent responses.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`, `projects/08-mcp-trading-floor/services.py`

**Exercise:**
- Ingest both supplied documents and retrieve evidence for a question; display exact supporting source passages and an explicit insufficient-evidence path.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Verify duplicate ingestion policy, source/chunk linkage, tenant isolation, bounded retrieval and actual agent answer trace. Unsupported answers are not accepted as grounded merely because they contain a citation.

**Outstanding evidence:**
- Model-backed answer generation not run; extractive grounding remains explicit baseline.

## s28-l14 — Connect Vector Search with Qdrant

**Objective:** Store embeddings and return relevant records through an MCP retrieval capability.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`

**Exercise:**
- Index the same course documents, inspect stored payload provenance and retrieve relevant chunks through the MCP tool.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Start real Qdrant; verify collection dimensions, upsert/read/search and restart persistence, deleted-record behavior and invalid-vector rejection. Record actual embedding model identity and compare relevance against a small human-authored expected-document set, without inventing scores.

**Outstanding evidence:**
- Actual local Qdrant uses deterministic teaching encoder; pretrained semantic-embedding comparison not executed.

## s28-l15 — Build a Market Data MCP Service

**Objective:** Provide normalized educational market data through typed and permission-aware tools.

**Implementation:** `projects/08-mcp-trading-floor/mcp_server.py`, `projects/08-mcp-trading-floor/fixtures/market.json`

**Exercise:**
- Query clearly labeled synthetic quotes, inspect their source and age, and optionally compare one bounded configured provider observation.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Assert decimal precision, currency/unit normalization, timestamp timezone, stale-data flag, unknown symbols and denied writes. Synthetic rows never appear as live prices; a live adapter needs an actual retained response before any narrated current-price claim.

## s28-l16 — Apply Progressive Tool Discovery

**Objective:** Reduce tool overload by revealing specialist capabilities only when the current task requires them.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/core.py`

**Exercise:**
- Run the same educational task with the full catalogue and progressive discovery; record exposed tool names and actual invocation traces.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Assert initial specialist tools are withheld, the selected capability becomes discoverable, authorization cannot be bypassed and unknown routes fail clearly. Measure real exposed-tool count; claim quality, latency or cost improvement only if an actual controlled comparison supports it.

## s29-l01 — Design the MCP Trading Floor

**Objective:** Define the educational paper-trading scope, users, workflows, controls and final application experience.

**Implementation:** `projects/08-mcp-trading-floor/architecture.md`

**Exercise:**
- Complete the scope worksheet and classify actions as read-only, proposal, approval or simulated execution.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-01/tests/test_lesson_01.py: Missing simulation label and live brokerage capabilities fail validation; scope includes explicit users, reset and approval controls.

## s29-l02 — Define the Capstone Architecture

**Objective:** Map agents, application services, MCP servers, state, approvals, evaluations and interface components.

**Implementation:** `projects/08-mcp-trading-floor/architecture.md`

**Exercise:**
- Trace one proposal from evidence through manual approval into the paper ledger and identify trust boundaries.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-02/tests/test_lesson_02.py: Every component reference resolves; execution depends on independent manual approval; agents cannot grant themselves execution authority.

## s29-l03 — Define the Market Research Agent

**Objective:** Create an agent that gathers and structures company, industry and market evidence.

**Implementation:** `projects/08-mcp-trading-floor/services.py`, `projects/08-mcp-trading-floor/fixtures/market.json`

**Exercise:**
- Implement structured evidence extraction and expose unavailable and stale evidence explicitly.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-03/tests/test_lesson_03.py: Claims reference known sources and timestamps; invented evidence identifiers fail; stale facts stay visibly marked.

**Outstanding evidence:**
- Real role implementation is deterministic reference; genuine model-agent orchestration acceptance remains unexecuted.

## s29-l04 — Define the Trading Strategy Agent

**Objective:** Create an agent that converts research into a transparent simulated trading proposal.

**Implementation:** `projects/08-mcp-trading-floor/trading_floor.py`, `projects/08-mcp-trading-floor/services.py`

**Exercise:**
- Implement a no-trade result when evidence is insufficient and keep deterministic policy outside model text.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-04/tests/test_lesson_04.py: Validate symbol, side, quantity, rationale and evidence IDs; reject unknown symbols and proposals without evidence.

**Outstanding evidence:**
- Real role implementation is deterministic reference; genuine model-agent orchestration acceptance remains unexecuted.

## s29-l05 — Define the Risk Management Agent

**Objective:** Create an agent that applies position limits, portfolio rules and deterministic risk checks.

**Implementation:** `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Add position, concentration and freshness checks with reviewable violation messages.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-05/tests/test_lesson_05.py: Boundary, over-limit, missing-price and insufficient-cash cases reject correctly; model explanations cannot override deterministic rejection.

## s29-l06 — Define the Portfolio and Paper-Execution Agent

**Objective:** Create an agent that maintains simulated account state and executes approved paper trades.

**Implementation:** `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Implement idempotent paper submission and account reset without brokerage credentials or routes.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-06/tests/test_lesson_06.py: Duplicate idempotency keys have one ledger effect; mismatched approvals and stale account revisions cannot change holdings or cash.

## s29-l07 — Build the Market Data MCP Integration

**Objective:** Connect normalized prices, company data and market information to the research workflow.

**Implementation:** `projects/08-mcp-trading-floor/mcp_server.py`, `projects/08-mcp-trading-floor/fixtures/market.json`

**Exercise:**
- Create clearly labelled fictional company records and fixed-time synthetic quotes; invoke actual MCP price and company tools.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-07/tests/test_lesson_07.py: Actual handshake, list-tools and call-tool succeed; unknown symbol, stale quote and malformed input return controlled errors with provenance.

## s29-l08 — Build the Research MCP Integration

**Objective:** Provide search and evidence-collection capabilities through a controlled service interface.

**Implementation:** `projects/08-mcp-trading-floor/retrieval_lab/server.py`, `projects/08-mcp-trading-floor/retrieval_lab/core.py`

**Exercise:**
- Implement source-ID lookup, domain permission rules and bounded results with preserved citations.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-08/tests/test_lesson_08.py: Real MCP calls return source IDs and retrieval times; denied sources and oversized queries fail; document instructions cannot change tool permissions.

## s29-l09 — Build the Memory MCP Integration

**Objective:** Preserve prior analyses, decisions, feedback and portfolio context across sessions.

**Implementation:** `projects/08-mcp-trading-floor/services.py`, `projects/08-mcp-trading-floor/mcp_server.py`

**Exercise:**
- Implement write, retrieve and reset tools with per-account isolation and actual session restart retrieval.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-09/tests/test_lesson_09.py: Data survives a fresh session; cross-account access fails; resetting one account leaves another untouched; old quotes never become current prices.

## s29-l10 — Build the Portfolio MCP Service

**Objective:** Implement tools for simulated cash, positions, orders, transactions and portfolio valuation.

**Implementation:** `projects/08-mcp-trading-floor/mcp_server.py`, `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Use Decimal or integer minor units and atomic writes; value holdings with explicit quote timestamps.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-10/tests/test_lesson_10.py: Atomic commit preserves cash and holding invariants; duplicate orders, rounding, overselling and unavailable valuation prices have tested outcomes.

## s29-l11 — Use the Researcher-as-a-Tool Pattern

**Objective:** Allow other agents to request structured research without duplicating research responsibilities.

**Implementation:** `projects/08-mcp-trading-floor/services.py`

**Exercise:**
- Validate a research request and run an actual agent-to-researcher invocation without duplicated research roles.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-11/tests/test_lesson_11.py: Return the common research schema; recursion and exhausted call budgets fail safely; freshness-bound cache cannot hide changed evidence.

**Outstanding evidence:**
- Real role implementation is deterministic reference; genuine model-agent orchestration acceptance remains unexecuted.

## s29-l12 — Pass Structured Information Between Agents

**Objective:** Define reliable contracts for research, proposals, risk decisions and execution results.

**Implementation:** `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Replace free-text handoffs with typed contracts and inspect actual validation failures.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-12/tests/test_lesson_12.py: Valid envelopes round-trip; invalid enum, missing ID, changed proposal revision and forged evidence reference stop downstream execution.

## s29-l13 — Apply Risk and Portfolio Rules

**Objective:** Enforce deterministic checks before any proposed simulated transaction can continue.

**Implementation:** `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Add table-driven cash, concentration, quote-age and portfolio-revision checks and demonstrate state changes invalidating a proposal.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-13/tests/test_lesson_13.py: Boundary cases behave as specified; stale state and quotes reject; every rejected transaction leaves the ledger unchanged.

## s29-l14 — Execute Controlled Paper Trades

**Objective:** Validate, approve and record simulated orders without connecting the project to live brokerage execution.

**Implementation:** `projects/08-mcp-trading-floor/approve_order.py`, `projects/08-mcp-trading-floor/trading_floor.py`

**Exercise:**
- Approve one exact proposal, reject another and demonstrate expiry, duplicate submission and audit history through actual local runs.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-14/tests/test_lesson_14.py: Approval binds account, proposal hash, reviewer action and expiry; replay/mismatch fails; successful execution records one transaction.

## s29-l15 — Orchestrate the Complete Trading Floor

**Objective:** Coordinate research, strategy, risk and execution agents through the full capstone workflow.

**Implementation:** `projects/08-mcp-trading-floor/services.py`, `projects/08-mcp-trading-floor/evaluation_lab/workflow.py`

**Exercise:**
- Run approved trade, insufficient-evidence hold, risk rejection and interrupted-session resume scenarios.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-15/tests/test_lesson_15.py: Legal transitions and budgets are enforced; no automatic approval; resume has exactly-once ledger effects; only actual run traces support observed results.

**Outstanding evidence:**
- Real role implementation is deterministic reference; genuine model-agent orchestration acceptance remains unexecuted.

## s29-l16 — Build the Gradio Trading Dashboard

**Objective:** Display research, proposals, approvals, simulated positions, activity and agent status.

**Implementation:** `projects/08-mcp-trading-floor/gradio_app.py`

**Exercise:**
- Inspect real interface states, approve a paper order and compare displayed balances with the authoritative ledger.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- projects/08-mcp-trading-floor/stage29/lesson-16/tests/test_lesson_16.py: Actual Gradio browser smoke covers initial, research, rejected, awaiting-approval, executed and error states; changed proposals revoke stale approval; no live brokerage controls or secrets appear.

## s30-l01 — Add Tracing and Observability to the Trading Floor

**Objective:** Record model calls, agent transitions, MCP activity, approvals, errors and execution timing.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/observability.py`, `projects/08-mcp-trading-floor/evaluation_lab/workflow.py`

**Exercise:**
- Add one trace event around the risk tool and follow its parent span without logging credentials or private prompt data.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- A complete real local run has an unbroken parent-child trace from research to approved paper-order ledger; rejected and failed runs retain their outcome.
- Secret sentinel values are absent from exported events; event times and durations are nonnegative and documented.

## s30-l02 — Build Capstone Evaluation Datasets

**Objective:** Create representative market scenarios, expected constraints and repeatable test cases.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/dataset.py`, `projects/08-mcp-trading-floor/evaluation_lab/scenarios.json`

**Exercise:**
- Add normal, stale-data, over-limit and conflicting-evidence scenarios and explain each expected invariant.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Every case validates against the schema and references a real fixture ID; dataset manifest hashes every fixture.
- Split development and held-out cases by scenario family; no case asserts an invented model response or future investment return.

## s30-l03 — Evaluate Research and Trading Decisions

**Objective:** Measure evidence quality, decision consistency, rule compliance and explanation clarity.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/dataset.py`, `projects/08-mcp-trading-floor/evaluation_lab/quality.py`

**Exercise:**
- Compare actual two-run decisions for one unchanged scenario and record supported differences rather than claiming determinism for a model.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Metric calculations pass hand-computed fixture tests and report denominator, failures and unavailable values.
- Every reported observed metric resolves to retained actual run artifacts and dataset revision; identical seeded fixture logic is reproducible.

## s30-l04 — Add Deterministic Risk Checks

**Objective:** Test portfolio limits and execution constraints with ordinary software assertions.

**Implementation:** `projects/08-mcp-trading-floor/trading_floor.py`, `projects/08-mcp-trading-floor/evaluate.py`

**Exercise:**
- Write tests immediately below, at and above an allocation limit, then prove a rejected order never reaches the simulated ledger.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Reject NaN, negative quantities, missing approvals and overspending using typed validation and explicit currency/decimal rules.
- Boundary and property-based tests establish exposure/cash invariants across paper-trade batches; no live brokerage adapter is configured.

## s30-l05 — Add Model-Based Quality Evaluators

**Objective:** Score qualitative outputs using explicit rubrics and structured evaluator responses.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/quality.py`

**Exercise:**
- Score two labelled illustrative explanations with the same rubric and compare actual judge output against a human assessment.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Schema-invalid responses are counted as evaluator failures, never converted into passes; per-dimension scores cite output evidence.
- Fixtures test judge parsing offline, while any claimed actual judge example requires a separate genuine bounded provider run and retained model/version/input hashes.

**Outstanding evidence:**
- Structured judge implementation exists; genuine authorized model response/rubric evaluation not executed.

## s30-l06 — Collect Human Feedback

**Objective:** Capture reviewer ratings, corrections and comments for later analysis and improvement.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/quality.py`

**Exercise:**
- Submit one genuine reviewer correction in the practice app, then inspect its provenance and compare the two evaluator opinions.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Feedback cannot mutate historical decisions or silently approve paper orders; duplicate submissions use a stable key.
- Ratings validate allowed ranges, comments are escaped in the UI, and exported examples use only Academy practice identities.

## s30-l07 — Test Tool and Agent Failure Scenarios

**Objective:** Simulate unavailable services, malformed data, agent errors and incomplete workflows.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/recovery.py`

**Exercise:**
- Inject an MCP timeout after research and inspect the failed trace, unchanged portfolio and unresolved workflow state.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Each injected fault produces a classified failure with retained trace and no unapproved ledger write.
- Use an owned local MCP test server for unavailable/malformed-response cases; distinguish simulated failure fixtures from actual remote outages.

## s30-l08 — Add Retry and Recovery Strategies

**Objective:** Resume interrupted operations and select appropriate retries, fallbacks or human escalation.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/recovery.py`

**Exercise:**
- Interrupt a workflow after checkpoint persistence and resume it once without duplicating the simulated order.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Retryable reads obey maximum attempts/backoff/deadline; validation failures do not retry.
- An actual process interruption/restart test proves single ledger effect; unknown write outcomes stay unresolved until reconciled, never blindly replayed.

## s30-l09 — Monitor Token Usage, Latency and Cost

**Objective:** Measure resource consumption by model, agent, tool and complete workflow.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/observability.py`

**Exercise:**
- Generate a report from actual local traces and mark missing provider token counts or unpriced models as unknown.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Totals reconcile to leaf call records without double-counting agent/tool containers; cached tokens are separately identified.
- Measured durations use a monotonic clock; fixture arithmetic passes known hand calculations and unknown is never silently treated as free.

## s30-l10 — Build the FastAPI Backend

**Objective:** Expose capstone operations, state and results through validated API endpoints.

**Implementation:** `projects/08-mcp-trading-floor/api.py`

**Exercise:**
- Start the backend and submit one controlled scenario using its real OpenAPI interface; poll the resulting status and inspect validation errors.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Actual in-process integration tests exercise schema validation, missing IDs, state transitions, idempotency and approval requirements.
- API authentication/authorization configuration is explicit; public endpoints do not reveal secrets, and no model request executes merely from viewing status.

## s30-l11 — Build the React Front End

**Objective:** Create a responsive dashboard that communicates with the backend and displays system activity.

**Implementation:** `projects/08-mcp-trading-floor/frontend/src/main.jsx`, `projects/08-mcp-trading-floor/frontend/package.json`, `projects/08-mcp-trading-floor/frontend/vite.config.js`

**Exercise:**
- Launch the app, run a fixture scenario, inspect evidence and give explicit approval before the paper-order update.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Browser tests cover loading, success, failure, disconnected backend, rejected approval and safe rendering of comments.
- A genuine full-stack browser run shows backend state changing after a real practice interaction; synthetic example data remains labelled and no static mock is presented as live integration.

## s30-l12 — Package the Application with Docker

**Objective:** Containerize the services and configure networking, environment variables and persistent storage.

**Implementation:** `projects/08-mcp-trading-floor/Dockerfile`

**Exercise:**
- Build the containers, start the stack on an owned local host and restart it to verify persisted paper-portfolio state.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Actual build and compose health checks succeed using a recorded dependency lock and image revision; missing mandatory configuration fails clearly.
- No secret is baked into an image or committed; persistence survives a documented restart and service-to-service addressing matches the running network.

**Outstanding evidence:**
- Docker image build/persistent container restart not yet executed.

## s30-l13 — Deploy the MCP-Powered Trading Floor

**Objective:** Release the application to a hosting environment and verify the complete deployed workflow.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/deployment/RUNBOOK.md`

**Exercise:**
- Follow the deployment runbook, run an actual research-to-approved-paper-order smoke test and exercise the rollback procedure on the practice service.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Deployment evidence includes actual host/environment, revision, healthy services and one real complete test, with credentials removed.
- A local container run alone is not claimed as hosted deployment; hosting access and cost require an approved environment before recording this lesson.

**Outstanding evidence:**
- Hosting deployment not performed; runbook is not deployed evidence.

## s30-l14 — Inspect Complete Capstone Traces

**Objective:** Follow representative executions from initial research through approval and simulated portfolio updates.

**Implementation:** `projects/08-mcp-trading-floor/evaluation_lab/workflow.py`, `projects/08-mcp-trading-floor/validate_runtime.py`

**Exercise:**
- Annotate one accepted and one rejected real run, linking every conclusion to a trace event or evidence record.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- The walkthrough links to existing immutable run IDs and every excerpt matches retained actual trace bytes.
- Approved paper-order totals reconcile with the before/after ledger; rejected runs show no portfolio mutation.

## s30-l15 — Present the Final Capstone Project

**Objective:** Demonstrate the problem, architecture, workflow, controls, evaluation results and application interface.

**Implementation:** `projects/08-mcp-trading-floor/README.md`, `projects/08-mcp-trading-floor/architecture.md`

**Exercise:**
- Deliver a short demonstration from a fresh checkout and attach a failure example alongside a successful run.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Every advertised feature and metric links to implemented code and actual evidence; setup works from the documented locked environment.
- The presentation explicitly identifies simulated trading, synthetic market data and any provider-dependent limitations; no claims of investment performance are invented.

## s30-l16 — Choosing the Right Agent Framework

**Objective:** Compare frameworks by control, state, ecosystem, interoperability, observability and deployment requirements.

**Implementation:** `projects/08-mcp-trading-floor/portfolio-and-framework-decisions.md`

**Exercise:**
- Choose a framework for two contrasting requirements and justify trade-offs using course projects and pinned official documentation.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Matrix rows include version/date and evidence source; no untested feature is labelled measured or supported by a fabricated benchmark.
- Solution rationale allows multiple defensible choices and ties each choice to concrete state, interoperability and deployment requirements.

**Outstanding evidence:**
- Actual same-fixture framework comparison runs remain to be observed; decision worksheet and criteria are authored.

## s30-l17 — Ten Principles of Effective Agentic AI Engineering

**Objective:** Consolidate the architectural and operational principles that support dependable agent applications.

**Implementation:** `projects/08-mcp-trading-floor/portfolio-and-framework-decisions.md`

**Exercise:**
- Audit the capstone against all ten principles and open a concrete improvement issue for one documented limitation.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Each principle cites an actual repository component and a test or observation where available.
- Checklist failures remain visible; principle summaries do not imply all application risks have been eliminated.

## s30-l18 — Your Agentic AI Engineering Career Roadmap

**Objective:** Translate completed projects into portfolio assets, interview demonstrations, services and product opportunities.

**Implementation:** `projects/08-mcp-trading-floor/portfolio-and-framework-decisions.md`

**Exercise:**
- Prepare a project-specific interview walkthrough and a 30/60/90-day plan using only work the learner actually completed.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Portfolio template separates completed work, proposed work and measured outcomes; it makes no invented customer, employment, certification or revenue claims.
- Example roadmap references all eight real project folders and marks learner-specific links as required inputs rather than nonexistent published URLs.

**Outstanding evidence:**
- Learner portfolio and peer handoff are learner assessments, not observations claimed by this starter.

## s30-l19 — Course Completion and Next Steps

**Objective:** Review the completed journey and provide a path for continued specialization and project development.

**Implementation:** `projects/08-mcp-trading-floor/portfolio-and-framework-decisions.md`

**Exercise:**
- Complete the final checklist, verify repository/resource links and identify one next project without declaring unfinished labs complete.

**Worked approach:** Trace the named implementation above, run its relevant tests, change one input at the taught boundary, and preserve the actual observed result. Use the lab READMEs for executable commands and worked boundary expectations. Do not replace a required named framework/product or model observation with the deterministic baseline.

**Acceptance to demonstrate:**
- Checklist resolves all 362 planned lesson IDs and eight project deliverables, records incomplete items honestly and excludes the separate bonus from the 362-lesson count.
- All published links and setup commands are verified before recording the final lesson; no certificate or assessment result is invented.
