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
- **Practical:** Follow `labs/s02/s02-l01.md` in a disposable exercise clone: use stdlib-first uv sync, generate a real lockfile, pin the observed Python version, and push the inspected exercise to your own authorized GitHub repository. Add an SDK extra only for that integration track.
- **Deliverable:** Actual tool/interpreter versions, generated lock and Python pin, inspected staged-file list, remote commit URL and a fresh-clone frozen-sync receipt.
- **Accept when:** A fresh clone recreates the demonstrated environment from its actual lock; no credentials or private files are committed. Existing Academy CI is not evidence of your clone, uv setup or GitHub push.

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
- **Practical:** Use `data/s02/.env.example` with explicit `stage02_configuration.load_configuration` in `examples/stages02-04/stage02_configuration.py`. Demonstrate dummy-file loading, environment precedence, conflicting aliases and missing credentials; separately inspect actual Git tracked/staged files before using a real key.
- **Deliverable:** A redacted environment-loading demonstration and secret-exclusion check.
- **Accept when:** Missing or conflicting configuration fails without echoing secrets; no real key is printed, committed or captured. Ignore-file declarations alone do not prove the Git index is clean.

### s02-l06: Managing Model Costs, Usage Limits and Development Budgets
- **Practical:** Use `Observation` and `UsageLedger` in `examples/stages02-04/stage02_configuration.py` to reserve a bounded request budget, account for reported tokens and stop on missing usage, unresolved pending requests or overrun. Separately inspect real provider controls and current pricing for any live demonstration.
- **Deliverable:** An attributed usage/cost worksheet with model, units, price date, observed usage status and stop reason, plus an actual provider-limit screenshot when a dashboard control is claimed.
- **Accept when:** Missing usage remains unknown rather than zero; pending/unknown requests retain their admission and block further calls. Illustrative estimated cost is distinct from billed charges, and the local ledger is not a provider billing cap.

### s02-l07: Make Your First Model API Call in Python
- **Practical:** Send one real prompt through a configured Python SDK or `ObservedCompatibleModel` documented HTTP adapter in `examples/stages02-04/stage02_configuration.py`; save the redacted actual response observation.
- **Deliverable:** A minimal Python client, model identifier, request ID when available and actual response.
- **Accept when:** Credentials come from explicit configuration; an injected HTTP transport is not a provider observation, and an HTTP adapter run is not mislabeled an SDK run.

### s02-l08: Chain Multiple Model Calls into a Workflow
- **Practical:** Use `requirements_chain` and `validate_requirements` in `examples/stages02-04/stage02_configuration.py` to pass actual extracted requirements into a checklist/summary transformation. Validate IDs, text, bounds and uniqueness before admitting the second call.
- **Deliverable:** Two linked request records and an intermediate schema validation result.
- **Accept when:** The second request uses the validated actual first output; malformed prerequisites block it and preserve diagnostics. Schema validity alone does not certify factual accuracy.

### s02-l09: Handle API Errors, Rate Limits and Invalid Responses
- **Practical:** Use `ModelBoundaryError`, `qualified_retry` and the observed HTTP boundary to exercise injected 429/Retry-After, authentication, timeout/unknown and malformed-response cases. Reuse the exact s02-l07 actual happy-path observation when its input/configuration match.
- **Deliverable:** Tests for capped backoff, retry exhaustion and schema rejection plus a live response receipt.
- **Accept when:** Only qualified transient failures retry within elapsed/attempt budgets; authentication/input failures stop. Unknown outcomes retain their state and are not blindly replayed; injected failures require no paid failure generation.


## Stage 3

### s03-l01: What Is an AI Agent?
- **Practical:** Describe a digital-twin agent in terms of objective, observation, state, tool, feedback and termination. Inspect `observed_agent_loop` in `examples/stages02-04/stage03_patterns.py` for component-tagged events and terminal records.
- **Deliverable:** A state-transition diagram for one grounded answer and one unsupported question.
- **Accept when:** Each transition names the application component responsible; a chatbot without tools is not mislabeled autonomous.

### s03-l02: AI Agents vs Deterministic Workflows
- **Practical:** Implement the same fictional contact task as a fixed workflow and a bounded agent loop. Use that module's `contact_workflow`, `contact_agent` and application-owned `RequestState`, with separate in-memory stores.
- **Deliverable:** Two execution traces and a short architecture decision record.
- **Accept when:** The comparison identifies predictability, ambiguity, cost and the conditions favoring each approach.

