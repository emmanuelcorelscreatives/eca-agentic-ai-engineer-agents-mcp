# Practical workbook — stages 11–20

Run commands from the repository root. Each section is a learner exercise and acceptance contract, not a claim that the exercise has already been implemented or executed. The checked-in deterministic baselines support local validation; CrewAI, LangChain, LangGraph, Playwright MCP, Deep Agents and Gradio lessons retain their real framework requirements. Credentialed provider calls and hosted tracing are optional manual external verification and must retain actual redacted outputs; missing access is recorded as incomplete, never replaced with invented results. New learner extensions belong in a separate workspace and must not overwrite supplied fixtures.

## Stage 11

### s11-l01 — Introduction to CrewAI
- Task: Draw the company-research workflow using actual CrewAI agents, tasks and process boundaries.
- Deliverable and acceptance: Deliver a diagram identifying researcher and reviewer ownership; each task has a named producer and inspectable result.

### s11-l02 — Agents, Tasks, Crews, Processes and Flows
- Task: Map an agent, task, crew, process and flow to one company-screening request.
- Deliverable and acceptance: Deliver an abstraction table distinguishing task dependency from flow routing; include one failure route rather than calling every component an agent.

### s11-l03 — Install CrewAI with uv
- Task: Create a dedicated uv environment and install frameworks/requirements/crewai.txt; record installed versions without printing credentials.
- Deliverable and acceptance: Deliver the resolved package list and successful import of Crew, Agent and Task; do not substitute the offline market runner for this installation.

### s11-l04 — Create Your First CrewAI Project
- Task: Create a CrewAI starter in a new learner workspace; compare its entry point with frameworks/crewai_crew.py.
- Deliverable and acceptance: Deliver the starter tree and the command reaching configuration loading; provider execution is separately marked if credentials are unavailable.

### s11-l05 — Understand CrewAI Project Structure
- Task: Annotate the generated project's configuration, crew module, tool module and CLI entry point.
- Deliverable and acceptance: Deliver a path-to-responsibility map tracing a runtime input from main to a task; no unexplained generated files.

### s11-l06 — Configure Agents and Tasks with YAML
- Task: Write agents.yaml and tasks.yaml for researcher and evidence reviewer, including measurable expected outputs.
- Deliverable and acceptance: Deliver valid YAML with matching agent/task identifiers and no API secrets; the review task explicitly requires evidence for numeric claims.

### s11-l07 — Configure Crews with Python
- Task: Implement the Python crew wrapper using the installed CrewAI API and sequential execution.
- Deliverable and acceptance: Deliver a constructor that resolves both configured agents and tasks; importing the module must not make provider calls.

### s11-l08 — Build a Multi-Agent Debate Crew
- Task: Create advocate, skeptic and adjudicator roles debating whether missing financial evidence permits ranking.
- Deliverable and acceptance: Deliver both positions and an adjudication rubric; any live debate transcript must be a real credentialed run, while a design-only submission is labeled unexecuted.

### s11-l09 — Connect crew.py and main.py
- Task: Pass a company symbol from the CLI into the crew kickoff inputs and task template.
- Deliverable and acceptance: Deliver the entry point plus an input-binding test showing a changed symbol reaches the research task rather than a hard-coded value.

### s11-l10 — Run and Inspect Your First Crew
- Task: Run frameworks.crewai_crew with the explicit live-run consent and configured model, then inspect task progression.
- Deliverable and acceptance: Deliver redacted actual logs and final output, or a precise credential-blocked status; verify the synthetic company margin calculation independently and never invent a crew result.

## Stage 12

### s12-l01 — The Five-Step Method for Building CrewAI Applications
- Task: Apply outcomes → roles → tasks → tools → execution to the fictional market fixture.
- Deliverable and acceptance: Deliver a five-part design with a final report schema, correction limit and one named owner for each artifact.

### s12-l02 — Design Clear Agent Roles and Goals
- Task: Split company research, screening and evidence review into focused responsibilities.
- Deliverable and acceptance: Deliver role contracts showing which agent may collect evidence, calculate scores and reject unsupported claims; no role silently overrides another's result.

### s12-l03 — Create Tasks with Measurable Expected Outputs
- Task: Specify company-profile and review tasks with explicit required fields and coverage rules.
- Deliverable and acceptance: Deliver expected-output contracts that reject a profile without a symbol or evidence and distinguish absent metrics from observed zero.

