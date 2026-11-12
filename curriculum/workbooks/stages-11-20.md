# Practical workbook — stages 11–20

Run commands from the repository root. Each section is a learner exercise and acceptance contract, not a claim that the exercise has already been implemented or executed. Deterministic baselines and authored native framework paths are distinct. CrewAI, LangChain, LangGraph, Playwright MCP, Deep Agents and Gradio lessons retain their real framework requirements. Source pointers identify implementations, not observed runs or approval; inspect exact-current independent runtime evidence before describing successful execution. Credentialed provider calls and hosted tracing are optional manual external verification and must retain actual redacted outputs; missing access is recorded as incomplete, never replaced with invented results. New learner extensions belong in a separate workspace and must not overwrite supplied fixtures.

## Stage 11

### s11-l01 — Introduction to CrewAI
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l01.md`.
- Task: Map Alder Retail's advocate, skeptic and reviewer roles to support, challenge and verdict artifacts.
- Deliverable and acceptance: Deliver ownership and fact-citation contracts; company-screening researcher roles are a later extension, not this debate.

### s11-l02 — Agents, Tasks, Crews, Processes and Flows
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l02.md`.
- Task: Inspect Agent, Task, Crew, Process and Flow wiring in the authored debate.
- Deliverable and acceptance: Deliver distinct abstraction/dependency mappings; Flow scheduling with a substituted worker is not model-backed debate evidence.

### s11-l03 — Install CrewAI with uv
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l03.md`.
- Task: Inspect learning/pyproject.toml and its actual uv.lock, then prepare a dedicated frozen uv environment.
- Deliverable and acceptance: Deliver actual install/version/import receipts when run; lockfile existence alone is not installation proof.

### s11-l04 — Create Your First CrewAI Project
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l04.md`.
- Task: Compare the genuinely generated academy_practice starter with the authored academy_market_debate package.
- Deliverable and acceptance: Deliver the starter tree and explicit name/structure mapping; scaffold generation does not prove kickoff.

### s11-l05 — Understand CrewAI Project Structure
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l05.md`.
- Task: Trace YAML, core validation, tools, crew.py and main.py in the debate package.
- Deliverable and acceptance: Deliver the actual validated topic-to-task path, distinguishing the CLI starter from the authored application.

### s11-l06 — Configure Agents and Tasks with YAML
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l06.md`.
- Task: Inspect advocate/skeptic/reviewer agents and support/challenge/verdict YAML tasks.
- Deliverable and acceptance: Deliver matching identifiers, expected outputs and context edges; do not present nonexistent researcher/reviewer configuration as the existing application.

### s11-l07 — Configure Crews with Python
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l07.md`.
- Task: Follow build_crew from configuration to SDK Agent/Task/Crew construction and process selection.
- Deliverable and acceptance: Deliver constructor wiring and input contracts; construction is separate from actual provider task execution.

### s11-l08 — Build a Multi-Agent Debate Crew
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l08.md`.
- Task: Execute one independently admitted bounded Alder Retail debate using its real configured model path.
- Deliverable and acceptance: Deliver actual support/challenge/verdict outputs and citations; retain disagreement and never substitute fixture outputs for a real debate.

### s11-l09 — Connect crew.py and main.py
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l09.md`.
- Task: Trace load_facts and the validated topic into kickoff inputs in main.py.
- Deliverable and acceptance: Deliver actual topic-binding evidence; the entrypoint accepts --facts, not a company-symbol argument, and offline mode returns model_output=null.

### s11-l10 — Run and Inspect Your First Crew
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s11-l10.md`.
- Task: Inspect a real bounded main.py --run-live execution with explicit --facts and --model.
- Deliverable and acceptance: Deliver task progression, tool records and validated verdict; lesson 8 may share that same genuine evidence when scope matches, without inventing another run.

## Stage 12

### s12-l01 — The Five-Step Method for Building CrewAI Applications
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l01.md`.
- Task: Apply outcome, roles, tasks, tools and execution design to the reversible fictional retailer pilot.
- Deliverable and acceptance: Deliver a five-step design linking the fixed fact pack, three debate roles and validated verdict.

### s12-l02 — Design Clear Agent Roles and Goals
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l02.md`.
- Task: Compare advocate, skeptic and reviewer responsibilities and overlap against actual configuration.
- Deliverable and acceptance: Deliver distinct role contracts; all ordinary debate agents share the fact tool, so do not claim researcher-only permissions there.

### s12-l03 — Create Tasks with Measurable Expected Outputs
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l03.md`.
- Task: Specify support/challenge/verdict output requirements and validate citations against current fact IDs.
- Deliverable and acceptance: Deliver rejection examples for invented/duplicate citations and unsupported decisions; schema validity alone does not establish truth.

### s12-l04 — Pass Context Between CrewAI Tasks
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l04.md`.
- Task: Follow support→challenge→verdict context dependencies in build_crew.
- Deliverable and acceptance: Deliver configured edges and actual upstream-output handoff evidence only when a genuine kickoff has observed that behavior.

