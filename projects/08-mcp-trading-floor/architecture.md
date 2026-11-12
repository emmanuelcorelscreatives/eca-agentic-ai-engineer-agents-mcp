# Capstone architecture and trust contracts

## The four specialist roles

The researcher supplies evidence records (`symbol`, `evidence_id`, exact text and synthetic as-of date). The strategist turns that evidence into an immutable `Proposal`; it cannot choose an arbitrary execution price. The risk manager applies deterministic account rules to the actual current cash and marked positions. The portfolio/execution component alone writes account state in a single SQLite transaction after validating an unused human approval bound to the proposal digest.

The offline implementation executes these same boundaries through `ToolServices.orchestrate`. Framework or provider adapters should return an identical proposal contract. Their language explanations cannot replace risk checks or act as human approval. Returning a tool result to a model is separate from running the model again. A bounded agent loop must count both model and tool steps, preserve raw failed outcomes and stop for unresolved or malformed results.

## State transition table

| Current state | Event and guard | Next state | Durable side effect |
|---|---|---|---|
| NEW | researcher finds known fixture | RESEARCHED | research memory and evidence trace |
| RESEARCHED | proposal matches exact quote and typed quantity | PROPOSED | proposal digest trace |
| PROPOSED | deterministic risk rejects | RISK_REJECTED | result returned; no position/cash changes |
| PROPOSED | deterministic risk passes | AWAITING_HUMAN_APPROVAL | grounded role result saved in namespaced memory |
| AWAITING_HUMAN_APPROVAL | human reviews exact digest | APPROVED | one-use approval record |
| APPROVED | transaction rechecks risk and unused approval | PAPER_FILLED | account, positions, fill result and trace commit atomically |
| PAPER_FILLED | same request ID and digest retried | PAPER_FILLED | original fill returned; no additional purchase |
| Any | malformed input / quote mismatch | ERROR | rejection; never silently correct a model-generated price |

A new request ID with the same already-consumed approval fails. An idempotency key with a different proposal fails. Persist the database across process restarts to preserve both guards. Do not use an in-memory account behind a supposedly durable remote service.

## Research and retrieval lineage

`fixtures/market.json` is the sole original synthetic evidence source. `search_research` returns exact source text and evidence IDs. `grounded_brief` is an extractive retrieval baseline; it abstains when nothing matches. It is not a claim of model reasoning, public-web discovery or investment analysis. Model-backed RAG should retain the retrieved IDs and reject unsupported citations before presenting an answer. A vector-search adapter may choose records semantically, but cannot fabricate a document or convert fixture data into a real-market observation.

## MCP boundaries

`mcp_server.py` implements eight model-callable tools with official SDK v1 annotations. Research, proposal, memory and portfolio tools are available; approval and execution are absent. A client owns the model invocation, its API key and any sampling policy. A server requesting sampling does not acquire permission to call the model directly. Incoming web pages, documents and MCP results are untrusted data and cannot change this permission boundary.

A remote transport needs independent service identity, TLS, per-user scope and an explicit trusted-origin policy. Local stdio inherits its process identity and should expose only a disposable owned workspace. A tool name allowlist alone is insufficient if arguments can escape an allowed filesystem root or fetch an arbitrary private-network URL. Validate the resource target as well as the tool name; do not forward secrets in a tool schema or log.

## UI and application coherence

Gradio and React display the same synthetic company symbols, evidence and account contracts. Gradio is a read/propose demonstration; it does not share the API's persistent account unless explicitly configured in an extension. React uses FastAPI `/proposals` and `/state` through a localhost Vite proxy. Only the separately reviewed CLI can create an approval. `/execute` remains an authenticated state-changing API endpoint and reuses the same transactional service.

No screenshot should imply that a model, real exchange, public deployment or live brokerage was contacted unless an actual authorized run did so and its response is retained. Showing a working fictional paper-trading dashboard is a legitimate course application, provided its synthetic labels remain explicit.

## Operational and assessment contract

The default offline test suite proves monetary/risk/persistence/thread boundaries. It does not prove optional framework compatibility. Record interpreter/package versions, installed API signature checks, actual HTTP and MCP sessions, browser observations and raw results separately. Dependency installation, a successful import, callback tests with framework registration stubs, a simulated protocol transcript and a real client-server session are different evidence classes.

For a portfolio submission include: exact source commit; original fixture manifest; actual test and protocol outputs; one approved paper transaction and one rejected transaction; complete digest-linked trace; a recovery/idempotency demonstration; an honest list of unimplemented or untested features. Treat native course narration production separately from application-level model evaluation.