### s12-l04 — Pass Context Between CrewAI Tasks
- Task: Wire research output into analysis and review using explicit CrewAI task context.
- Deliverable and acceptance: Deliver a dependency graph and an input trace showing the reviewer receives the actual upstream profile, not a rewritten summary without provenance.

### s12-l05 — Add Search and Research Tools
- Task: Design a search adapter that returns source URL, observed time, excerpt and provider failure separately.
- Deliverable and acceptance: Deliver a typed response and tests for empty results and timeout; optional credentialed search retains actual responses and never labels fixture locators as public sources.

### s12-l06 — Build Custom CrewAI Tools
- Task: Wrap the deterministic market screening function as a typed CrewAI BaseTool.
- Deliverable and acceptance: Deliver a tool with bounded arguments, a useful description and a local invocation test; the tool returns calculated values rather than a claimed model opinion.

### s12-l07 — Validate Tool Inputs and Results
- Task: Reject nonfinite thresholds, unknown metrics and malformed evidence before tool execution.
- Deliverable and acceptance: Deliver positive and negative tests, including NaN and a missing evidence locator; validation failure must remain distinguishable from a valid score of zero.

### s12-l08 — Add Structured Outputs with Pydantic
- Task: Define Pydantic company-profile and report models for CrewAI task output.
- Deliverable and acceptance: Deliver schema validation that accepts a supported fictional company and rejects a string score, missing symbol and unsupported extra claim.

### s12-l09 — Understand Sequential and Hierarchical Processes
- Task: Run or design the same dependencies in sequential and manager-led modes.
- Deliverable and acceptance: Deliver a process comparison identifying delegation authority and a correction stopping rule; only call a mode executed when an actual run trace exists.

### s12-l10 — Add Memory and Shared Context to a Crew
- Task: Store validated company profiles in shared context while keeping secrets and raw unrelated data out.
- Deliverable and acceptance: Deliver a context schema, retrieval example and test that one company's missing field is not filled from another company's profile.

## Stage 13

### s13-l01 — Plan the Market Intelligence Crew
- Task: Inspect projects/04-market-intelligence/companies.json and define the market crew's research boundary.
- Deliverable and acceptance: Deliver a scope document listing the fictional symbols, screening criteria, evidence requirements and final report; explicitly distinguish educational fixtures from live investment analysis.

### s13-l02 — Define Market Research Data Models
- Task: Model Company, Criteria, evidence and ranked profile fields from market.py.
- Deliverable and acceptance: Deliver a schema diagram and validation cases for missing margin, nonfinite growth and evidence-free values; preserve the difference between missing and zero.

### s13-l03 — Build the Company Research Agent
- Task: Implement a CrewAI research task using a typed company-source adapter.
- Deliverable and acceptance: Deliver normalized profiles for all three fixture symbols with their original evidence locators; any live-source extension supplies actual source timestamps separately.

### s13-l04 — Build the Market Analysis Agent
- Task: Build a market-context task that separates sector grouping from verified market conditions.
- Deliverable and acceptance: Deliver sector summaries plus explicit unavailable-context fields; a fictional fixture cannot justify claims about current markets.

### s13-l05 — Build the Screening and Ranking Agent
- Task: Run python3 projects/04-market-intelligence/market.py and inspect deterministic scoring.
- Deliverable and acceptance: Deliver the three ranked profiles and rule-level score evidence; reproduce Cedar 3, Pine 2 and Maple 1 from supplied fixture data.

### s13-l06 — Build the Risk and Evidence Reviewer
- Task: Add a reviewer that checks each credited metric against its evidence locator.
- Deliverable and acceptance: Deliver an unsupported-claim list containing the missing Pine margin evidence; the reviewer must not silently invent a margin or treat missing as zero observation.

### s13-l07 — Connect Market and Company Data Tools
- Task: Define replaceable company and market adapters with typed success, absence and failure results.
- Deliverable and acceptance: Deliver adapter contract tests using the fixture source; external adapters remain optional credentialed verification with their real provenance retained.

### s13-l08 — Add Custom Analysis Tools
- Task: Extend one calculation tool with explicit units and bounded numeric inputs.
- Deliverable and acceptance: Deliver tests for boundary values and malformed inputs; rerun python3 -m unittest discover -s tests -p 'test_projects_4_5.py' without changing fixture facts to satisfy a score.

