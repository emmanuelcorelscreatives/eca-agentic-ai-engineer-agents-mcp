# Practical workbook: stages 1–10

These are lesson-specific assignments and acceptance criteria, not claims of completed live runs. Work from the repository root. Record commands, pinned versions and actual observations in a private evidence folder; never publish credentials, personal documents or private traces. The repository reference cores are deterministic teaching fixtures. Named SDK, model, n8n, Gradio, hosted tracing and deployment lessons require the corresponding real integration: offline fixtures do not replace their learning objectives. External integrations require your configured account and manual verification of the resulting application or provider receipt.

Each entry preserves the exact curriculum title. Deliverables described here are learner-created unless an existing path is explicitly named.

## Stage 1

### s01-l01: Welcome to the Agentic AI Engineer Course
- **Practical:** Inventory all eight portfolio applications and choose a weekly study schedule.
- **Deliverable:** An outcomes checklist linking each application to a user problem and evidence of completion.
- **Accept when:** All eight projects appear; distinguish runnable reference exercises from live integration evidence.

### s01-l02: Build Your First Autonomous AI Workflow with n8n
- **Practical:** Import `examples/s01/first-workflow.n8n.json` into n8n, follow `examples/s01/README.md` to configure the model credential, and use the supplied synthetic FAQ enquiries. Record one answerable enquiry and one enquiry requiring review as separate manual executions; each execution admits one model request with retries disabled.
- **Deliverable:** Redacted workflow export and actual execution screenshots showing the manual trigger, model response, validation, allowlisted FAQ tool, decision and draft or review output.
- **Accept when:** Both branches run in n8n, the FAQ answer cites the configured fixture, the review branch produces no external delivery, and secrets are absent. The separate arithmetic starter `frameworks/n8n/order-workflow.json` is a foundational deterministic example and does not satisfy this model-enabled practical. Existing authoring tests and an imported canvas are not model-execution proof.

### s01-l03: Course Roadmap—Six Modules, Thirty Stages and Eight Projects
- **Practical:** Map all 30 stages into the six curriculum modules and annotate the eight project milestones.
- **Deliverable:** A dependency roadmap identifying prerequisites and a review checkpoint for each project.
- **Accept when:** Every stage appears once in order; projects retain their authored scope.

### s01-l04: Your Path to Becoming an Agentic AI Engineer
- **Practical:** Compare an AI engineering role, freelance service and product opportunity against the course skills.
- **Deliverable:** A personal skills-gap matrix and one portfolio evidence plan.
- **Accept when:** Each selected skill links to a concrete project artifact; avoid unsupported employment or revenue promises.

### s01-l05: Understanding the Agentic AI Development Stack
- **Practical:** Trace one digital-twin question through UI, model, retrieval, tool execution, memory, evaluation and hosting.
- **Deliverable:** An architecture diagram with trust boundaries, input/output types and failure ownership.
- **Accept when:** Distinguish the model from the application/tool executor and MCP from persistent memory.

### s01-l06: How the Course Projects Connect to Real-World Applications
- **Practical:** Choose one real-world use case for each portfolio project, identifying the buyer and an operational risk.
- **Deliverable:** An eight-row use-case and success-metric matrix.
- **Accept when:** Metrics are measurable; fictional exercise data is not claimed as a customer result.


## Stage 2

### s02-l01: Environment Setup with Python, uv, Git and GitHub
- **Practical:** Create a Python 3.11+ environment with uv, initialize a private practice Git repository and push a harmless README to your own GitHub repository.
- **Deliverable:** Output of `python --version`, `uv --version`, `git --version`, environment interpreter path and remote commit URL.
- **Accept when:** A fresh clone recreates the environment; no credentials or generated private files are committed.

### s02-l02: Windows Development Environment Setup
- **Practical:** On Windows, install Python, uv and Git; create a venv and run `python -m unittest discover -s tests -v` in PowerShell.
- **Deliverable:** Version outputs, activated interpreter path and actual test summary.
- **Accept when:** Commands use the intended environment and work from a path containing spaces; execution-policy changes are scoped and explained.

### s02-l03: macOS Development Environment Setup
- **Practical:** On macOS, install the tools and run the repository tests in an isolated environment.
- **Deliverable:** `sw_vers`, tool versions, interpreter path and actual test summary.
- **Accept when:** Record the CPU architecture; do not use a Linux screenshot as evidence of macOS installation.

