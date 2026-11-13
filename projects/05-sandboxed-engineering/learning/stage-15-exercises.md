# Stage 15: exercises and reference solutions

Use `learning/README.md` for repository checks. Distinguish the baseline control fixtures in `workflow.py` and `sandbox.py` from the generated application workflow in `semantic_team.py`, `crewai_roles.py` and `container_entrypoint.py`. The recorded worked example below is an observed private course run; it does not certify a fresh installation or the current public runtime. New runs require their own actual receipts.

## s15-l01: Design the Four-Agent Engineering Team

Objective: Define the workflow, artifacts, responsibilities, sandbox permissions and project completion criteria.

Implementation: `reference-contracts.json`.

Exercise: Assign each artifact and permission to PM, architect, developer and QA; write completion criteria.

Reference solution: PM produces criteria; architect binds them to modules; developer writes src; QA runs immutable tests. Completion requires all observed criteria, real role evidence and independent review.

Verification: `test_tasks`.

## s15-l02: Build the Product Manager Agent

Objective: Convert a product request into user stories, requirements, acceptance criteria and delivery priorities.

Implementation: `semantic_team.py:validate_requirements` and `crewai_roles.py:CrewAIRoleProvider`; `workflow.py` supplies separate baseline contract exercises.

Exercise: Produce measurable expense stories and criteria; try an empty criteria object or malformed identifier.

Reference solution: Use R1 empty→0, R2 125+275→400 and R3 invalid-input rejection. Empty or unlabelled criteria fail validation; human reference is not a provider response.

Verification: `test_contracts`.

## s15-l03: Build the Software Architect Agent

Objective: Transform requirements into components, data flows, interfaces and an implementation plan.

Implementation: `semantic_team.py:validate_architecture` and `crewai_roles.py:CrewAIRoleProvider`.

Exercise: Bind a module/interface to every approved criterion and explain why dependencies are empty.

Reference solution: In the generated workflow, use the application component `expense_app.py` and `total_expenses(amounts)`, bound to the current requirements hash and every R ID. Put the test and documentation deliverables in the implementation plan; they are not extra application components. The earlier `sandbox.py` control fixture uses a different `src/` workspace layout. Unknown IDs and stale revisions block consumption.

Verification: `test_unknown_reference`.

## s15-l04: Build the Developer Agent

Objective: Generate and modify source code according to the approved architecture and task specification.

Implementation: `semantic_team.py:validate_files` and `run_team`; `sandbox.py:FileTools` is a separate control exercise.

Exercise: Generate the approved four-file application bundle, then inspect a source-only repair against the retained implementation hash. In the separate FileTools exercise, try an out-of-scope write.

Reference solution: The generated bundle contains `expense_app.py`, `test_expense_app.py`, `README.md` and `requirements.txt`. A repair changes only the approved application source and keeps developer, QA and course tests intact. The separate FileTools fixture permits writes only in its `src/` scope.

Verification: `test_stale_write`.

## s15-l05: Build the Quality Assurance Agent

Objective: Review requirements, create tests, run validations and report defects to the development workflow.

Implementation: `semantic_team.py:run_team`, its immutable `CourseAcceptance` tests, and the QA role in `crewai_roles.py`.

Exercise: Inspect the recorded generated implementation, independent QA tests and actual failure receipt. Identify the failing requirement and distinguish an application error from an infrastructure error.

Reference solution: In the recorded generated run, arithmetic passed; two invalid-type cases errored because the architecture used `TypeError` while the unchanged course acceptance suite expected `ValueError`. This is an R3 contract mismatch. The separate baseline fixture returning 125 rather than 400 is a different, explicitly seeded R2 exercise. Keep each example's own failing and passing receipts; do not substitute one story for the other.

Verification: `test_actual_arithmetic_failure_and_repair`.

## s15-l06: Define Engineering Tasks and Dependencies

Objective: Sequence planning, design, implementation and testing so each agent receives the required artifacts.

Implementation: `workflow.py:task_order`.

Exercise: Introduce a missing prerequisite, a cycle and a failed predecessor in the role graph.

Reference solution: Unknown prerequisites and cycles fail early; failed or absent predecessor artifacts prevent dispatch.

Verification: `test_tasks`.

## s15-l07: Pass Specifications and Context Between Agents