### s13-l09 — Apply User-Defined Screening Criteria
- Task: Run market.py with --min-growth .20 and compare criteria effects.
- Deliverable and acceptance: Deliver before/after criterion tables showing Cedar and Pine tied at 2 with deterministic symbol ordering; document that the threshold changed, not observed data.

### s13-l10 — Add Crew Memory and Context
- Task: Persist validated profiles and screening criteria as crew context across tasks.
- Deliverable and acceptance: Deliver a round-trip saved context and a test rejecting a context from a different criteria version; evidence locators survive serialization.

### s13-l11 — Use a Hierarchical Crew Process
- Task: Implement a real CrewAI hierarchical process with a manager and bounded evidence-correction request.
- Deliverable and acceptance: Deliver runnable configuration and, when credentials are available, a real delegation trace; the stdlib market runner alone does not demonstrate manager delegation.

### s13-l12 — Generate Structured Company Profiles
- Task: Serialize each company into the shared profile schema with evidence, uncertainty and risks.
- Deliverable and acceptance: Deliver three schema-valid profiles retaining Pine's missing-margin uncertainty and each original symbol; no prose-only replacement of required fields.

### s13-l13 — Produce the Final Market Intelligence Report
- Task: Assemble the final report from validated profiles and deterministic scoring outputs.
- Deliverable and acceptance: Deliver report JSON and a readable comparison with declared fictional provenance, criteria and risk notes; every credited point maps to a metric and evidence locator.

### s13-l14 — Evaluate the Quality of the Crew’s Analysis
- Task: Test ranking stability, evidence removal and criteria changes against the report.
- Deliverable and acceptance: Deliver passing market tests plus a negative test showing removal of Cedar's margin evidence removes one point; retain unsupported-claim counts rather than hiding them.

## Stage 14

### s14-l01 — Introduction to AI Coding Agents
- Task: Trace a coding-agent request through planning, file modification, command execution and test feedback.
- Deliverable and acceptance: Deliver a sequence diagram separating generated proposals from actual executed changes; identify the review boundary before running untrusted code.

### s14-l02 — Why Coding Agents Require Isolated Environments
- Task: Compare a temporary directory with an OS-isolated execution environment.
- Deliverable and acceptance: Deliver a threat table covering host files, network, secrets and resource exhaustion; explicitly state that Python isolated import mode alone is not a security sandbox.

### s14-l03 — Install and Configure Docker
- Task: Install Docker using the learner's authorized environment and verify the daemon and a minimal container.
- Deliverable and acceptance: Deliver actual docker version/info and a successful disposable test run; if unavailable, record the blocker rather than claiming host execution is containerized.

### s14-l04 — Understand Containers, Images, Volumes and Workspaces
- Task: Map image layers, container lifetime, bind mounts and workspaces for the expense application.
- Deliverable and acceptance: Deliver a mount diagram identifying which files are read-only and which outputs persist after container deletion.

### s14-l05 — Build a Sandboxed File Tool
- Task: Inspect team.safe_path and implement a workspace-constrained file interface.
- Deliverable and acceptance: Deliver tests rejecting ../ escape, absolute paths and symlink traversal while allowing a nested project file; never expose arbitrary host reads.

### s14-l06 — Build a Controlled Shell Execution Tool
- Task: Design an allowlisted command tool with argument arrays, fixed cwd and captured execution metadata.
- Deliverable and acceptance: Deliver rejection tests for shell metacharacter injection and unauthorized binaries; do not implement validation by concatenating an untrusted shell string.

### s14-l07 — Run Python Code Inside Docker
- Task: Run the reviewed expense calculator tests in a dedicated Docker image.
- Deliverable and acceptance: Deliver the actual container command, exit code and test output; label the existing local template runner separately from container execution.

### s14-l08 — Install Project Dependencies Safely
- Task: Create an isolated uv environment inside the project container and install a pinned test dependency.
- Deliverable and acceptance: Deliver lock/dependency files and proof the host environment was unchanged; dependency installation failure must stop the run rather than be reported as success.

### s14-l09 — Add Timeouts and Resource Limits
- Task: Set wall-clock timeout, memory and CPU limits for a deliberately overlong disposable command.
- Deliverable and acceptance: Deliver actual termination evidence and a bounded log; demonstrate that the caller regains control without killing unrelated workloads.

