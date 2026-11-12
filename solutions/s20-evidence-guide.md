# Stage 20 evidence and reference guide

An Academy-owned local workshop/catalog research task, with synthetic draft-form interactions only. Keep planning, browser observations, source-attributed findings, evaluation, approvals, artifacts and user-facing progress in one persisted session.

No new runtime was executed by the documentation author. Every expected behavior below needs source-bound actual evidence from the sole centralized QA owner before an observed-result lesson is recorded. Historic baseline tests retain their narrow original scope.

## s20-l01: Design the Browser Task Sidekick

Reference source: `projects/06-browser-sidekick` → `advanced.py: Plan, SessionController; sidekick.py: TaskStore`.

Distinguish trusted user objective/application policy from untrusted page content. Show persisted task/step IDs, completion evidence, resource limits and approval boundaries. The architecture must include the integrated planner/evaluator/UI rather than treating disconnected helper functions as the finished application.

The detailed [reference answer](s20/s20-l01.md) preserves the exercise and evidence boundary.

## s20-l02: Build the Sidekick Planner

Reference source: `projects/06-browser-sidekick` → `advanced.py: Plan, parse_model_plan`.

A fixed fixture_plan is a labeled test double. The actual objective must reach the model-backed planner and its structured output must pass the real plan validator before persistence. Unknown tools, off-origin targets, oversized plans and cyclic or missing dependencies fail. A model proposal never grants permission to execute.

The detailed [reference answer](s20/s20-l02.md) preserves the exercise and evidence boundary.

## s20-l03: Build the Browser Executor

Reference source: `projects/06-browser-sidekick` → `sidekick.py: PlaywrightBrowser; sandbox_server.py: Sandbox`.

Own the browser/context/page and close them on failure. Use semantic locators, state waits and bounded timeouts. Keep the planned step and observation linked. The earlier urllib sandbox POST test is a real HTTP test but is not proof that a Playwright browser performed an interaction. Sensitive interactions wait for exact approval.

The detailed [reference answer](s20/s20-l03.md) preserves the exercise and evidence boundary.

## s20-l04: Build the Task Evaluator

Reference source: `projects/06-browser-sidekick` → `advanced.py: evaluate, Evaluation, Decision; SessionController`.

An evaluator is useful only when its result affects the persisted execution lifecycle. Missing source evidence cannot become COMPLETE because an assistant says so. Revision preserves completed/unknown work and respects remaining replan/step budgets; unsupported or exhausted work stops honestly.

The detailed [reference answer](s20/s20-l04.md) preserves the exercise and evidence boundary.

## s20-l05: Add Research and File Tools

Reference source: `projects/06-browser-sidekick` → `sidekick.py: ArtifactTools; advanced.py: Finding`.

Artifacts retain source URL and observed data alongside any synthesized summary. Reject traversal, symlink escape, oversized writes and unowned paths. The final app must wire controlled file saves to execution and genuine owned artifact views, not merely contain an unused file-tool class.

The detailed [reference answer](s20/s20-l05.md) preserves the exercise and evidence boundary.

## s20-l06: Add Memory and Persistent Task State

Reference source: `projects/06-browser-sidekick` → `advanced.py: SessionController; sidekick.py: TaskStore`.

Persist trusted ownership, current action digest/expiry, plan counters and event history. A completed local effect may be reused only with its authentic receipt. An interrupted consequential action with uncertain outcome remains unresolved; never automatically replay it to make the checklist green.

The detailed [reference answer](s20/s20-l06.md) preserves the exercise and evidence boundary.

## s20-l07: Add Middleware and Execution Policies

Reference source: `projects/06-browser-sidekick` → `advanced.py: Plan.validate, SessionController.advance; sandbox_server.py: ApprovedSandboxExecutor`.

Logging, validation, permissions and context rules must apply on the actual dispatched path. Redact dummy secrets/personal fields and keep correlation and timing evidence. Native-framework middleware is only a native-framework claim if that actual path runs; application policy wrappers can enforce the same boundary without pretending to be another API.

The detailed [reference answer](s20/s20-l07.md) preserves the exercise and evidence boundary.

## s20-l08: Add Human Approval for Sensitive Actions

Reference source: `projects/06-browser-sidekick` → `advanced.py: SessionController.decide, SessionController.advance`.

Approval binds the persisted task owner, exact current payload revision and expiry. Unsupported upload/download/message families must fail closed or be explicitly unimplemented, not be presented as tested. Do not use personal accounts or real irreversible actions to demonstrate the boundary.

The detailed [reference answer](s20/s20-l08.md) preserves the exercise and evidence boundary.

