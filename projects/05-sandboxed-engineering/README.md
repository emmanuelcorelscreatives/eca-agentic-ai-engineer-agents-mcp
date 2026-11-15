# Project 5 — Sandboxed AI Engineering Team

Stage 14–15 teaching baseline: product manager → architect → developer → QA.
This offline version uses a reviewed deterministic application template, without
provider calls or claims that a live CrewAI team has run.

## Start here

Use Python 3.10 or newer for the standard-library template below. Use Linux/WSL
and Python 3.12 for the [learning laboratory](learning/README.md), whose file
tools require POSIX descriptor operations. The optional CrewAI environment is
separate and requires Python 3.12, Docker and additional reviewed dependencies.
Run the following commands from the **repository root**, not this directory.
The output path must not already exist; choose a new course-only path on reruns.

```sh
python3 projects/05-sandboxed-engineering/team.py --output /tmp/eca-expense-source.zip
python3 -m unittest discover -s tests -p 'test_projects_4_5.py'
```

The plan records requirements, architecture, dependency order and SHA-256 artifact
identities. Generated source, tests, standard-library-only requirements and usage
instructions are packaged only after actual six-test success. Every run uses a new
temporary directory, deleted on completion. ZIP creation is exclusive and never
replaces existing files. Currency amounts are non-negative integer minor units;
this example has no networking, database, credentials or third-party packages.

## Inspect and use the offline result

This walkthrough is only for the unchanged, reviewed `team.py` template ZIP you
just created. Never use it to run unreviewed generated source on your host.
First inspect its five members (`expense_app.py`, `test_expense_app.py`,
`requirements.txt`, `README.md`, `delivery-plan.json`):

```sh
python3 -m zipfile -l /tmp/eca-expense-source.zip
python3 -m zipfile -t /tmp/eca-expense-source.zip
```

Extract only that known template into a new directory, inspect it, then run its
documented tests and one use case:

```sh
python3 - <<'PY'
from pathlib import Path
import tempfile
from zipfile import ZipFile

destination = Path(tempfile.mkdtemp(prefix='eca-expense-student-'))
with ZipFile('/tmp/eca-expense-source.zip') as archive:
    expected = {'expense_app.py', 'test_expense_app.py', 'requirements.txt', 'README.md', 'delivery-plan.json'}
    assert len(archive.namelist()) == 5 and set(archive.namelist()) == expected
    archive.extractall(destination)
print(destination)
PY
```

Change directory to the printed path. Read the source and README before running:

```sh
python3 -m unittest -v
python3 -c 'from expense_app import total_expenses; print(total_expenses([125, 275]))'
```

Expected: six passing tests and `400` integer minor units. This is an expected
result for the fixed template, not a claim that your run has already succeeded.
Retain your own output and remove only your own scratch directory when finished.

Continue with the [offline worked activities](learning/WORKED-EXAMPLE.md),
[Stage 14 exercises](learning/stage-14-exercises.md),
[Stage 15 exercises](learning/stage-15-exercises.md) and the optional
[whole-container setup](learning/CONTAINER.md). The worked activities include
complete file-tool and repair calls for the short exercises below.

## Execution boundaries

A temporary folder is **not a general code sandbox**. Host execution is permitted
only after every generated program/test byte matches the reviewed fixed template,
and the directory contains exactly the expected files. Arbitrary model-written
code is rejected. Path traversal, absolute paths and symlink targets are rejected.
The subprocess has a bounded timeout and uses isolated Python mode.

`test(workspace, docker_image='python@sha256:REAL_PRELOADED_DIGEST')` offers the
optional Docker path. Replace the placeholder with a real locally installed digest.
It uses no network, no image pulls, a read-only root/workspace, an unprivileged UID,
no capabilities, no privilege escalation, 1 CPU, 256 MiB, 64 PIDs and a small tmpfs.
Only its unique owned container name may be removed on timeout; unproven cleanup
raises a hard error. **Docker has not been run or installed by this example.** A
root-owned, unreadable temporary directory must first be deliberately staged as a
readable course-only workspace for UID 65534; never expose another user's files.
No Docker socket, host home, secrets or arbitrary host directories should be mounted.
The reviewed-template guard also applies to this optional path.

## Optional live crew and uv extension

Map the four roles to CrewAI tasks with the same typed specification and explicit
dependencies. Give the developer only a contained file-writing tool. Put model-written
code in a **separate, independently provisioned restricted container executor**;
never disable `verify_template` to run it on the host. Planning text is not permission
to invoke arbitrary commands. A uv environment may be prepared with explicitly
approved pinned dependencies before disabling network for the exercise. This
stdlib example's empty requirements file is intentional and needs no download.

Bound repairs to two attempts: retain the failing test report, identify the failed
requirement, propose a minimal patch, run QA again and record all changed hashes.
Exhaustion means a held delivery, not a fabricated pass. A live adapter is a student
extension, not an undocumented dependency of the offline runnable project.

## Exercises and solutions

1. Try a `../escape.py` path. **Solution:** `safe_path` raises before writing.
2. Alter generated source before QA. **Solution:** `verify_template` rejects it;
   changing the expected hash to bypass review is not a valid repair.
3. Test floating amounts and booleans. **Solution:** both raise `ValueError`; integers
   preserve exact arithmetic without accidental binary floating-point rounding.
4. Design a subtraction feature. **Solution design:** write acceptance criteria,
   distinguish refunds from invalid negative expenses, add tests and independently
   review a new allowed template. The existing specification rejects unsupported
   features instead of pretending to implement them.
5. Add a faulty template to an isolated exercise copy. **Solution:** retain actual
   failing QA, repair the source and tests against the original criteria, and package
   only after the same requirements pass. Do not change the answer to match a bug.

## Implemented optional live engineering crew

`crewai_adapter.py` implements actual CrewAI product-manager, architect, developer
and QA agents with structured source-bundle output and explicit task dependencies.
Generated code is syntax-checked only on the host, then executed **only** inside the
restricted Docker container. The course adds its own six acceptance tests separately
from generated tests. Only an actual successful test run may produce the ZIP and
its `actual-qa.json`; a model's claimed pass is ignored. No automatic retry hides a
failed run. Review failed source and retained process output before approving a new run.

```sh
python3 -m venv /tmp/eca-engineering-live
/tmp/eca-engineering-live/bin/pip install -r projects/05-sandboxed-engineering/requirements-live.txt
# Provision Docker and a real Python image digest separately; no auto-pull is allowed.
/tmp/eca-engineering-live/bin/python projects/05-sandboxed-engineering/crewai_adapter.py \
  --run-live --model PROVIDER/MODEL --docker-image python@sha256:REAL_DIGEST \
  --output /tmp/eca-live-source.zip
```

The optional adapter has not made provider calls or run Docker in this build. Pure
validation and syntax checks are tested; actual SDK and container runtime integration
remain explicit execution prerequisites. The constraints isolate host resources,
while tests check this exercise's acceptance criteria; they are not a proof that
arbitrary malicious code is safe. Reviewed current API reference:
[CrewAI crews](https://docs.crewai.com/v1.15.40/en/concepts/crews) and
[tasks](https://docs.crewai.com/v1.15.40/en/concepts/tasks).

### Bounded live-code logs

The optional live adapter now delegates Docker execution to `learning/sandbox.py`:
stdout/stderr spool to size-limited files, Docker daemon logs are disabled, timeout
cleanup targets only the owned container, and unproven cleanup fails delivery. An
actual local controlled subprocess flood and timeout were tested with Docker calls
mocked; neither result is evidence that a real container was run. A model's claimed
success or an exit-zero process without the minimum observed test count is rejected.
