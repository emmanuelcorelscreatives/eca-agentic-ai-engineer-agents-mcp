# Stage 20 — Project 6: Browser Task Sidekick

These exercises connect the actual baseline to the complete curriculum. Each section distinguishes the executed offline contract from additional framework/browser/model/Docker work. Passing an offline contract does not certify the complete lesson.

## s20-l01: Design the Browser Task Sidekick

Define the task lifecycle, architecture, tools, state, safety boundaries and user experience.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py research
```

Complete these specific curriculum requirements before recording the full practical:

- Create typed Task, Step, Finding, Artifact and Approval records with stable identifiers and explicit lifecycle enums.
- Specify CREATED, PLANNED, RUNNING, WAITING_APPROVAL, COMPLETED, FAILED and CANCELLED transitions and an explicit allowed host list.
- Document untrusted web text versus trusted task instructions, the browser session owner, persistence owner and per-run resource limits.

Acceptance checks:

- Reject invalid lifecycle transitions and duplicate step identifiers.
- Every consequential action has an approval boundary in the architecture, including download, upload and form submission.
- Architecture links each objective to observable completion evidence rather than an assistant assertion.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l02: Build the Sidekick Planner

Convert a user objective into ordered steps with completion criteria and tool requirements.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py research
```

Complete these specific curriculum requirements before recording the full practical:

- Build a genuine model-backed planning adapter using the shared pinned framework from Stage 19; validate its structured result against the task schema.
- Require step dependency IDs, permitted tools, target host, success predicate and sensitivity classification; cap plan length and reject unknown tools.
- Keep deterministic planner fixtures explicitly labelled test doubles; do not present fixture output as a live model plan.

Acceptance checks:

- Reject cyclic dependencies, non-allowlisted targets, impossible completion predicates and unknown tool names.
- A genuine bounded provider run creates a persisted validated plan with provider/model/time/call evidence.
- Both a simple research task and a task containing a sensitive proposed action yield bounded typed plans.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l03: Build the Browser Executor

Carry out approved navigation, extraction and interaction steps through Playwright.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py research
```

Complete these specific curriculum requirements before recording the full practical:

- Use Playwright with explicit browser/context/page ownership, locator expectations, timeouts and cleanup.
- Serve an Academy-owned local HTTP site with catalog, detail, delayed-content and draft form routes; issue real browser navigation and extraction.
- Bind each executed action to the exact persisted plan step; route sensitive actions to approval without dispatching them.

Acceptance checks:

- Real Chromium loads the catalog, follows a detail link and extracts validated visible values.
- A locator timeout records a bounded failure and leaves later dependent steps unexecuted.
- Submissions, uploads and downloads have zero observed effects before approval.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l04: Build the Task Evaluator

Compare current progress with the objective and determine whether to continue, revise or stop.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py research
```

Complete these specific curriculum requirements before recording the full practical:

- Compare required output fields, page observations and completion criteria with the original objective.
- Implement evaluator decisions CONTINUE, REVISE, COMPLETE and STOP with reason/evidence references and bounded replans.
- A live model-based evaluator may propose revisions but cannot override permissions or mark unsupported facts complete.

Acceptance checks:

- Missing required evidence prevents COMPLETE even if the generated narrative claims success.
- A deliberately changed detail-page layout causes one bounded revision, then convergence or an explicit stop.
- Maximum steps/replans stop the run without further browser or provider calls.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l05: Add Research and File Tools

Allow the Sidekick to collect information and preserve useful artifacts in controlled files.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py approval
```

Complete these specific curriculum requirements before recording the full practical:

- Extract catalog facts with URL, capture time and content hash; keep page text untrusted.
- Write JSON/CSV/Markdown artifacts only beneath a per-task workspace using validated paths and size/type limits.
- Preserve source evidence alongside synthesized findings; treat network research pages as current only after an actual permitted fetch.

Acceptance checks:

- Known catalog facts match the rendered fixture and include provenance.
- Path traversal, symlink escape and oversized writes are refused without modifying files outside the workspace.
- A seeded prompt injection in page content cannot grant tools, change the objective or dispatch a sensitive action.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l06: Add Memory and Persistent Task State

Store plans, completed actions, findings and pending approvals across sessions.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py recovery
```

