# Stage 27 lesson 8 — Trace public MCP actions

The PDF objective is to record server selection, arguments, responses, latency, failures and agent decisions. Here “agent decisions” means the public action the provider returned: which tool/route it requested, or that it finished. It does **not** mean hidden reasoning, chain of thought or private prompts.

`AgentHarness.trace` records `agent_decision` events with a run ID, decision ID, iteration, public action (`tool` or `finish`) and elapsed time. A tool choice records only its known host-configured server/qualified tool. Unknown names appear as `unknown`; raw model-supplied names are not copied into telemetry. Final-answer text and user/system prompts are absent from this trace.

`MCPRegistry.trace` records each actual dispatch boundary with the same run and decision ID, a unique call ID, known server/tool, start/end, terminal result status, error code and measured latency. Joining decision ID to call ID distinguishes “requested a tool” from “the tool actually ran.” A denied request or exhausted budget must never be described as a successful tool call.

## Argument and response privacy

Arguments are represented by their bounded top-level count and an opaque HMAC-SHA256 digest of redacted canonical JSON. Credential-shaped dictionary fields and explicitly configured known secret values are redacted before computing the digest. Argument values, paths, query text and prompt content are never written to trace events.

The registry creates a private random digest key for each instance and never exports it. Thus equal canonical redacted arguments compare equal within that registry, independently of dictionary key order, while public low-entropy values cannot be guessed from an unkeyed SHA. Digests from different registries are intentionally incomparable. This digest is correlation metadata, not an approval token or a proof of semantic correctness.

Successful results likewise receive only an opaque digest; failed tools retain their actual status/error classification. Full SDK results remain in the application observation boundary where permission and redaction apply, rather than being duplicated into public telemetry. Never add credentials, raw prompts, private documents, exception messages or hidden reasoning to the trace to “improve visibility.”

## Worked exercise

Select `first::lookup`, then `second::lookup`, then finish. The two public decision events must name the intended server alias. Each dispatched decision joins to exactly one call ID, and its terminal event records the actual outcome and nonnegative latency. A failure on the second route must remain an error even if the provider later produces a final answer.

Compare `{"query":"private","password":"first-secret"}` with `{"password":"different-secret","query":"private"}` in one registry. Their argument digests match because credential values are redacted and key order is canonical. The raw query and either password must be absent from the public trace. A second registry uses a different private HMAC key and produces a different digest.

## Central QA only

The new tests are authored, not executed by the author:

```sh
ACADEMY_REQUIRE_PROJECT8_TRACE_SDK=1 python -m unittest discover -s tests -p test_project8_public_trace_v2.py -v
```

The real-SDK case launches the genuine course server, obtains an actual synthetic quote and then invokes a real tool error before sampling. Provider public actions are explicitly scripted for deterministic routing; that test proves actual SDK transport/correlation, not model intelligence. A later genuine model demonstration must retain its actual public choices without inventing rationale or reporting the scripted sequence as a model observation.
