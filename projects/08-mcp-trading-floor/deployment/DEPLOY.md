# Stage 30 container lab

**Source prepared, not build/hosting evidence.** Build context is the project folder. The React UI uses same-origin `/api`, nginx forwards to internal `backend:8000`, and only the localhost UI port is published. No broker is configured. Supply two distinct private tokens in an uncommitted environment file; the operator and reviewer are educational local roles, not production user identities.

```sh
cd projects/08-mcp-trading-floor
cp deployment/.env.example deployment/.env
# Edit both tokens privately; never copy this file into an image or screenshot.
docker compose --env-file deployment/.env -f deployment/compose.yaml config --quiet
docker compose --env-file deployment/.env -f deployment/compose.yaml build
docker compose --env-file deployment/.env -f deployment/compose.yaml up -d --wait
docker compose --env-file deployment/.env -f deployment/compose.yaml ps
curl --fail http://127.0.0.1:8088/health
curl --fail http://127.0.0.1:8088/api/health
```

The frontend requires its committed `package-lock.json`; `npm ci` deliberately fails if it is absent or inconsistent. Base image tags are specified for authoring; the release operator must record resolved image digests, installed dependency inventory and build logs. This file does not claim a digest-pinned/reproducible build has been observed.

On a fresh volume, propose ACA quantity 5 in the real UI. Review evidence and risk, explicitly approve using the reviewer role, execute once with one stable request ID, and expect cash 9373.75 and ACA position 5. Repeat that exact request ID; cash must remain 9373.75. Save genuine UI/HTTP/ledger observations and redacted traces. Restart using `docker compose ... restart`; prove the same state and feedback remain. Do not use `down -v`, which deliberately deletes the practice volume.

For hosted release, obtain an explicitly owned approved host, TLS/identity controls suitable for that environment, a private backup and immutable prior release digest. Do not expose this localhost educational token design directly to the public internet. Follow `../evaluation_lab/deployment/RUNBOOK.md` and record the real host/revision/images/health/full workflow/restart/rollback. An observed local build is not a hosted deployment.

Rollback exercise: capture the previous actual image digest and database backup with SQLite backup API before upgrade. Stop mutations; switch to the prior digest only after verifying schema compatibility. Reconcile any orders newer than the backup before restoring it. Re-run health and read-only balances. Retain failed rollback evidence as a failure rather than overwriting it with a green template.