### s02-l04: Configure Your IDE with Cursor or Visual Studio Code
- **Practical:** Open the workspace in Cursor or VS Code, select the venv interpreter and debug a local fixture.
- **Deliverable:** Editor screenshot of interpreter selection, a breakpoint and inspected variable.
- **Accept when:** The debugger and integrated terminal resolve the same interpreter; no secrets are visible.

### s02-l05: API Keys, Environment Variables and .env Files
- **Practical:** Copy `.env.example` locally, load a dummy credential and inspect ignored/tracked files before using a real key.
- **Deliverable:** A redacted environment-loading demonstration and secret-exclusion check.
- **Accept when:** A missing key fails clearly; no actual key is printed, committed or embedded in screenshots.

### s02-l06: Managing Model Costs, Usage Limits and Development Budgets
- **Practical:** Set a small development budget and calculate estimated cost from a recorded request's actual token usage.
- **Deliverable:** A provider-limit screenshot and a cost worksheet with model, units, date and stop threshold.
- **Accept when:** Distinguish estimates from billed charges; show how the application stops additional calls when its budget is reached.

### s02-l07: Make Your First Model API Call in Python
- **Practical:** Send one real prompt through a configured provider SDK and save a redacted request/response record.
- **Deliverable:** A minimal Python client, model identifier, request ID when available and actual response.
- **Accept when:** Credentials come from the environment; an offline canned answer is not accepted as a model call.

### s02-l08: Chain Multiple Model Calls into a Workflow
- **Practical:** Chain a real extraction call into a second summarization call, validating the first result before forwarding it.
- **Deliverable:** Two linked request records and an intermediate schema validation result.
- **Accept when:** The second request uses the actual first output; malformed intermediate data prevents the second call.

### s02-l09: Handle API Errors, Rate Limits and Invalid Responses
- **Practical:** Exercise timeout, 429 and malformed-response paths with injected failures, then run one live happy path.
- **Deliverable:** Tests for capped backoff, retry exhaustion and schema rejection plus a live response receipt.
- **Accept when:** Retries are bounded and respect retry hints; unknown external actions are not blindly repeated.


## Stage 3

### s03-l01: What Is an AI Agent?
- **Practical:** Describe a digital-twin agent in terms of objective, observation, state, tool, feedback and termination.
- **Deliverable:** A state-transition diagram for one grounded answer and one unsupported question.
- **Accept when:** Each transition names the application component responsible; a chatbot without tools is not mislabeled autonomous.

### s03-l02: AI Agents vs Deterministic Workflows
- **Practical:** Implement the same fictional contact task as a fixed workflow and a bounded agent loop.
- **Deliverable:** Two execution traces and a short architecture decision record.
- **Accept when:** The comparison identifies predictability, ambiguity, cost and the conditions favoring each approach.

### s03-l03: Understanding the Agent Loop
- **Practical:** Instrument observe, tool request, validated action, tool result and stop events in the shared bounded loop.
- **Deliverable:** An event log including a successful request and a maximum-turn stop.
- **Accept when:** Actions only execute after validation; tool errors return as feedback without an infinite loop.

### s03-l04: Prompt Chaining and Sequential Workflows
- **Practical:** Create a three-step extraction, validation and formatting workflow with explicit intermediate records.
- **Deliverable:** Code and examples showing valid and invalid intermediate outputs.
- **Accept when:** A failed prerequisite blocks dependent steps and preserves the diagnostic record.

### s03-l05: Routing and Conditional Execution
- **Practical:** Route fictional requests into professional-information retrieval, contact capture or unsupported-request handling.
- **Deliverable:** A routing table and tests with ambiguous and out-of-scope examples.
- **Accept when:** Unsupported inputs cannot trigger contact storage; each decision has an explicit category.

### s03-l06: Parallelization and Concurrent Model Calls
- **Practical:** Run three independent model requests sequentially and concurrently with a fixed concurrency cap.
- **Deliverable:** Actual elapsed timings, per-request IDs and a deterministic result association.
- **Accept when:** Compare the same tasks; one failed branch remains attributable and does not reorder results incorrectly.

### s03-l07: Orchestrator-Worker Systems
- **Practical:** Divide a professional profile review into factual grounding, tone and privacy workers under one coordinator.
- **Deliverable:** A typed work plan and a combined report with worker provenance.
- **Accept when:** Only independent work runs concurrently; missing workers are reported rather than fabricated.