### s14-l10 — Capture Command Output and Errors
- Task: Capture stdout, stderr, exit code and timeout as separate structured fields.
- Deliverable and acceptance: Deliver one successful command and one failing command receipt; nonempty stderr alone must not imply failure when the exit code is zero.

### s14-l11 — Build Automated Testing Tools
- Task: Connect the expense test suite to the coding-agent feedback schema.
- Deliverable and acceptance: Deliver real unittest output parsed into a pass/fail result, with failing test identifiers retained; a model saying tests passed is insufficient.

### s14-l12 — Secure the Coding-Agent Environment
- Task: Review file, command, network, secret and approval boundaries of the sandbox.
- Deliverable and acceptance: Deliver a security checklist with adversarial tests for traversal and unapproved execution; explicitly preserve the Docker requirement for executing newly generated untrusted code.

## Stage 15

### s15-l01 — Design the Four-Agent Engineering Team
- Task: Design the manager → architect → developer → QA workflow for an integer-cent expense calculator.
- Deliverable and acceptance: Deliver role contracts, artifact dependencies and completion criteria covering empty input, sum, negative amounts and invalid types.

### s15-l02 — Build the Product Manager Agent
- Task: Convert the expense request into user stories and testable acceptance criteria.
- Deliverable and acceptance: Deliver a product specification defining integer cents and the invalid-input behavior; avoid vague requirements such as works correctly.

### s15-l03 — Build the Software Architect Agent
- Task: Design the pure total_expenses interface, CLI boundary and test layout.
- Deliverable and acceptance: Deliver component/interface diagrams and decisions explaining why floats and booleans are rejected as expense values.

### s15-l04 — Build the Developer Agent
- Task: Implement the approved expense application in a learner workspace through the controlled file tool.
- Deliverable and acceptance: Deliver source changes tied to requirements; new generated code must pass review and run in the Docker boundary rather than bypassing the template verifier.

### s15-l05 — Build the Quality Assurance Agent
- Task: Create QA cases for empty values, positive sums, zeros, negatives, floats and booleans.
- Deliverable and acceptance: Deliver executable tests with at least one deliberate defect caught; remove the defect only after saving its failing test receipt.

### s15-l06 — Define Engineering Tasks and Dependencies
- Task: Define dependencies between specification, architecture, implementation, tests and packaging.
- Deliverable and acceptance: Deliver a task DAG that prevents packaging before QA success and exposes the artifact required to begin each task.

### s15-l07 — Pass Specifications and Context Between Agents
- Task: Pass structured specifications and test failures between role implementations.
- Deliverable and acceptance: Deliver an end-to-end artifact trace preserving requirement IDs and exact failing assertions; no dropped errors in a conversational summary.

### s15-l08 — Build uv-Based Sandbox Tools
- Task: Build allowlisted uv environment and test commands for the sandbox workspace.
- Deliverable and acceptance: Deliver command receipts with cwd, argv and exit status; reject commands escaping the workspace or modifying the host environment.

### s15-l09 — Generate Project Requirements and Dependencies
- Task: Generate dependency declarations from actual imports and the approved architecture.
- Deliverable and acceptance: Deliver a minimal dependency file and reproducible environment setup; justify every non-stdlib dependency rather than adding unused packages.

### s15-l10 — Run the Engineering Crew Inside Docker
- Task: Execute the actual multi-agent engineering crew in Docker with the chosen model configured.
- Deliverable and acceptance: Deliver a real role/task trace and container execution receipt, or a precise credential/runtime blocker; running team.py's reviewed template is only a baseline, not proof of a live crew.

### s15-l11 — Execute Automated Tests
- Task: Run python3 -m unittest discover -s tests -p 'test_projects_4_5.py' and the generated application tests.
- Deliverable and acceptance: Deliver actual exit codes and outputs; the baseline must report six expense tests, while the integration suite separately verifies sandbox/path behavior.

### s15-l12 — Diagnose and Repair Failed Builds
- Task: Introduce one known assertion failure and perform a bounded repair from its feedback.
- Deliverable and acceptance: Deliver the before/after diff and failing/passing receipts with attempt count; stop on exhausted repair budget instead of silently cycling.

### s15-l13 — Review the Completed Application
- Task: Review the delivered application against the product specification and threat boundaries.
- Deliverable and acceptance: Deliver a requirement-to-test matrix and explicit unresolved limitations; QA approval depends on actual test output and reviewed source.