### s03-l03: Understanding the Agent Loop
- **Practical:** Instrument observe, tool request, validated action, tool result and stop events in the shared bounded loop. Use `observed_agent_loop` and `application_tool` in `examples/stages02-04/stage03_patterns.py`.
- **Deliverable:** An event log including a successful request and a maximum-turn stop.
- **Accept when:** Actions only execute after validation; tool errors return as feedback without an infinite loop.

### s03-l04: Prompt Chaining and Sequential Workflows
- **Practical:** Create a three-step extraction, validation and formatting workflow with explicit intermediate records. Use `extract_validate_format`, `Profile` and `validate_profile` in `examples/stages02-04/stage03_patterns.py`.
- **Deliverable:** Code and examples showing valid and invalid intermediate outputs.
- **Accept when:** A failed prerequisite blocks dependent steps and preserves the diagnostic record.

### s03-l05: Routing and Conditional Execution
- **Practical:** Route fictional requests into professional-information retrieval, contact capture or unsupported-request handling. Use `route_request` and `RequestState` in `examples/stages02-04/stage03_patterns.py`; the taxonomy is explicit structured input, not a demonstrated natural-language classifier.
- **Deliverable:** A routing table and tests with ambiguous and out-of-scope examples.
- **Accept when:** Unsupported inputs cannot trigger contact storage; each decision has an explicit category.

### s03-l06: Parallelization and Concurrent Model Calls
- **Practical:** Use `ModelTask` and `measured_requests` in `examples/stages02-04/stage03_patterns.py` to compare identical independent requests sequentially and concurrently under a fixed cap. First inspect labeled fixture transports; actual model-call timing requires a separately authorized real transport.
- **Deliverable:** Observed elapsed timing, stable request IDs, input hashes and per-branch success/failure attribution, labeled fixture transport or actual provider observation.
- **Accept when:** Compare the same tasks and preserve result identity on failure or reordered completion. Fixture/barrier timing establishes scheduling behavior, never provider speed; a claimed model-performance comparison requires actual model observations.

### s03-l07: Orchestrator-Worker Systems
- **Practical:** Divide a professional profile review into factual grounding, tone and privacy workers under one coordinator. Use `profile_review_plan`, `ReviewTask`, `WorkerResult` and `review_profile` in `examples/stages02-04/stage03_patterns.py`; deterministic grounding/tone/privacy heuristics have limited stated scope.
- **Deliverable:** A typed work plan and a combined report with worker provenance.
- **Accept when:** Only independent work runs concurrently; missing workers are reported rather than fabricated.

### s03-l08: Evaluator-Optimizer Loops
- **Practical:** Create a reviewer that requests at most two revisions to a draft using an explicit rubric. Inspect the bounded `optimize` implementation in `examples/stages02-04/foundations.py` and its fixture demonstration in `stage03_patterns.py`.
- **Deliverable:** Versioned drafts, reviewer feedback and a recorded termination reason.
- **Accept when:** The revision limit is enforced; a score increase is not claimed without the actual evaluations.

### s03-l09: Agentic AI Risks, Failure Modes and Common Traps
- **Practical:** Threat-model malicious document instructions, invented credentials, unbounded loops and unauthorized contact capture. Use `RISK_REGISTER` and the application-tool negative cases in `examples/stages02-04/stage03_patterns.py`.
- **Deliverable:** A risk register with attack inputs, affected boundary and mitigation tests.
- **Accept when:** Retrieved text remains data; tests show the application enforces tool and budget boundaries.

### s03-l10: Guardrails, Evaluations and Human Oversight
- **Practical:** Create a small evaluation set with grounded, unsupported, malicious and contact-consent cases. Use `EVALUATION_CASES`, `evaluate_controls` and `HUMAN_ESCALATION_CHECKLIST` in `examples/stages02-04/stage03_patterns.py`; subjective relevance/tone remains separately reviewed.
- **Deliverable:** A rubric, actual run results and a human escalation checklist.
- **Accept when:** Separate deterministic validation from subjective review; no model output can grant human approval.


## Stage 4

