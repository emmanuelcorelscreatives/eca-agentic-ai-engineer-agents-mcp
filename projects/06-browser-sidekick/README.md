# Project 6 — Browser Task Sidekick

Stage 20's working foundation is a persistent task executor. The default demo reads a bundled **synthetic** workshop catalogue. It makes no external model, account, booking or payment calls.

```sh
python3 sidekick.py --database /tmp/academy-sidekick.sqlite
```

The output includes the real extracted workshop dates and prices, persisted results and a checklist. Reopening the same SQLite database retains the plan, decisions and trace. Each task has its own UUID.

## Execution contract

A `Step` has an allowlisted action, target, value and explicit completion criterion. `TaskStore.advance` executes the earliest unfinished step. Empty results fail; this basic evaluator checks tool execution, **not the semantic truth of every objective**. A rejected or failed step stops following work.

`submit`, `download`, `upload` and `message` require approval bound to the exact step digest. `decide(..., 'edit', replacement)` clears approval. Execution is checkpointed before calling a tool. A process crash can leave `executing`, meaning **unknown outcome requiring investigation**, never an automatic retry. An explicit approved state does not make an unsupported tool available: the bundled fixture and browser adapters reject consequential actions.

`ArtifactTools(reader, dedicated_output_root)` wraps a read adapter with approval-required `save`. It accepts only simple filenames and creates each file exclusively, refusing existing paths. Use a trusted dedicated output directory. Browser mutation adapters must independently enforce destination, identity, content and idempotency controls.

## Optional genuine Playwright browser

Install Playwright in a disposable virtual environment and its Chromium runtime, then serve only this project's fixture directory:

```sh
python3 -m venv /tmp/academy-browser-venv
/tmp/academy-browser-venv/bin/pip install playwright
/tmp/academy-browser-venv/bin/playwright install chromium
python3 -m http.server 8765 --bind 127.0.0.1 --directory fixtures
```

Instantiate `PlaywrightBrowser('http://127.0.0.1:8765')` and use the same `extract` step. It launches an actual browser and reads actual page text. The adapter allows only GET requests to that exact loopback origin, blocks service workers/downloads, closes the browser, and rejects sensitive actions. Use a dedicated fixture server rather than a local account/admin service. A genuine Chromium loopback extraction was executed successfully in the separate SDK proof using the optional `executable_path` constructor parameter and the owned Chromium executable. This proves that bounded browser path; interactive UI behavior and external research are separate requirements.

## Curriculum development sequence

1. Start with the typed plan and explicit criteria; inspect real checklist and SQLite trace.
2. Run fixture extraction, reopen the database, and demonstrate persistent state.
3. Add middleware using a wrapper implementing `Executor.execute` without changing approval binding.
4. Demonstrate approve/edit/reject with a recording test executor; label its synthetic result.
5. Add narrowly scoped research specialists returning cited fixture findings; central execution remains the only action authority.
6. Add a Gradio interface over `create`, `checklist`, `decide` and `advance`; treat UI display as separate from tool authorization.
7. Evaluate actual browser behavior and failure recovery before enabling a new action adapter.

The shipped core does not claim to implement an LLM planner, Gradio app, external mutation adapter or autonomous semantic evaluator. Those extensions require actual code and genuine results before their specific lessons are recorded.

See `EXERCISES.md` and `SOLUTIONS.md`; repository tests include resume, crash recovery, approval tampering by edit, rejection, empty output and path escape.

## Installed optional environment evidence

`requirements-optional.txt` pins the direct SDKs actually installed for the course verification; `requirements-optional-lock.txt` records the full pip-resolved environment. `pip check` passed. Actual LangGraph SQLite interrupt/close/reopen/resume and Gradio Blocks construction also passed. These results do not claim live-model planning, live native subagent responses, browser UI callbacks, screenshot links or external-site research.