### s15-l14 — Package the Source Code and Documentation
- Task: Run python3 projects/05-sandboxed-engineering/team.py --output /tmp/eca-engineering-delivery.zip using a new destination.
- Deliverable and acceptance: Deliver the source ZIP and verify its member inventory/CRC; the runner refuses overwriting an existing package.

### s15-l15 — Complete the Sandboxed Engineering Team
- Task: Demonstrate planning, implementation, actual QA and packaging as one traceable delivery.
- Deliverable and acceptance: Deliver the final application, setup instructions, artifact lineage and execution limitations; separately identify which agent/framework/provider stages were actually exercised.

## Stage 16

### s16-l01 — Understanding the LangChain Ecosystem
- Task: Map LangChain, LangGraph, LangSmith and Deep Agents to the Sidekick architecture.
- Deliverable and acceptance: Deliver an ecosystem diagram distinguishing model/tool APIs, state orchestration, hosted tracing and long-running harness responsibilities.

### s16-l02 — Models, Tools, Agents and Orchestration
- Task: Describe the order-total example using a model, line_total tool, agent loop and execution policy.
- Deliverable and acceptance: Deliver a component contract showing which part performs exact arithmetic and which selects a tool; the model must not claim a purchase happened.

### s16-l03 — Invoke and Stream Model Responses
- Task: Add both invoke and stream examples using the installed LangChain model interface.
- Deliverable and acceptance: Deliver real message and chunk observations when credentials are available; assert the assembled stream matches the captured final content without inventing chunks offline.

### s16-l04 — Create Tools with the Tool Decorator
- Task: Wrap a typed local calculation function with the LangChain tool decorator.
- Deliverable and acceptance: Deliver tool schema and direct invocation tests for valid prices and invalid quantity; required parameter names appear in the generated schema.

### s16-l05 — Bind Tools to Language Models
- Task: Bind that tool to the configured language model and inspect its actual tool-call arguments.
- Deliverable and acceptance: Deliver a redacted real response with tool-call ID and arguments, or credential-blocked status; a hand-written tool call is not a model observation.

### s16-l06 — Add Structured Outputs
- Task: Define a typed order-total result schema and request structured output.
- Deliverable and acceptance: Deliver schema-valid captured output and negative validation tests for missing total and wrong quantity; distinguish validation tests from a live structured response.

### s16-l07 — Build Your First LangChain Agent
- Task: Run python3 -m frameworks.langchain_agent with explicit live consent, OPENAI_API_KEY and COURSE_MODEL configured.
- Deliverable and acceptance: Deliver a real final answer and tool trace for three items at 12.50; independently verify 37.50 and no external purchase.

### s16-l08 — Add Agent Middleware
- Task: Add middleware recording request IDs, tool outcomes and a bounded-input policy.
- Deliverable and acceptance: Deliver a test showing overlong input is rejected before a model request and logs omit secret values; test middleware independently of paid execution.

### s16-l09 — Add Short-Term Memory
- Task: Store messages by thread and add a documented history-trimming rule.
- Deliverable and acceptance: Deliver a two-turn test retaining the relevant order context while isolating a second user's messages; avoid claiming an in-memory store survives restart.

### s16-l10 — Trace and Inspect Agent Runs
- Task: Capture an agent trace including model/tool timing and one failure branch.
- Deliverable and acceptance: Deliver trace IDs or local redacted trace artifacts from actual execution; optional LangSmith upload requires its own authorized credentials.

## Stage 17

### s17-l01 — Introduction to LangGraph
- Task: Compare an explicit state graph with a free-form model loop for the order approval example.
- Deliverable and acceptance: Deliver a graph design explaining why calculate and approval are separate nodes and where a run can be inspected.

### s17-l02 — Graphs, State, Nodes and Edges
- Task: Identify State, calculate, approval and START/END edges in frameworks/langgraph_state.py.
- Deliverable and acceptance: Deliver an annotated state-transition diagram listing the fields written by each node and the meaning of rejection.

### s17-l03 — State Reducers and Shared Graph Data
- Task: Add a reducer to combine parallel evidence lists without overwriting sibling results.
- Deliverable and acceptance: Deliver a two-branch test proving both entries survive merge; document ordering expectations instead of assuming concurrent completion order.

### s17-l04 — Build Your First LangGraph Workflow
- Task: Install frameworks/requirements/langgraph.txt and run python3 -m frameworks.langgraph_state.
- Deliverable and acceptance: Deliver an actual paused state followed by the scripted rejection; explicitly distinguish this scripted fixture decision from a human's observed approval.

