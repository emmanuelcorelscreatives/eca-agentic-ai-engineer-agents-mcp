# Solution guide

1. Synthetic catalogue: Agent Foundations — 2030-04-12 — USD 30; Browser Tools — 2030-04-19 — USD 45.
2. The task identifier is a UUID primary key. Inspect `TaskStore.checklist(task_id)` after constructing a new `TaskStore` pointing to the same file. The persisted result remains associated with the original UUID.
3. Expected state is `awaiting_approval`. No external call occurs before a matching approved digest.
4. `decide(task, 0, 'edit', replacement)` sets `approved_hash` to null. The edited target has a different digest and must be approved again.
5. `executing` is retained. Investigate the real destination's receipt/idempotency key and local trace; reconcile a known outcome explicitly. The core intentionally provides no automatic state-reset operation.
6. Resolve both root and candidate paths, then require `candidate.is_relative_to(root)`. Merely checking the string prefix would permit sibling-directory confusion.
7. Expected policy: GET only, same scheme and netloc as the dedicated fixture origin. This is a policy expectation, not a captured browser execution result.
8. Create a new adapter using an explicit artifact root, bounded text input, a validated relative filename, exclusive `open(..., 'x')` and an approval-bound action. Preserve any partial file and unknown result after a crash rather than overwriting it on retry.
