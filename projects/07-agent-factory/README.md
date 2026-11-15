# Project 7 — Agent Application Factory

This runnable factory demonstrates Stage 25's typed specification → requirements → architecture → scaffolding → tests → validated project pipeline. Its baseline is an honest deterministic `stdlib` adapter. It does **not** fabricate AutoGen, model reasoning, code-review judgments or API results.

```sh
cd projects/07-agent-factory
python3 factory.py examples/text_helper.json /tmp/academy-generated-text-helper
cd /tmp/academy-generated-text-helper
python3 -m unittest -v
python3 agent.py < request.json
```

Start the block from the repository root. On Windows, replace `/tmp/academy-generated-text-helper` throughout with a new writable local directory. Return to the repository root to run `python3 scripts/run_tests.py`. The [stage 21–30 workbook](../../curriculum/workbooks/stages-21-30.md) covers the framework lessons and stage 25 exercises. `EXERCISES.md` and `SOLUTIONS.md` beside this README contain the baseline tasks and reference answers.

Choose a new output directory on each run. A successful factory run has actually executed the generated application's tests before writing the final artifact set. Its `validation-receipt.json` records the command, actual exit code/stdout/stderr and SHA256 of every generated source/config/document file. For the supplied request, the real application returns `{"words": 2}`.

## Specification and architecture

`AgentSpec` requires purpose, users, tools, data, outputs and policies. Names are safe Python identifiers. Tools are the explicit typed `word_count` and `uppercase` implementations. The executable adapter permits only `stdlib` with local/Docker deployment; other framework values raise a clear error rather than pretending integration succeeded.

Requirements and architecture are serialized alongside code. Policy text remains data in documentation/instructions, not interpolated executable code. Structural review parses Python and verifies the expected artifact inventory and application imports. Actual behavioral tests reject forbidden tools and invalid input as well as checking enabled functionality.

The temporary-directory test runner uses Python isolated import mode and a 15-second timeout. **This is not an OS security sandbox and must not be used for untrusted generated code.** Only the factory's fixed validated templates may enter this runner. Docker configuration is supplied for the separate isolation lesson:

```sh
docker build -t academy-text-helper /tmp/academy-generated-text-helper
docker run --rm -i --network none --read-only --cap-drop ALL --security-opt no-new-privileges academy-text-helper < /tmp/academy-generated-text-helper/request.json
```

Building the Python base image may require network access. The runtime command blocks network, uses a nonroot user and a read-only filesystem. These Docker commands are instructions, **not a claim that Docker was executed during the offline unit-test run**.

## Curriculum extensions

Use the same typed specification and executable acceptance tests to add a genuine framework adapter. Each adapter must produce its own real imports, dependencies, entry point and smoke tests; do not simply relabel the stdlib implementation. Replaceable adapter design does not mean every framework is already implemented.

For the bounded repair-loop lesson: retain the actual failure diagnostics and changed source, diagnose the exact failed assertion, produce one explicit changed template patch, generate into a fresh directory and rerun all generated tests. The baseline writes `validation-receipt.json` only after success; a failed validation raises an error instead. [Solution 8](SOLUTIONS.md#8-retain-a-tool-failure-and-repair-it) is a complete offline example that preserves both attempts without changing this repository's templates. No generated app should be launched until its actual validation passes.

See `EXERCISES.md` and `SOLUTIONS.md`. No API credentials or paid calls are needed for the baseline.

## Stage 25: choose the right path

| Path | Input and tools | Exercise/result |
| --- | --- | --- |
| Text-helper baseline above | `factory.AgentSpec`, `examples/text_helper.json`; `word_count`, `uppercase` | Four generated tests; `{"words": 2}`. No model calls. |
| [Offline catalog worked example](SOLUTIONS.md#offline-catalog-worked-example) | `advanced.TypedSpec`, [catalog template](templates/catalog_research-spec.json); `catalog_lookup`, `draft_notification` | Five generated tests, an actual local catalog match and unsent drafts. No model calls. |
| [Typed model-pipeline guide](MODEL-PIPELINE-AUTHORING.md) | Catalog `TypedSpec`, `AutoGenBackend`, `Pipeline` | Optional real specialist proposals, then separately implemented contained validation and launch. Requires explicit account/budget authorization. |
| [Legacy AutoGen proposal adapter](FRAMEWORKS.md) | Text-helper `AgentSpec`, four-turn proposal team | Optional proposal only; not the typed catalog pipeline or a validated/started application. |

The advanced examples target Python 3.12 on Linux or another supported POSIX environment because the call ledger uses `fcntl`; Windows learners need a suitable POSIX environment for that path. This restriction does not apply to the stdlib text-helper baseline. No private helper or pre-existing virtual environment is needed. The [guide](MODEL-PIPELINE-AUTHORING.md#setup-and-offline-checks) gives clean environment commands and explains skipped optional tests.

For s25-l07, the typed instructions specialist produces **`instructions.json`**, not the legacy baseline's `instructions.md`. It contains role, goals, allowed tools, policies, refusal, escalation and untrusted-data handling. Use that JSON as the specialist deliverable; a Markdown rendering is optional.

`run_factory` validates and records a release decision; it does **not** launch the application (`launch_performed` remains false). The guide identifies the existing callbacks and the separate `launch_validated` extension. Do not treat offline fixture tests, generated SDK scaffolds or an approved proposal as real model/Docker/launch evidence.
