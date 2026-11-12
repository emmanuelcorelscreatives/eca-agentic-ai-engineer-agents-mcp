# Stage 27–28 controlled research and retrieval

This folder now contains substantive source solutions, not just a topic-to-file mapping. **New semantic-repair code has been authored but has not been executed by its author.** Parent repository QA owns all runtime commands. Passing control-flow doubles does not establish model intelligence; a real MCP session does not establish every lesson objective or production visual approval.

## Components and tested-history boundaries

- `core.py`, `mcp_adapter.py`, `server.py`, `reference.py`: retained earlier teaching components. Their historical proof remains limited to its recorded bytes and actual run. The old static server is not the new progressive service.
- `workflow.py`: complete bounded research controller over actual `agent_harness.MCPRegistry`. It presents only `research::fetch_page` and `research::browse_page` to a provider, maps them to actual `fetch::fetch` and `browser::browser_navigate`/`browser_snapshot`, and checks exact URL, role and shared time/tool/output budgets. Each native tool request counts, including both browser steps. No click, submit, evaluate, upload or generic dispatch tool is exposed to the model.
- `solutions.py`: concrete two-product comparison, progressive-discovery measurement, document ingestion, exact-quote grounding, and bounded model/MCP RAG answering solutions. Callers explicitly supply real sessions and an actual provider; no canned provider is the production default.
- `rag.py`: Qdrant service adapter plus owner-bound chunks, deterministic IDs, SHA256, offsets, duplicate policy, explicit replacement, delete, score threshold and insufficient-evidence handling. Credentials and tenant identity belong to the trusted launcher, not model arguments.
- `research_server.py`: stdio-only MCP server. Initially lists only `discover_capability`; revealing `rag` returns the actual permitted `ingest_document`, `retrieve_documents` and/or `delete_document` names. Dispatch rejects hidden, guessed and unauthorized names. One process belongs to one authenticated principal. This state must not be shared across HTTP users.
- `progressive.py`: independent per-session catalogue with permission checked again on every dispatch. A mutable trusted ACL supplier can revoke permission even after discovery. The sample stdio launcher uses a fixed process-lifetime permission set; changing it requires a new authenticated session.
- `search.py`: configured real SearxNG-compatible provider with normalized queries, bounded results and typed unavailable/quota/timeout/invalid-response errors. No invented fixture fallback.
- `secret_boundary.py`: recursive redaction of explicit fake canaries and common credential patterns. This is defense in depth, not proof that arbitrary unknown secrets can be recognized. Keep real credentials outside documents and prompts.

The old named-server observations are retained outside this public code: official `mcp-server-fetch==2025.4.7` fetched Python asyncio documentation, and official `@playwright/mcp==0.0.54` rendered an owned dynamic Academy page. Their actual negative file-access result is retained too. Those observations do **not** prove the new two-product agent, Qdrant HTTP service, semantic embedding, real search provider or source-current captures are complete.

## Dependency and existing-server selection

The shared SDK is `mcp==1.26.0`; use `requirements.txt`. The historical first experiment used1.22.0 and remains historical. Existing Fetch2025.4.7 needs its own environment with `manifests/fetch-requirements.txt` because its `httpx<0.28` requirement conflicts with the shared UI runtime. Do not mutate the shared environment to resolve this conflict.

`manifests/existing-servers.json` records exact official distributions, versions and launch arguments. `launch.OfficialServerPaths` verifies the Playwright package name/version and uses an explicit browser executable. `launch.existing_session` connects the real SDK with restricted nonsecret configuration. No model may choose a command, interpreter, workspace or environment variable. Parent QA records full resolved package/image locks and launch identities before evidence is promoted.

## Worked Stage 27 solutions

### Lessons 2–3: fetch and browser

Serve only `fixtures/site` in the same private network namespace as the browser. Select the two exact URLs ending in `static-product.html` and `dynamic-product.html`. The first page declares Academy Ledger, CSV and a human-approval policy. The second inserts Academy Canvas, JSON and its five-record table through JavaScript. Both are clearly fictional Academy products.

1. Connect the pinned existing Fetch and Playwright MCP processes through real SDK sessions. Discover actual tools before calls; do not replace either with the custom teaching server.
2. Pass the real sessions, an explicit provider and both enrolled URLs to `solutions.compare_products`. The provider chooses the exposed fetch/browser actions. The host maps actions to the intended actual server and records server/tool, SHA-bound arguments, call ID, measured elapsed time, status and source provenance.
3. A valid final answer contains exact quotations with `source-1`/`source-2` citations. The code validates every quotation against the corresponding actual returned text. It abstains when claims are empty; citation-looking invented assertions fail.
4. Check the fixture server log: zero `POST` requests. Add a missing page and malformed result; retain explicit failures rather than filling in product details. None of those outcomes may be narrated as observed until the new actual run exists.

### Lesson 7: complete controlled browsing agent

Use the preceding workflow on both pages, then add `injection.html`. Its hostile instruction is source data. The only model descriptors remain the two research wrappers; trying `browser::browser_click`, a `file:` URL, metadata address or a modified unapproved query must fail before MCP dispatch. Tests implement these exact regressions. The model's actual response, decision trace and final citations must be retained in the independent real run; scripted test providers establish control flow only.

### Lessons 8–11: trace, failures, filtering and least privilege

