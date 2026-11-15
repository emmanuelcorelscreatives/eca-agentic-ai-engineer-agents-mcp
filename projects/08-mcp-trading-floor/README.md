# Project 8 — MCP-powered AI trading floor

Emmanuel Corels Academy · stages 26–30 of *Agentic AI Engineer: The Complete AI Agents & MCP Course*.

This capstone starter provides a real, runnable deterministic application boundary for agents. All prices, companies and research are explicitly fictional fixtures. There is no brokerage adapter, live order capability, real-market claim or investment recommendation. The default run has no external network calls, model calls or paid dependencies.

## Run the complete offline workflow

Use Python 3.11 or later, as in the course quickstart. From the repository root:

```sh
cd projects/08-mcp-trading-floor
python3 trading_floor.py
python3 evaluate.py
python3 trading_floor.py --database paper.sqlite
```

The demo performs research → structured proposal → explicit local demonstration approval → deterministic risk recheck → paper execution → portfolio and trace. Five ACA shares cost exactly 626.25; cash becomes 9373.75. Retrying the same persisted demo request returns its original result instead of buying again. The CLI demonstration acts as the local reviewer; autonomous MCP tools cannot approve orders.

Subsequent optional commands in this README use this project directory unless noted otherwise. Follow the [stage 21–30 workbook](../../curriculum/workbooks/stages-21-30.md) for the capstone lessons. Return to the repository root to run the course tests:

```sh
python3 -m unittest discover -s tests -p test_project_8.py -v
```

## Architecture and lesson alignment

| Stage / lessons | Implemented course artifact |
|---|---|
| 26–28 MCP foundations, clients, custom tools | `mcp_server.py`: optional stdio research/proposal/portfolio/search/RAG/memory/orchestration tools |
| 29.1–6 scope and specialist boundaries | `research`, `propose`, `risk`, `execute` separate evidence, strategy, deterministic control and accounting |
| 29.7–12 market, research, memory, portfolio and researcher tools | normalized `fixtures/market.json`, SQLite memory and traces, typed immutable `Proposal` |
| 29.13–15 risk, approvals, controlled orchestration | exact proposal digest, one-use human approval, atomic ledger, idempotency keys |
| 29.16 Gradio dashboard | `gradio_app.py`: persistent research, human review and approved paper execution |
| 30.1–4 tracing, scenarios, deterministic evaluation | append-only application trace and `evaluate.py` four-case fixture suite |
| 30.5–9 quality evaluation, feedback, failures and metrics | exercises below; actual demo latency measured, model tokens/cost honestly zero |
| 30.10–12 API, React and container | `api.py`, `frontend/`, `Dockerfile` |
| 30.13–19 deployment, traces, portfolio presentation | local deployment and presentation checklist below |

The default researcher and strategist are deterministic teaching functions, **not claimed to be live AI agents**. Add a chosen framework adapter around these exact typed boundaries when following the model-integration lessons. Keep deterministic risk and approval outside model authority. The starter does not claim that an LLM judge, cloud deployment or human study has already run.

## Accounting and trust boundary

- Money is `Decimal` stored as text. Quotes and evidence must match the selected fixture exactly.
- Maximum order notional is 2000; maximum resulting single-symbol position is 25% of portfolio equity; cash cannot go negative and short sales are disabled.
- Execution reruns current risk inside `BEGIN IMMEDIATE`, consumes one exact approval and commits cash, positions, result and trace together.
- Request IDs are persistent idempotency keys; reusing a key for a different proposal fails.
- The model-facing research MCP service exposes no approval or execution tool. The API separates operator actions from reviewer approval: `/reviews` requires a distinct reviewer token. A model/tool response cannot supply that authority.
- This is an educational localhost application. The token is not a production identity system. Before remote deployment add proper authentication, per-user authorization, CSRF/origin policy, TLS, rate limits and isolated databases.

## Optional MCP adapter