### s04-l01: Comparing Hosted and Local Language Models
- **Practical:** Compare a hosted model with an actually available local model on the same three prompts.
- **Deliverable:** A table of observed latency, output quality, hardware, data flow and dated cost estimates.
- **Accept when:** Identify hardware and model versions; unmeasured dimensions are marked unmeasured.

### s04-l02: Configure Multiple Model Providers
- **Practical:** Use `load_provider_settings`, `provider_factory` and `SelectedProvider` in `examples/stages02-04/stage04_selection.py` to select declared hosted-compatible or native Ollama configurations without changing workflow logic. Supply the selected hosted credential through its configured environment name; request execution is a separate explicit opt-in.
- **Deliverable:** Two validated provider configurations, rejection observations for unsupported options, and separately retained actual responses from both providers when a live demonstration is claimed.
- **Accept when:** Construction sends no request; missing selected credentials or unsupported provider/options fail visibly. Native Ollama supports this text route only and rejects unimplemented tool normalization; injected HTTP fixtures do not certify real provider or Ollama observations.

### s04-l03: Work with OpenAI-Compatible APIs
- **Practical:** Call an OpenAI-compatible endpoint using explicit base URL, model and environment credential settings.
- **Deliverable:** A redacted client configuration and actual response/error record.
- **Accept when:** Verify the endpoint's supported capabilities rather than assuming tool calling or structured output parity.

### s04-l04: Run Local Models with Ollama
- **Practical:** Install Ollama, pull a model that fits the machine and run `frameworks/ollama_chat.py` using its documented configuration.
- **Deliverable:** `ollama list`, actual model response, hardware and elapsed time.
- **Accept when:** The Python response comes from the local service; a missing service produces a clear error.

### s04-l05: Select Models by Capability, Cost, Speed and Reliability
- **Practical:** Use `TaskRubric`, `Measurement` and `weighted_model_worksheet` in `examples/stages02-04/stage04_selection.py` to predeclare three grounded-Q&A tasks, metric/task weights, quality floors, latency/cost ceilings and required capabilities before measuring candidate models.
- **Deliverable:** A dated three-task worksheet retaining quality labels, latency, cost units, successes/attempts, capability observations and a justified task-specific selection or explicit incomplete/tied result.
- **Accept when:** Weights and thresholds precede observations; missing metrics remain missing without an imputed score or winner. Synthetic measurements stay labeled, ties/all-ineligible outcomes remain explicit, and a real recommendation needs actual comparable model observations and current dated pricing.

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
- **Practical:** Use `CONTACT_TOOL`, `CONTACT_RESULT_SCHEMA`, `ContactResult`, `dispatch_contact` and `validate_contact_result` in `examples/stages02-04/stage04_selection.py`. Exercise matching application-owned consent, malformed inputs and malformed/mismatched backend returns against the synthetic in-memory contact backend.
- **Deliverable:** Typed input/result contracts and positive/negative observations identifying NOT_INVOKED versus UNKNOWN_DO_NOT_RETRY, with final in-memory state inspected.
- **Accept when:** Invalid input or missing consent prevents backend invocation. Result identity, email, types and storage/synthetic fields validate after execution; an invalid backend result may follow an effect and is held unknown, never described as rolled back or automatically retried. No external CRM/email action is implied.

### s04-l10: Build a Tool-Calling Agent Loop with Python
- **Practical:** Use `contact_tool_loop` in `examples/stages02-04/stage04_selection.py` with the result-validating contact dispatcher and application-owned matching consent. Demonstrate two tool calls in one assistant turn, both correlated results in the next model input, final response, duplicate-ID rejection and bounded stopping.
- **Deliverable:** An explicitly labeled model-double trace for the two-call round trip and failure boundaries; separately retain a genuine supported-provider request/tool-result/final-response observation when claimed.
- **Accept when:** Each result preserves its tool_call_id and all input/consent/result checks; an unknown backend effect stops before another model request. The bound is at most three tools per model turn with max_calls 1–5, hence no more than 15 backend admissions. Double outputs and final prose are not proof of provider inference or stored contacts; native Ollama tool normalization remains unsupported.


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
- **Practical:** Use the isolated SDK environment described in `examples/stages06-07/README.md` and its pinned `requirements.txt`; inspect the catalogue agent in `examples/stages06-07/sdk_adapter.py`. The separate arithmetic framework companion is a comparison, not the catalogue walkthrough.
- **Deliverable:** Installed SDK version, a component map and the adapter's actual bounded run.
- **Accept when:** A live SDK response is required for SDK execution claims; deterministic core tests remain separate.