### s12-l05 — Add Search and Research Tools
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l05.md`.
- Task: Inspect external_research.py/research_main.py approved official-document retrieval variant.
- Deliverable and acceptance: Deliver actual URL/time/body-hash/excerpt or honest failure, with bounds and redirect controls; fixed retailer facts are not external information and direct HTTP is not model research.

### s12-l06 — Build Custom CrewAI Tools
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l06.md`.
- Task: Inspect the real typed CrewAI fact-search tool around FactSearch.
- Deliverable and acceptance: Deliver query/max_results schema, description and direct SDK invocation with fact IDs; direct invocation is not autonomous model selection.

### s12-l07 — Validate Tool Inputs and Results
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l07.md`.
- Task: Validate query bounds, result limits, source IDs and failed/exhausted retrieval outcomes.
- Deliverable and acceptance: Deliver blank-query/boolean-limit/unknown-citation/budget rejection cases, keeping absence and failure distinct from observed zero.

### s12-l08 — Add Structured Outputs with Pydantic
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l08.md`.
- Task: Inspect DebateVerdict and verdict Task output_pydantic wiring.
- Deliverable and acceptance: Deliver negative schema/citation cases and actual parsed task output only when genuinely produced; a local object is not provider-generated structured output.

### s12-l09 — Understand Sequential and Hierarchical Processes
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l09.md`.
- Task: Compare sequential and hierarchical configurations of the same retailer debate.
- Deliverable and acceptance: Deliver actual process/manager wiring; execution and delegation claims need genuine admitted traces rather than constructor success.

### s12-l10 — Add Memory and Shared Context to a Crew
- Source: `projects/04-market-intelligence/learning/src/academy_market_debate/`; detailed exercise: `projects/04-market-intelligence/learning/docs/s12-l10.md`.
- Task: Inspect memory_integration.py's explicit memory-enabled crew and scoped role views.
- Deliverable and acceptance: Deliver authorized actual remember/recall, scope denial, task reuse and owned-scope reset observations where claimed; ordinary debate framework memory stays disabled and ScopedMemory is only application state.

## Stage 13

### s13-l01 — Plan the Market Intelligence Crew
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Inspect projects/04-market-intelligence/companies.json and define the market crew's research boundary.
- Deliverable and acceptance: Deliver a scope document listing the fictional symbols, screening criteria, evidence requirements and final report; explicitly distinguish educational fixtures from live investment analysis.

### s13-l02 — Define Market Research Data Models
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Model Company, Criteria, evidence and ranked profile fields from market.py.
- Deliverable and acceptance: Deliver a schema diagram and validation cases for missing margin, nonfinite growth and evidence-free values; preserve the difference between missing and zero.

### s13-l03 — Build the Company Research Agent
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Inspect advanced/sources.py FixtureResearchAdapter business/product/competition records and the company-research task.
- Deliverable and acceptance: Deliver attributed dated fictional source documents for each supported symbol; the numeric-only baseline is not this substantive research adapter.

### s13-l04 — Build the Market Analysis Agent
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Inspect typed MarketResearch conditions and Signal records and connect them to the market-analysis task.
- Deliverable and acceptance: Deliver reconciled source dates, units, conditions and uncertainty; these are fictional dated scenarios, not verified present-day market observations.

### s13-l05 — Build the Screening and Ranking Agent
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Run python3 projects/04-market-intelligence/market.py and inspect deterministic scoring.
- Deliverable and acceptance: Deliver the three ranked profiles and rule-level score evidence; reproduce Cedar 3, Pine 2 and Maple 1 from supplied fixture data.

### s13-l06 — Build the Risk and Evidence Reviewer
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Add a reviewer that checks each credited metric against its evidence locator.
- Deliverable and acceptance: Deliver an unsupported-claim list containing the missing Pine margin evidence; the reviewer must not silently invent a margin or treat missing as zero observation.

### s13-l07 — Connect Market and Company Data Tools
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Use ResearchAdapter and Result success/absent/error contracts for company and sector data.
- Deliverable and acceptance: Deliver typed outputs plus unavailable/malformed-source cases retaining source SHA; absence must never become a fabricated fact.

### s13-l08 — Add Custom Analysis Tools
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Extend one calculation tool with explicit units and bounded numeric inputs.
- Deliverable and acceptance: Deliver tests for boundary values and malformed inputs; rerun python3 -m unittest discover -s tests -p 'test_projects_4_5.py' without changing fixture facts to satisfy a score.

### s13-l09 — Apply User-Defined Screening Criteria
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Run market.py with --min-growth .20 and compare criteria effects.
- Deliverable and acceptance: Deliver before/after criterion tables showing Cedar and Pine tied at 2 with deterministic symbol ordering; document that the threshold changed, not observed data.

### s13-l10 — Add Crew Memory and Context
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Persist validated profiles and screening criteria as crew context across tasks.
- Deliverable and acceptance: Deliver a round-trip saved context and a test rejecting a context from a different criteria version; evidence locators survive serialization.

### s13-l11 — Use a Hierarchical Crew Process
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Implement a real CrewAI hierarchical process with a manager and bounded evidence-correction request.
- Deliverable and acceptance: Deliver runnable configuration and, when credentials are available, a real delegation trace; the stdlib market runner alone does not demonstrate manager delegation.

### s13-l12 — Generate Structured Company Profiles
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Serialize each company into the shared profile schema with evidence, uncertainty and risks.
- Deliverable and acceptance: Deliver three schema-valid profiles retaining Pine's missing-margin uncertainty and each original symbol; no prose-only replacement of required fields.

### s13-l13 — Produce the Final Market Intelligence Report
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Assemble the integrated report through advanced/full_report.py and compare its source-backed coverage with the deterministic baseline.
- Deliverable and acceptance: Deliver actual report artifacts including business/products/competition, sector signals, rankings and uncertainty; local assembly is not a model crew run.

### s13-l14 — Evaluate the Quality of the Crew’s Analysis
- Source: `projects/04-market-intelligence/advanced/; projects/04-market-intelligence/crewai_adapter.py`; detailed exercise: `projects/04-market-intelligence/README.md`.
- Task: Test ranking stability, evidence removal and criteria changes against the report.
- Deliverable and acceptance: Deliver passing market tests plus a negative test showing removal of Cedar's margin evidence removes one point; retain unsupported-claim counts rather than hiding them.

## Stage 14

### s14-l01 — Introduction to AI Coding Agents
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Trace a coding-agent request through planning, file modification, command execution and test feedback.
- Deliverable and acceptance: Deliver a sequence diagram separating generated proposals from actual executed changes; identify the review boundary before running untrusted code.

### s14-l02 — Why Coding Agents Require Isolated Environments
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Compare a temporary directory with an OS-isolated execution environment.
- Deliverable and acceptance: Deliver a threat table covering host files, network, secrets and resource exhaustion; explicitly state that Python isolated import mode alone is not a security sandbox.

### s14-l03 — Install and Configure Docker
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Install Docker using the learner's authorized environment and verify the daemon and a minimal container.
- Deliverable and acceptance: Deliver actual docker version/info and a successful disposable test run; if unavailable, record the blocker rather than claiming host execution is containerized.

### s14-l04 — Understand Containers, Images, Volumes and Workspaces
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Map image layers, container lifetime, bind mounts and workspaces for the expense application.
- Deliverable and acceptance: Deliver a mount diagram identifying which files are read-only and which outputs persist after container deletion.

### s14-l05 — Build a Sandboxed File Tool
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Inspect team.safe_path and implement a workspace-constrained file interface.
- Deliverable and acceptance: Deliver tests rejecting ../ escape, absolute paths and symlink traversal while allowing a nested project file; never expose arbitrary host reads.

### s14-l06 — Build a Controlled Shell Execution Tool
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Design an allowlisted command tool with argument arrays, fixed cwd and captured execution metadata.
- Deliverable and acceptance: Deliver rejection tests for shell metacharacter injection and unauthorized binaries; do not implement validation by concatenating an untrusted shell string.

### s14-l07 — Run Python Code Inside Docker
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Inspect learning/Dockerfile, container_entrypoint.py and CONTAINER.md before preparing an independently reviewed digest-pinned image.
- Deliverable and acceptance: Deliver actual image/build/runtime inventory and generated-Python test output only after real Docker execution; mocks or a Dockerfile are not container evidence.

### s14-l08 — Install Project Dependencies Safely
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Inspect learning/pyproject.toml, actual uv.lock and the offline-cache image preparation workflow.
- Deliverable and acceptance: Deliver genuine frozen lock/check/sync and in-container runtime receipts when run; host uv setup does not demonstrate container installation.

### s14-l09 — Add Timeouts and Resource Limits
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Set wall-clock timeout, memory and CPU limits for a deliberately overlong disposable command.
- Deliverable and acceptance: Deliver actual termination evidence and a bounded log; demonstrate that the caller regains control without killing unrelated workloads.

### s14-l10 — Capture Command Output and Errors
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Capture stdout, stderr, exit code and timeout as separate structured fields.
- Deliverable and acceptance: Deliver one successful command and one failing command receipt; nonempty stderr alone must not imply failure when the exit code is zero.

### s14-l11 — Build Automated Testing Tools
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Trace semantic_team acceptance and QA receipts through container_entrypoint.py.
- Deliverable and acceptance: Deliver actual test IDs, stdout/stderr, return codes and requirement mapping; wrapper doubles and arithmetic fixtures are not generated-code execution.

### s14-l12 — Secure the Coding-Agent Environment
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-14-exercises.md`.
- Task: Review file, command, network, secret and approval boundaries of the sandbox.
- Deliverable and acceptance: Deliver a security checklist with adversarial tests for traversal and unapproved execution; explicitly preserve the Docker requirement for executing newly generated untrusted code.

