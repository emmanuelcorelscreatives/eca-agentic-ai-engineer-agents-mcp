# Stage 28 Lesson 11 — persistent controlled memory search

PDF objective: **Store, retrieve, update and search persistent memories through controlled operations.** This solution implements those operations; it does not invent a retention period, benchmark target, number of exercise records or a separate business objective.

Status: authored source and tests, awaiting centralized execution and genuine source-current captures. Earlier passing remember/recall evidence remains historical and does not certify the new search code.

## Scope and honest identity boundary

`ToolServices` operates one account per SQLite database. It is not a login server and a namespace string is not an authenticated owner identity. The trusted application already selects the database. An external multi-account deployment must authenticate the caller outside this class and select a separate account database and explicit scope configuration before exposing tools. Never let a model select a database path, grant namespace permissions or assert its own owner ID.

The new constructor accepts immutable `memory_read_namespaces` and `memory_write_namespaces`. An explicit empty set grants no access. `None` retains the existing trusted local application's unrestricted single-account access; it is not a suitable external caller policy. Read/write checks run before database access. Each invocation still opens, uses and closes its own SQLite connection on the calling thread.

The MCP adapter uses a **separate scoped service instance** for memory. Its trusted application service remains unchanged so internal orchestration can persist application checkpoints. External model memory defaults to the `course-notes` namespace. The operator can supply JSON arrays through `ACADEMY_MEMORY_READ_NAMESPACES` and `ACADEMY_MEMORY_WRITE_NAMESPACES`; `[]` is a read or write denial as appropriate. Reserved `agent-runs` and `orchestration` namespaces are never model-accessible, including read/search. Scope configuration is process-bound; changing it requires a new owner-configured server session.

## Concrete worked solution

For a local exercise, create `ToolServices(database_path, memory_read_namespaces={'lesson'}, memory_write_namespaces={'lesson'})`. These are application configuration values, not model-generated grants.

1. `remember('lesson', 'policy', 'Paper orders need approval')` stores the initial note.
2. `remember('lesson', 'policy', 'Paper orders need human approval')` updates the same key rather than creating a duplicate.
3. `recall('lesson', 'policy')` returns the exact current value.
4. `search_memory('lesson', 'approval', limit=5)` searches keys and values in **that namespace only**. Results are ordered by key, with a bounded limit and explicit literal-search mode. No semantic relevance score is invented.
5. Close that process and start a new service/server against the same database. Repeat recall and search. The supplied real MCP regression creates two successive server/client processes to test this, but it remains an unexecuted test until central QA runs it.
6. Ask the scoped service to recall or search another namespace. It raises a permission error before a query is dispatched, even when the other namespace contains a matching fixture row.

`search_memory` accepts a nonempty query of at most500 characters and integer limit1–10. These are input/output safety bounds, not fabricated performance claims. The query is a parameterized literal substring; `%`, `_`, quotes and SQL-looking input do not become wildcard or SQL instructions. SQLite performs ASCII case folding; Unicode semantic search is not claimed.

The namespace predicate is always part of the SQL query. The caller does not receive counts, suggestions, values or existence observations from a forbidden scope. The read-only configuration can search permitted notes while being unable to update them. A mutable set passed at construction is copied, so later accidental caller-side mutation cannot widen the service's scope.

## Secrets and historical rows

Do not put secrets or personal data in course memory. Credential-shaped content (`Bearer ...`, `api_key=...`, `password=...` and similar) and explicitly operator-configured forbidden strings are rejected on write and lookup. `ACADEMY_MEMORY_FORBIDDEN_STRINGS` may supply a trusted JSON string array for known values that must not appear in this course memory. Use fake canaries in tests, never real credentials.

Historical unsafe rows remain preserved in SQLite. Recall withholds their values; search excludes them before the result limit. This is defense in depth, not a guarantee that every unknown credential or personal detail can be recognized automatically. Namespace permissions, account-level database selection and keeping secrets out of memory remain the primary boundaries. Searches do not log raw queries or returned values. Existing write traces contain namespace/key metadata only, after validation; no value is placed in that trace.

## Central QA handoff

Run only through the repository's designated admitted QA owner:

```sh
python -m unittest discover -s tests -p test_project8_memory_search_v1.py -v
python -m unittest discover -s tests -p test_project_8.py -v
python -m unittest discover -s tests -p test_project8_trading_mcp.py -v
```

The new file contains direct persistence/update/search validation, literal-input and limit cases, frozen scopes, read-only access, historical-secret withholding, and an optional **real MCP stdio** store/update/recall/search/restart/denial test. If MCP is missing, that test is explicitly skipped, not counted as a genuine server pass. No child author ran these tests or launched an SDK/server while preparing the source change. Capture the actual tested server/editor/terminal and independently verify this lesson before authoring an observed walkthrough or releasing it to render.