### s03-l08: Evaluator-Optimizer Loops
- **Practical:** Create a reviewer that requests at most two revisions to a draft using an explicit rubric.
- **Deliverable:** Versioned drafts, reviewer feedback and a recorded termination reason.
- **Accept when:** The revision limit is enforced; a score increase is not claimed without the actual evaluations.

### s03-l09: Agentic AI Risks, Failure Modes and Common Traps
- **Practical:** Threat-model malicious document instructions, invented credentials, unbounded loops and unauthorized contact capture.
- **Deliverable:** A risk register with attack inputs, affected boundary and mitigation tests.
- **Accept when:** Retrieved text remains data; tests show the application enforces tool and budget boundaries.

### s03-l10: Guardrails, Evaluations and Human Oversight
- **Practical:** Create a small evaluation set with grounded, unsupported, malicious and contact-consent cases.
- **Deliverable:** A rubric, actual run results and a human escalation checklist.
- **Accept when:** Separate deterministic validation from subjective review; no model output can grant human approval.


## Stage 4

### s04-l01: Comparing Hosted and Local Language Models
- **Practical:** Compare a hosted model with an actually available local model on the same three prompts.
- **Deliverable:** A table of observed latency, output quality, hardware, data flow and dated cost estimates.
- **Accept when:** Identify hardware and model versions; unmeasured dimensions are marked unmeasured.

### s04-l02: Configure Multiple Model Providers
- **Practical:** Implement environment-based provider selection with provider-specific credentials and model names.
- **Deliverable:** Two configurations and one real response from each configured provider.
- **Accept when:** Changing provider does not change business logic; unsupported options fail visibly.

### s04-l03: Work with OpenAI-Compatible APIs
- **Practical:** Call an OpenAI-compatible endpoint using explicit base URL, model and environment credential settings.
- **Deliverable:** A redacted client configuration and actual response/error record.
- **Accept when:** Verify the endpoint's supported capabilities rather than assuming tool calling or structured output parity.

### s04-l04: Run Local Models with Ollama
- **Practical:** Install Ollama, pull a model that fits the machine and run `frameworks/ollama_chat.py` using its documented configuration.
- **Deliverable:** `ollama list`, actual model response, hardware and elapsed time.
- **Accept when:** The Python response comes from the local service; a missing service produces a clear error.

### s04-l05: Select Models by Capability, Cost, Speed and Reliability
- **Practical:** Select a model for grounded professional Q&A using an explicit weighted rubric.
- **Deliverable:** A three-task comparison and a justified selection decision.
- **Accept when:** Weights precede scoring; record factual errors and missing measurements without inventing a winner.

### s04-l06: Use a Model as an Evaluator
- **Practical:** Ask a model evaluator to score two candidate answers against grounding and uncertainty criteria.
- **Deliverable:** Structured evaluator records and a human comparison on at least one disagreement.
- **Accept when:** The evaluator's scores are observations, not proof of truth; malformed scores are rejected.

### s04-l07: The Agent Framework and Tooling Landscape
- **Practical:** Map SDKs, visual builders, orchestration frameworks, MCP and tracing tools onto the course architecture.
- **Deliverable:** A tooling decision map with one reason to adopt and one reason to avoid each selected tool.
- **Accept when:** Separate protocols from frameworks and runtimes; name the role each tool actually performs.

### s04-l08: How AI Agent Tool Calling Works
- **Practical:** Capture one real model tool request and execute the approved function in application code.
- **Deliverable:** A redacted model request, validated arguments, function output and final answer.
- **Accept when:** The model requests the tool; application code executes it and returns the correctly linked result.

### s04-l09: Tool Schemas, Arguments, Results and Validation
- **Practical:** Define a typed contact tool and test missing fields, invalid types, unknown arguments and invalid return values.
- **Deliverable:** Tool schema and positive/negative validation tests.
- **Accept when:** Reject invalid inputs before any write and return a predictable structured error.

### s04-l10: Build a Tool-Calling Agent Loop with Python
- **Practical:** Implement a bounded Python loop with a tool allowlist and multiple-call handling.
- **Deliverable:** A real tool-using run plus unknown-tool and turn-limit tests.
- **Accept when:** Each tool result references its request; unsupported tools do not execute and limits terminate the loop.


## Stage 5

### s05-l01: Plan the Professional Digital Twin
- **Practical:** Scope the fictional Amara professional digital twin around approved knowledge, contact consent and deployment boundaries.
- **Deliverable:** A project brief with audience, source inventory and measurable acceptance cases.
- **Accept when:** Private information and unsupported credentials are excluded; success criteria cover uncertainty and contact consent.