## Stage 15

### s15-l01 — Design the Four-Agent Engineering Team
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Design the manager → architect → developer → QA workflow for an integer-cent expense calculator.
- Deliverable and acceptance: Deliver role contracts, artifact dependencies and completion criteria covering empty input, sum, negative amounts and invalid types.

### s15-l02 — Build the Product Manager Agent
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Trace semantic_team product-manager requirements including stories, acceptance and priorities.
- Deliverable and acceptance: Deliver the typed artifact and real response lineage where model behavior is claimed; construction supplies no model-written requirements.

### s15-l03 — Build the Software Architect Agent
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Design the pure total_expenses interface, CLI boundary and test layout.
- Deliverable and acceptance: Deliver component/interface diagrams and decisions explaining why floats and booleans are rejected as expense values.

### s15-l04 — Build the Developer Agent
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Follow the developer artifact into reviewed source and container-contained execution.
- Deliverable and acceptance: Deliver requirement-linked changes and actual execution receipts; generated code must not bypass Docker through the trusted template runner.

### s15-l05 — Build the Quality Assurance Agent
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Inspect QA-role artifacts, immutable acceptance tests and generated-test checks.
- Deliverable and acceptance: Deliver actual failures/successes and test IDs; QA prose or weakened tests do not establish correctness.

