# Worked trading-floor solutions — authored revision, QA pending

These worked solutions explain the actual source contracts. New semantic-repair tests have not yet been executed; expected arithmetic below is derived from original synthetic fixture values, not fabricated model output. Every real model experiment requires its own explicit opt-in and retained actual response.

## Scope and architecture (stage29 lessons1–2)

The application researches three fictional companies, proposes whole-share orders, applies deterministic cash/concentration constraints, requests a separate human review and records paper fills. It never connects to a real broker. Research MCP exposes evidence/proposals/memory. The separate trusted portfolio MCP service exposes account, proposals and transactions plus execution of already-approved orders. Neither MCP service can grant approval. The same `TradingFloor` ledger backs API, Gradio and portfolio MCP; using the same `ACADEMY_PAPER_DB` is essential.

Map the responsibilities explicitly: model roles explain and propose; `risk` decides policy; the reviewer approves an exact proposal at the current account revision; `execute` is the transaction boundary. A model-provided statement “approved” has no effect on the approval table.

## Research, strategy and risk specialists (lessons3–5)

`capstone_agents.py` runs a configured async model for three distinct specialist contracts. The researcher receives the real fixture record and must return its exact evidence ID and supported quotation. The strategist receives a versioned handoff with account identity/revision and must return BUY, SELL or HOLD, whole-share quantity, rationale and uncertainty. HOLD does not place an order. No model chooses its own quote price: the ledger constructs it from the fixture. The risk explainer receives the actual deterministic decision and may explain it, but cannot change allowed/reasons or grant approval.

For ACA the fixture price is125.25. Five shares cost626.25, which is below the2000order limit and below25% of initial10000equity. Thirty shares cost3757.50 and breach both order and concentration limits. This is a fictional exercise, not a prediction or recommendation.

A supported researcher quotation is `Fictional component maker` with evidence ID `fixture-aca-001`. A quotation not present in the fixture fails even when its citation ID looks valid. A real model may choose HOLD; record that actual result rather than editing it into an invented BUY. The model adapter `sdk_role_provider.py` uses the course's optional Agents SDK and explicit `--run`; nothing is sent on import. Official API references: [running agents](https://developers.openai.com/api/docs/guides/agents/running-agents), [models and providers](https://developers.openai.com/api/docs/guides/agents/models).

## Portfolio state and controlled execution (lessons6,10,13–14)

First propose and approve five ACA shares, then execute request ID `academy-order-001`. Expected derived cash is9373.75 and positions ACA=5. Repeating the same request ID returns its original fill. Reusing that ID for a changed proposal fails. A new request with an already-consumed approval fails.

Approval records bind to an account identity/revision and expiry. To demonstrate changed-state handling, approve ACA and LAB proposals at revision0, execute LAB, then attempt ACA. ACA must be reviewed again because the account is now revision1. To demonstrate rejection, record a reason with `reject`; no paper position changes. Old approval records without the new binding fields cannot silently authorize a fill after migration.

`risk(..., reference_time=...)` can evaluate quote age against an explicit clock. The default fixture uses a fixed historical snapshot and labels it as such. Do not compare a January fixture with today's clock and call the exercise a live market feed. For the fixture timestamp2026-01-15T16:00Z, a reference16:01Z is within the default freshness window;17:00Z is stale. A real current-feed adapter must explicitly provide its observed timestamp and clock.

## MCP data, research and memory (lessons7–9,11–12)

The actual trading-server tests are `test_project8_trading_mcp.py`; generic `mcp_lab` protocol tests are separate. Initialize a real client for `mcp_server.py`, discover `research_company` and call ACA. Compare the returned evidence ID/quote with `fixtures/market.json`. The portfolio service is a separate process with a different tool allowlist.

`ToolServices.orchestrate` remains the deterministic reference. `TradingAgents` is the model-driven implementation: its configured provider is awaited for each role; tests use openly labeled scripted responses. The researcher owns evidence collection and passes a schema-versioned, run-correlated envelope to the strategist rather than asking every role to independently invent a research record. Call/time budgets are explicit and failures stop for review. They are not a production narration gate.

Memory persists in the configured SQLite database across tool invocations and process restarts. Each call opens its own connection on its caller thread. Research-facing memory writes cannot overwrite `agent-runs` or `orchestration` checkpoints. Namespaces are teaching record organization, not a multi-user authentication system; use one separately authorized database per course account.

## Full orchestration and Gradio dashboard (lessons15–16)

The model-driven run returns AWAITING_HUMAN_APPROVAL when risk passes, or RISK_REJECTED/HOLD when it does not. `resume_approved` uses the same ledger and cannot manufacture approval. Existing failed or pending run IDs return their checkpoint rather than silently repeating model calls.

The Gradio interface now uses the persistent account selected by `ACADEMY_PAPER_DB`. It displays saved proposals, review state, transactions, account revision, activity and an honest agent-status label. Copy the exact proposal JSON into the review pane, enter the separate local reviewer token, approve or reject, then execute the approved order with a stable request ID. Refresh the dashboard or restart it against the same database: the filled positions remain. This local reviewer token is an educational role boundary, not a public OAuth/account system.

## API, React and feedback

The API accepts operator credentials only for proposals/execution and separate reviewer credentials for approvals/rejections/feedback. Identical operator/reviewer tokens are rejected for review. A review comment does not authorize execution. Feedback binds to a previously registered exact run/output SHA; unknown hashes cannot create a review of an invented output. Corrections are stored as suggestions and do not rewrite historical output.

React shows loading, backend-error and rejection states, a persistent portfolio summary, exact-proposal approval/rejection, stable-ID execution and run-bound reviewer comments/corrections. Text is rendered through ordinary React text nodes; do not use raw HTML for comments. The `/api` proxy is shared with the container frontend. Deployment source and review exercises live under `deployment/` and `evaluation_lab/`; actual container and hosted observations remain separate QA work.

## Commands proposed for central QA

Run dependency-free regressions first, then actual optional SDK/API/browser suites with the selected pinned dependencies. Optional test skips must not be reported as successful execution. The central QA command manifest lists these suites and required environment flags. Do not run `sdk_role_provider.py --run` as part of offline testing: it can incur provider charges.
