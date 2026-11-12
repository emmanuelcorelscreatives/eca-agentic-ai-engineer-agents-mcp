# Controlled retrieval practicals

These working reference components support Stage 27–28 exercises. They are **not a claim that every planned existing-server lesson has been implemented**. Every result identifies its actual source; synthetic Academy fixtures are never live market observations.

## Run

From `projects/08-mcp-trading-floor`, use the course runtime containing `qdrant-client==1.16.1` and `mcp==1.22.0`:

```sh
python -m retrieval_lab.reference
python -m retrieval_lab.server
```

The first command performs real embedded Qdrant indexing/querying. No external service or model call occurs. The second starts a genuine custom MCP stdio server; tools are discovered through the real SDK. Configure `ACADEMY_FETCH_ORIGINS` as a comma-separated list of exact approved origins. An empty list denies all fetches. Set `ACADEMY_SEARCH_ENDPOINT` only for a provider you operate, and enroll that origin explicitly. Search uses SearxNG-compatible `q` and `format=json`; missing configuration is an error, not fabricated search output. HTTP quota/timeouts propagate as explicit failures.

`mcp_adapter.session(command,args)` connects to an explicitly pinned existing stdio server. `discover` returns the server's actual tool schemas. `browser_extract` only dispatches discovered `browser_navigate` and `browser_snapshot` after checking the destination. **An existing Playwright MCP server/browser integration has not yet been run for this component.** Launch that server with an isolated temporary profile and enforced outbound network sandbox; the facade does not by itself stop a web page making remote subrequests. It exposes no submit function. Do not use a personal browser/profile.

## Exercises and reference solutions

1. Serve a new Academy-only HTML policy using Python's HTTP server. Approve its exact origin and fetch it. Change the server port: the original allowlist must reject it. Reference: `ControlledFetch` and `test_real_owned_http`.
2. Add a redirect to an unapproved origin and a 404 page. Confirm both fail explicitly and no destination is silently followed. Reference: `test_destination_redirect_missing_and_size`.
3. Wrap a real configured SearxNG-compatible provider. Retain URL/query/time and raw redacted response; compare it with an explicitly labeled owned fixture server. **No genuine external-provider result has been collected by these tests.** Reference: `SearchProvider` and `test_search_real_owned_http`.
4. Index two tenant-owned documents; query one tenant, restart the store, delete a document and verify it is absent. Reference: `reference.py` and `test_real_qdrant_local_persistence_tenant_delete_and_dimensions`.
5. Begin with only `discover`, reveal `rag`, then revoke its permission before invocation. A previous discovery is not authorization. Reference: `CapabilityCatalogue`.
6. Supply a model-generated quotation with a real citation but unsupported text. It must fail. Reference: `GroundedModelAdapter`; its callable boundary works with any framework's completion function. Tests use a deterministic test callable and **do not establish a live model or framework run**. Only exact supported quotations are accepted; semantic correctness beyond quotation support is outside this adapter.

## Embeddings and limitations

`academy-token-hash-sha256-v1` uses 64-dimensional normalized token hashing. This is a reproducible teaching encoder, **not a pretrained semantic embedding model**. Qdrant local mode persists real vector/payload data without a daemon. A separate Qdrant server, pretrained encoder, existing filesystem/fetch/Playwright server integrations, credentialed search, and a real bounded model loop remain separate required integrations before those course walkthroughs can claim observed success.

The local Qdrant backend accepted a length-one vector by broadcasting during development. This adapter therefore validates dimension and finite numeric values before upsert; tests verify the adapter rejects invalid vectors. We do not claim the backend itself rejected them.

HTTP hostname allowlisting is insufficient against hostile DNS rebinding. Public/untrusted fetch demonstrations require network-level outbound restrictions. Tenant arguments here are explicit teaching inputs; a deployed service must bind tenants to authenticated identities rather than trusting arbitrary caller-supplied names. Progressive disclosure reduces exposed catalogue size; no speed/cost/quality improvement is claimed without a measured comparison.
