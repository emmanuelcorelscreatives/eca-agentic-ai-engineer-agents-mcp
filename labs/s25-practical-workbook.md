# Stage 25 — Project 7: Agent Application Factory

These exercises connect the actual baseline to the complete curriculum. Each section distinguishes the executed offline contract from additional framework/browser/model/Docker work. Passing an offline contract does not certify the complete lesson.

## s25-l01: Design the Agent Application Factory

Define the factory workflow, generated artifacts, supported capabilities, validation and safety boundaries.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py schema
```

Complete these specific curriculum requirements before recording the full practical:

- Define a supported-capability matrix with unsupported requests rejected before generation.
- Write an artifact graph and trust-boundary diagram for model output, source code, tools and host execution.
- Specify separate output directories and a release gate requiring all mandatory acceptance tests.

Acceptance checks:

- A missing approved specification prevents downstream generation.
- A request for host shell or credential access outside the capability policy fails closed.
- Every downstream artifact has input hashes and generator/version provenance.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l02: Define the Typed Agent Specification

Create a schema describing purpose, users, tools, data, outputs, policies and deployment requirements.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py schema
```

Complete these specific curriculum requirements before recording the full practical:

- Reject unknown fields, ambiguous tool definitions, invalid identifiers and undeclared secret references.
- Create valid research-assistant and support-triage specs plus intentionally invalid cases.
- Version the schema and serialize normalized specs deterministically.

Acceptance checks:

- Valid specs round-trip without losing required fields.
- Missing policy, malformed output schema and duplicate tool names produce precise validation errors.
- Traversal paths and literal credentials are rejected.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l03: Build the Requirements Analysis Agent

Transform the specification into functional requirements, constraints and measurable acceptance criteria.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py schema
```

Complete these specific curriculum requirements before recording the full practical:

- Use typed requirement IDs and trace each acceptance criterion to a spec field.
- Represent unresolved questions explicitly and require approval before architecture planning.
- Keep the deterministic fixture harness separate from a real opt-in model-backed requirements agent.

Acceptance checks:

- Every mandatory spec capability has at least one requirement and executable acceptance criterion.
- An unresolved deployment constraint blocks advancement.
- Prompt-injected requests cannot expand tools or remove safety policy.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l04: Build the Architecture Planning Agent

Select components and produce an implementation plan based on the approved requirements.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py schema
```

Complete these specific curriculum requirements before recording the full practical:

- Define component and dependency manifests with entry points, storage and adapter boundaries.
- Record rationale tied to requirements without inventing package APIs.
- Validate supported framework versions and explicit human approval before scaffolding.

Acceptance checks:

- All requirements map to components and planned test IDs.
- Unsupported framework or unavailable capability is rejected rather than silently substituted.
- An unapproved requirements revision invalidates an older architecture plan.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l05: Build the Agent Scaffolding Agent

Generate the project directories, modules, configuration and application entry points.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Generate files into a new isolated workspace using relative allowlisted paths.
- Use Python syntax/compile checks and explicit overwrite protection.
- Retain a manifest of generated paths and content hashes.

Acceptance checks:

- A generated minimal package imports and exposes the promised entry point.
- Absolute paths, symlink escapes and ../ traversal are refused.
- A pre-existing edited file is not silently overwritten.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l06: Build the Tool Generation Agent

Create typed tool definitions, validation logic and placeholder integrations from the specification.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Create a read-only synthetic catalog lookup and a draft-only notification tool with typed schemas.
- Keep credentials environment-only and distinguish placeholders from working integrations.
- Implement timeouts, typed failures and policy checks before tool execution.

Acceptance checks:

- Valid lookup arguments return a fixture-backed result; invalid arguments never reach the tool.
- Draft generation causes no email delivery or other external side effect.
- A placeholder raises an explicit integration-not-configured result instead of fake success.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l07: Build the Prompt and Instruction Generator

Produce focused agent instructions that define role, behavior, boundaries and tool-use policy.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Use structured role/goals/allowed-tools/refusal/escalation sections.
- Quote untrusted source content as data, not authoritative instructions.
- Version prompts and trace each policy clause to the spec.

Acceptance checks:

- A required no-delivery boundary remains present in generated instructions.
- Injected spec commentary cannot grant undeclared tools.
- Missing tool-use or escalation policy blocks release.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l08: Build the Test Generation Agent

Generate unit, integration and behavioral tests from the project’s acceptance criteria.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py failure
```

Complete these specific curriculum requirements before recording the full practical:

- Generate tests independently of implementation details and preserve requirement-to-test traceability.
- Include negative authorization, malformed input and timeout cases.
- Separate deterministic adapter tests from bounded real model behavioral evaluations.

Acceptance checks:

- Deliberately broken output validation is caught by the generated test suite.
- Each acceptance criterion has an explicit test or a documented unresolved evaluation requirement.
- Fixtures never masquerade as observed model quality or live integration evidence.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l09: Build the Code Review Agent

Inspect generated code for correctness, consistency, security and missing requirements.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py review
```

