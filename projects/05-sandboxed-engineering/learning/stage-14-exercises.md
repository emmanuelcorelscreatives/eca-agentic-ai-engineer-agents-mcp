# Stage 14: exercises and reference solutions

Run the repository-root commands in [README.md](README.md#local-verification-map).
The [offline notebook](WORKED-EXAMPLE.md) supplies runnable file-tool and repair
activities. Runtime exercises are separate optional work in an authorized lab;
local tests do not imply that containers or models ran.

## s14-l01: Introduction to AI Coding Agents

Objective: Explain how coding agents plan changes, manipulate files, execute tools and respond to test feedback.

Implementation: `workflow.py:bounded_repair`.

Exercise: Draw propose → validate → execute → inspect → repair; identify which step can actually change files.

Reference solution: Only validated file writes and the Docker capability change the environment; model prose is never execution evidence.

Verification: `test_actual_arithmetic_failure_and_repair`.

## s14-l02: Why Coding Agents Require Isolated Environments

Objective: Examine the security and reliability risks of allowing generated code to run directly on a host system.

Implementation: `sandbox.py:docker_command`.

Exercise: Compare an unrestricted host subprocess with the declared container argv; identify kernel, credentials and volume risks.

Reference solution: Readonly tests, no network, nonroot, resource limits and no Docker socket reduce capability; shared kernel and hostile host renames remain residual risks.

Verification: `test_restricted_command`.

## s14-l03: Install and Configure Docker

Objective: Install Docker, verify the runtime and prepare it for sandboxed course projects.

Implementation: `README.md#docker-execution-boundary`.

Exercise: On a separately authorized lab, install Docker from the official procedure and record client/server versions and daemon health.

Reference solution: Record actual docker version output, platform and ownership; an absent executable or daemon failure is a setup blocker, never a passed exercise.

Verification: `runtime-not-executed`.

## s14-l04: Understand Containers, Images, Volumes and Workspaces

Objective: Explain the Docker concepts required to isolate code while preserving project files and outputs.

Implementation: `sandbox.py:docker_command`.

Exercise: Locate image digest, owned container name, readonly mounts, ephemeral tmpfs and cleanup owner in the argv.

Reference solution: Image identifies immutable runtime; mounts expose only current source and tests; /tmp holds disposable environment; cleanup removes only the random owned name.

Verification: `test_restricted_command`.

## s14-l05: Build a Sandboxed File Tool

Objective: Allow an agent to inspect and modify files only within an approved project workspace.

Implementation: `sandbox.py:FileTools`.

Exercise: Run `student_lab.py files` using the root-relative command in the offline notebook. Inspect its scratch setup, src/app.py write/read/list, traversal, absolute path, symlink and tests/ write attempts. Add the notebook's nested-file exercise in your own copy.

Reference solution: Canonical descriptor-relative opens reject traversal and symlinks; tests are readonly; replacing app.py requires its previous SHA256.

Verification: `test_symlink_read_and_write`.

## s14-l06: Build a Controlled Shell Execution Tool

Objective: Execute approved commands with validation, logging and restricted working directories.

Implementation: `sandbox.py:COMMANDS`.

Exercise: Inspect `test_command_injection` in `tests/test_engineering_learning.py`. Supply dangerous strings only as rejected command-ID data, never as shell commands. Compare the allowed `tests` identity with unknown command identities.

Reference solution: Both proposals are rejected before subprocess creation; COMMANDS supplies immutable argv and no shell interpolation.

Verification: `test_command_injection`.

## s14-l07: Run Python Code Inside Docker

Objective: Build an image, execute generated Python and capture the container’s output.

Implementation: `sandbox.py:execute`.

Exercise: In the authorized prepared image, execute the application command and save source/image/argv/exit/output identity.

Reference solution: Use a preloaded digest, readonly mounts, no network and owned cleanup. Follow [CONTAINER.md](CONTAINER.md) for prerequisites; stop if the prepared image/cache/runtime is missing. Offline tests are not container observations.

Verification: `runtime-not-executed`.

## s14-l08: Install Project Dependencies Safely

Objective: Manage project dependencies inside the sandbox without modifying the host environment.

Implementation: `sandbox.py:COMMANDS`.

Exercise: As offline preparation, explain what uv-sync may install and why no package-name argument is exposed to agents. Inspect the supplied `pyproject.toml` and `uv.lock`: these are the CrewAI orchestrator dependencies, not dependencies of the standard-library expense app. Then read the cache/build recipe in [CONTAINER.md](CONTAINER.md). Actual frozen check/sync output is optional runtime work, not a result of the flag test below.

Reference solution: Only frozen reviewed lockfile dependencies from offline cache are allowed; absent lock/cache must fail, not activate network or modify the host.

Verification: `DockerPolicyTests.test_uv_offline` in `tests/test_engineering_learning.py` checks command flags only. Follow the README discovery command; record frozen installation observations separately only if performed.

## s14-l09: Add Timeouts and Resource Limits

Objective: Restrict execution time, memory and processing resources to contain failed or excessive operations.

Implementation: `sandbox.py:Policy`.

Exercise: Try seconds=61, cpus=0 and an excessive memory quota; inspect a fake timeout receipt.

Reference solution: Bounds reject oversized policies; a timed-out process remains failed even when its exact container is removed.

Verification: `test_timeout_retains_failure_and_removes_only_owner`.

## s14-l10: Capture Command Output and Errors

Objective: Return structured standard output, error output and exit status to the coding agent.

Implementation: `sandbox.py:execute`.

Exercise: Inspect the mocked invalid UTF-8, missing-runtime and cleanup receipts; distinguish application and infrastructure failures.

Reference solution: Decode replacement is explicit; infrastructure_error, returncode, timed_out, truncated and cleanup_confirmed are separate fields; no successful sentence promotes a failure.

Verification: `test_missing_runtime_is_not_success`.

## s14-l11: Build Automated Testing Tools

Objective: Enable the agent to run test suites and convert failures into actionable feedback.

Implementation: `workflow.py:expense_fixture` for preparation; `semantic_team.py:validate_receipt` and `container_entrypoint.py:InsideContainerExecutor` for the generated workflow.

Exercise: Run `student_lab.py repair` using the notebook command and inspect the failed/passing cases. Then trace how integrated source/test hashes, observations and QA review are checked in `SemanticTests.test_all_roles_typed_and_tool_failure_routes_back` in `tests/test_engineering_semantic_team.py`. The executor there is a labelled double, not a generated-Python run. Actual generated-Python testing requires the separate container extension.

Reference solution: 125+275 first yields 125 and fails; summation yields 400 and passes. These actual arithmetic observations do not claim execution of generated Python.

Verification: `WorkflowTests.test_actual_arithmetic_failure_and_repair` in `tests/test_engineering_learning.py` is the arithmetic control; `SemanticTests.test_execution_bound_to_exact_source` in `tests/test_engineering_semantic_team.py` checks integrated receipt binding with a double. Commands are in README's local verification map.

## s14-l12: Secure the Coding-Agent Environment

Objective: Add allowlists, path controls, secret isolation and approval boundaries around sensitive actions.

Implementation: `README.md#docker-execution-boundary`.

Exercise: Review command, path, dependency, secret, network, readonly-test, quota and cleanup boundaries before a real agent run.

Reference solution: Reject new mounts/images/dependencies pending operator review. No provider secrets or Docker socket enter the workspace; unit tests do not prove production hostile-code isolation.

Verification: `test_read_only_tests`.
