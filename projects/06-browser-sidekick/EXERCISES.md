# Exercises

These are the standard-library foundation exercises. Start with the [README setup](README.md), then use [Browser labs](BROWSER-LABS.md) and the [Stage 20 workbook](../../labs/s20-practical-workbook.md) for the separate integrated application. Do not substitute foundation test output for a native planner, browser or MCP observation.

1. Run the demo. Record both workshop names, dates and prices. State whether the catalogue is real or synthetic.
2. Close/reopen the database and inspect the previous task. Explain why a new demo invocation creates a new task rather than overwriting it.
3. Create a `message` step with criterion `adapter acknowledges the exact message`. Call `advance` before approval with an executor that would raise if called. Confirm it is not called.
4. Approve the message, then edit its target. Confirm the old approval no longer authorizes execution.
5. Set a test task's state to `executing` to model a crash after dispatch. Confirm no subsequent call silently replays it. Write the operator investigation steps.
6. Try a `../` fixture target. Confirm it cannot escape the fixture root.
7. Optional browser lab: follow the two-terminal [browser foundation recipe](BROWSER-LABS.md#browser-foundation). In a disposable fixture copy, add `<img src="http://127.0.0.1:8766/not-allowed.png">`, serve that copy on port 8765, and inspect the adapter's `requests` list after extraction. Expect an entry for the other origin with `allowed: false`; no server on port 8766 is needed. The list contains only method, origin and policy outcome, not request bodies or query strings. Preserve the bundled original; do not describe a browser observation as completed until actually run.
8. Extension: design a controlled artifact writer with a separate output root and exclusive filename creation. Do not turn the read-only browser into an arbitrary filesystem writer.