### s06-l02: Async Python and asyncio for Agent Applications
- **Practical:** Write async coroutines for independent research subtasks and a dependent synthesis step.
- **Deliverable:** An asyncio script demonstrating awaited results, cancellation and an error path.
- **Accept when:** The dependent step waits for prerequisites; no blocking sleep is used inside the event loop.

### s06-l03: Agents, Runners, Results and Execution Traces
- **Practical:** Trace Agent configuration through Runner execution into the result and visible execution events. Inspect `ObservationHooks` in `examples/stages06-07/sdk_observation.py` alongside `Runner` and actual result fields in `sdk_adapter.py`.
- **Deliverable:** A redacted object/event inspection from an actual SDK run.
- **Accept when:** Identify model output, tool events and the final result distinctly; do not print credentials or hidden reasoning.

### s06-l04: Build Your First SDK Agent
- **Practical:** Define a minimal SDK Agent and run it with a configured model and explicit turn cap. Use the catalogue mode of `examples/stages06-07/sdk_adapter.py` with `data/s06-catalogue.json` and an explicitly selected available model.
- **Deliverable:** Runnable code and an actual final-output record.
- **Accept when:** The response comes from Runner, with the exact SDK/model version recorded.

### s06-l05: Stream Agent Responses
- **Practical:** Use catalogue streaming in `examples/stages06-07/sdk_adapter.py` and `stream_receipt.consume_sdk_stream` to display actual deltas and lifecycle events; inspect partial-error and same-iterator cancellation behavior with labeled fixtures before a separately authorized real streaming observation.
- **Deliverable:** A streaming client and captured ordered event log.
- **Accept when:** Partial text is separate from a completed answer; cancellation requests immediate stop and drains the same iterator, retaining cleanup uncertainty. A failed stream never automatically sends a second model request.

### s06-l06: Add Tools with the Function Tool Decorator
- **Practical:** Expose `catalogue_lookup(course_id)` through the function-tool decorator in `examples/stages06-07/sdk_adapter.py`, reading `data/s06-catalogue.json`; inspect its schema and validated tool result.
- **Deliverable:** A real SDK request, validated function arguments and observed tool result.
- **Accept when:** The function returns only the requested fixture facts or the explicit unknown variant; argument and result validation remain distinct. Arithmetic examples are separate companion exercises.

### s06-l07: Validate Tool Inputs and Outputs
- **Practical:** Use `CatalogueRecord`, `CatalogueToolResult` and `validated_catalogue_result` in `examples/stages06-07/sdk_adapter.py`. Compare known ECA-101 and unknown ECA-999, then mutate input/return shape, Boolean type, prerequisites, title and cross-request ID.
- **Deliverable:** Validation observations for missing/extra/malformed fields, known/unknown variants and plausible but invented or mismatched catalogue facts; separately retain an actual live tool-use receipt when claimed.
- **Accept when:** Invalid tool arguments reject and invalid returned facts fail before reaching the model. `found=False, course=None` is the unknown result; final `CourseAnswer` validation does not replace this tool-return boundary.

### s06-l08: Add Conversation Memory with Sessions
- **Practical:** Use `run_dialogue_turn` and the seed/followup/control dialogue steps in `examples/stages06-07/sdk_adapter.py` with a new course-owned SQLite database; each invocation admits one separately budgeted actual SDK call.
- **Deliverable:** Two real turn records sharing one session and an unrelated session for comparison.
- **Accept when:** Record what the model actually recalls and whether the unrelated session admits missing information; do not assume success or manually inject an answer. The synthetic history-contract probe establishes SDK wiring, not model recall.

### s06-l09: Persist Agent Sessions with SQLite
- **Practical:** Continue the same `SQLiteSession` in a second process using the dialogue entrypoint and compare its persisted input with an unrelated control session. Inspect `session_contract_probe.py` as a separately labeled provider-free real-SDK contract exercise.
- **Deliverable:** Database path, restart transcript and separate-session isolation check.
- **Accept when:** History persists and stays session-specific; real process/SDK persistence evidence is distinct from learned recall. Private SQLite files stay out of commits, and application/SDK schemas never share an existing learner database.