## s20-l09: Implement Approve, Edit and Reject Controls

Reference source: `projects/06-browser-sidekick` → `advanced.py: SessionController.decide; ui_gradio.py: build_ui`.

Editing persists a replacement and clears prior approval. A fresh exact approval is required before the changed payload executes. Reject creates no side effect. Keep the original and edited payload histories and the actual synthetic endpoint effect count; a button label alone does not prove this flow.

The detailed [reference answer](s20/s20-l09.md) preserves the exercise and evidence boundary.

## s20-l10: Add Subagents for Specialist Tasks

Reference source: `projects/06-browser-sidekick` → `advanced.py: coordinate_research, build_deep_agent`.

Finite Python threads demonstrate worker coordination, not native model subagents. The taught native model-backed specialist path must actually contribute findings through central policy and budgets. Subagents cannot grant themselves browser permissions or override pending human decisions.

The detailed [reference answer](s20/s20-l10.md) preserves the exercise and evidence boundary.

## s20-l11: Add Progress Tracking and Visible Checklists

Reference source: `projects/06-browser-sidekick` → `advanced.py: SessionController.snapshot; ui_gradio.py: build_ui`.

Progress derives from persisted execution records, not a fabricated percentage. Completed counts must correspond to completed steps; pending approvals and unknown effects remain visible. Capture real transitions from the owned app.

The detailed [reference answer](s20/s20-l11.md) preserves the exercise and evidence boundary.

## s20-l12: Test the Sidekick on Real-World Tasks

Reference source: `projects/06-browser-sidekick` → `sandbox_server.py: Sandbox; test_advanced.py`.

Local Academy tasks model real workflow shape without touching personal accounts. Keep genuine browser/model/policy/evaluator observations separate from deterministic contract tests. Report failures and unimplemented features, not only successful screenshots. An earlier partial smoke test is not this integrated task suite.

The detailed [reference answer](s20/s20-l12.md) preserves the exercise and evidence boundary.

## s20-l13: Build the Gradio Interface

Reference source: `projects/06-browser-sidekick` → `ui_gradio.py: build_ui`.

A genuine Blocks constructor proves UI construction only. The finished UI must feed the actual integrated planner/executor/evaluator, show genuine browser updates, and expose only owned artifacts/results. No arbitrary public file serving or personal browser session may be used.

The detailed [reference answer](s20/s20-l13.md) preserves the exercise and evidence boundary.

## s20-l14: Trace and Evaluate Sidekick Runs

Reference source: `projects/06-browser-sidekick` → `advanced.py: sidekick_event records, SessionController.snapshot`.

Timing and status must come from the actual run. Keep controlled failures, user interventions and unresolved gaps. Distinguish local traces from hosted traces; no fabricated throughput/quality benchmarks. A constructor or disconnected helper result cannot prove full run latency.

The detailed [reference answer](s20/s20-l14.md) preserves the exercise and evidence boundary.

## s20-l15: Complete the Browser Task Sidekick

Reference source: `projects/06-browser-sidekick` → `sidekick.py; advanced.py; ui_gradio.py`.

The same persisted task must connect all taught components. Retain exact source/environment and genuine full-run evidence, including configured model inputs/results where claimed, browser views, artifacts, decisions and final objective checks. Document limits and unknown-effect handling. Do not call the project complete because individual helpers pass.

The detailed [reference answer](s20/s20-l15.md) preserves the exercise and evidence boundary.

## Model and artifact evidence boundary

Configure a model transport with retries disabled for an admitted native run. A timed-out or missing planning receipt remains unresolved; recover its original evidence rather than automatically resubmitting. Use synthetic Academy data and an isolated owned browser context. Browser updates and files shown in the UI must resolve to current recorded observations for that task and owner. Capture only genuine screens or truthful conceptual illustrations, with no baked subtitles or decorative desks/devices.

## Stable UI startup and mode contract

The actual entrypoint is `projects/06-browser-sidekick/ui_gradio.py`. `build_ui(database, sandbox, *, model=None, workspace_root=None, executable_path=None, application=None)` uses the same integrated application. A configured native run passes an explicit `--model provider:model`; omitting it deliberately selects the visibly labeled deterministic fixture, with no silent fallback after a native error. `--database`, `--workspace-root` and optional `--browser-executable` bind owned local state and the admitted installed Chromium. The server binds loopback with public sharing disabled.

Current UI source shows genuine owned Playwright PNG observations inline and returns artifact data links only after session membership and exact SHA checks, together with final lifecycle/evaluation and trace. That authored rendering path still requires actual central browser/UI interaction proof; a constructed Blocks object does not establish that it ran.
