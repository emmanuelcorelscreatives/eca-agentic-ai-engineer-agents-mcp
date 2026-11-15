# Stage 18: practical guide

Read each lesson handout and its corresponding reference solution under `solutions/s18/`. The [stage 11–20 workbook](../../curriculum/workbooks/stages-11-20.md) supplies the exact titles, tasks and acceptance criteria.

## Shared case

LangGraph conversation, bounded Academy fixture-action review and persisted recovery. Edited action proposals require a fresh exact approval; a model cannot approve itself.

## Set up the optional framework environment

From the repository root, create a separate Python 3.11+ environment rather than modifying the dependency-free core environment:

```sh
python3 -m venv .venv-browser
. .venv-browser/bin/activate
python -m pip install -r projects/06-browser-sidekick/requirements-optional.txt
python -m unittest discover -s tests -p test_s18_native_features.py -v
```

On Windows, activate with `.venv-browser\Scripts\Activate.ps1`. Core tests can skip optional SDK cases when dependencies are absent; those skips do not verify the framework. Installing the optional requirements is not a model call. Read each exercise before enabling provider or hosted tracing operations.

## Verify your result

Record the exact checkout, dependency versions, command and actual output. SDK construction, scripted native-framework execution, live provider responses and browser interactions verify different things. Do not infer an integration result from source presence or a historical test count. SQLite is the required persistent database here; PostgreSQL is an optional extension. Stage 17 lesson 10 requires an explicitly configured real LangSmith observation; local timed instrumentation alone does not complete that hosted-tracing exercise.