### s06-l10: Inspect and Debug Agent Traces
- **Practical:** Use `--trace-file` in `examples/stages06-07/sdk_adapter.py` to retain actual local SDK spans and `ObservationHooks` timing/available usage. Hosted tracing remains a separate explicit telemetry opt-in.
- **Deliverable:** Actual trace identifier or supported trace export with model/tool/error timing.
- **Accept when:** Actual span IDs, hierarchy and outcomes remain distinct from printed application events; missing usage stays null, not zero. A local SDK export or requested hosted upload is not evidence of hosted acceptance.


## Stage 7

### s07-l01: Single-Agent vs Multi-Agent Architecture
- **Practical:** Compare a generalist with specialist inventory/policy/shipping agents for the synthetic support cases in `data/s07-support-cases.json`, using `examples/stages06-07/workflows.py` and `sdk_adapter.py` as separate application/SDK layers.
- **Deliverable:** An architecture decision backed by actual outputs, call count and observed latency.
- **Accept when:** Extra agents need a measured benefit; limitations and disagreement are recorded.

### s07-l02: Orchestration by Code vs Orchestration by the Model
- **Practical:** Compare code-directed support coordination in `examples/stages06-07/workflows.py` with the actual SDK manager mode in `sdk_adapter.py` for the same synthetic facts and request context.
- **Deliverable:** Two execution graphs and actual delegation traces.
- **Accept when:** Distinguish fixed sequencing from the model's observed choice of specialists.

### s07-l03: Run Agents Concurrently with asyncio.gather
- **Practical:** Run independent SDK specialists with `asyncio.gather` and a concurrency cap. Use `run_parallel_live`/parallel mode in `examples/stages06-07/sdk_adapter.py`; each role retains healthy, failed or unknown results without retrying uncertain requests.
- **Deliverable:** Per-agent results, timing and an injected failure demonstration.
- **Accept when:** Result identity survives completion-order changes; exceptions have explicit handling.

### s07-l04: Use Agents as Tools
- **Practical:** Expose a specialist using the SDK's agent-as-tool mechanism. Inspect inventory/policy `Agent.as_tool` calls with `SpecialistInput` in `examples/stages06-07/sdk_adapter.py`.
- **Deliverable:** A manager run showing the specialist tool invocation and returned result.
- **Accept when:** The manager retains control; distinguish this from transferring control through a handoff.

### s07-l05: Build a Manager-Agent Architecture
- **Practical:** Use the SDK support manager in `examples/stages06-07/sdk_adapter.py` to call inventory and policy specialists and synthesize only their attributed results, retaining missing facts as unresolved.
- **Deliverable:** Manager instructions, specialist contracts and actual execution trace.
- **Accept when:** The final answer uses actual specialist results and reports missing evidence.

### s07-l06: Delegate Work Through Handoffs
- **Practical:** Implement a handoff between an intake agent and a specialist with a clear transfer condition. Use triage mode and its shipping handoff in `examples/stages06-07/sdk_adapter.py`.
- **Deliverable:** A real SDK trace showing which agent owns each stage.
- **Accept when:** Only the intended recipient receives the handoff; responsibility for final response is explicit.

### s07-l07: Pass Context Between Agents
- **Practical:** Pass the actual `RequestContext` in `examples/stages06-07/workflows.py` through the SDK agents: request ID, product ID and policy version remain application-owned. Exercise two distinct request contexts and permission boundaries.
- **Deliverable:** Typed context schema and isolation observations for the two requests, with source attribution and tool permissions.
- **Accept when:** Do not forward unnecessary private conversation history; each agent sees the intended context.

### s07-l08: Control Agent Responsibilities and Boundaries
- **Practical:** Restrict each agent to its own tools and demonstrate attempts outside its role. Use the inventory, policy and shipping capability boundaries defined in `examples/stages06-07/workflows.py` and the matching SDK tools.
- **Deliverable:** A permissions matrix and positive/negative execution tests.
- **Accept when:** Instructions and application tool permissions agree; a specialist cannot silently acquire extra tools.

