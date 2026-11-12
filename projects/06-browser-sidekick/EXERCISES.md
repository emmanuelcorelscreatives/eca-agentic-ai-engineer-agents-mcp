# Exercises

1. Run the demo. Record both workshop names, dates and prices. State whether the catalogue is real or synthetic.
2. Close/reopen the database and inspect the previous task. Explain why a new demo invocation creates a new task rather than overwriting it.
3. Create a `message` step with criterion `adapter acknowledges the exact message`. Call `advance` before approval with an executor that would raise if called. Confirm it is not called.
4. Approve the message, then edit its target. Confirm the old approval no longer authorizes execution.
5. Set a test task's state to `executing` to model a crash after dispatch. Confirm no subsequent call silently replays it. Write the operator investigation steps.
6. Try a `../` fixture target. Confirm it cannot escape the fixture root.
7. Optional browser lab: run the genuine loopback Playwright adapter, then add an external image URL to a disposable copy of the fixture. Inspect the request log and verify that the external request is aborted. Do not describe this observation as completed until actually run.
8. Extension: design a controlled artifact writer with a separate output root and exclusive filename creation. Do not turn the read-only browser into an arbitrary filesystem writer.