Create an isolated virtual environment, then install optional requirements. This adapter deliberately targets **official Python SDK v1 (`mcp>=1.20,<2`)** and its `mcp.server.fastmcp.FastMCP` API. SDK v2 uses different names; do not silently upgrade this adapter across that boundary.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-optional.txt
python mcp_server.py
```

The stdio process waits for a real MCP client; launching it alone is not an end-to-end protocol test. Configure the client command with this project's absolute Python and script paths. Inspect the nine registered tool schemas, call `research_company` with `ACA`, then call `propose_order` and verify that no execution or approval tool is advertised. The separate trusted `portfolio_mcp_server.py` has a different role; do not confuse its capabilities with this research service.

Official references: [Python SDK](https://github.com/modelcontextprotocol/python-sdk), [SDK migration guide](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/migration.md), [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/), [Gradio Blocks](https://www.gradio.app/docs/gradio/blocks). These links explain transport/framework APIs; fixture evidence comes from this repository, not those documentation sites.

## Optional API, human approval and React

Activate the project virtual environment and install `requirements-optional.txt` as above before starting either interface. Keep the API terminal running. In the frontend terminal, use Node.js 18 or later and return to this project directory before entering `frontend/`. Set the two token values privately; the strings below are placeholders, not usable course credentials.

```sh
# Choose two different private tokens in your shell; never commit or display them.
export ACADEMY_LOCAL_TOKEN='replace-with-your-private-operator-token'
export ACADEMY_REVIEW_TOKEN='replace-with-your-different-private-reviewer-token'
export ACADEMY_PAPER_DB=paper.sqlite
uvicorn api:app --host 127.0.0.1 --port 8000
```

In another terminal, POST `/proposals` with the `X-Academy-Token` header and JSON `{"symbol":"ACA","quantity":5,"side":"BUY"}`. Save its response to `proposal.json`. Review it using:

```sh
python approve_order.py proposal.json --database paper.sqlite --reviewer academy-reviewer
# Only after inspecting the exact proposal and risk decision:
python approve_order.py proposal.json --database paper.sqlite --reviewer academy-reviewer --approve
```

Alternatively, POST `/reviews` with the reviewer token in `X-Academy-Review-Token` and `{"proposal": <the exact saved proposal>, "action":"APPROVE", "reason":"Reviewed synthetic paper order"}`. Rejection uses `"action":"REJECT"`. The reviewer and operator tokens must differ; a browser-entered reviewer token is an explicit human capability, not a model-generated approval.

POST `/execute` with `{"proposal": <the exact saved proposal>, "request_id":"lesson-order-1"}` and the operator token header. GET `/state` shows the persistent portfolio, proposals, transactions and trace. To use the React source in a second terminal, starting from this project directory:

```sh
cd frontend
npm ci
npm run dev
```

Open the printed localhost URL, enter the operator token, research a proposal and refresh the portfolio. Vite proxies `/api` to localhost:8000. A human reviewer may enter the separate reviewer token to explicitly approve or reject the exact proposal; execution still uses the operator capability and reruns risk checks. `npm ci` uses the committed lockfile. The optional browser/framework/server routes require installed dependencies and separate tests; a dependency-free test pass does not establish browser interaction.

For the stage 29 dashboard instead, run `python gradio_app.py` from the project directory with the same database and token settings. It displays fixture research, proposals, explicit human review, execution and the persistent paper account, with no shared public Gradio link. Never expose either teaching interface or its tokens publicly.

## Deployment practice

The Dockerfile runs the API as a non-root user and expects persistent `/data` storage and externally supplied distinct `ACADEMY_LOCAL_TOKEN` and `ACADEMY_REVIEW_TOKEN` values. Build locally, bind to loopback only and mount a private data directory writable by UID 10001. Do not expose the teaching token service publicly or store secrets in images. Verify GET state, an unapproved execution rejection, a reviewed execution, an idempotent retry and state after container restart. Record actual image digest and observed outputs in your deployment report; no hosted deployment is claimed in this starter.

## Exercises and worked solutions

Use the [74-lesson capstone workbook](workbook-stages26-30.md), [trading solutions](solutions/trading-workflows.md), [MCP host solutions](mcp_lab/worked-host-solutions.md) and [evaluation solutions](evaluation_lab/WORKED-SOLUTIONS.md). The shared [stage 21–30 workbook](../../curriculum/workbooks/stages-21-30.md) preserves the course progression.

1. **Risk boundary:** propose 30 ACA shares. Expected: order and position limits reject it. Propose 15, approve and execute, then propose another six. The second order breaches aggregate position limit even though its own notional is below 2000.
2. **Approval tampering:** approve five ACA shares, then edit the price in the proposal file. Expected: fixture quote validation rejects it; changing quantity also changes the approval digest. Never “repair” this by trusting model-supplied price.
3. **Recovery:** submit one request twice, then the same request ID for four shares. Expected: the exact retry returns the prior fill, whereas changed order fails. See `test_exact_decimal_and_idempotent_retry` and `test_reused_key_for_changed_order_rejected`.
4. **Tool failure:** request symbol `UNKNOWN`; expect a handled `ValueError`. A retry cannot make an unknown fixture exist. Add separate transient-service exceptions before adding bounded retries; do not retry validation errors.
5. **Research evidence:** require every structured research response to name its existing evidence ID. Reject invented citations. The fixture is synthetic and must remain labeled in every UI.
6. **Evaluation:** add cash-exhaustion and sell-after-buy cases to `evaluate.py`. The four shipped cases must remain passing. Add a JSON model-judge rubric with evidence coverage, explanation clarity and explicit uncertainty, but keep model quality scores separate from deterministic risk decisions. Store real judge output only after running an explicitly authorized model call.
7. **Human feedback:** follow the [bound feedback solution](evaluation_lab/WORKED-SOLUTIONS.md) using the existing `evaluation_lab.feedback.BoundFeedbackStore` and app review controls. Register an exact run/output, submit a reviewer rating 1–5 and correction, then test unknown output hashes, invalid ratings and duplicate submission IDs. Feedback cannot approve an order or rewrite its original output. These are learner tasks, not a claim of collected human ratings.
8. **Latency and cost:** use observed provider usage metadata when adding an LLM. Record model name, input/output tokens, measured elapsed time, pricing source/date and estimated cost. The current no-model run correctly reports zero tokens and zero model cost.
9. **Presentation:** trace one proposal digest through research, approval and fill, show a rejected order, demonstrate restart/idempotency and describe which parts are deterministic and which added components call models. Include a repository commit and actual test output in the portfolio report.

No screenshot should show a fake live brokerage, invented return or invented evaluation score. Capture the actual running app with its synthetic labels visible.

## Worker-thread safety and grounded tool services

`services.py` holds only the configured database path. Every tool invocation opens and closes its own SQLite connection on its caller thread; no import-time SQLite connection crosses FastMCP worker threads. Set `ACADEMY_PAPER_DB` to an explicit persistent course database for shared memory/account state. A per-call `:memory:` database is rejected by this service to avoid silently discarding memory.

The nine MCP tools provide research, proposals, portfolio, lexical local-corpus search, extractive retrieval with source citations and abstention, namespaced persistent memory write/read/search, and a complete reference multi-role orchestration. Search is explicitly local synthetic data, not internet search. `orchestrate` returns researcher/strategist/risk-manager records and stops at `AWAITING_HUMAN_APPROVAL`; it never grants itself approval. These deterministic adapters are real runnable course components, not a claim that external model agents have been evaluated.

Boundary tests cover concurrent SQLite service calls, persistent memory across worker threads/instances, retrieval grounding/abstention, and MCP/API/Gradio Python callbacks invoked on worker threads with stub framework registration shells. Those callback tests exercise connection ownership, **not** framework transport, schema validation, HTTP, UI or full SDK compatibility; optional dependency end-to-end tests remain separate. Run the tests in your own environment and retain their actual results, including skips.

## Optional integration checks

Use the pinned optional requirements and a new disposable synthetic database when checking HTTP, SDK or browser behavior. `validate_runtime.py` is an optional local validation helper; inspect its requirements before running it. Test initial state, missing-token rejection, typed proposal validation, unapproved execution rejection, reviewed execution, idempotent retry and both interfaces. A passing callback test does not establish that your browser or server is working.

Follow the [MCP laboratory](mcp_lab/README.md) for stdio, Streamable HTTP and the restricted official Node filesystem-server exercises. The deterministic sampling callback demonstrates protocol negotiation, not external model intelligence. Follow the [retrieval lab](retrieval_lab/README.md) for optional web/search/Qdrant integrations; those require separate setup and observations.

The [evaluation lab](evaluation_lab/README.md) covers tracing, redaction, usage, feedback, recovery and dataset accounting. Its illustrative judge/feedback examples are not actual model or peer verdicts. A real paid model judge or hosted deployment requires its own authorized run. The [74-lesson workbook](workbook-stages26-30.md) distinguishes implementation exercises from acceptance you must still demonstrate; reusable components do not imply every lesson has been completed.