### s07-l09: Handle Multi-Agent Failures
- **Practical:** Exercise worker timeout, provider error and partial completion in a coordinated task. Inspect `specialists_with_fallback`: retain original failure, `unresolved`, `facts_recovered=False` and an unsent `draft_manual_review`; fallback is an application recovery action, never an invented product fact.
- **Deliverable:** Failure fixtures, bounded recovery logic and an actual partial-result report.
- **Accept when:** Unknown side effects are reconciled rather than repeated; unavailable results are labeled missing.

### s07-l10: Trace a Complete Multi-Agent Run
- **Practical:** Follow one complete multi-agent run from user request through delegation and synthesis. Use complete mode in `examples/stages06-07/sdk_adapter.py`: inventory/policy tools, handoff, shipping tool and receiving-agent synthesis. Compare `complete_lineage_observed` with actual callbacks; the deterministic application lineage is separately labeled.
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
- **Practical:** Scope a research question, evidence boundaries, report audience and completion criteria. Scope the current workshop evidence and any genuinely fetched sources separately; the legacy Cedar Library corpus is only a comparison fixture.
- **Deliverable:** A research brief separating corpus practice from live-web research.
- **Accept when:** The brief names coverage requirements and what would count as insufficient evidence.

### s09-l02: Define the Research Workflow and Agent Responsibilities
- **Practical:** Assign planning, search, evidence analysis, source review and report writing to explicit components. Inspect the planner/analyst in `projects/03-deep-research/research_lab/sdk_v2.py` and phase ownership in `pipeline_v2.py`.
- **Deliverable:** A workflow diagram and typed handoff contracts.
- **Accept when:** Each component has one accountable output; source review precedes supported conclusions.

### s09-l03: Build the Research Planning Agent
- **Practical:** Build a planner that decomposes a broad question into bounded research tasks. Use `research_lab/sdk_v2.py` and `capstone_v2.py` under `projects/03-deep-research`; the actual question drives the structured plan, not a fixed workshop-topic list.
- **Deliverable:** An actual generated plan with task IDs, coverage and stop conditions.
- **Accept when:** Tasks address the question and specify evidence needs rather than claiming results prematurely.

### s09-l04: Generate Focused Search Queries
- **Practical:** Generate distinct focused queries for each planned subtopic. Use the versioned plan/query contracts in `projects/03-deep-research/research_lab/contracts_v2.py` and retain task/dependency attribution.
- **Deliverable:** A query set with task mapping, rationale and duplicate detection.
- **Accept when:** Queries cover multiple angles without fabricating sources or implying searches already ran.

### s09-l05: Build the Web Search Agent
- **Practical:** Implement a real search-provider adapter alongside the labeled local-corpus baseline. Use `projects/03-deep-research/research_lab/brave_search.py`; preserve the actual raw Brave response, retrieval time and response hash. Search descriptions are snippets, publication dates may remain unknown and page reachability is not inferred.
- **Deliverable:** Actual query receipts, retrieved URLs and normalized results from a configured live search.
- **Accept when:** Do not present `research.py`'s synthetic corpus lookup as web search; failed queries remain visible.

### s09-l06: Capture Sources and Evidence
- **Practical:** Capture source title, URL/location, publication/access dates, excerpt and claim IDs. Use the current source/evidence contracts in `projects/03-deep-research/research_lab/contracts_v2.py`; an exact snippet is not an independently fetched full-page quotation.
- **Deliverable:** An evidence ledger and saved source snapshots when permitted.
- **Accept when:** Excerpts match the captured source; invented or inaccessible references cannot support conclusions.

### s09-l07: Build the Evidence Analysis Agent
- **Practical:** Use the actual analyst in `projects/03-deep-research/research_lab/sdk_v2.py` and `capstone_v2.py` to analyze the same current workshop/search evidence consumed by the report. Keep the older Cedar Library 45/70-minute corpus as a separate comparability exercise, never as workshop or live-web evidence.
- **Deliverable:** A structured findings table linking every conclusion to source IDs.
- **Accept when:** Primary findings cite the actual current source scope and disclose uncertainty; separate 45/70-minute observations retain their different measurement scopes and are not averaged or mixed into workshop results.

### s09-l08: Build the Research Report Writer
- **Practical:** Write a report from the actual plan and evidence ledger with citations and limitations. Use `projects/03-deep-research/research_lab/pipeline_v2.py` with its actual current plan, attributed evidence and findings.
- **Deliverable:** A report whose factual claims point to captured evidence.
- **Accept when:** Unsupported sections state uncertainty; no new sources appear only in the prose.