### s15-l06 — Define Engineering Tasks and Dependencies
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Define dependencies between specification, architecture, implementation, tests and packaging.
- Deliverable and acceptance: Deliver a task DAG that prevents packaging before QA success and exposes the artifact required to begin each task.

### s15-l07 — Pass Specifications and Context Between Agents
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Trace semantic_team envelope/consume across role revisions and response hashes.
- Deliverable and acceptance: Deliver exact content/response lineage for each consumed artifact; the older workflow.Envelope example is distinct from the integrated path.

### s15-l08 — Build uv-Based Sandbox Tools
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Inspect allowlisted sandbox uv commands and the whole-container locked runtime.
- Deliverable and acceptance: Deliver actual in-container uv/environment/test observations when authorized; host venv evidence is insufficient.

### s15-l09 — Generate Project Requirements and Dependencies
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Compare learning/pyproject.toml and actual uv.lock with the generated expense app dependency contract.
- Deliverable and acceptance: Deliver real orchestrator dependencies and the standard-library-only app declaration with genuine frozen installation receipts when run; do not claim this project lacks a lockfile.

### s15-l10 — Run the Engineering Crew Inside Docker
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Trace container_launch.launch through host broker transport and in-container CrewAIRoleProvider/semantic_team execution.
- Deliverable and acceptance: Deliver actual container, role-request, framework-output and final-QA lineage from a coherent admitted run; the host broker must not execute generated source.

### s15-l11 — Execute Automated Tests
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Inspect generated QA/developer tests and immutable acceptance execution through container_entrypoint.py.
- Deliverable and acceptance: Deliver actual generated-project receipts and requirement observations; six baseline tests alone do not establish the new team.

### s15-l12 — Diagnose and Repair Failed Builds
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Trace semantic_team.run_team bounded repair with preserved acceptance tests and role revisions.
- Deliverable and acceptance: Deliver genuine failing receipt, diagnosis, source diff and retest where observed; uncertain provider requests remain unresolved without automatic replay.

### s15-l13 — Review the Completed Application
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Review the delivered application against the product specification and threat boundaries.
- Deliverable and acceptance: Deliver a requirement-to-test matrix and explicit unresolved limitations; QA approval depends on actual test output and reviewed source.

### s15-l14 — Package the Source Code and Documentation
- Source: `projects/05-sandboxed-engineering/learning/delivery_package.py:package_delivery`; successful `container_entrypoint.py` route; `container_launch.py:verified_delivery`. Detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md` section s15-l14; execution boundary: `learning/CONTAINER.md`.
- Task: After an admitted real whole-crew container run, inspect its exact generated application, setup/usage documentation, dependency declarations and tests through the completion-bound delivery bridge. Verify the returned `delivery.zip` and `delivery-receipt.json`, then perform a fresh documented extraction/setup/test in the approved execution boundary without executing unreviewed generated code on the host.
- Deliverable and acceptance: Retain the exact final generated files, typed role artifacts and actual response lineage, original completion event, all attempted-test receipts, immutable course and independent QA tests, and the requirement acceptance matrix. Bind the final source and actual passed container receipt to the whole-team result; verify archive/member inventory, exact bytes, CRC and hashes against the delivery receipt and embedded manifest. Preserve failed attempts and review outputs for credentials before sharing. A fixed `team.py` template ZIP or explicit `OFFLINE_FIXTURE_NOT_PRODUCTION` package cannot certify this generated whole-crew delivery; genuine model/container execution, clean extraction/setup/tests and independent acceptance remain required observations rather than claims made by this workbook.


### s15-l15 — Complete the Sandboxed Engineering Team
- Source: `projects/05-sandboxed-engineering/learning/`; detailed exercise: `projects/05-sandboxed-engineering/learning/stage-15-exercises.md`.
- Task: Demonstrate the whole four-role container/broker workflow and delivery package.
- Deliverable and acceptance: Deliver genuine response/source/test/package lineage and outstanding limitations; authored code is not evidence of Docker, provider, installation or capture success.

## Stage 16

### s16-l01 — Understanding the LangChain Ecosystem
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l01.md`.
- Task: Map LangChain, LangGraph, LangSmith and Deep Agents to the Academy documentation-lookup case.
- Deliverable and acceptance: Deliver the four distinct responsibilities; the ecosystem map is a design artifact, not a nonexistent runnable function.