### s05-l02: Extract Professional Information from PDF Documents
- **Practical:** Create a synthetic résumé PDF, extract its text using a PDF parser and review section order before indexing.
- **Deliverable:** Synthetic PDF, extraction script and reviewed structured sections.
- **Accept when:** Extracted facts match the PDF; headers, page breaks and missing text are explicitly checked.

### s05-l03: Design an Effective Digital Twin System Prompt
- **Practical:** Write system instructions covering identity, cited facts, uncertainty, tone and contact boundaries.
- **Deliverable:** A versioned prompt and responses to grounded, unsupported and private-information questions.
- **Accept when:** The prompt never authorizes invented awards, salary or availability; tool permissions enforce the same boundaries.

### s05-l04: Context Engineering for Personal Knowledge Agents
- **Practical:** Budget context for instructions, approved profile sections, conversation and tool results.
- **Deliverable:** A context assembly function and an example showing deliberate truncation priorities.
- **Accept when:** Stable source IDs survive assembly; truncation cannot silently remove safety or uncertainty rules.

### s05-l05: Add Document Retrieval and Grounded Responses
- **Practical:** Run `projects/01-digital-twin/twin.py` and extend retrieval while preserving approved-source filtering.
- **Deliverable:** Retrieval tests and a grounded answer containing stable source IDs.
- **Accept when:** Unapproved or irrelevant sections never support an answer; an unsupported question returns insufficient evidence.

### s05-l06: Build the Agent’s Tools
- **Practical:** Implement typed lead-recording and question-capture tools against a local practice database.
- **Deliverable:** Tool contracts and tests proving consent-required writes.
- **Accept when:** Unknown tools reject; failed validation leaves no partial contact record.

### s05-l07: Handle Multiple Tool Calls
- **Practical:** Submit retrieval, an unknown operation and consented contact storage within one ordered turn.
- **Deliverable:** An ordered per-tool result list and database state checks.
- **Accept when:** The unknown operation is rejected explicitly without losing valid results or bypassing consent.

### s05-l08: Add Contact and Notification Capabilities
- **Practical:** Add a notification adapter with dry-run and a separately configured real test destination.
- **Deliverable:** A local contact receipt, dry-run notification and, when enabled, a redacted actual provider receipt.
- **Accept when:** Saving and notification have distinct outcomes; retrying notification cannot duplicate contact storage.

### s05-l09: Build a Visible Planning and Checklist System
- **Practical:** Emit public progress events for retrieval, answer readiness and contact storage.
- **Deliverable:** A UI-ready event stream with stable task IDs and terminal states.
- **Accept when:** Show operational status without exposing hidden model reasoning or personal contact details.

### s05-l10: Create the Gradio Chat Interface
- **Practical:** Build a real Gradio chat interface around the configured model and retrieval tools.
- **Deliverable:** A runnable app and actual browser captures of grounded Q&A and explicit contact consent.
- **Accept when:** UI state reflects actual operations; the deterministic CLI alone does not satisfy this interface exercise.

### s05-l11: Refactor the Agent into Reusable Python Modules
- **Practical:** Split the implementation into configuration, prompts, retrieval, tools, agent and UI modules.
- **Deliverable:** An import map and passing regression tests after refactoring.
- **Accept when:** Imports do not start the server or send requests; public behavior remains unchanged.

### s05-l12: Test the Agent with Real Professional Questions
- **Practical:** Evaluate real professional questions against the fictional approved profile, including adversarial and uncertain cases.
- **Deliverable:** A versioned question set, observed outputs and a failure analysis.
- **Accept when:** Every factual assertion is traceable; consent and privacy failures are counted rather than hidden.

### s05-l13: Deploy the Professional Digital Twin
- **Practical:** Deploy the actual application using environment secrets, request limits and a retention policy.
- **Deliverable:** A reachable deployment URL, health check and redacted configuration/runbook.
- **Accept when:** A fresh visitor can complete a grounded question; secrets and local contact databases are not publicly served.


## Stage 6

### s06-l01: Introduction to the OpenAI Agents SDK
- **Practical:** Create an isolated OpenAI Agents SDK environment using `frameworks/requirements/openai-agents.txt` and inspect `frameworks/openai_agents.py`.
- **Deliverable:** Installed SDK version, a component map and the adapter's actual bounded run.
- **Accept when:** A live SDK response is required for SDK execution claims; deterministic core tests remain separate.

