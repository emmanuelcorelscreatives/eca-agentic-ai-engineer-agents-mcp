# Your offline engineering notebook

These activities use the supplied local fixtures and source, not an inaccessible
recording. Run from the **repository root** on Linux/WSL with Python 3.12. No
Docker, uv, API key, SDK install or paid call is needed. The helper only writes
and removes its own temporary file-activity directory; it never executes the
written Python text. Repair inputs `first` and `sum` are allowlisted labels,
not Python code. Do not replace them with `eval`, shell text or a host-code runner.

## 1. File tool: setup, attempt, inspect

```sh
python3 projects/05-sandboxed-engineering/learning/student_lab.py files
```

Read `file_activity` in `student_lab.py`. It creates `src/` and `tests/` in a new
scratch workspace, writes and reads `src/app.py`, lists files and replaces content
using the previous SHA-256. Expected output includes:

- `content`: `amount = 400\n`; changed original/updated hashes.
- Rejected traversal and absolute paths (`ValueError`), tests write
  (`PermissionError`), stale update (`ValueError`) and symlink read (OS error).
- `application_executed: false` and `temporary_workspace_removed: true`.

Exercise: in an isolated copy of the helper, add a nested `src/models/` directory
before writing `src/models/expense.py`. Explain why its parent must already exist.
Keep dangerous paths as input strings to `FileTools`, never commands to a shell.
Solution: explicitly create that parent inside the scratch workspace; traversal,
symlinks and writes outside the allowed `src` scope must still be rejected.

## 2. Failed case, diagnosis, bounded repair

```sh
python3 projects/05-sandboxed-engineering/learning/student_lab.py repair
```

Record your own output. Expected trace:

| Attempt | Label | Input | Expected | Observed | Fixture status |
| --- | --- | --- | --- | --- | --- |
| 0 | first | [125, 275] | 400 | 125 | failed |
| 1 | sum | [125, 275] | 400 | 400 | passed |

The empty and zero cases also run. Compare both `source_sha256` values and
receipts in `result.trace`; the source mapping changes only
`src/operator.py: first -> sum`, keeping `tests/fixed.txt` unchanged.
This is actual local arithmetic, **not generated Python execution**, a model
response, a 22-test recording or a container pass. It does not check R3.

Exercise: use `workflow.bounded_repair` as shown in `repair_activity`, but supply
no patches and `maximum=0`. Then try the unchanged `first` patch. Expected
solutions: one failed attempt with budget exhausted; unchanged repair stops
without repeating the same source. Changing a `tests/` entry raises `ValueError`.
See `WorkflowTests.test_budget_exhausted`, `test_repeated_patch_stops` and
`test_test_weakening_denied` in `tests/test_engineering_learning.py` for exact calls.

## 3. Requirements and integrated handoff contracts

```sh
python3 projects/05-sandboxed-engineering/learning/student_lab.py handoffs
```

`handoff_activity` adapts the supplied human reference to the integrated
`semantic_team.validate_requirements` schema: S1, R1–R3, priorities 1–3 and a
complete ordered priority list. Its local envelope is consumed, then changed
content and obsolete revision are rejected. `response_sha256` here identifies
explicit local reference data; it is **not** a fabricated model receipt.

Exercise: copy the requirements into your own exercise file; remove R3, use an
unknown story ID, or remove a priority. Each must fail validation. Build an
architecture using `expense_app.py`, `total_expenses(amounts)`, all R IDs, the
current requirements hash, data flows, implementation plan and empty dependencies.
Use `validate_architecture`; R99 or a stale requirements hash must fail. See the
schemas in `semantic_team.py:run_team` and the corresponding validation functions.

## 4. QA, invalid inputs and application delivery

Inspect the literal `APP`, `TESTS` and `FILES` in `../team.py`. They provide the
complete standard-library expense app, six test cases, README and dependency
declaration. Compare their R3 tests with `semantic_team.ACCEPTANCE_TESTS`: negatives,
decimals and booleans must raise `ValueError`. The arithmetic fixture above cannot
stand in for these cases. The [project quickstart](../README.md#inspect-and-use-the-offline-result)
shows how to build, inspect, extract and test the **unchanged reviewed template**.

Learner-created exercise: make a two-column contract table with an architect
requesting `TypeError` and QA expecting `ValueError` for invalid types. Predict
why these conflict, and propose one agreed exception before implementation.
Reference solution: use `ValueError` consistently with the supplied course tests;
do not weaken tests to conceal disagreement. This is a design exercise, not a
claim that a historical team or a new generated application ran.

## 5. Four-role orchestration and final review

Run the local suites listed in [README](README.md#local-verification-map).
`tests/test_engineering_semantic_team.py` supplies `ProviderDouble` and
`ExecutorDouble` for tracing PM → architect → developer → QA → repair → QA. Its
executor returns canned observations; it does **not** execute its source strings.
`tests/test_engineering_delivery_package.py` packages explicit fixture results,
labelled `OFFLINE_FIXTURE_NOT_PRODUCTION`. Inspect its `fixture` method and archive
checks as a packaging exercise, not a real-provider delivery.

For your final notebook, include the local outputs, initial/final label mapping,
unchanged test marker, requirement/handoff checks, R1/R2 versus R3 coverage,
template file inventory and a list of what was **not** run. A fresh live four-role
project is a separate optional exercise using [CONTAINER.md](CONTAINER.md), with
its own actual outputs. No private course recording or paid rerun is required to
complete this offline notebook.
