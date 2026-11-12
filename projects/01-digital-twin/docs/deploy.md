# Deploy and verify the fictional twin

This is executable deployment configuration and a runbook, not a claim that hosting already occurred. Central QA must execute the image build, local visitor actions and health check under the approved resource guard, then obtain genuine browser captures. A public deployment requires an approved host, HTTPS and explicit configured credentials.

## Local container

Build `docker build -t academy-twin .`. Use a private writable volume owned by the container's `academy` user. Mount it at `/data`, set `TWIN_DATABASE=/data/twin.sqlite` and keep all contact/lead/question state outside the image and public source tree. Default `TWIN_PUBLIC_BIND=false` binds loopback and is appropriate for a direct local process. For Docker networking use `TWIN_PUBLIC_BIND=true` with a configured username and password of at least 16 characters, and map the host only to `127.0.0.1:7860`. Store the password in a private environment file, never a shell history example or screenshot. Put an authenticated HTTPS reverse proxy in front only after explicit deployment approval.

Run `python health.py --url http://127.0.0.1:7860` for the local unauthenticated configuration check. For an authenticated public-bind deployment, use the container healthcheck's internal readiness probe; a separate visitor smoke test must authenticate through the approved TLS origin. A `401` proves access restriction, not full visitor readiness. Record identity disclosure, one approved-source answer, no-consent rejection, consented contact receipt and a second isolated visitor session. Never capture real stored contacts or credentials.

## Privacy, rate and retention

The UI keeps each visitor's session/action identifiers separate. Each service has a per-session rolling request limit; network-wide abuse controls also belong at the reverse proxy. `TWIN_RATE_LIMIT` and `TWIN_RETENTION_DAYS` must be positive. Public binding is refused without configured authentication. Secrets are not returned by health responses.

Schedule `python maintenance.py purge` daily as the same unprivileged service account using the private configuration. This erases expired lead/question personal data and completed local outbox records, while preserving minimal dedupe tombstones and held unknown external outcomes so a deleted request cannot be recreated by replay. Confirm the configured retention policy with the owner. `python maintenance.py outbox` is a private operator action; its output must not be made public. `dry-run-one` records a local dry-run receipt and never notifies a remote person.

## Notification configuration

Default mode is a durable local SQLite outbox containing JSON record identifiers. To send a real notification, implement a `NotificationAdapter` whose `send` returns an actual delivered status and provider receipt ID. Dispatching an external adapter additionally requires `allow_external=True` for that exact operation. Missing receipts, transport errors or a crash after dispatch leave UNKNOWN/dispatching holds. Investigate provider state before any manual resolution; this reference never automatically retries an uncertain external send. Re-running contact storage with the same stable call ID reuses its receipt and does not send a notification again.