### s06-l02: Async Python and asyncio for Agent Applications
- **Practical:** Write async coroutines for independent research subtasks and a dependent synthesis step.
- **Deliverable:** An asyncio script demonstrating awaited results, cancellation and an error path.
- **Accept when:** The dependent step waits for prerequisites; no blocking sleep is used inside the event loop.

### s06-l03: Agents, Runners, Results and Execution Traces
- **Practical:** Trace Agent configuration through Runner execution into the result and visible execution events.
- **Deliverable:** A redacted object/event inspection from an actual SDK run.
- **Accept when:** Identify model output, tool events and the final result distinctly; do not print credentials or hidden reasoning.

### s06-l04: Build Your First SDK Agent
- **Practical:** Define a minimal SDK Agent and run it with a configured model and explicit turn cap.
- **Deliverable:** Runnable code and an actual final-output record.
- **Accept when:** The response comes from Runner, with the exact SDK/model version recorded.

### s06-l05: Stream Agent Responses
- **Practical:** Use the SDK's current streaming API to display response increments and lifecycle events.
- **Deliverable:** A streaming client and captured ordered event log.
- **Accept when:** Cancellation stops further work; final assembled output matches the streamed content.

### s06-l06: Add Tools with the Function Tool Decorator
- **Practical:** Expose a typed arithmetic function through the SDK function-tool decorator.
- **Deliverable:** A real SDK request, validated function arguments and observed tool result.
- **Accept when:** The result is computed by the function; invalid arguments cannot execute silently.

### s06-l07: Validate Tool Inputs and Outputs
- **Practical:** Validate an amount and currency before tool execution, and validate the returned record.
- **Deliverable:** Schema tests for valid, missing, extra and malformed values plus one live tool use.
- **Accept when:** Bad input fails before a side effect; invalid output cannot be passed downstream as success.

### s06-l08: Add Conversation Memory with Sessions
- **Practical:** Add an SDK session to a two-turn fictional conversation.
- **Deliverable:** Two real turn records sharing one session and an unrelated session for comparison.
- **Accept when:** The second turn recalls only the intended session; session isolation is demonstrated.

### s06-l09: Persist Agent Sessions with SQLite
- **Practical:** Persist the SDK session in SQLite, restart the process and continue the same conversation.
- **Deliverable:** Database path, restart transcript and separate-session isolation check.
- **Accept when:** History survives restart without exposing it to a new session; the database is excluded from commits.

### s06-l10: Inspect and Debug Agent Traces
- **Practical:** Explicitly enable tracing for a sanitized SDK run; the baseline adapter disables tracing by default.
- **Deliverable:** Actual trace identifier or supported trace export with model/tool/error timing.
- **Accept when:** Confirm trace configuration and redaction; a fabricated dashboard or local print log is not a hosted trace.


## Stage 7

### s07-l01: Single-Agent vs Multi-Agent Architecture
- **Practical:** Compare one generalist with specialist agents for a multi-part fictional company task.
- **Deliverable:** An architecture decision backed by actual outputs, call count and observed latency.
- **Accept when:** Extra agents need a measured benefit; limitations and disagreement are recorded.

### s07-l02: Orchestration by Code vs Orchestration by the Model
- **Practical:** Implement code-directed and model-directed coordination for the same research/draft/review task.
- **Deliverable:** Two execution graphs and actual delegation traces.
- **Accept when:** Distinguish fixed sequencing from the model's observed choice of specialists.

### s07-l03: Run Agents Concurrently with asyncio.gather
- **Practical:** Run independent SDK specialists with `asyncio.gather` and a concurrency cap.
- **Deliverable:** Per-agent results, timing and an injected failure demonstration.
- **Accept when:** Result identity survives completion-order changes; exceptions have explicit handling.

### s07-l04: Use Agents as Tools
- **Practical:** Expose a specialist using the SDK's agent-as-tool mechanism.
- **Deliverable:** A manager run showing the specialist tool invocation and returned result.
- **Accept when:** The manager retains control; distinguish this from transferring control through a handoff.

### s07-l05: Build a Manager-Agent Architecture
- **Practical:** Build a manager that delegates research and writing and assembles a cited answer.
- **Deliverable:** Manager instructions, specialist contracts and actual execution trace.
- **Accept when:** The final answer uses actual specialist results and reports missing evidence.

### s07-l06: Delegate Work Through Handoffs
- **Practical:** Implement a handoff between an intake agent and a specialist with a clear transfer condition.
- **Deliverable:** A real SDK trace showing which agent owns each stage.
- **Accept when:** Only the intended recipient receives the handoff; responsibility for final response is explicit.