### s16-l02 — Models, Tools, Agents and Orchestration
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l02.md`.
- Task: Trace make_agent, academy_page and native message/tool envelopes in native_features.py.
- Deliverable and acceptance: Deliver component ownership and request/result identities; scripted SDK messages do not prove provider intelligence.

### s16-l03 — Invoke and Stream Model Responses
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l03.md`.
- Task: Use invoke_and_stream with native AIMessage and AIMessageChunk objects.
- Deliverable and acceptance: Deliver separate invoke and streamed observations, SDK chunk addition and interrupted/empty stream handling; these are separate requests and their stochastic text need not match.

### s16-l04 — Create Tools with the Tool Decorator
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l04.md`.
- Task: Inspect the @tool-decorated academy_page schema and invoke it on valid/invalid page IDs.
- Deliverable and acceptance: Deliver schema and direct invocation observations; arithmetic is a separate framework adapter rather than this stage's case.

### s16-l05 — Bind Tools to Language Models
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l05.md`.
- Task: Use bind_and_inspect to bind academy_page and inspect tool_calls/invalid_tool_calls without executing proposals.
- Deliverable and acceptance: Deliver actual bound schema and captured arguments when run; the application dispatch helper is not model binding.

### s16-l06 — Add Structured Outputs
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l06.md`.
- Task: Use PageAnswer with structured_answer and make_agent(structured=True).
- Deliverable and acceptance: Deliver native structured-output observations and negative cases; valid Pydantic syntax alone does not establish factual grounding.

### s16-l07 — Build Your First LangChain Agent
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l07.md`.
- Task: Construct make_agent and invoke it with explicit thread_config on Academy documentation.
- Deliverable and acceptance: Deliver actual tool-loop and cited response evidence when run, distinguishing deterministic SDK-model execution from configured-provider behavior.

### s16-l08 — Add Agent Middleware
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l08.md`.
- Task: Inspect make_agent model_policy and tool_policy middleware.
- Deliverable and acceptance: Deliver bounded-input/tool rejection, request-local context override and redacted correlated timing evidence; traces exclude prompts, arguments and secrets.

### s16-l09 — Add Short-Term Memory
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l09.md`.
- Task: Use thread_config, recent_turns and prune_thread with the agent checkpointer.
- Deliverable and acceptance: Deliver two-turn retention, thread separation and whole-turn pruning; context trimming differs from stored-history pruning, and InMemorySaver is process-local.

### s16-l10 — Trace and Inspect Agent Runs
- Source: `examples/s16/native_features.py`; detailed exercise: `labs/s16/s16-l10.md`.
- Task: Inspect actual model/tool spans including an error path through make_agent.
- Deliverable and acceptance: Deliver trace IDs, parent linkage, elapsed time and outcome from genuine SDK execution; local events do not prove a hosted LangSmith observation.

## Stage 17

### s17-l01 — Introduction to LangGraph
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l01.md`.
- Task: Compare graph_workflow.py and native_graph_features.py orchestration for Academy support examples.
- Deliverable and acceptance: Deliver state/node diagrams distinguishing parallel evidence, tool-loop and recovery graphs; deterministic graph concepts do not require a model call.

### s17-l02 — Graphs, State, Nodes and Edges
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l02.md`.
- Task: Identify EvidenceState, AgentState, RecoveryState and actual START/END/conditional edges.
- Deliverable and acceptance: Deliver per-graph field-write ownership and transitions rather than a falsely combined single execution.

### s17-l03 — State Reducers and Shared Graph Data
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l03.md`.
- Task: Exercise build_parallel_graph's merge_evidence reducer with duplicates and conflicts.
- Deliverable and acceptance: Deliver actual native sibling reduction retaining compatible evidence and rejecting conflicts; ordinary Python thread tests are not native graph evidence.

### s17-l04 — Build Your First LangGraph Workflow
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l04.md`.
- Task: Build and compile a documented evidence, tool-loop or recovery graph.
- Deliverable and acceptance: Deliver actual initial state, node transitions and terminal result; the order-approval adapter is separate.

### s17-l05 — Add Tool-Calling Nodes
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l05.md`.
- Task: Trace academy_product through build_tool_loop and real ToolNode.
- Deliverable and acceptance: Deliver linked AIMessage request ID and ToolMessage before the next reasoning state; deterministic request production is not provider-selected tool use.

### s17-l06 — Create Conditional Edges
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l06.md`.
- Task: Inspect conditional routes in build_tool_loop and build_recovery_graph.
- Deliverable and acceptance: Deliver observed continuation/completion/retry/fallback/intervention routes as applicable; deterministic routing is within the original objective.

