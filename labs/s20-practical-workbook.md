# Stage 20: Browser Task Sidekick

An Academy-owned local workshop/catalog research task, with synthetic draft-form interactions only. Keep planning, browser observations, source-attributed findings, evaluation, approvals, artifacts and user-facing progress in one persisted session.

This workbook preserves every original PDF lesson objective. It is author-only semantic repair, not production approval. Deterministic contracts, genuine SDK construction, real browser/container execution and model-generated observations are distinct evidence classes. A passing helper or constructor does not establish a finished application.

## Integrated-source handoff

The new source is projects/06-browser-sidekick/pipeline.py. NativePlanner and the explicitly labeled FixturePlanner feed SidekickApplication.create; PlaywrightSandboxExecutor performs bounded owned browser execution; evaluate/revise/decide update the same persisted lifecycle; snapshot/owned_file/export_trace support the user-facing workspace. UI source is projects/06-browser-sidekick/ui_gradio.py. All new integration awaits centralized runtime verification; the stable startup handoff below identifies the explicit native and fixture modes. Baseline helper success is not full-app proof.

## s20-l01: Design the Browser Task Sidekick

Define the task lifecycle, architecture, tools, state, safety boundaries and user experience.

Read [the lesson practical](s20/s20-l01.md) and [reference answer](../solutions/s20/s20-l01.md).

Draw the task lifecycle and ownership boundaries. Trace one request from objective through persisted plan, browser tools, evaluator and final workspace.

Acceptance: Distinguish trusted user objective/application policy from untrusted page content. Show persisted task/step IDs, completion evidence, resource limits and approval boundaries. The architecture must include the integrated planner/evaluator/UI rather than treating disconnected helper functions as the finished application.

## s20-l02: Build the Sidekick Planner

Convert a user objective into ordered steps with completion criteria and tool requirements.

Read [the lesson practical](s20/s20-l02.md) and [reference answer](../solutions/s20/s20-l02.md).

Submit two different objectives to the configured planner and inspect ordered steps, dependencies, tool requirements and measurable completion criteria.

Acceptance: A fixed fixture_plan is a labeled test double. The actual objective must reach the model-backed planner and its structured output must pass the real plan validator before persistence. Unknown tools, off-origin targets, oversized plans and cyclic or missing dependencies fail. A model proposal never grants permission to execute.

## s20-l03: Build the Browser Executor

Carry out approved navigation, extraction and interaction steps through Playwright.

Read [the lesson practical](s20/s20-l03.md) and [reference answer](../solutions/s20/s20-l03.md).

Navigate the local catalog, inspect a detail view, extract visible values and prepare a bounded approved interaction through the intended Playwright executor.

Acceptance: Own the browser/context/page and close them on failure. Use semantic locators, state waits and bounded timeouts. Keep the planned step and observation linked. The earlier urllib sandbox POST test is a real HTTP test but is not proof that a Playwright browser performed an interaction. Sensitive interactions wait for exact approval.

## s20-l04: Build the Task Evaluator

Compare current progress with the objective and determine whether to continue, revise or stop.

Read [the lesson practical](s20/s20-l04.md) and [reference answer](../solutions/s20/s20-l04.md).

Compare findings against the original requested result. Produce CONTINUE, REVISE, COMPLETE and STOP outcomes for deliberately incomplete, contradicted, complete and exhausted cases.

Acceptance: An evaluator is useful only when its result affects the persisted execution lifecycle. Missing source evidence cannot become COMPLETE because an assistant says so. Revision preserves completed/unknown work and respects remaining replan/step budgets; unsupported or exhausted work stops honestly.

## s20-l05: Add Research and File Tools

Allow the Sidekick to collect information and preserve useful artifacts in controlled files.

Read [the lesson practical](s20/s20-l05.md) and [reference answer](../solutions/s20/s20-l05.md).

Extract source-attributed findings and preserve a bounded research artifact inside the owned task workspace. Open its actual UI file/result view.

Acceptance: Artifacts retain source URL and observed data alongside any synthesized summary. Reject traversal, symlink escape, oversized writes and unowned paths. The final app must wire controlled file saves to execution and genuine owned artifact views, not merely contain an unused file-tool class.

## s20-l06: Add Memory and Persistent Task State

Store plans, completed actions, findings and pending approvals across sessions.

Read [the lesson practical](s20/s20-l06.md) and [reference answer](../solutions/s20/s20-l06.md).

Restart the application while a review is pending and after a read completes; inspect the same plan, findings, pending revision and completed evidence.

Acceptance: Persist trusted ownership, current action digest/expiry, plan counters and event history. A completed local effect may be reused only with its authentic receipt. An interrupted consequential action with uncertain outcome remains unresolved; never automatically replay it to make the checklist green.

## s20-l07: Add Middleware and Execution Policies

Apply logging, validation, permissions and context rules consistently across the agent.

Read [the lesson practical](s20/s20-l07.md) and [reference answer](../solutions/s20/s20-l07.md).

Attempt direct, resumed and specialist-origin actions with invalid origin, stale approval, malformed input and exhausted resources. Inspect denial traces and bounded context.

Acceptance: Logging, validation, permissions and context rules must apply on the actual dispatched path. Redact dummy secrets/personal fields and keep correlation and timing evidence. Native-framework middleware is only a native-framework claim if that actual path runs; application policy wrappers can enforce the same boundary without pretending to be another API.

## s20-l08: Add Human Approval for Sensitive Actions

Interrupt execution before submissions, downloads, uploads, messages or other consequential actions.

Read [the lesson practical](s20/s20-l08.md) and [reference answer](../solutions/s20/s20-l08.md).

