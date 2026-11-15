# s10-l10: Deploy and download a completed own-run report

Follow the [v3 deployment guide](../../projects/03-deep-research/deployment/research-v3/README.md) from its stated working directory. Use the supplied transitive hash lock in `projects/03-deep-research/deployment/research-v3/requirements.lock`; it is not a request to invent or resolve a replacement lock. The guide specifies Docker context, private persistent state, environment-only credentials, localhost URLs and owned cleanup. Building or starting the configured-live application requires your chosen accounts and explicit budget; it is not an offline fixture exercise.

In a fresh browser session, complete one finite research run and use “Prepare my completed report downloads” to obtain Markdown, HTML, JSON and SHA manifest. Inspect actual bytes and hashes. A second session must not use the first session's opaque run token; no arbitrary filesystem path is accepted. Verify incomplete or changed runs cannot export. Keep actual health, startup, persistence, report and download observations separate.

Expected behavior is not a record that deployment, live search/model calls or browser interactions succeeded. Report unavailable dependencies, failed builds and incomplete runs honestly; offline callback tests do not complete this practical.