### s17-l07 — Build Agent Loops with Graphs
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l07.md`.
- Task: Run build_tool_loop with normal completion and never_finish under max_rounds.
- Deliverable and acceptance: Deliver native loop histories and incomplete budget-exhausted outcome; tool-cycle budget and SDK recursion limit are different controls.

### s17-l08 — Understand Supersteps and Graph Execution
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l08.md`.
- Task: Inspect parallel siblings, thread barrier and AND-join in build_parallel_graph.
- Deliverable and acceptance: Deliver native events showing prior-superstep reads and join after both siblings; elapsed time alone does not establish concurrency.

### s17-l09 — Add Error and Recovery Paths
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l09.md`.
- Task: Exercise build_recovery_graph transient, permanent and invalid-data routes.
- Deliverable and acceptance: Deliver actual attempts and finish/fallback/intervention outcomes; cached synthetic fallback is not a successful live lookup.

### s17-l10 — Trace Graph Runs with LangSmith
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l10.md`.
- Task: Use the explicit --langsmith option only with separately authorized hosted tracing.
- Deliverable and acceptance: Deliver an actually inspected hosted run with node/tool transitions and redaction; emitted SDK URLs and local traces do not replace the named LangSmith observation.

### s17-l11 — Add Checkpoints to LangGraph Applications
- Source: `examples/s17/native_graph_features.py; examples/s17/graph_workflow.py`; detailed exercise: `labs/s17/s17-l11.md`.
- Task: Attach a checkpointer to a native graph and inspect get_state/get_state_history for an explicit thread.
- Deliverable and acceptance: Deliver actual checkpoint IDs/resume points; distinguish process-local storage from the durable SQLite route used in Stage 18.

## Stage 18

### s18-l01 — Add Conversation Memory to LangGraph
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l01.md`.
- Task: Use native_durability.State.messages and sqlite_graph to append turns and replace one message by stable ID.
- Deliverable and acceptance: Deliver native add_messages state before/after correction; earlier assistant quotations, ledger observations and historical checkpoints may retain old text, so correction is not privacy erasure.

### s18-l02 — Persist Agent State with SQLite
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l02.md`.
- Task: Use sqlite_graph with separate durable checkpoint and MockLedger files, then close and reopen in another process.
- Deliverable and acceptance: Deliver actual continuation and file identities; these separate SQLite stores are not a distributed atomic transaction.

### s18-l03 — Use Threads to Separate Agent Sessions
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l03.md`.
- Task: Interleave two conversation threads using explicit native thread_config identities.
- Deliverable and acceptance: Deliver disjoint current histories and empty-ID rejection; thread partitioning is distinct from authentication and retention/deletion policy.

### s18-l04 — Replay Previous Agent Runs
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l04.md`.
- Task: Select a native historical snapshot configuration and invoke its subsequent nodes.
- Deliverable and acceptance: Deliver original/replay checkpoint IDs and node observations; replay re-executes nodes and does not undo prior external actions.

### s18-l05 — Fork Agent State from Earlier Checkpoints
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l05.md`.
- Task: Update state at a historical checkpoint and execute the modified branch.
- Deliverable and acceptance: Deliver parent/fork/final checkpoints preserving the original snapshot; copying a custom Sessions row alone is not native continuation.

### s18-l06 — Understand LangGraph Time Travel
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l06.md`.
- Task: Compare actual historical replay and edited-fork continuation in the durable native example.
- Deliverable and acceptance: Deliver a timeline identifying rerun nodes and preserved state; time travel does not roll back real-world effects.

### s18-l07 — Pause and Resume Agent Execution
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l07.md`.
- Task: Pause native review mode through interrupt and resume with the current proposal-bound decision.
- Deliverable and acceptance: Deliver actual paused/resumed state and strict validation; the fixture reviewer label is not authenticated human approval evidence.

### s18-l08 — Add Human-in-the-Loop Interrupts
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l08.md`.
- Task: Trace native review before dispatch and inspect MockLedger while approval is pending.
- Deliverable and acceptance: Deliver zero mock effects before exact approval and on rejection; local teaching effects are not remote deliveries or a production identity service.

### s18-l09 — Approve, Edit or Reject Agent Actions
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l09.md`.
- Task: Exercise native review approve/edit/reject with the exact current proposal digest.
- Deliverable and acceptance: Deliver edit clearing approval and re-interrupting on a changed action identity; a fresh exact decision must precede dispatch.

### s18-l10 — Recover from Interrupted and Failed Runs
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l10.md`.
- Task: Use recovery mode to fail after a completed first step, restart and resume the second step.
- Deliverable and acceptance: Deliver actual recovery with completed mock effects deduplicated; unknown outcomes stay unresolved without replay, while terminal validation requires explicit input repair.