Prepare a synthetic consequential action and inspect zero effect before approval, after expiry and after rejection; then approve the exact current action.

Acceptance: Approval binds the persisted task owner, exact current payload revision and expiry. Unsupported upload/download/message families must fail closed or be explicitly unimplemented, not be presented as tested. Do not use personal accounts or real irreversible actions to demonstrate the boundary.

## s20-l09: Implement Approve, Edit and Reject Controls

Let users confirm, modify or cancel proposed browser actions before execution.

Read [the lesson practical](s20/s20-l09.md) and [reference answer](../solutions/s20/s20-l09.md).

Use the real app to edit a proposed draft, try its old approval revision, then approve the edited revision. Separately reject another action.

Acceptance: Editing persists a replacement and clears prior approval. A fresh exact approval is required before the changed payload executes. Reject creates no side effect. Keep the original and edited payload histories and the actual synthetic endpoint effect count; a button label alone does not prove this flow.

## s20-l10: Add Subagents for Specialist Tasks

Delegate focused research, extraction or review tasks while preserving central coordination.

Read [the lesson practical](s20/s20-l10.md) and [reference answer](../solutions/s20/s20-l10.md).

Delegate disjoint research/extraction/review tasks, collect attributed contributions and preserve an explicit gap when one specialist fails.

Acceptance: Finite Python threads demonstrate worker coordination, not native model subagents. The taught native model-backed specialist path must actually contribute findings through central policy and budgets. Subagents cannot grant themselves browser permissions or override pending human decisions.

## s20-l11: Add Progress Tracking and Visible Checklists

Present completed, active and pending tasks through an understandable progress display.

Read [the lesson practical](s20/s20-l11.md) and [reference answer](../solutions/s20/s20-l11.md).

Observe pending, active, completed, rejected and unresolved states in the actual running checklist and inspect the linked evidence.

Acceptance: Progress derives from persisted execution records, not a fabricated percentage. Completed counts must correspond to completed steps; pending approvals and unknown effects remain visible. Capture real transitions from the owned app.

## s20-l12: Test the Sidekick on Real-World Tasks

Evaluate navigation, research quality, recovery behavior, permissions and task completion.

Read [the lesson practical](s20/s20-l12.md) and [reference answer](../solutions/s20/s20-l12.md).

Run scoped harmless tasks for navigation/research, a reviewed synthetic draft, permission denial and interrupted recovery. Compare actual outcome with measurable objective criteria.

Acceptance: Local Academy tasks model real workflow shape without touching personal accounts. Keep genuine browser/model/policy/evaluator observations separate from deterministic contract tests. Report failures and unimplemented features, not only successful screenshots. An earlier partial smoke test is not this integrated task suite.

## s20-l13: Build the Gradio Interface

Create a workspace for requests, browser updates, approvals, files and final results.

Read [the lesson practical](s20/s20-l13.md) and [reference answer](../solutions/s20/s20-l13.md).

Use one workspace for objective entry, current browser view, approval controls, progress, owned files and final results. Reopen the session and verify ownership isolation.

Acceptance: A genuine Blocks constructor proves UI construction only. The finished UI must feed the actual integrated planner/executor/evaluator, show genuine browser updates, and expose only owned artifacts/results. No arbitrary public file serving or personal browser session may be used.

## s20-l14: Trace and Evaluate Sidekick Runs

Analyze execution paths, tool success, user interventions, latency and completion quality.

Read [the lesson practical](s20/s20-l14.md) and [reference answer](../solutions/s20/s20-l14.md).

Analyze one complete run with model/planner, browser/tool, specialist, evaluator and user-decision events. Identify latency, evidence quality and the actual completion decision.

Acceptance: Timing and status must come from the actual run. Keep controlled failures, user interventions and unresolved gaps. Distinguish local traces from hosted traces; no fabricated throughput/quality benchmarks. A constructor or disconnected helper result cannot prove full run latency.

## s20-l15: Complete the Browser Task Sidekick

Integrate the application, run a full demonstration and review the finished architecture.

Read [the lesson practical](s20/s20-l15.md) and [reference answer](../solutions/s20/s20-l15.md).

Demonstrate one complete request from objective to validated plan, actual browser execution, evidence/research artifacts, evaluation, review if needed and final user-facing result.

Acceptance: The same persisted task must connect all taught components. Retain exact source/environment and genuine full-run evidence, including configured model inputs/results where claimed, browser views, artifacts, decisions and final objective checks. Document limits and unknown-effect handling. Do not call the project complete because individual helpers pass.

## Model and artifact evidence boundary

Configure a model transport with retries disabled for an admitted native run. A timed-out or missing planning receipt remains unresolved; recover its original evidence rather than automatically resubmitting. Use synthetic Academy data and an isolated owned browser context. Browser updates and files shown in the UI must resolve to current recorded observations for that task and owner. Capture only genuine screens or truthful conceptual illustrations, with no baked subtitles or decorative desks/devices.

## Stable UI startup and mode contract

The actual entrypoint is `projects/06-browser-sidekick/ui_gradio.py`. `build_ui(database, sandbox, *, model=None, workspace_root=None, executable_path=None, application=None)` uses the same integrated application. A configured native run passes an explicit `--model provider:model`; omitting it deliberately selects the visibly labeled deterministic fixture, with no silent fallback after a native error. `--database`, `--workspace-root` and optional `--browser-executable` bind owned local state and the admitted installed Chromium. The server binds loopback with public sharing disabled.

Current UI source shows genuine owned Playwright PNG observations inline and returns artifact data links only after session membership and exact SHA checks, together with final lifecycle/evaluation and trace. That authored rendering path still requires actual central browser/UI interaction proof; a constructed Blocks object does not establish that it ran.