### s07-l07: Pass Context Between Agents
- **Practical:** Pass a typed context object containing prospect ID, allowed actions and approved source IDs.
- **Deliverable:** Typed context schema and isolation tests for two concurrent prospects.
- **Accept when:** Do not forward unnecessary private conversation history; each agent sees the intended context.

### s07-l08: Control Agent Responsibilities and Boundaries
- **Practical:** Restrict each agent to its own tools and demonstrate attempts outside its role.
- **Deliverable:** A permissions matrix and positive/negative execution tests.
- **Accept when:** Instructions and application tool permissions agree; a specialist cannot silently acquire extra tools.

### s07-l09: Handle Multi-Agent Failures
- **Practical:** Exercise worker timeout, provider error and partial completion in a coordinated task.
- **Deliverable:** Failure fixtures, bounded recovery logic and an actual partial-result report.
- **Accept when:** Unknown side effects are reconciled rather than repeated; unavailable results are labeled missing.

### s07-l10: Trace a Complete Multi-Agent Run
- **Practical:** Follow one complete multi-agent run from user request through delegation and synthesis.
- **Deliverable:** A sanitized trace annotated with input IDs, tools, handoffs, latency and final outcome.
- **Accept when:** Every claimed step is present in the actual run and linked to its predecessor.


## Stage 8

### s08-l01: Design the AI Sales Development Architecture
- **Practical:** Design the fictional Cedar Library sales workflow with research, strategy, writing, review and approval stages.
- **Deliverable:** An architecture diagram identifying data ownership and the external-send boundary.
- **Accept when:** Human approval is outside model authority; fictional prospect records remain clearly labeled.

### s08-l02: Define Prospect and Company Data Models
- **Practical:** Define validated prospect, company, evidence, strategy and draft models.
- **Deliverable:** Schemas with valid fixtures and rejection tests for missing source IDs and invalid emails.
- **Accept when:** Downstream records retain prospect/source identity and do not invent absent research.

### s08-l03: Build the Prospect Research Agent
- **Practical:** Build a research specialist that structures approved company and role evidence.
- **Deliverable:** A real agent output grounded in the fictional prospect fixture and its source IDs.
- **Accept when:** Each personalization claim is attributed; a missing fact remains unknown.

### s08-l04: Build the Outreach Strategy Agent
- **Practical:** Generate an outreach strategy from the research record with an explicit value proposition.
- **Deliverable:** A structured strategy containing audience, supported need, message angle and exclusions.
- **Accept when:** The strategy introduces no fabricated relationship, performance guarantee or unsupported claim.

### s08-l05: Build the Professional Email Writer Agent
- **Practical:** Build an email-writing specialist consuming the approved strategy and prospect facts.
- **Deliverable:** An actual generated subject/body with source-linked personalization notes.
- **Accept when:** The draft is concise and unsent; it does not invent customer results or prior contact.

### s08-l06: Build the Sales Quality Reviewer Agent
- **Practical:** Review an accurate draft and a deliberately unsupported draft with a structured rubric.
- **Deliverable:** Reviewer outputs and human comparison against the source fixture.
- **Accept when:** The seeded unsupported claim is identified; model approval cannot authorize sending.

### s08-l07: Create Email Drafting and Delivery Tools
- **Practical:** Keep draft creation, preview and delivery as distinct tools, starting with `sales.py`'s simulated outbox.
- **Deliverable:** Tool contracts and tests for preapproval refusal, editing and idempotency.
- **Accept when:** Simulation is labeled; a real delivery adapter needs authenticated approval and an actual provider receipt.

### s08-l08: Coordinate the Sales Agents Through Code
- **Practical:** Coordinate actual research, strategy, writer and reviewer calls in application code.
- **Deliverable:** A deterministic orchestration trace with each validated intermediate record.
- **Accept when:** A failed review prevents approval progression; downstream agents use actual upstream outputs.

### s08-l09: Coordinate the Sales Agents with a Manager Agent
- **Practical:** Implement a manager agent that chooses specialists and requests a bounded revision.
- **Deliverable:** An actual trace documenting selected specialists and the revision reason.
- **Accept when:** The manager cannot bypass validation or issue human approval; maximum iterations terminate.

### s08-l10: Add Handoffs Between Sales Specialists
- **Practical:** Add a specialist handoff carrying the prospect, evidence IDs and draft revision.
- **Deliverable:** A real handoff run and a typed transfer record.
- **Accept when:** The recipient receives required context without unrelated prospects or private history.

