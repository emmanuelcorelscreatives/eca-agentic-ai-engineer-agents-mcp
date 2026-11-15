# Stage 17: practical guide

Read each lesson handout and its corresponding reference solution under `solutions/s17/`. The [stage 11–20 workbook](../../curriculum/workbooks/stages-11-20.md) supplies the exact titles, tasks and acceptance criteria.

## Shared case

Synthetic Academy support/product lookup using LangGraph routing, ToolNode loops, parallel evidence reduction and recovery graphs. Scripted model responses are fixtures, not provider observations.

## Set up the optional framework environment

From the repository root, create a separate Python 3.11+ environment rather than modifying the dependency-free core environment:

```sh
python3 -m venv .venv-browser
. .venv-browser/bin/activate
python -m pip install -r projects/06-browser-sidekick/requirements-optional.txt
python -m unittest discover -s tests -p test_s17_native_features.py -v
```

On Windows, activate with `.venv-browser\Scripts\Activate.ps1`. Core tests can skip optional SDK cases when dependencies are absent; those skips do not verify the framework. Installing the optional requirements is not a model call. Read each exercise before enabling provider or hosted tracing operations.

## Verify your result

Record the exact checkout, dependency versions, command and actual output. SDK construction, scripted native-framework execution, live provider responses and browser interactions verify different things. Do not infer an integration result from source presence or a historical test count. SQLite is the required persistent database here; PostgreSQL is an optional extension. Stage 17 lesson 10 requires an explicitly configured real LangSmith observation; local timed instrumentation alone does not complete that hosted-tracing exercise.

## Run the native fixture graphs

```sh
python -m examples.s17.native_graph_features
```

This executes the parallel-evidence, tool-loop and recovery graphs against synthetic fixtures. Hosted telemetry is disabled by default. The separate `--langsmith` option requires private account configuration and deliberately sends tracing data; inspect the actual hosted run before claiming success.