Complete these specific curriculum requirements before recording the full practical:

- Use SQLite transactions, schema migrations and a durable event log plus stable task/step IDs.
- Persist before/after action checkpoints, approval proposals and action idempotency tokens; model interrupted actions as UNKNOWN until reconciled.
- On restart resume safe pending work, retain completed evidence, and never replay an unknown consequential action automatically.

Acceptance checks:

- Restart an actual subprocess while awaiting approval and recover the same pending proposal and task state.
- A crash after a simulated side effect before receipt persistence creates UNKNOWN and requires reconciliation, not automatic replay.
- Duplicate completion events do not duplicate findings or browser side effects.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l07: Add Middleware and Execution Policies

Apply logging, validation, permissions and context rules consistently across the agent.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py unknown
```

Complete these specific curriculum requirements before recording the full practical:

- Implement an ordered middleware chain before every tool dispatch; centralize policy checks rather than relying on model compliance.
- Redact credentials and personal fields from event/trace output; maintain correlation IDs and bounded context construction.
- Use trusted server-side policy and a deny-by-default allowlist; ensure subagent tools pass through the same policy.

Acceptance checks:

- An unapproved sensitive action is denied through direct dispatch, resumed execution and subagent invocation.
- Synthetic secret sentinels do not appear in exported logs, traces or model-visible unrelated context.
- Validation runs before the underlying browser/file tool and records a structured denial.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l08: Add Human Approval for Sensitive Actions

Interrupt execution before submissions, downloads, uploads, messages or other consequential actions.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py approval
```

Complete these specific curriculum requirements before recording the full practical:

- Classify form submission, file download, upload, message sending and destructive clicks as consequential even on the Academy sandbox.
- Create an approval record bound to action payload hash, target host, task, step, proposed file and expiry; require server-side authorization.
- The practice server records actual requests so screenshots and tests can demonstrate the absence of effects before approval.

Acceptance checks:

- Each sensitive action family enters WAITING_APPROVAL with no effect observed by the local server.
- Approval for one target/payload cannot authorize a changed payload, another task or expired proposal.
- A stale tab or restart cannot bypass the pending approval.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l09: Implement Approve, Edit and Reject Controls

Let users confirm, modify or cancel proposed browser actions before execution.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py edit-reject
```

Complete these specific curriculum requirements before recording the full practical:

- Approve executes once using a transactionally consumed token.
- Edit creates a new revision with a new payload hash and policy validation; changes must be shown to the user before execution.
- Reject cancels the proposal and records the reason without browser effects; concurrent controls resolve through compare-and-swap.

Acceptance checks:

- Double approve and concurrent approve/reject create at most one authorized server-side effect.
- Edited destination outside the host allowlist is refused; a valid edit requires explicit confirmation of its final payload.
- Reject preserves proposal history and leaves the task safely resumable or cancelled.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l10: Add Subagents for Specialist Tasks

Delegate focused research, extraction or review tasks while preserving central coordination.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py research
```

Complete these specific curriculum requirements before recording the full practical:

- Use the Stage 19 pinned framework native subagent API for specialist execution, not a renamed local sequential function.
- Provide each specialist a minimal context, scoped tools, task budget and typed result; central coordinator owns plan, approvals and artifact publication.
- Run independent subtasks concurrently under a configurable finite semaphore; collect completion/error evidence and cancellation propagation.

Acceptance checks:

- An actual framework run shows two specialist task identities and typed outputs merged by the coordinator.
- A research specialist cannot access another task workspace or issue a sensitive executor action.
- One specialist timeout is isolated and cancellation releases the browser/resource slot.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l11: Add Progress Tracking and Visible Checklists