### s08-l11: Add Structured Outputs with Pydantic
- **Practical:** Use Pydantic models for research, strategy and draft outputs and test malformed provider results.
- **Deliverable:** Validation code and observed success/failure cases.
- **Accept when:** Invalid structures never advance to delivery; schema repair attempts are bounded.

### s08-l12: Add Human Approval Before Sending
- **Practical:** Build a human approve/edit/reject control bound to the exact draft hash and recipient.
- **Deliverable:** UI captures and tests showing that edits revoke approval.
- **Accept when:** A model saying approved has no effect; repeated approved submission cannot duplicate delivery.

### s08-l13: Build Sales Quality and Personalization Evaluations
- **Practical:** Evaluate a set of fictional prospects including sparse data and deceptive claims.
- **Deliverable:** A rubric, actual agent outputs and scored personalization/grounding results.
- **Accept when:** Count failures explicitly; distinguish mechanical checks from human factual review.

### s08-l14: Complete the AI Sales Development Team
- **Practical:** Integrate the SDK agents, approval UI, trace capture and evaluation suite around the sales state machine.
- **Deliverable:** A runnable application and one end-to-end observed draft-to-approved-simulated-delivery run.
- **Accept when:** All stages remain attributable; actual external sending stays disabled unless separately configured and approved.


## Stage 9

### s09-l01: Design the Deep Research System
- **Practical:** Scope a research question, evidence boundaries, report audience and completion criteria.
- **Deliverable:** A research brief separating corpus practice from live-web research.
- **Accept when:** The brief names coverage requirements and what would count as insufficient evidence.

### s09-l02: Define the Research Workflow and Agent Responsibilities
- **Practical:** Assign planning, search, evidence analysis, source review and report writing to explicit components.
- **Deliverable:** A workflow diagram and typed handoff contracts.
- **Accept when:** Each component has one accountable output; source review precedes supported conclusions.

### s09-l03: Build the Research Planning Agent
- **Practical:** Build a planner that decomposes a broad question into bounded research tasks.
- **Deliverable:** An actual generated plan with task IDs, coverage and stop conditions.
- **Accept when:** Tasks address the question and specify evidence needs rather than claiming results prematurely.

### s09-l04: Generate Focused Search Queries
- **Practical:** Generate distinct focused queries for each planned subtopic.
- **Deliverable:** A query set with task mapping, rationale and duplicate detection.
- **Accept when:** Queries cover multiple angles without fabricating sources or implying searches already ran.

### s09-l05: Build the Web Search Agent
- **Practical:** Implement a real search-provider adapter alongside the labeled local-corpus baseline.
- **Deliverable:** Actual query receipts, retrieved URLs and normalized results from a configured live search.
- **Accept when:** Do not present `research.py`'s synthetic corpus lookup as web search; failed queries remain visible.

### s09-l06: Capture Sources and Evidence
- **Practical:** Capture source title, URL/location, publication/access dates, excerpt and claim IDs.
- **Deliverable:** An evidence ledger and saved source snapshots when permitted.
- **Accept when:** Excerpts match the captured source; invented or inaccessible references cannot support conclusions.

### s09-l07: Build the Evidence Analysis Agent
- **Practical:** Analyze evidence for agreement, contradiction and comparability using the 45/70-minute fixture and live evidence separately.
- **Deliverable:** A structured findings table linking every conclusion to source IDs.
- **Accept when:** Preserve the two different measurement scopes; do not average incompatible observations.

### s09-l08: Build the Research Report Writer
- **Practical:** Write a report from the actual plan and evidence ledger with citations and limitations.
- **Deliverable:** A report whose factual claims point to captured evidence.
- **Accept when:** Unsupported sections state uncertainty; no new sources appear only in the prose.

### s09-l09: Add Structured Research Outputs
- **Practical:** Define schemas for plans, queries, evidence, findings, sections and final reports.
- **Deliverable:** Schema validation tests for missing citation IDs, dates and malformed sections.
- **Accept when:** Invalid records fail at boundaries and cannot masquerade as complete research.

### s09-l10: Coordinate the Research Team Through Code
- **Practical:** Coordinate planning, search, normalization, analysis and reporting through explicit code dependencies.
- **Deliverable:** An execution log linking phase inputs, outputs and failure states.
- **Accept when:** Report generation waits for validated evidence and identifies missing branches.