`ResearchWorkflow.trace` links actual native server/tool, call IDs, argument digest, status and elapsed time. It stores no raw credential-bearing arguments or page body. `ResearchBudget` bounds iterations, total time, per-call time, native calls and output size. A failure/timeout is not retried automatically; retain unknown outcomes. Researcher gets fetch plus browser; reviewer gets fetch only. Exact URLs are a second boundary independent of discovered server tools. MCPRegistry additionally validates actual advertised JSON schemas and fresh host tool permissions. Broader filesystem report/draft and mutation-approval exercises are owned by `agent_harness`/`mcp_lab`, not certified by this folder.

### Lesson 12: repair an unsafe log

Unsafe exercise: logging `repr(arguments)` or entire provider exception bodies can expose an `api_key` or a fake `Bearer FAKE_TOKEN_XYZ`. The concrete solution stores only bounded status/class/call IDs and argument SHA, and cleans source text with `SecretBoundary` before model forwarding. Inject nested fake canaries and assert none survive in messages, generated reports, errors or captures. Existing tests cover textual propagation; genuine end-to-end capture inspection remains a separate QA requirement. Never use a live secret as a test canary.

## Worked Stage 28 solutions

### Lesson 12: actual search adapter

Configure an authorized SearxNG-compatible endpoint and enroll its exact origin. Call `BoundedSearch.search` through the revealed `search_web` MCP tool. Whitespace is normalized, limit is1–10, results retain URL/title/excerpt/provider/time and actual response SHA. Empty results remain empty;429 becomes `RATE_LIMIT`, timeout becomes `TIMEOUT`, bad shape becomes `INVALID_RESPONSE`. No automatic retry or provider change occurs. Unit fixtures are explicitly labeled; a genuine authorized provider query and retained sanitized response are still needed before a live-search walkthrough.

### Lesson 13: document RAG and agent answer

Use the two files in `fixtures/documents`. The trusted launcher supplies `ACADEMY_SUBJECT`, `ACADEMY_TENANT`, `ACADEMY_PERMISSIONS` and a real `ACADEMY_QDRANT_URL`. Start `python -m retrieval_lab.research_server`. A write-authorized preparation session discovers `rag` and indexes both files with their stable `academy://documents/...` source URIs using `solutions.ingest_course_documents`. The model's separate session is read-only.

`solutions.answer_with_rag` uses the real MCP registry and bounded AgentHarness, discovers only permitted RAG tools, lets the explicit provider select retrieval and validates the final chunk-ID quotations against actual successful MCP observations. Missing evidence produces empty claims. Model-selected ingestion, cross-tenant arguments and unsupported citation claims are unavailable or rejected. This is implemented source; no actual model run is claimed yet.

### Lesson 14: real Qdrant service

`manifests/compose.qdrant.yaml` supplies a localhost-bound Qdrant1.16.0 service with a persistent volume. Parent QA must resolve and retain its actual image digest, then use `DocumentRAG.service` rather than silently substituting embedded mode. Verify collection dimensions/metric, actual upsert/query/delete, process restart persistence, owner isolation and rejected vectors. Test documents and chunks carry source URI, character offsets, document/chunk hashes and encoder identity.

The default `academy-token-hash-sha256-v1` is a reproducible64-dimensional teaching encoder, **not a pretrained semantic model**. `SentenceTransformerEncoder` requires an explicit immutable40-hex model revision, verified dimensions and `trust_remote_code=False`; the optional dependency/model and actual encoder run remain pending. Compare real retrieved IDs and scores with the human-authored expected documents in `manifests/embedding-model.json`. Do not invent scores or claim semantic quality from token hashing.

Replacement validates all new vectors before mutating old records, upserts acknowledged new chunks, then removes stale old chunks. These are separate service requests, not an atomic cross-request transaction. An uncertain cleanup outcome remains held for reconciliation; never blindly repeat writes.

### Lesson 16: progressive discovery

Each session begins with exactly `discover_capability`. Calling a guessed specialist fails. After authorized `discover_capability(capability="rag")`, call `list_tools` again and inspect the actual permitted native names. `solutions.progressive_solution` records the actual before/after lists and count change. Independent sessions maintain independent exposure. Revocation is checked on dispatch even after discovery; hidden write tools never become available to a read-only identity. Tool-count reduction alone establishes no quality, latency or cost improvement.

## Crucial security boundary discovered in the real existing server

The actual pinned Playwright0.0.54 server **allowed a direct `file:` navigation outside cwd** to an Academy-owned harmless sentinel. No unrelated/private file was inspected. `PrivateNetwork=yes` confines networking, not files. The host therefore exposes only the strict URL facades, never the generic browser session or arbitrary native tool dispatcher. Do not claim native filesystem containment. Broader adversarial browser use requires an OS filesystem sandbox in addition to network isolation. Likewise old Fetch2025.4.7 needs egress controls against redirects/DNS rebinding for untrusted pages. An origin allowlist alone is insufficient.

## QA handoff

Parent QA runs both `tests/test_project8_retrieval.py` and `tests/test_project8_retrieval_semantics.py` in its single admitted finite helper. New tests distinguish unit doubles, actual embedded Qdrant, actual MCP stdio and opt-in actual Qdrant HTTP service. Set `ACADEMY_QDRANT_TEST_URL` only for the owned test service; it is otherwise explicitly skipped. A real provider-selected workflow, real provider search, semantic encoder, Qdrant restart, new actual captures and independent per-lesson acceptance remain explicit work after source tests. No child author launched any new tests, installs or browsers for this semantic repair.