Present completed, active and pending tasks through an understandable progress display.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py recovery
```

Complete these specific curriculum requirements before recording the full practical:

- Compute progress from durable events rather than optimistic generated prose.
- Display step IDs, current status, short evidence links, pending approvals and last update time in a real application view.
- Support reconnecting clients using persisted snapshots plus ordered events without duplicating completed steps.

Acceptance checks:

- A restarted UI reproduces the same checklist as the task database.
- A pending approval never displays as completed and a failed step shows its actual failure.
- Concurrent specialist completions update each unique checklist row once.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l12: Test the Sidekick on Real-World Tasks

Evaluate navigation, research quality, recovery behavior, permissions and task completion.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py research
```

Complete these specific curriculum requirements before recording the full practical:

- Create a task matrix covering a public documentation research task, Academy catalog comparison, a draft form action and layout/network failure recovery.
- Permit only bounded read-only access to explicitly authorized public sites; consequential exercises run only against the Academy sandbox.
- Record actual correctness, evidence coverage, completion, policy violations, retries and timings with environment/date; report offline/sandbox/live cases separately.

Acceptance checks:

- Real browser evidence reproduces the public documentation citations from an actual allowed fetch.
- The sandbox sensitive-action run proves human approval occurred before the recorded effect.
- Failure cases terminate within budgets and evaluations disclose unsupported/failed outcomes without fabricating success.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l13: Build the Gradio Interface

Create a workspace for requests, browser updates, approvals, files and final results.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py approval
```

Complete these specific curriculum requirements before recording the full practical:

- Implement real Gradio Blocks components and callbacks for objective input, task selection, progress, browser screenshots, proposed actions and artifact links.
- Keep browser/process/state ownership on the server; bind callbacks to an authorized session and exact task/approval revision.
- Run loopback-only for the course lab by default and document authentication/reverse-proxy requirements for a deployment without making an unsupported production claim.

Acceptance checks:

- An actual browser can start a task, see progress and approve or reject a sandbox proposal through Gradio.
- A second session cannot view or approve the first task by changing task IDs.
- Artifact download resolves only owned validated paths; stale approval callback is denied.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l14: Trace and Evaluate Sidekick Runs

Analyze execution paths, tool success, user interventions, latency and completion quality.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py unknown
```

Complete these specific curriculum requirements before recording the full practical:

- Capture tool calls, model calls, step transitions, approvals, errors and wall-clock timings with parent/child correlation IDs.
- Implement a redacted local trace export and, only if actually configured/run, the framework tracing integration.
- Calculate completion rate, tool success, interventions, latency and evidence quality for the same task matrix; retain unsuccessful runs.

Acceptance checks:

- Trace events reconstruct the executed step order and link each approval to its effect.
- Metrics match independent calculations from fixture events and actual retained runs.
- Trace exports contain no credentials or synthetic private sentinel; remote tracing is not claimed when only local JSON was produced.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.

## s20-l15: Complete the Browser Task Sidekick

Integrate the application, run a full demonstration and review the finished architecture.

Run the existing engineering contract:

```sh
python3 examples/s20_sidekick_labs.py recovery
```

Complete these specific curriculum requirements before recording the full practical:

- Provide a clean-install quickstart, pinned dependencies, sample configuration, architecture document, exercises, reference solutions and a bounded end-to-end command.
- Demonstrate planning, real browser research, specialist delegation, file output, human-edited approval, restart/resume, progress and final evidence-based evaluation.
- Publish the actual test result and capture genuine application screens before deriving walkthrough narration; disclose remaining limitations and costs.

Acceptance checks:

- A clean environment installs and passes unit, integration and real-browser end-to-end suites using the documented commands.
- One bounded model-backed demo records all required genuine features and produces an inspectable artifact/evidence bundle.
- The final review maps every stage objective to implementation, tests and actual observations, with unresolved failures explicitly held.

Retain actual command output and source hashes. Classify each result as offline, genuine browser/sandbox, installed framework, Docker or live model; do not mix those evidence classes.
