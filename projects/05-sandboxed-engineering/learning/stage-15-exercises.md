# Stage 15: exercises and reference solutions

Use [README.md](README.md#local-verification-map) for repository-root checks and
[WORKED-EXAMPLE.md](WORKED-EXAMPLE.md) for complete accessible exercise inputs.
Distinguish baseline controls from the integrated `semantic_team.py`,
`crewai_roles.py` and `container_entrypoint.py` workflow. The offline notebook
uses local fixtures and learner-created contract exercises, not private recorded
runs. Optional live work requires separate setup, consent and actual outputs.

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

Verification: run `student_lab.py handoffs` as shown in the notebook; `SemanticTests.test_missing_priority_refused` in `tests/test_engineering_semantic_team.py` checks the integrated requirements contract. `WorkflowTests.test_contracts` is a separate baseline check.

## s15-l03: Build the Software Architect Agent

Objective: Transform requirements into components, data flows, interfaces and an implementation plan.

Implementation: `semantic_team.py:validate_architecture` and `crewai_roles.py:CrewAIRoleProvider`.

Exercise: Bind a module/interface to every approved criterion and explain why dependencies are empty.

Reference solution: In the generated workflow, use the application component `expense_app.py` and `total_expenses(amounts)`, bound to the current requirements hash and every R ID. Put the test and documentation deliverables in the implementation plan; they are not extra application components. The earlier `sandbox.py` control fixture uses a different `src/` workspace layout. Unknown IDs and stale revisions block consumption.

Verification: `SemanticTests.test_stale_architecture_refused` and `test_unapproved_dependency_refused` in `tests/test_engineering_semantic_team.py`. `WorkflowTests.test_unknown_reference` is a separate baseline check.

## s15-l04: Build the Developer Agent

Objective: Generate and modify source code according to the approved architecture and task specification.

Implementation: `semantic_team.py:validate_files` and `run_team`; `sandbox.py:FileTools` is a separate control exercise.

Exercise: Inspect the supplied four-file template bundle in `../team.py`, then inspect the source-only repair inputs in `ProviderDouble` and `SemanticTests.test_stale_patch_refused` in `tests/test_engineering_semantic_team.py`. These strings are not executed by that suite. Use the notebook's separate FileTools activity for out-of-scope writes. A new model-generated bundle is optional container work, never host execution.

Reference solution: The generated bundle contains `expense_app.py`, `test_expense_app.py`, `README.md` and `requirements.txt`. A repair changes only the approved application source and keeps developer, QA and course tests intact. The separate FileTools fixture permits writes only in its `src/` scope.

Verification: `SemanticTests.test_test_changes_and_extra_files_forbidden` and `test_stale_patch_refused` in `tests/test_engineering_semantic_team.py`; `FileTests.test_stale_write` is the separate file-tool control.

## s15-l05: Build the Quality Assurance Agent

Objective: Review requirements, create tests, run validations and report defects to the development workflow.

Implementation: `semantic_team.py:run_team`, its immutable `CourseAcceptance` tests, and the QA role in `crewai_roles.py`.

Exercise: Complete notebook sections 2 and 4. Identify the R2 failure in your local arithmetic trace, compare the supplied template and course R3 tests, and write the learner-created TypeError/ValueError contract comparison. Inspect the integrated QA-double test separately; do not call it a runtime observation.

Reference solution: The seeded arithmetic fixture observes 125 instead of 400, an R2 failure. The learner-created exception table exposes a separate R3 contract disagreement; agree on `ValueError` before implementation. An infrastructure error or missing run is not a test failure/pass observation. No historical failure receipt is required or invented.

Verification: `SemanticTests.test_model_cannot_override_actual_tool_observations` and `test_model_review_must_reference_current_receipt` in `tests/test_engineering_semantic_team.py` check integrated QA with doubles. `WorkflowTests.test_actual_arithmetic_failure_and_repair` covers only the local arithmetic fixture.

## s15-l06: Define Engineering Tasks and Dependencies

Objective: Sequence planning, design, implementation and testing so each agent receives the required artifacts.

Implementation: `workflow.py:task_order`.

Exercise: Introduce a missing prerequisite, a cycle and a failed predecessor in the role graph.

Reference solution: Unknown prerequisites and cycles fail early; failed or absent predecessor artifacts prevent dispatch.

Verification: `test_tasks`.

## s15-l07: Pass Specifications and Context Between Agents

Objective: Share structured requirements, architecture decisions, code locations and test feedback between specialists.

Implementation: `semantic_team.py:envelope` and `consume`; `workflow.py:Envelope` is the separate baseline example.

Exercise: Run `student_lab.py handoffs` using the notebook command. Inspect the valid integrated requirements envelope, changed-content rejection and obsolete-revision rejection. Its response hash identifies local human reference data only.

Reference solution: Both mismatches fail; transfer role, schema version, revision, exact SHA and honest provenance rather than an unstructured success sentence.

Verification: `SemanticTests.test_artifact_content_or_revision_tamper` in `tests/test_engineering_semantic_team.py`; `WorkflowTests.test_handoff` checks the older baseline separately.

## s15-l08: Build uv-Based Sandbox Tools

Objective: Give the team controlled commands for creating environments, installing packages and running applications.

Implementation: `sandbox.py:COMMANDS`.

Exercise: Construct uv-version, uv-venv, uv-lock-check and uv-sync commands without accepting arbitrary shell text.

Reference solution: The command builder declares Docker-only commands, read-only source inputs and ephemeral outputs with offline/frozen dependency controls. Inspect the whole-container cache recipe separately in [CONTAINER.md](CONTAINER.md). Command construction and mocked tests do not establish an installation, cache hit or uv version in your environment.

Verification: `test_uv_offline`.

## s15-l09: Generate Project Requirements and Dependencies

Objective: Create and validate dependency declarations based on the planned application architecture.

Implementation: `workflow.py:architecture`.

Exercise: Propose an unnecessary external dependency for this standard-library expense calculator and inspect the rejection.

Reference solution: Dependencies remain empty for the expense app. The supplied real `uv.lock` and `pyproject.toml` describe the separate Python-3.12 CrewAI orchestrator. Inspect both and the offline preparation recipe; do not regenerate the lock merely to run this exercise, install app dependencies from it or infer installation from its presence.

Verification: `test_dependency_rejected`.

## s15-l10: Run the Engineering Crew Inside Docker

Objective: Execute the complete team workflow within an isolated project workspace.

Implementation: `container_entrypoint.py`, `container_launch.py`, `semantic_team.py:run_team` and `crewai_roles.py:CrewAIRoleProvider`.

Exercise: First trace the four-role integrated fixture in `tests/test_engineering_semantic_team.py`; all model/executor responses there are doubles. For the optional real-container extension, follow [CONTAINER.md](CONTAINER.md), including its deliberately unconfigured provider transport. Stop if prerequisites are missing; credentials stay outside the no-network container.

Reference solution: PM, architect, developer and QA are the four roles; review and repair are stages, not extra agents. The current executor uses `sys.executable`. Source inspection and fixture checks are distinct from actually running CrewAI, Docker and a provider. A future live run must retain its own role bindings and runtime output.

Verification: Inspect actual role bindings and container receipts; repository control tests alone do not prove a new provider run.

## s15-l11: Execute Automated Tests

Objective: Run unit and integration tests and return structured failures to the responsible agents.

Implementation: `container_entrypoint.py:InsideContainerExecutor` and `semantic_team.py:validate_receipt`; `sandbox.py` provides separate command-control fixtures.

Exercise: Inspect the two attempts from the local repair activity and the integrated `ExecutorDouble`/QA checks. Map exit status, timeout, source/test hashes and R observations to QA in the integrated source. Try the suite's contradictory-success and source-mismatch cases; do not invent a real execution receipt.

Reference solution: Only actual Docker or explicitly labelled executed fixture evidence is accepted; runtime failure and absent receipt never become PASS.

Verification: `SemanticTests.test_contradictory_success_refused`, `test_execution_bound_to_exact_source` and `test_missing_cleanup_not_pass` in `tests/test_engineering_semantic_team.py`. `WorkflowTests.test_fake_success_denied` is baseline-only.

## s15-l12: Diagnose and Repair Failed Builds

Objective: Use test and runtime feedback to implement bounded, traceable repair cycles.

Implementation: `semantic_team.py:run_team`; `workflow.py:bounded_repair` remains a separate baseline control fixture.

Exercise: Use the notebook's failed `first` to passing `sum` trace and keep both outputs. Inspect the integrated fixture's source-only repair and unchanged tests. Try exhausted budgets, repeated patch identities and attempted test modification using the supplied test cases.

Reference solution: Diagnose the seeded R2 first-element aggregation and replace only the allowed label/source. The local trace preserves the failed observation and unchanged test marker. Reconcile the separate learner-created exception contract before implementation; do not change tests to hide a failure. Neither trace nor canned integrated receipt proves a live generated-code repair.

Verification: `SemanticTests.test_zero_budget_preserves_unresolved`, `test_repeat_source_refused` and `test_test_changes_and_extra_files_forbidden` in `tests/test_engineering_semantic_team.py`; baseline budget checks are separate in `tests/test_engineering_learning.py`.

## s15-l13: Review the Completed Application

Objective: Compare the implementation against requirements, acceptance criteria and quality standards.

Implementation: `reference-contracts.json`.

Exercise: Compare implementation and actual evidence against R1–R3, including negative, bool and decimal rejection.

Reference solution: Use the notebook's supplied template/course tests for the R1–R3 source review. Do not infer R3 from the arithmetic-only fixture or a generated application pass from canned observations. If you run the unchanged reviewed template quickstart, retain its actual six-test output separately; it does not certify a new whole-team application.

Verification: `test_projects_4_5.py`.

## s15-l14: Package the Source Code and Documentation

Objective: Organize the final application, setup instructions, dependencies, tests and usage documentation.

Implementation: `delivery_package.py`, the successful `container_entrypoint.py`
route and `container_launch.py:verified_delivery`.

Exercise: Offline, inspect the explicit fixture packaging in `tests/test_engineering_delivery_package.py` and its member/hash assertions. This supplies accessible package inputs without private recordings. For an optional authorized whole-crew run, package its exact successful result
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

Verification: run `tests/test_engineering_delivery_package.py` using the README
discovery command. `WholeTeamDeliveryTests.test_exact_generated_source_artifacts_and_receipts_are_packaged`
checks fixture archive contents; this is not live delivery evidence. A future live
archive needs its own actual clean extraction/setup/tests inside the approved
execution boundary, not host execution of unreviewed source.

## s15-l15: Complete the Sandboxed Engineering Team

Objective: Demonstrate the end-to-end workflow and review its architecture, traces and delivered artifacts.

Implementation: `README.md#role-and-completion-contracts`.

Exercise: Assemble the offline notebook with your local outputs, template inventory, requirement coverage and explicit runtime limits. Optionally demonstrate a fresh real four-role run only after the advanced prerequisites and paid/live opt-in are satisfied.

Reference solution: Keep the failed/passing local arithmetic trace, unchanged test marker, integrated handoff checks and fixture packaging distinctions. State that model calls, generated-code execution, uv installation and container isolation were not demonstrated by these activities. A future live result must use its own genuine responses, tests and package, never substituted fixture results.

Verification: use the notebook checklist and README's local suites. A new real end-to-end run needs its own actual observations.


## Accessible inputs and delivery layout

The [offline notebook](WORKED-EXAMPLE.md) identifies every supplied input and
learner-created activity. No private recording, old receipt or historical archive
is needed. The four application deliverables are `expense_app.py`,
`test_expense_app.py`, `README.md` and `requirements.txt`. Whole-team package tests
also include QA/course tests and result metadata: inspect the actual manifest
rather than confusing the application-file count with the archive-member count.
Keep your failed local attempts and distinguish fixture packages from real runs.