### s09-l11: Manage Parallel Research Tasks
- **Practical:** Run independent research branches concurrently while preserving query and source attribution.
- **Deliverable:** A bounded parallel execution trace and equivalent sequential comparison.
- **Accept when:** Concurrency does not change citation identity or silently discard failed branches.

### s09-l12: Assemble a Complete Evidence-Based Report
- **Practical:** Assemble specialist sections into one report, deduplicate sources and verify claim references.
- **Deliverable:** A merged report and a citation coverage check.
- **Accept when:** Every cited ID exists; duplicate source records do not count as independent corroboration.

### s09-l13: Handle Missing, Conflicting and Insufficient Evidence
- **Practical:** Test contradictory, stale, absent and incomparable evidence cases.
- **Deliverable:** Observed reports and a rubric for uncertainty and conflict disclosure.
- **Accept when:** The system preserves disagreement and missing evidence instead of fabricating a confident answer.


## Stage 10

### s10-l01: Refactor the Research System into Python Modules
- **Practical:** Separate research agents, schemas, search adapters, orchestration, settings and UI modules.
- **Deliverable:** A module map and passing baseline/citation regression tests.
- **Accept when:** Imports do not trigger searches or launch a server; actual adapter behavior stays explicit.

### s10-l02: Build the Deep Research Gradio Interface
- **Practical:** Build a real Gradio interface for entering a research question and inspecting the final report.
- **Deliverable:** A runnable UI with actual browser captures and a configured research run.
- **Accept when:** The interface displays real execution results and separates synthetic corpus mode from live web mode.

### s10-l03: Stream Research Progress to the User
- **Practical:** Stream planning, searching, analyzing and writing events from the actual orchestration.
- **Deliverable:** A timestamped event log and matching UI progress captures.
- **Accept when:** Events describe completed/current operations; failure and cancellation produce truthful terminal states.

### s10-l04: Display Plans, Sources and Agent Activity
- **Practical:** Display the plan, source ledger and public agent activity in separate UI panels.
- **Deliverable:** Browser captures linking a report claim back to its source record.
- **Accept when:** Operational activity is visible without revealing hidden reasoning or provider credentials.

### s10-l05: Add Report Export and Email Delivery
- **Practical:** Export a report and implement an approval-gated email adapter with dry-run default.
- **Deliverable:** A readable exported report plus preview/approval records; a live send requires a redacted real receipt.
- **Accept when:** Export preserves citations; recipient and report hash bind approval, and repeat submission is idempotent.

### s10-l06: Create a Research Evaluation Dataset
- **Practical:** Create evaluation cases for straightforward, ambiguous, conflicting and unanswerable questions.
- **Deliverable:** A versioned dataset specifying expected coverage, evidence constraints and failure criteria.
- **Accept when:** Expected criteria do not contain fabricated live answers; include at least one deliberately unsupported case.

### s10-l07: Evaluate Source Quality and Report Completeness
- **Practical:** Score actual reports for source relevance, diversity, question coverage and cited factual support.
- **Deliverable:** A scored evaluation sheet with human-reviewed disagreements.
- **Accept when:** Several pages from one source are not independent evidence; scores retain supporting examples.

### s10-l08: Analyze Traces, Latency and Token Usage
- **Practical:** Analyze observed model/search events for latency, token usage and cost concentration.
- **Deliverable:** A per-stage timing/usage table from one actual run and a measured optimization proposal.
- **Accept when:** Missing provider usage is marked unavailable; estimated cost is not reported as billed spend.

### s10-l09: Add Retries and Failure Recovery
- **Practical:** Inject failed search, malformed agent output and interruption after saved evidence.
- **Deliverable:** Recovery tests and a resumed execution log with checkpoint IDs.
- **Accept when:** Resume reuses verified evidence, bounds retries and avoids duplicate approved email delivery.

### s10-l10: Deploy the Deep Research Application
- **Practical:** Deploy the real research UI with secure secrets, limits and separate user sessions.
- **Deliverable:** A reachable deployment, sanitized configuration and a fresh-user test report.
- **Accept when:** A new session can complete research and export; source provenance and private sessions remain protected.

### s10-l11: Complete the OpenAI Agents SDK Module
- **Practical:** Run a final demonstration connecting SDK tools, handoffs, research, tracing, evaluations and approval boundaries.
- **Deliverable:** A module completion checklist linking each claim to actual project evidence.
- **Accept when:** Unfinished live SDK/UI/deployment work remains explicitly incomplete; local baseline tests alone do not certify those features.

