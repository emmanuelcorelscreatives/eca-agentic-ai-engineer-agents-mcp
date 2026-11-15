# Project 6 — Browser Task Sidekick

Stage 20's working foundation is a persistent task executor. The default demo reads a bundled **synthetic** workshop catalogue. It makes no external model, account, booking or payment calls.

Use Python 3.11 or newer. Choose the exercise you want to run:

| Route | Entry point | Requirements and expected result |
|---|---|---|
| Offline foundation | `sidekick.py` | Standard library only; parses bundled HTML and persists a checklist. No browser or model. |
| Browser foundation | `PlaywrightBrowser` | Installed Playwright/Chromium; reads the same catalogue through an actual loopback browser. No model or MCP. |
| Integrated fixture workspace | `ui_gradio.py` without `--model` | Optional SDK environment, Gradio and Chromium; deterministic plan, actual local browser observations, approvals and files. No model calls. |
| Native workspace | `ui_gradio.py --model provider:model` | Explicitly configured provider and budget in addition to the UI/browser environment; model requests may cost money. No silent fallback to a fixture. |
| Browser through MCP | [Browser labs](BROWSER-LABS.md#browser-through-mcp) | Separate MCP client/server exercise; direct Playwright reads alone do not establish MCP connectivity. |

```sh
cd projects/06-browser-sidekick
python3 sidekick.py --database /tmp/academy-sidekick.sqlite
```

Run this block from the repository root; subsequent commands in this README use the project directory. Replace `/tmp/academy-sidekick.sqlite` with a new writable local path on Windows. Run the shared tests from the repository root with `python3 scripts/run_tests.py`. Follow the [stage 11–20 workbook](../../curriculum/workbooks/stages-11-20.md) for lesson exercises.

The output includes the real extracted workshop dates and prices, persisted results and a checklist. Reopening the same SQLite database retains the plan, decisions and trace. Each task has its own UUID.

Expected **synthetic** catalogue values are Agent Foundations — 2030-04-12 — USD 30 and Browser Tools — 2030-04-19 — USD 45. A second demo invocation creates a new task; it does not resume the previous UUID. [Foundation exercises](EXERCISES.md) and [solutions](SOLUTIONS.md) use these values. The integrated fixture is a different catalogue: Python $40, SQL $35, with a Python detail date of 2026-12-01; do not compare its observations with the foundation answer key.

For complete setup, actual browser/client commands, the integrated UI interaction sequence and restart limitations, use [Browser labs](BROWSER-LABS.md). The [Stage 20 practical workbook](../../labs/s20-practical-workbook.md) contains the fifteen integrated exercises; the [shared workbook](../../curriculum/workbooks/stages-11-20.md#stage-16) starts the Stage 16–20 progression. Construction, deterministic test behavior and actual model/browser/UI execution are distinct observations.

## Execution contract

A `Step` has an allowlisted action, target, value and explicit completion criterion. `TaskStore.advance` executes the earliest unfinished step. Empty results fail; this basic evaluator checks tool execution, **not the semantic truth of every objective**. A rejected or failed step stops following work.

`submit`, `download`, `upload` and `message` require approval bound to the exact step digest. `decide(..., 'edit', replacement)` clears approval. Execution is checkpointed before calling a tool. A process crash can leave `executing`, meaning **unknown outcome requiring investigation**, never an automatic retry. An explicit approved state does not make an unsupported tool available: the bundled fixture and browser adapters reject consequential actions.

`ArtifactTools(reader, dedicated_output_root)` wraps a read adapter with approval-required `save`. It accepts only simple filenames and creates each file exclusively, refusing existing paths. Use a trusted dedicated output directory. Browser mutation adapters must independently enforce destination, identity, content and idempotency controls.

## Optional genuine Playwright browser

Follow the pinned environment and two-terminal commands in [Browser labs](BROWSER-LABS.md#browser-foundation). Serve only this project's fixture directory, not an account/admin service.

Instantiate `PlaywrightBrowser('http://127.0.0.1:8765')` and use the same `extract` step. It launches an actual browser and reads actual page text. The adapter allows only GET requests to that exact loopback origin, blocks service workers/downloads, closes the browser, and rejects sensitive actions. Use a dedicated fixture server rather than a local account/admin service. A genuine Chromium loopback extraction was executed successfully in the separate SDK proof using the optional `executable_path` constructor parameter and the owned Chromium executable. This proves that bounded browser path; interactive UI behavior and external research are separate requirements.

## Curriculum development sequence

1. Start with the typed plan and explicit criteria; inspect real checklist and SQLite trace.
2. Run fixture extraction, reopen the database, and demonstrate persistent state.
3. Add middleware using a wrapper implementing `Executor.execute` without changing approval binding.
4. Demonstrate approve/edit/reject with a recording test executor; label its synthetic result.
5. Add narrowly scoped research specialists returning cited fixture findings; execution in your environment remains the only action authority.
6. Use the supplied integrated Gradio interface and trace its calls to `SidekickApplication`; treat UI display as separate from tool authorization. Extend it in your own exercise copy rather than rebuilding an already supplied interface.
7. Evaluate actual browser behavior and failure recovery before enabling a new action adapter.

`sidekick.py` is the deterministic foundation, not an LLM planner or complete interface. The supplied `pipeline.py`, `advanced.py` and `ui_gradio.py` add separate integrated planning, execution and UI paths; read their lab instructions before enabling them. Source presence does not verify model quality, browser callbacks or external mutation. The offline demo never enables those paths.

See `EXERCISES.md` and `SOLUTIONS.md`; repository tests include resume, crash recovery, approval tampering by edit, rejection, empty output and path escape.

## Restarting the integrated fixture

The UI stores the owned fixture's exact loopback port, private authorization token and synthetic idempotency receipts alongside task state in the exercise database. Reopen with the **same database and workspace**, and restore your private session secret before selecting a task. Completed and unknown steps are not replayed; approval expiry still applies. If the saved port is occupied, startup fails instead of selecting another port or retargeting an approved plan. Stop the other instance or investigate the conflict; do not change unrelated services.

Older databases created without persisted sandbox identity are retained but cannot be silently adopted by a new server. Inspect their saved state without execution and use a fresh database for a new exercise. Keep database files and workspaces private and out of Git. These guarantees concern the synthetic local fixture only, not restart recovery for external websites or production services. Tests use local HTTP/recording adapters; actual browser/UI restart interaction remains a separate integration check.

## Installed optional environment evidence

`requirements-optional.txt` pins the direct SDKs actually installed for the course verification; `requirements-optional-lock.txt` records the full pip-resolved environment. `pip check` passed. Actual LangGraph SQLite interrupt/close/reopen/resume and Gradio Blocks construction also passed. These results do not claim live-model planning, live native subagent responses, browser UI callbacks, screenshot links or external-site research.
