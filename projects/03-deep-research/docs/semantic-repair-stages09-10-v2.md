# Stages 9–10: research contracts and workflow

Start with the [student guide](student-guide.md) for setup, runnable fixture practice,
lesson checks and opt-in live SDK/search. This document explains the current contracts.
Fixture tests do not establish actual model/search behavior, browser interaction,
approved SMTP delivery or deployment. Record each of those outcomes separately when
you actually observe it; do not treat a historical fixture report as live evidence.

## Required features and actual new interfaces

- `contracts_v2.py` and `schemas/research-v2.schema.json` define versioned plans,
  queries, normalized sources, exact evidence, findings, sections and final reports.
  Runtime validation checks missing/extra fields, enums, versions, task dependencies,
  source/query attribution, exact excerpts, and dangling citations.
- `sdk_v2.build_team` constructs actual Agents SDK planner and analyst with structured
  outputs. The actual question—not a fixed list of workshop topics—drives planning.
  The analyst sees the same attributed current workshop/search evidence used by the
  report. Source text is untrusted data; source instructions cannot become tool access.
- `brave_search.BraveSearch` is the concrete Web Search provider, not a custom service
  requiring another unimplemented adapter. Official contracts consulted 2026-11-12:
  https://api-dashboard.search.brave.com/api-reference/web/search/get and
  https://api-dashboard.search.brave.com/app/documentation/web-search . It makes one
  GET with `q`, `count`, and the documented subscription-token header; normalizes real
  `web.results` fields; retains raw response, retrieval time and response SHA. Descriptions
  are explicitly search snippets, publication dates stay unknown, and link reachability
  stays not_checked. No page fetch or live request has been performed by the author.
- `pipeline_v2.run_research` controls planning → dependency-ready searches → evidence
  → analysis → writing. Independent branches use a bounded semaphore; dependent tasks
  wait for prerequisites. Each actual phase emits observed start/end/status/duration.
  `quality_v2` checks nullable dates, freshness, incomparable scopes, broken-link
  observations and source instruction attacks. No missing publication date is guessed.
- `Journal` writes every step before a request and saves actual responses before
  validation. Known completed query results are revalidated/reused for identical input.
  It binds question, source revision/source IDs, provider identity and caller configuration;
  current code hashes are bound by capstone_v2. A changed source manifest cannot resume
  the old run. IN_FLIGHT/UNKNOWN requests are held. Failed or malformed known responses
  retain their raw evidence and require an explicit revised run, never hidden retry.
- `interface_v2` streams actual planning/search/analysis/writing status through an
  async generator. Cancel closes pending tasks; an interrupted provider call remains
  unknown. Every submission gets a private fresh run directory; one browser session
  never inherits another session's raw report. The public event allowlist omits keys,
  private reasoning and arbitrary payloads. Report markup is escaped.
- `exports_v2` exports Markdown, HTML, full JSON and file hashes. Delivery requires exact
  recipient/report approval and an idempotency key. A delivery interrupted after starting
  is held instead of replayed. A real approved local SMTP receipt is still required;
  `reporting.SimulatedOutbox` is not that evidence.
- `data/s10-evaluation-v2.json` supplies twelve human-authored representative questions,
  explicit source/uncertainty criteria, and a held-out split. `annotated_rubric` records
  attributed 0–4 human judgments for relevance, source diversity, coverage, organization
  and factual support with evidence references. These are interpretation, not an
  automated truth certificate. Structural counts remain separate.
- `trace_summary` aggregates actually observed spans and explicitly distinguishes span
  sums from concurrent wall time. Unknown provider token usage stays null, never zero.
  The SDK team records actual Runner usage if supplied. Local operational spans are
  not claimed to be a remote OpenAI tracing dashboard observation.

## Optional finite live capstone

Install the isolated Python 3.12 runtime using the supplied hash lock as described in
the [live setup](student-guide.md#optional-live-sdk-and-search). Set secrets outside
the repository. The following command performs real search and model requests;
run only after explicitly choosing the account and budget, not as an ordinary offline test:

```
python3 projects/03-deep-research/capstone_v2.py --live \
  --question 'Compare evidence for an accessible community workshop scheduling pilot.' \
  --source-revision ACTUAL_REVIEWED_REVISION --workers 3 \
  --state "$HOME/eca-research/run-01/state" --output "$HOME/eca-research/run-01/output"
```

The client uses zero automatic transport retries. Keep the state directory and original
known/unknown receipts. Do not delete state and rerun to bypass an UNKNOWN outcome.
Retain the configured provider/model identity and actual results privately; never
include credential values in the evidence you share.

## Deployment contract

Use the [v3 deployment exercise](../deployment/research-v3/README.md), supplied v3
transitive hash lock and `deploy_v3.create_app` for the current download-enabled UI.
It mounts Gradio at `/research` and exposes `/healthz` without secrets.
Health means local application configuration is ready; it never claims the remote
search/model account is healthy without an actual request. Run under a non-root user,
read-only filesystem and writable private /state volume, behind authenticated TLS.

The older `deployment/research/Dockerfile` / `deploy_v2` is retained as a legacy
comparison and references a v2 lock that is not supplied. Do not select it for the v3
exercise or regenerate the existing v3 lock merely to satisfy that legacy prerequisite.
An existing lock is not successful build/startup/provider/browser evidence. Verify
those outcomes in your isolated learning environment before claiming they work.

## Module capstone checklist

Compare the digital-twin approved-source/tool boundary, the sales-team draft/approval
boundary and this research evidence/source boundary. Each claimed outcome must link
to its actual source, raw output, operational span, evaluation annotation and meaningful
error path. A model construction smoke alone does not establish a completed system.
