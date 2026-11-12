# Owned practice deployment and rollback exercise

This is an execution runbook, **not a deployment receipt**. Work only on an explicitly authorized host. The trading service is simulated; never configure real broker credentials.

1. Record the exact repository revision and SHA256 of dependency lock files, Dockerfiles and configuration templates. Run core and evaluation tests. Do not declare optional framework transports tested from stub tests.
2. Verify the real backend API contracts and frontend against that revision. Supply a unique practice API key through the host's secret store/environment; keep it out of image layers, screenshots and shell history. Bind a private interface until authentication is tested.
3. Create a dedicated persistent volume for the Academy paper database. Back it up with SQLite's backup API while the service is live, or stop the service cleanly before file copying. Record backup hash and schema version. Do not mount unrelated host data.
4. Build both backend and frontend images with pinned dependencies. Record resulting image digests and actual build logs. Configure the frontend's backend URL for the intended browser/network; container service DNS is not necessarily resolvable from a browser.
5. Start the stack. Record actual service health, host identifier and UTC release time. Verify unauthorized mutation fails. Submit a fresh synthetic scenario, inspect research/risk, explicitly approve the exact proposal as a practice human, execute once with a unique request ID and reconcile cash/positions with the ledger. Repeat the same request ID and prove no additional effect. Retain redacted trace and screenshots of the real app.
6. Restart services, then prove the same order/state survives. Verify feedback persists independently of approval and untrusted comments render as inert text. Do not manufacture an approval or provider response for the lesson.
7. Roll back to the previous **recorded image digest** on the practice host. If schema changed, use the compatible backup and document how writes since that backup are reconciled. Never blindly overwrite current state. Repeat health and read-only state checks. Save actual rollback logs.
8. Publish a sanitized evidence index: release revision, image digests, lock hashes, real test results, trace/run/order IDs, before/after balances, rollback result and remaining limitations. A local container execution is local evidence; call it hosted only after the actual authorized remote deployment succeeds.

## Worked solution / expected arithmetic

For a fresh default synthetic account, buy 5 ACA shares at 125.25 after approval. Notional is 626.25; cash becomes 9373.75 and ACA position becomes 5. Repeating the same request ID returns the previous result without another debit. An unapproved request fails and leaves cash unchanged. These are fixture expectations, not a claim that this runbook has been executed on a host.

## Student exercise

Introduce an unavailable research **read** service in an owned test environment, then recover it within the bounded read policy. Capture retry counts and failed spans. Next simulate losing the response to a paper-order write: reconcile by request ID before deciding whether any action is needed. Explain why the retry policies differ. Keep genuine fault-server observations separate from mocked unit-test evidence.