### s09-l09: Add Structured Research Outputs
- **Practical:** Define schemas for plans, queries, evidence, findings, sections and final reports. Inspect `research_lab/contracts_v2.py` and `schemas/research-v2.schema.json` under `projects/03-deep-research`, including versions, dependencies, exact excerpts and dangling-citation rejection.
- **Deliverable:** Schema validation tests for missing citation IDs, dates and malformed sections.
- **Accept when:** Invalid records fail at boundaries and cannot masquerade as complete research.

### s09-l10: Coordinate the Research Team Through Code
- **Practical:** Coordinate planning, search, normalization, analysis and reporting through explicit code dependencies. Use `projects/03-deep-research/research_lab/pipeline_v2.py` and its per-step `Journal`, recording admission before requests and raw known responses before validation.
- **Deliverable:** An execution log linking phase inputs, outputs and failure states.
- **Accept when:** Report generation waits for validated evidence and identifies missing branches.

### s09-l11: Manage Parallel Research Tasks
- **Practical:** Run independent research branches concurrently while preserving query and source attribution. Use the dependency-aware bounded scheduler in `projects/03-deep-research/research_lab/pipeline_v2.py`; independent tasks may overlap, prerequisites must complete first.
- **Deliverable:** A bounded parallel execution trace and equivalent sequential comparison.
- **Accept when:** Concurrency does not change citation identity or silently discard failed branches.

### s09-l12: Assemble a Complete Evidence-Based Report
- **Practical:** Assemble specialist sections into one report, deduplicate sources and verify claim references. Use current report contracts and reference validation in `projects/03-deep-research/research_lab/contracts_v2.py` and `pipeline_v2.py`.
- **Deliverable:** A merged report and a citation coverage check.
- **Accept when:** Every cited ID exists; duplicate source records do not count as independent corroboration.

### s09-l13: Handle Missing, Conflicting and Insufficient Evidence
- **Practical:** Test contradictory, stale, absent and incomparable evidence cases. Use `projects/03-deep-research/research_lab/quality_v2.py`; nullable dates, stale evidence, incomparable scope, link observations and untrusted instructions remain explicit.
- **Deliverable:** Observed reports and a rubric for uncertainty and conflict disclosure.
- **Accept when:** The system preserves disagreement and missing evidence instead of fabricating a confident answer.


## Stage 10

### s10-l01: Refactor the Research System into Python Modules
- **Practical:** Separate research agents, schemas, search adapters, orchestration, settings and UI modules. Use the current `research_lab/*_v2.py` modules under `projects/03-deep-research`; historical v1 test receipts do not certify this revised implementation.
- **Deliverable:** A module map and passing baseline/citation regression tests.
- **Accept when:** Imports do not trigger searches or launch a server; actual adapter behavior stays explicit.

### s10-l02: Build the Deep Research Gradio Interface
- **Practical:** Build a real Gradio interface for entering a research question and inspecting the final report. Use `projects/03-deep-research/research_lab/interface_v2.py`; retain genuine browser observations and separate private run directories per submission.
- **Deliverable:** A runnable UI with actual browser captures and a configured research run.
- **Accept when:** The interface displays real execution results and separates synthetic corpus mode from live web mode.

### s10-l03: Stream Research Progress to the User
- **Practical:** Stream planning, searching, analyzing and writing events from the actual orchestration. Use the async status stream in `projects/03-deep-research/research_lab/interface_v2.py` and observed per-step journal/spans from `pipeline_v2.py`; cancellation does not erase an unknown in-flight request.
- **Deliverable:** A timestamped event log and matching UI progress captures.
- **Accept when:** Events describe completed/current operations; failure and cancellation produce truthful terminal states.

### s10-l04: Display Plans, Sources and Agent Activity
- **Practical:** Display the plan, source ledger and public agent activity in separate UI panels. Use the current interface's public event allowlist and escaped report display; arbitrary payloads/private reasoning are excluded.
- **Deliverable:** Browser captures linking a report claim back to its source record.
- **Accept when:** Operational activity is visible without revealing hidden reasoning or provider credentials.