### s17-l05 — Add Tool-Calling Nodes
- Task: Extend a graph with a typed calculation tool node and tool-result state.
- Deliverable and acceptance: Deliver an execution trace proving the tool's exact 37.50 result enters state before any final answer; malformed arguments route to an error.

### s17-l06 — Create Conditional Edges
- Task: Route approved, rejected and missing-input states through conditional edges.
- Deliverable and acceptance: Deliver one test per branch; a rejected order must not reach an execution node.

### s17-l07 — Build Agent Loops with Graphs
- Task: Add a bounded research → evaluate loop to the graph.
- Deliverable and acceptance: Deliver tests for early completion and maximum-iteration termination; retain unfinished status when the bound is reached without adequate evidence.

### s17-l08 — Understand Supersteps and Graph Execution
- Task: Run two independent nodes in one superstep and inspect merged state after completion.
- Deliverable and acceptance: Deliver recorded node events explaining when updates become visible; do not infer a node ran solely from its final field value.

### s17-l09 — Add Error and Recovery Paths
- Task: Inject a tool failure and route it to one bounded retry followed by graceful failure.
- Deliverable and acceptance: Deliver trace and assertions for retry count, preserved error and non-success completion; no infinite catch-and-repeat loop.

### s17-l10 — Trace Graph Runs with LangSmith
- Task: Enable LangSmith tracing for an authorized graph run or produce a local node-event trace when hosted credentials are absent.
- Deliverable and acceptance: Deliver actual transition/timing evidence; clearly label local trace as local rather than claiming a LangSmith dashboard observation.

### s17-l11 — Add Checkpoints to LangGraph Applications
- Task: Inspect graph.get_state and checkpoint history for a named thread.
- Deliverable and acceptance: Deliver checkpoint IDs and a documented resume point; InMemorySaver checkpoints are not advertised as durable across process restart.

## Stage 18

### s18-l01 — Add Conversation Memory to LangGraph
- Task: Add a message-list state with the appropriate reducer and perform two turns on one thread.
- Deliverable and acceptance: Deliver a real second-turn use of prior messages and a test preventing accidental replacement of the conversation list.

### s18-l02 — Persist Agent State with SQLite
- Task: Replace the in-memory checkpointer with the installed SQLite checkpoint adapter in a learner extension.
- Deliverable and acceptance: Deliver a saved database and a restart/resume demonstration preserving state; the repository's InMemorySaver example alone does not satisfy persistence.

### s18-l03 — Use Threads to Separate Agent Sessions
- Task: Run two thread IDs against one checkpointer with different requests.
- Deliverable and acceptance: Deliver separate checkpoint histories and an assertion that neither result contains the other thread's private message.

### s18-l04 — Replay Previous Agent Runs
- Task: Select an existing checkpoint and replay its subsequent execution.
- Deliverable and acceptance: Deliver original/replay checkpoint identifiers and differences; replaying a tool with external effects requires a stub or explicit new authorization.

### s18-l05 — Fork Agent State from Earlier Checkpoints
- Task: Fork a state from a saved checkpoint and change one comparison criterion.
- Deliverable and acceptance: Deliver parent and fork histories showing independent results while the original state remains unchanged.

### s18-l06 — Understand LangGraph Time Travel
- Task: Compare replay with state update plus fork using one saved graph history.
- Deliverable and acceptance: Deliver a timeline explaining the checkpoint selected, modifications and nodes rerun; no claim that historical external actions were undone.

### s18-l07 — Pause and Resume Agent Execution
- Task: Pause with interrupt and resume using Command with an explicit decision.
- Deliverable and acceptance: Deliver actual pre-pause and resumed states; input validation rejects a non-boolean decision for the supplied order graph.

### s18-l08 — Add Human-in-the-Loop Interrupts
- Task: Insert an interrupt before a hypothetical consequential browser action.
- Deliverable and acceptance: Deliver a test proving the executor is not called before a decision; use a local fixture to avoid performing a real external mutation.

### s18-l09 — Approve, Edit or Reject Agent Actions
- Task: Implement approve, edit and reject decisions over a digest-bound proposed action.
- Deliverable and acceptance: Deliver tests showing rejection stops execution and editing invalidates earlier approval; approval of an old payload cannot authorize a changed target.