### s18-l11 — Build Agents with LangChain create_agent
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l11.md`.
- Task: Build the higher-level documentation agent using examples/s16/native_features.py make_agent.
- Deliverable and acceptance: Deliver actual create_agent tool/state behavior compared with explicit graphs, labeling fixture/provider scope; durable_sessions.py does not implement create_live_agent and arithmetic is a separate case.

### s18-l12 — Add Structured Outputs and Middleware
- Source: `examples/s18/native_durability.py; examples/s16/native_features.py`; detailed exercise: `labs/s18/s18-l12.md`.
- Task: Inspect PageAnswer and native_features.py structured configuration and model/tool middleware.
- Deliverable and acceptance: Deliver schema, redaction, context and policy observations with correlation IDs when executed; structured validity never substitutes for an independent action approval.

## Stage 19

### s19-l01 — Introduction to Browser Automation for AI Agents
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l01.md`.
- Task: Define browser-agent permissions for the owned Academy documentation fixture.
- Deliverable and acceptance: Deliver navigation/extraction versus consequential-action boundaries and stale-selector/dialog failure cases; personal accounts are excluded.

### s19-l02 — Set Up Playwright for Browser Control
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l02.md`.
- Task: Install or use the admitted Playwright/Chromium environment and inspect browser_research.actual_browser.
- Deliverable and acceptance: Deliver a genuine owned-browser launch and page capture when run; FixtureBrowser HTML parsing is not browser execution.

### s19-l03 — Navigate and Inspect Websites
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l03.md`.
- Task: Navigate actual owned index/docs pages, wait for status and inspect URL/title/links.
- Deliverable and acceptance: Deliver genuine page-state and selector observations; sleep alone is not proof loading completed.

### s19-l04 — Extract Structured Information from Web Pages
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l04.md`.
- Task: Extract typed documentation records from the actual owned DOM.
- Deliverable and acceptance: Deliver JSON matching the observed source and missing/duplicate-field rejection; documentation fixtures must not be presented as live workshop listings.

### s19-l05 — Work with Forms and Interactive Elements
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l05.md`.
- Task: Use prepare_form to fill actual owned Name/Topic/checkbox controls without submitting.
- Deliverable and acceptance: Deliver genuine selected values and zero-submission/request evidence; use no personal account or external recipient.

### s19-l06 — Connect Playwright Through MCP
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l06.md`.
- Task: Connect create_browser_mcp's actual server to a client and discover/call inspect_page.
- Deliverable and acceptance: Deliver genuine protocol/tool-discovery/read result and cleanup evidence; direct Playwright is not MCP connectivity.

### s19-l07 — Build a Browser Research Agent
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l07.md`.
- Task: Use native_harness browser_tools/create_native_agent to connect owned index search, navigation, extraction and research synthesis.
- Deliverable and acceptance: Deliver actual bounded URL/source-SHA observations and supported report claims; resumable_research alone is deterministic infrastructure, not native research-agent evidence.

### s19-l08 — Introduction to Deep Agents
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l08.md`.
- Task: Inspect native_harness planner, FilesystemBackend, skills, specialist and SQLite wiring.
- Deliverable and acceptance: Deliver a harness map separating authored capability, construction and observed work; filesystem scoping is not an OS sandbox.

### s19-l09 — Planning and File-System Tools
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l09.md`.
- Task: Use native plan/file tools in a fresh dedicated workspace.
- Deliverable and acceptance: Deliver actual todo/tool history, research.md and report.md with observed sources; prewritten artifacts are not model-generated plans.

### s19-l10 — Progressive Disclosure with Agent Skills
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l10.md`.
- Task: Inspect install_skills and skills=[/skills/] integration, then observe selected native body reads.
- Deliverable and acceptance: Deliver metadata-first selection and selected-body access with unrelated-calendar unread; custom Skills.disclose alone does not demonstrate native disclosure.

### s19-l11 — Build Skills with SKILL.md
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l11.md`.
- Task: Inspect installed source-research and report-writing SKILL.md files.
- Deliverable and acceptance: Deliver frontmatter, triggers, procedure and resource references applied to the owned task; skill instructions remain separate from untrusted page text.

### s19-l12 — Delegate Tasks to Subagents
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l12.md`.
- Task: Observe native task delegation to source-researcher and evidence-critic.
- Deliverable and acceptance: Deliver actual specialist requests/results and parent synthesis preserving discrepancies; ThreadPool workers and a model's unsupported claim of delegation are insufficient.

### s19-l13 — Build Long-Running Agent Workflows
- Source: `examples/s19/browser_research.py; examples/s19/native_harness.py`; detailed exercise: `labs/s19/s19-l13.md`.
- Task: Use native_harness run_phase start/resume with the same SQLite checkpoints and pinned sources/artifacts.
- Deliverable and acceptance: Deliver genuine separate-process interruption/continuation, native plan/specialist history and final evaluation; changed sources/artifacts block resume and contract checks are not human content approval.

## Stage 20

### s20-l01 — Design the Browser Task Sidekick
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l01.md`.
- Task: Map pipeline.SidekickApplication, NativePlanner, PlaywrightSandboxExecutor, SessionController and ui_gradio.build_ui.
- Deliverable and acceptance: Deliver one persisted objective→plan→observation→evaluation→approval→artifact lifecycle; FixturePlanner is a labeled alternative, never silent native fallback.