Objective: Share structured requirements, architecture decisions, code locations and test feedback between specialists.

Implementation: `workflow.py:Envelope`.

Exercise: Hash a requirements envelope, mutate the content and consume it using the old SHA; then try obsolete revision 2.

Reference solution: Both mismatches fail; transfer role, schema version, revision, exact SHA and honest provenance rather than an unstructured success sentence.

Verification: `test_handoff`.

## s15-l08: Build uv-Based Sandbox Tools

Objective: Give the team controlled commands for creating environments, installing packages and running applications.

Implementation: `sandbox.py:COMMANDS`.

Exercise: Construct uv-version, uv-venv, uv-lock-check and uv-sync commands without accepting arbitrary shell text.

Reference solution: Commands execute inside Docker only, with read-only source inputs, owned writable environment/cache outputs and offline/frozen dependency controls. Recorded controlled runs observed uv 0.13.8, an environment using CPython 3.12.16, a 141-package lock check and installation of 137 locked packages. These observations concern controlled commands, not a claim that an agent independently selected every command; a fresh runtime needs fresh receipts.

Verification: `test_uv_offline`.

## s15-l09: Generate Project Requirements and Dependencies

Objective: Create and validate dependency declarations based on the planned application architecture.

Implementation: `workflow.py:architecture`.

Exercise: Propose an unnecessary external dependency for this standard-library expense calculator and inspect the rejection.

Reference solution: Dependencies remain empty for the chosen interface. A real lockfile must be generated by uv and checked; no fabricated uv.lock is supplied.

Verification: `test_dependency_rejected`.

## s15-l10: Run the Engineering Crew Inside Docker

Objective: Execute the complete team workflow within an isolated project workspace.

Implementation: `container_entrypoint.py`, `container_launch.py`, `semantic_team.py:run_team` and `crewai_roles.py:CrewAIRoleProvider`.

Exercise: Trace the four actual roles through typed requirements, architecture, implementation and QA, using the recorded whole-container run. For a new run, first prepare the image and host broker boundary; credentials stay outside the no-network container.

Reference solution: The recorded workflow contains product-manager, architect, developer and quality-assurance roles. Planning, implementation, review and repair are stages, not a fifth agent. Retain exact provider-response bindings and actual container receipts separately. The recorded private runtime used an explicit interpreter-resolution correction; its success is not proof that an uncorrected public checkout runs.

Verification: Inspect actual role bindings and container receipts; repository control tests alone do not prove a new provider run.

## s15-l11: Execute Automated Tests

Objective: Run unit and integration tests and return structured failures to the responsible agents.

Implementation: `container_entrypoint.py:InsideContainerExecutor` and `semantic_team.py:validate_receipt`; `sandbox.py` provides separate command-control fixtures.

Exercise: Map exit status, timeout and structured acceptance evidence to QA; try fake model-says-passed provenance. Compare the recorded first 22-test execution with the final execution, including the immutable QA and course-test hashes.

Reference solution: Only actual Docker or explicitly labelled executed fixture evidence is accepted; runtime failure and absent receipt never become PASS.

Verification: `test_fake_success_denied`.

## s15-l12: Diagnose and Repair Failed Builds

Objective: Use test and runtime feedback to implement bounded, traceable repair cycles.

Implementation: `semantic_team.py:run_team`; `workflow.py:bounded_repair` remains a separate baseline control fixture.

Exercise: Trace the recorded exception-contract mismatch from the 22-test failure through QA review, one developer source patch and the unchanged 22-test rerun. Separately test exhausted budgets, repeated patch identities and attempted test modification in the baseline controls.

Reference solution: The actual generated repair introduced `InvalidAmountError(TypeError, ValueError)` for invalid types, satisfying both exception contracts while still rejecting the input. Discuss this compatibility tradeoff explicitly: multiple inheritance is the observed repair, not a general instruction to hide conflicting requirements. Prefer reconciling the exception contract before implementation in a new project. No test was weakened or rewritten; budget exhaustion and repeated patches remain stops.

Verification: `test_budget_exhausted`.

## s15-l13: Review the Completed Application

Objective: Compare the implementation against requirements, acceptance criteria and quality standards.

Implementation: `reference-contracts.json`.

Exercise: Compare implementation and actual evidence against R1–R3, including negative, bool and decimal rejection.