### s18-l10 — Recover from Interrupted and Failed Runs
- Task: Interrupt a run, restart the process with the durable checkpointer and continue from the last safe point.
- Deliverable and acceptance: Deliver actual recovery evidence and an execution ledger preventing replay of an ambiguously completed side effect.

### s18-l11 — Build Agents with LangChain create_agent
- Task: Build the same order-total behavior using LangChain create_agent and compare its state model with the explicit graph.
- Deliverable and acceptance: Deliver runnable code plus a real credentialed trace or a precise provider blocker; preserve the graph demonstration separately.

### s18-l12 — Add Structured Outputs and Middleware
- Task: Add a structured result model and middleware enforcing approval and logging policies.
- Deliverable and acceptance: Deliver validation/policy tests and, optionally, a real model run; missing approval must fail before a consequential tool is invoked.

## Stage 19

### s19-l01 — Introduction to Browser Automation for AI Agents
- Task: Define browser-agent permissions for the Academy workshop fixture and a public research task.
- Deliverable and acceptance: Deliver a boundary matrix separating navigation/extraction from forms, messages and purchases; identify stale selectors and unexpected dialogs as failure cases.

### s19-l02 — Set Up Playwright for Browser Control
- Task: Install Playwright and Chromium in a dedicated learner environment and serve the workshop fixture locally.
- Deliverable and acceptance: Deliver a real browser launch and screenshot of the local page; parsing HTML with FixtureBrowser is not a Playwright execution.

### s19-l03 — Navigate and Inspect Websites
- Task: Navigate the local page, wait for a named element and record the page URL/title.
- Deliverable and acceptance: Deliver a real Playwright trace or screenshot and selector assertions; no sleep-only assumption that loading completed.

### s19-l04 — Extract Structured Information from Web Pages
- Task: Extract workshop name, date and price into typed records from the actual DOM.
- Deliverable and acceptance: Deliver JSON whose values match fixtures/workshops.html and a missing-field failure test; preserve the fixture label rather than presenting events as live listings.

### s19-l05 — Work with Forms and Interactive Elements
- Task: Fill a form in a disposable local fixture and inspect its fields before submission.
- Deliverable and acceptance: Deliver actual selected/entered values with submission blocked; never use an existing personal account or external recipient for this exercise.

### s19-l06 — Connect Playwright Through MCP
- Task: Connect an actual Playwright MCP server to an MCP client and list/call its browser tools.
- Deliverable and acceptance: Deliver real protocol initialization, tool discovery and a navigation result; direct Playwright scripting alone does not prove MCP connectivity.

### s19-l07 — Build a Browser Research Agent
- Task: Build a bounded browser researcher with allowed origins, extraction schema and a stopping rule.
- Deliverable and acceptance: Deliver a real browser-backed research artifact and failed-navigation trace; live external browsing requires permission and independently retained URLs.

### s19-l08 — Introduction to Deep Agents
- Task: Design a Deep Agents harness with plan, filesystem, skills and delegated subtasks.
- Deliverable and acceptance: Deliver a component map and installed-version record; distinguish the harness framework from the underlying model and from the stdlib Sidekick fixture.

### s19-l09 — Planning and File-System Tools
- Task: Use controlled working files to persist the research plan, observations and final summary.
- Deliverable and acceptance: Deliver actual files with source locators and a path-escape rejection test; facts in the summary must come from captured observations.

### s19-l10 — Progressive Disclosure with Agent Skills
- Task: Design a skill index that loads browser-specific instructions only when relevant.
- Deliverable and acceptance: Deliver an instruction-load trace for a browser task and a non-browser task showing selective loading rather than injecting all skills every time.

### s19-l11 — Build Skills with SKILL.md
- Task: Create a learner SKILL.md for extracting workshop listings with prerequisites, procedure and output contract.
- Deliverable and acceptance: Deliver the skill file plus an application to the real local page; skill text must not include credentials or claim unavailable browser results.

### s19-l12 — Delegate Tasks to Subagents
- Task: Delegate separate extraction and evidence-review tasks to actual specialist agents in the chosen harness.
- Deliverable and acceptance: Deliver task/result IDs and a parent merge preserving disagreements; a diagram or sequential function call is not evidence of executed subagents.

### s19-l13 — Build Long-Running Agent Workflows
- Task: Run an extended task with a saved plan, progress updates and a recoverable interruption.
- Deliverable and acceptance: Deliver the resumed run history and completed artifacts without repeating an ambiguously completed external action; record actual subagent and checkpoint evidence separately.