Complete these specific curriculum requirements before recording the full practical:

- Emit structured findings with file/line, severity, evidence, requirement ID and proposed correction.
- Combine actual static/test diagnostics with agent reasoning without treating clean lint as full security proof.
- Require no unresolved blocking findings before sandbox validation.

Acceptance checks:

- Seeded path traversal and missing validation defects generate actionable findings.
- Review identifies a missing required test.
- A malformed or empty review response cannot certify the project safe.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l10: Add Framework Selection and Adapters

Map project requirements to supported frameworks through a replaceable adapter architecture.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Implement a Python Agno adapter and a TypeScript Mastra adapter against pinned verified APIs from Stage 24; each produces a runnable native-language project with its own dependency lock and smoke command.
- Normalize invocation, tool registration, configuration and lifecycle boundaries without hiding unsupported features.
- Keep core generated-project contracts independent of framework imports.

Acceptance checks:

- A shared deterministic contract suite runs against each implemented adapter.
- Unsupported streaming/tool capability is reported explicitly.
- At least one genuine opt-in invocation per selected framework is recorded before a live walkthrough.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l11: Generate Complete Agent Project Structures

Assemble code, prompts, schemas, tools, tests and configuration into a runnable project.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Stage all generated artifacts, verify hashes and reject unresolved imports.
- Emit a machine-readable bill of materials and requirement/test coverage report.
- Build into a new directory without modifying source templates or host files.

Acceptance checks:

- A fresh generated project installs into an isolated environment and runs its offline sample.
- A missing prompt, schema or tool module fails assembly.
- Two equivalent specs produce a stable normalized manifest, excluding explicitly recorded volatile metadata.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l12: Create README and Environment Templates

Generate setup instructions, usage examples, dependency information and .env.example files.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Derive command examples from actual entry points and tested environment setup.
- List required vs optional credentials, supported Python/framework versions and offline/live modes.
- Use placeholders only and document capability limitations and synthetic dataset provenance.

Acceptance checks:

- All README offline commands execute in a fresh test workspace.
- .env.example contains variable names and safe placeholders with no secrets.
- An optional provider is never required for the documented offline smoke test.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l13: Validate Generated Projects Inside Docker

Build and execute generated applications within an isolated environment.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Provide a pinned or digest-bound base image, non-root user and fixed dependency lock.
- Run with no host socket/credentials, restricted mounts, default network disabled and CPU/memory/pid/time limits.
- Retain build logs, exit codes and generated test reports; image build networking is separately scoped.

Acceptance checks:

- A genuine Docker build and container smoke test pass before this lesson is scripted as executed.
- Container cannot write outside its designated scratch mount or access injected host-secret sentinels.
- An intentional infinite loop is terminated by a bounded timeout/resource policy.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l14: Build an Automated Repair Loop

Use test and runtime failures to propose, validate and apply bounded corrections.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py failure
```

Complete these specific curriculum requirements before recording the full practical:

- Classify syntax, failing test, missing dependency and runtime errors using real retained diagnostics.
- Limit repair count, changed file scope and external call budget; require fresh tests and review after each candidate.
- Retain rejected patches and restore the prior workspace on validation failure.

Acceptance checks:

- A seeded syntax defect is corrected, tests rerun and provenance appended.
- A patch outside allowed files or one removing a required assertion is rejected.
- Exhausted budget ends in an explicit unresolved failure, never forced approval.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l15: Launch the Generated Agent

Start the validated application and demonstrate interaction with the generated agent.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Start only the approved generated artifact hash and verify effective configuration.
- Demonstrate the synthetic catalog lookup and draft-only response with genuine bounded model calls for agent behavior.
- Retain request/response/tool trace with secrets redacted and stop the owned process cleanly.

Acceptance checks:

- The launched instance reports its release manifest identity and passes health checks.
- An allowed request reaches the configured tool; an unauthorized delivery request produces no side effect.
- A genuine interaction trace exists before narrating observed model behavior; offline stubs are explicitly labeled.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s25-l16: Complete the Agent Application Factory

Review the full workflow, generated artifacts, evaluations, limitations and final project architecture.

Run the existing engineering contract:

```sh
python3 examples/s25_factory_labs.py generate
```

Complete these specific curriculum requirements before recording the full practical:

- Exercise the full artifact lineage and compare generated artifacts against each spec without changing objectives.
- Publish architecture, exercises, reference solutions, failure cases and documented limitations.
- Record actual end-to-end runs, test coverage and unresolved issues without claiming unsupported production readiness.

Acceptance checks:

- Both sample specs yield runnable projects passing mandatory deterministic and genuine sandbox checks.
- A deliberately invalid spec is rejected before code generation; a seeded failure follows the bounded repair path.
- A release inventory links every requirement, artifact, test, review and observed runtime trace.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.