Reference solution: Do not infer R3 from an arithmetic-only fixture. Inspect the actual generated source, developer tests, QA tests, course acceptance tests and per-criterion observations. The recorded final 22-test execution covers R1–R3; the initial 20-pass/two-error result and the exception-compatibility tradeoff remain part of the review. A smaller or unrelated passing suite cannot fill a missing observation.

Verification: `test_projects_4_5.py`.

## s15-l14: Package the Source Code and Documentation

Objective: Organize the final application, setup instructions, dependencies, tests and usage documentation.

Implementation: `delivery_package.py`, the successful `container_entrypoint.py`
route and `container_launch.py:verified_delivery`.

Exercise: After an admitted whole-crew run, package its exact successful result
against the original completion event. Inspect generated source/docs/dependencies,
immutable course and QA tests, typed artifacts, attempted-test receipts, acceptance
matrix and archive member hashes. Verify the new `delivery.zip` and its receipt,
then perform a clean documented extraction/setup/test. Retain private raw evidence
separately; review source and logs for credentials before sharing.

Reference solution: The production entrypoint packages the actual final files and
completion-bound evidence, never the fixed template. Unpassed observations, source
or receipt mismatch, unsafe/extra paths, quotas and existing/racing destinations
hold delivery. Explicit fixture packages remain `OFFLINE_FIXTURE_NOT_PRODUCTION`;
the production launcher rejects that class. The earlier baseline template ZIP is
a separate historical exercise and cannot certify a generated whole-crew package.

Verification: `test_engineering_delivery_package.py` and affected semantic-team/
whole-container regressions require first central execution for these new bytes.
The recorded original delivery archive was freshly extracted in an isolated,
no-network learner workspace: its documented README command passed seven tests,
and full discovery passed 22 tests. Its empty requirements needed no installation.
Those are observations of that archive, not validation of a new checkout or of
unexecuted candidate changes; independent acceptance remains separate.

## s15-l15: Complete the Sandboxed Engineering Team

Objective: Demonstrate the end-to-end workflow and review its architecture, traces and delivered artifacts.

Implementation: `README.md#role-and-completion-contracts`.

Exercise: Assemble a final trace with genuine four-role responses, actual container tests/repair, acceptance matrix and package evidence.

Reference solution: Reuse the same coherent recorded four-role run, its genuine failure and source-only repair, final acceptance matrix, original delivery archive and clean-extraction observations. Explicitly list private runtime compatibility and all remaining setup limitations. Offline fixtures prove separate controls and never substitute for real provider/container observations.

Verification: Cross-check original completion, final source, acceptance receipts and every archive member; a new end-to-end run needs its own observations.


## Recorded example: contracts, repair and delivery layout

The retained worked run used four CrewAI roles. Its first actual execution ran
22 tests: 20 passed and two invalid-type cases errored. QA reviewed the actual
failure; the developer changed only `expense_app.py`. The final execution ran
the same 22 tests successfully, followed by a successful QA review. Both executions
used the same course-test hash
`a404d35c05b9e680d4462f25caa3ed7b74b258ffd3705f70c1b7edcfc9314251`
and QA-test hash
`834b1c23f3fdc8aa27727a41bf2783a916d243a4fcfd4b951145d3146c2a6ff2`.
Do not describe this as the baseline first-element arithmetic defect.

The recorded architecture specified `TypeError` for invalid types; the course
acceptance suite required `ValueError`. The generated `InvalidAmountError`
inherited both, so either exception handler catches it. Explain this observed
compatibility choice and its maintenance cost; it does not justify accepting
invalid input or changing tests to manufacture a pass.

The four application deliverables are `expense_app.py`, `test_expense_app.py`,
`README.md` and `requirements.txt`. The delivery ZIP contains nine members because
it also includes QA/course tests and completion evidence. Inspect the actual
member manifest rather than treating the application-file count as the archive
member count. Keep the original ZIP and failed-run history unchanged.

The successful whole-container recording used a private copy of
`InsideContainerExecutor` selecting the already-running interpreter through
`sys.executable`, instead of searching for `python` through a restricted PATH.
Other private runtime compatibility settings are recorded with that run. These
recordings are historical observations; publishing a source correction still
requires the repository owner's normal integration and validation.