### s10-l05: Add Report Export and Email Delivery
- **Practical:** Export a report and implement an approval-gated email adapter with dry-run default. Use `projects/03-deep-research/research_lab/exports_v2.py` for Markdown/HTML/JSON/file hashes and recipient/report-bound approval. Actual approved local SMTP observation is distinct from the simulated outbox.
- **Deliverable:** A readable exported report plus preview/approval records; a live send requires a redacted real receipt.
- **Accept when:** Export preserves citations; recipient and report hash bind approval, and repeat submission is idempotent.

### s10-l06: Create a Research Evaluation Dataset
- **Practical:** Create evaluation cases for straightforward, ambiguous, conflicting and unanswerable questions. Use `projects/03-deep-research/data/s10-evaluation-v2.json`, preserving its representative questions, held-out split and explicit evidence/uncertainty criteria.
- **Deliverable:** A versioned dataset specifying expected coverage, evidence constraints and failure criteria.
- **Accept when:** Expected criteria do not contain fabricated live answers; include at least one deliberately unsupported case.

### s10-l07: Evaluate Source Quality and Report Completeness
- **Practical:** Score actual reports for source relevance, diversity, question coverage and cited factual support. Use the attributed `annotated_rubric` in `projects/03-deep-research/research_lab/quality_v2.py`; human 0–4 judgments require supporting evidence and remain separate from structural counts.
- **Deliverable:** A scored evaluation sheet with human-reviewed disagreements.
- **Accept when:** Several pages from one source are not independent evidence; scores retain supporting examples.

### s10-l08: Analyze Traces, Latency and Token Usage
- **Practical:** Analyze observed model/search events for latency, token usage and cost concentration. Use `trace_summary` and actual spans in the current `projects/03-deep-research/research_lab` implementation; distinguish summed concurrent spans from wall time and keep missing token usage null.
- **Deliverable:** A per-stage timing/usage table from one actual run and a measured optimization proposal.
- **Accept when:** Missing provider usage is marked unavailable; estimated cost is not reported as billed spend.

### s10-l09: Add Retries and Failure Recovery
- **Practical:** Use `projects/03-deep-research/research_lab/pipeline_v3.py` and `recovery_v3.py` for selective recovery in the same journal: bind a distinct reviewer's authorization to the exact known failed attempt, input and retained failure evidence, then give only that step a new attempt identity. Reuse validated completed sibling results.
- **Deliverable:** A retained original attempt/history, exact recovery authorization and resumed phase log showing a known HTTP/connection-refused or malformed-response case without repeating completed work.
- **Accept when:** Recovery keeps original inputs and all history, admits at most three total attempts and never replays current or historical IN_FLIGHT/UNKNOWN outcomes. Missing authorization, changed inputs or unverified failure classification remain held; test fixtures do not certify actual provider recovery.

### s10-l10: Deploy the Deep Research Application
- **Practical:** Use `projects/03-deep-research/research_lab/interface_v3.py`, `deploy_v3.py` and `deployment/research-v3/` to deploy the real research application. Resolve the exact direct-version requirements input into a complete tested transitive-hash lock; then exercise submit/report and the server-session-owned opaque-run-token File downloads after your own run completes.
- **Deliverable:** An actually resolved dependency hash lock, clean build/startup/health/private-state observations, reachable deployment and genuine browser evidence of own-run report download plus foreign-session/tampered-token refusal.
- **Accept when:** Deployment serves the actual v3 UI, private persistence and exact completed-run exports without accepting browser-supplied filesystem paths; download hashes match the completed report. `requirements.in`/`pyproject.toml` alone are resolver inputs, not lock/build evidence. Actual provider/Brave results, fresh-session browser behavior and a deployed build remain unproven until observed; secrets and other sessions stay protected.

### s10-l11: Complete the OpenAI Agents SDK Module
- **Practical:** Run a final demonstration connecting SDK tools, handoffs, research, tracing, evaluations and approval boundaries. Use `projects/03-deep-research/capstone_v2.py` for an explicitly admitted live capstone; preserve actual sources, raw responses, operational spans, human annotations and meaningful failure evidence.
- **Deliverable:** A module completion checklist linking each claim to actual project evidence.
- **Accept when:** Unfinished live SDK/UI/deployment work remains explicitly incomplete; local baseline tests alone do not certify those features.