## Stage 20

### s20-l01 — Design the Browser Task Sidekick
- Task: Design the Sidekick using Step, TaskStore and executor interfaces in projects/06-browser-sidekick/sidekick.py.
- Deliverable and acceptance: Deliver an architecture and task lifecycle covering pending, awaiting approval, executing, complete and failed states; identify which transitions are implemented versus extensions.

### s20-l02 — Build the Sidekick Planner
- Task: Convert find workshop dates and prices into steps with explicit completion criteria.
- Deliverable and acceptance: Deliver a validated plan whose extraction target is the local workshop fixture; reject a step without a criterion.

### s20-l03 — Build the Browser Executor
- Task: Implement or invoke PlaywrightBrowser against the locally served fixture.
- Deliverable and acceptance: Deliver actual DOM-derived results and a browser receipt; keep FixtureBrowser's parser-only unit tests labeled separately.

### s20-l04 — Build the Task Evaluator
- Task: Compare extracted workshop records with the user's objective and detect an empty result.
- Deliverable and acceptance: Deliver an evaluator test where an empty response remains failed rather than complete; partial coverage must identify missing requested fields.

### s20-l05 — Add Research and File Tools
- Task: Store research output in a controlled artifact directory with source URL and observation time.
- Deliverable and acceptance: Deliver a readable report and a traversal-rejection test; external pages, if used, retain their actual captured provenance.

### s20-l06 — Add Memory and Persistent Task State
- Task: Persist task and step state to SQLite, close TaskStore and reopen it.
- Deliverable and acceptance: Deliver a restart test preserving completed steps and pending approvals; an executing step must not be silently replayed.

### s20-l07 — Add Middleware and Execution Policies
- Task: Apply a shared policy layer for origin allowlists, bounded values and redacted logs.
- Deliverable and acceptance: Deliver blocked-origin and malformed-step tests demonstrating rejection before browser execution; successful logs must not expose credentials.

### s20-l08 — Add Human Approval for Sensitive Actions
- Task: Place approval before submit, upload, download and message actions.
- Deliverable and acceptance: Deliver tests proving no executor invocation occurs while approval is pending; the current read-only Playwright adapter must not be claimed to implement these mutations.

### s20-l09 — Implement Approve, Edit and Reject Controls
- Task: Exercise TaskStore.decide with approve, edit and reject on a disposable task.
- Deliverable and acceptance: Deliver exact-payload-once and edit-revokes-approval tests; a rejected task cannot proceed to later extraction steps.

### s20-l10 — Add Subagents for Specialist Tasks
- Task: Add real specialist research and review subagents to the Sidekick harness extension.
- Deliverable and acceptance: Deliver delegated task IDs, bounded scopes and merged evidence; mark this extension incomplete until actual subagent execution exists rather than equating it with the deterministic TaskStore.

### s20-l11 — Add Progress Tracking and Visible Checklists
- Task: Render TaskStore.checklist as a progress display with step criteria and errors.
- Deliverable and acceptance: Deliver a snapshot at pending, awaiting approval and complete states; active/executing must not be displayed as successfully completed.

### s20-l12 — Test the Sidekick on Real-World Tasks
- Task: Run python3 -m unittest discover -s tests -p 'test_projects_6_7.py' and an actual local-browser navigation task.
- Deliverable and acceptance: Deliver test output plus browser evidence for extraction, permission rejection and failure recovery; unit test adapters do not substitute for the browser demonstration.

### s20-l13 — Build the Gradio Interface
- Task: Build a real Gradio UI wiring request, checklist, approval decisions and final artifacts to TaskStore.
- Deliverable and acceptance: Deliver actual browser screenshots and a tested callback trace; no claim that the supplied CLI already provides a Gradio interface.

### s20-l14 — Trace and Evaluate Sidekick Runs
- Task: Record per-step timing, executor outcome and approval events for a Sidekick task.
- Deliverable and acceptance: Deliver a trace and quality rubric measuring requested-field coverage and recovery; report observed latency rather than a fabricated throughput figure.

### s20-l15 — Complete the Browser Task Sidekick
- Task: Demonstrate the integrated local-browser Sidekick with persistent task state and approval boundaries.
- Deliverable and acceptance: Deliver source, setup instructions, actual run artifacts and extension-status inventory; real Gradio, subagent and MCP functionality require their own genuine demonstrations.