### s20-l02 — Build the Sidekick Planner
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l02.md`.
- Task: Trace NativePlanner.plan from the trusted objective through native specialists and parse_model_plan.
- Deliverable and acceptance: Deliver actual request/result and strict origin/tool/dependency checks when run; uncertain planning intent is not automatically resubmitted.

### s20-l03 — Build the Browser Executor
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l03.md`.
- Task: Dispatch allowed actions through integrated PlaywrightSandboxExecutor.
- Deliverable and acceptance: Deliver genuine navigation, extraction and exact-approved synthetic interaction observations; earlier urllib receipts are separate HTTP evidence, not Playwright evidence.

### s20-l04 — Build the Task Evaluator
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l04.md`.
- Task: Trace SidekickApplication.evaluate/revise using persisted source-attributed findings.
- Deliverable and acceptance: Deliver actual COMPLETE/CONTINUE/REVISE/STOP decisions; generated prose cannot override missing observations or unknown execution.

### s20-l05 — Add Research and File Tools
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l05.md`.
- Task: Use pipeline.Workspace and artifact execution to preserve research outputs.
- Deliverable and acceptance: Deliver actual owned json/csv/md artifacts with current hashes/provenance and traversal rejection; UI links resolve only recorded files for the current session/task.

### s20-l06 — Add Memory and Persistent Task State
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l06.md`.
- Task: Close and reopen the integrated SQLite application for the same owned session/task.
- Deliverable and acceptance: Deliver retained counters, completed observations and current pending approval state; an ambiguous started action must not be replayed to manufacture progress.

### s20-l07 — Add Middleware and Execution Policies
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l07.md`.
- Task: Follow validation, policy checks and events on the actual integrated dispatch path.
- Deliverable and acceptance: Deliver genuine rejected-origin/input cases and redacted correlated traces; application wrappers must not be mislabeled native middleware.

### s20-l08 — Add Human Approval for Sensitive Actions
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l08.md`.
- Task: Pause before an exact sensitive synthetic Playwright action.
- Deliverable and acceptance: Deliver zero preapproval effects, owner/expiry enforcement and rejection; unsupported upload/download/message families stay explicitly unsupported.

### s20-l09 — Implement Approve, Edit and Reject Controls
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l09.md`.
- Task: Use actual Gradio callbacks wired to SidekickApplication.decide for approve/edit/reject.
- Deliverable and acceptance: Deliver real payload/predicate histories, fresh approval after edits and exact synthetic effect count; button construction alone does not establish behavior.

### s20-l10 — Add Subagents for Specialist Tasks
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l10.md`.
- Task: Inspect NativePlanner catalog-researcher/evidence-auditor delegation and completed native task messages.
- Deliverable and acceptance: Deliver genuine contributions and parent plan synthesis when observed; finite threads are not model subagents and specialists cannot authorize effects.

### s20-l11 — Add Progress Tracking and Visible Checklists
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l11.md`.
- Task: Render integrated snapshots into the real checklist/progress UI.
- Deliverable and acceptance: Deliver actual pending/active/approval-held/complete/uncertain transitions from durable records; executing work is not complete.

### s20-l12 — Test the Sidekick on Real-World Tasks
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l12.md`.
- Task: Exercise harmless Academy tasks through native planning, owned browser, evaluation and approvals.
- Deliverable and acceptance: Deliver actual outcomes, failures/recovery and source-backed objective coverage; contract test doubles do not substitute for genuine integration observations.

### s20-l13 — Build the Gradio Interface
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l13.md`.
- Task: Start ui_gradio.py using explicit model, owned database/workspace and admitted browser options.
- Deliverable and acceptance: Deliver actual integrated interactions, genuine browser PNG views, owned artifact links and final evaluation; Blocks construction or fixture mode is not a completed native run.

### s20-l14 — Trace and Evaluate Sidekick Runs
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l14.md`.
- Task: Export actual task traces through SidekickApplication.export_trace.
- Deliverable and acceptance: Deliver measured timings, interventions, source coverage and redaction evidence; report observed performance only and distinguish local from hosted tracing.

### s20-l15 — Complete the Browser Task Sidekick
- Source: `projects/06-browser-sidekick/pipeline.py; advanced.py; ui_gradio.py`; detailed exercise: `labs/s20/s20-l15.md`.
- Task: Demonstrate one integrated native task through specialists, Playwright, approval, persistence, artifacts and Gradio.
- Deliverable and acceptance: Deliver exact source/runtime/request/result lineage and actual final evaluation; preserve failures, gaps and unknown-effect no-replay instead of equating authored integration with observed success.

