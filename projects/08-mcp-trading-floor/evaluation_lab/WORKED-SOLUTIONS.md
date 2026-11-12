# Stage 30 worked solutions and evidence boundaries

These are concrete expected answers for supplied fixtures, not records of newly executed tests or human feedback.

## 1. Trace parentage and redaction

Wrap `dispatch_model` or `dispatch_mcp` inside `CorrelatedTrace.span('workflow','workflow')`. For two overlapping research tasks, each risk span's parent must equal its own research span ID; neither may point at the sibling. There is one workflow root. The JSONL contains `started` and `finished`; an interrupted operation may have only `started` and remains visibly incomplete. Join by `(run_id, span_id)`. Do not infer success from a start record. Failure retains the exception **type**, not its credential-bearing message. Payload/body bytes remain private; public trace records hashes and validated usage only.

## 2. Versioned dataset

`scenarios-v2.json` has eight cases. The normal family occurs only in development; order-limit, stale-data, conflict and agent-error families occur only in held-out. Transport and malformed families are development. A fixed January 15 snapshot with research stamped January 14 must become `RESEARCH_REJECTED`, even if a small ACA order would pass monetary risk. LAB research price 0.01 conflicts with the actual synthetic fixture 42.10 and must also be rejected. A successful network/tool envelope is not enough when its evidence fields are missing. Record dataset and market SHA256 from `load_suite` when measuring outcomes.

## 3. Research and decision metrics

Given evidence A `{revenue_growth:8}` and B `{revenue_growth:9}`, three claims are: value 8 citing A; value 8 citing A+B; value 8 with no citations. The answers are 3 claims, 2 cited claims, 1 supported claim, 1 conflicting claim, support fraction **1/3**. Do not count a conflicting set as fully grounded just because one reference matches.

For the identical scenario/input decisions BUY, BUY, HOLD, unavailable, the three comparable pairs have exactly one agreement. Agreement is **1/3** with three additional unavailable pairs. Empty comparisons produce `null`, never 100%. Different input hashes are not comparable even when scenario IDs match. Text word/sentence counts and Evidence/Limitations headings measure structure; only a rubric/human review can assess actual clarity.

## 5. Structured judge

For output `Synthetic evidence supports a bounded paper proposal.`, a schema example is:

```json
{"evidence":{"score":2,"evidence_quote":"Synthetic evidence"},"clarity":{"score":1,"evidence_quote":"bounded paper proposal"}}
```

This is an authored parsing example, not an actual provider verdict. A score `true`, missing dimension, extra dimension, score 3, invalid JSON or evidence quote absent from the output is an evaluator failure. No judge verdict authorizes an order. A real run must retain exact input, rubric hash, actual provider/model envelope, response ID/usage if supplied, and human disagreement. The HTTPS adapter reserves a once artifact before dispatch. Never delete a timeout intent to make a call look unused.

## 6. Human feedback

Register immutable output `actual registered test output` under `run-1`, then submit rating 3, comment `<script>untrusted</script>` and correction `Use exact evidence date` as an authenticated Academy practice reviewer. There must be one row after an identical duplicate. Changed correction under the same submission ID fails; an operator-only token fails; a nonexistent run/hash fails. The comment remains exact in private storage and appears as inert text in the UI. The original output is unchanged and `execution_approval` is false. This is an expected exercise, not a fabricated human review.

## 7–8. Failure and recovery

A local injected timeout after research must retain failed spans, unchanged cash/positions and `INCOMPLETE`. A missing-evidence response is `RESEARCH_REJECTED` even though the tool returned without a transport exception. For actual stdio MCP exercises, launch the owned fault server in timeout, malformed and error modes from a finite test client. Enforce client deadlines; terminate each child. Preserve raw actual envelopes and distinguish them from the separate direct Python fixture cases.

The checkpoint exercise prepares a unique request/digest, commits WRITE_INTENT, executes ACA 5, then deliberately exits 73 before marking COMMITTED. Restarting reconciliation should find the ledger's exact request/digest, return COMMITTED without dispatch, and retain cash **9373.75**, ACA **5**, one order. Repeating reconciliation preserves that state. If WRITE_INTENT exists but no order is found, the answer is **UNRESOLVED**, not retry-safe: the old writer must first be fenced/reconciled. A permanently invalid proposal does not retry; a retryable read has bounded admission/backoff and a real transport timeout.

## 9. Usage arithmetic

For 1000 input tokens including 200 cached, 100 output tokens, illustrative rates input 2/million, cached 1/million and output 4/million, the arithmetic is `(800*2 + 200*1 + 100*4)/1000000 = 0.0022`. Rates are illustrative, not a current provider quote. Cached tokens must not be charged again as uncached input. If a second call has unknown output tokens, known subtotal stays 0.0022 but full total is unknown. Count leaf calls once, not agent/container totals plus their child calls. Real usage must come from the actual recorded response, not an estimate substituted without a label.

## 12–14. Package, release and walkthrough

The compose network is frontend nginx → internal backend port 8000; browser requests use same-origin `/api`. Only UI port 8088 binds localhost. Database and feedback live in the named volume; a restart must preserve both. An image containing `deployment/.env` is a failed build design, so the backend uses selective COPY and the frontend copies only UI inputs plus nginx config. A successful source inspection is not a successful Docker build.

After a real build, retain image digests, dependency inventory and build logs; after actual hosting, add real host/revision/TLS/auth/health observations and a rollback receipt. For one accepted run, join its execution request ID/digest to the ledger and before/after balances; annotate research evidence, risk gate and explicit approval. For a rejected run, demonstrate no order was added. For a failure, keep incomplete/failed events visible. Do not paste these expected numbers into an evidence index as though observed.
