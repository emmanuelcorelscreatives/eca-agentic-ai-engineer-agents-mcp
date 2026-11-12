# Evaluation and operations lab

This extension supplies tested **offline** boundaries for Stage 30. It does not certify the full nineteen-lesson stage. No genuine model judge request, MCP fault-server transport, Docker build, hosted deployment, browser feedback form, or process-interruption recovery has been observed by this lab.

From the repository root:

```sh
python3 -m unittest discover -s tests -p test_project8_evaluation.py -v
PYTHONPATH=projects/08-mcp-trading-floor python3 -m evaluation_lab.dataset
```

`scenarios.json` is synthetic, fixed to the same January 15, 2026 market fixture as the paper ledger. Its family split prevents normal examples leaking into held-out families. The four cases assess ordinary risk rules; stale-data and conflicting-evidence workflow scenarios remain work for the full capstone integrator. `validate_dataset` returns SHA256 hashes for the exact dataset and market bytes. No future investment-return claim is made.

## Trace and usage integration

Create one `Trace(run_id)` for a sequential workflow and wrap nested research, risk, human approval and execution calls using `trace.span`. Span names must be fixed code identifiers, never prompt or user text. Correlate order/evidence IDs through allowed fields. The exporter discards arbitrary payload fields and exception messages. It is not an automatic detector for secrets embedded inside allowed fields; validate those identifiers at the application boundary. One `Trace` instance is sequential, not shared across concurrent threads/tasks.

Use `usage_report` on **leaf model calls only**. Cached tokens are a subset of input tokens and priced separately. Supply dated rates from a verified provider price sheet at the time of a real experiment. Never fill missing usage or missing rates with zero. Duplicate call IDs fail. The known subtotal is distinct from the complete cost, which stays unknown if any call is unknown. Span durations use a monotonic clock; UTC timestamps serve correlation, not elapsed-time arithmetic.

## Explicit structured judge

`quality.judge` requires a caller-supplied provider callable, explicit model and exact run ID. The callable must return a JSON object with exactly `evidence` and `clarity` dimensions, each containing integer `score` 0–2 and an `evidence_quote` present in the evaluated output. An invalid response is an evaluator failure, never an implicit pass or an execution approval. Risk checks remain independent and authoritative.

The caller must obtain an authorized bounded provider experiment before connecting a real adapter. Current tests use clearly named offline test doubles. The artifact is reserved and fsynced before dispatch; an existing artifact prevents another dispatch, including after an unknown outcome. Results retain exact raw responses, model, input/rubric hashes and status in private mode-0600 files. Preserve the original evaluated output separately under the same privacy policy so the input hash can be resolved. Do not commit those private artifacts indiscriminately. A timeout is unresolved, not evidence of zero provider usage.

## Human feedback

`FeedbackStore` persists a stable submission key, exact run/output version, practice reviewer, integer rating 1–5 and comments in SQLite. A repeated identical key is idempotent; a changed submission under that key fails. Feedback has **no order approval field** and never opens the trading ledger. The integrating authenticated UI must escape comments as text (React text interpolation, not `dangerouslySetInnerHTML`); this library intentionally stores the original comment for auditing. Real UI and authorization tests are still required.

## Recovery

`retry_read` retries only connection/timeouts within maximum attempts, exponential delay and an admission deadline. Validation/permission errors fail immediately. The deadline bounds retry admission, not an uninterruptible operation: the real transport must enforce its own remaining-time timeout. `write_once` classifies a network timeout as `UnknownWriteOutcome`, requiring reconciliation with the ledger's original request ID. It does not retry. Process restart/checkpoint integration and remote MCP fault tests remain distinct acceptance work.

`workflow.run_paper_workflow` wraps actual core research, proposal, deterministic risk, explicit caller-supplied practice approval and ledger execution. Its integration test reconciles accepted cash/positions and proves pending/rejected runs leave the ledger unchanged. This is actual local deterministic integration, not a real LLM agent/MCP transport trace.

## Semantic extensions — author-only, pending sole QA owner execution

`tracing.CorrelatedTrace` uses ContextVar parentage to isolate concurrent async children, writes started/finished records with fsync, and wraps the actual injected HTTP model or MCP `ClientSession.call_tool` dispatch. `provider.HTTPJudgeProvider` is an explicit HTTPS chat-completions protocol adapter with no automatic retry/redirect, bounded response size and a private once envelope. Imports make no requests. Real provider compatibility, real usage and SDK transport still require genuine bounded experiments.

`scenario_workflow` adds version-2 synthetic normal, oversized, stale, conflicting, timeout, missing-evidence and agent-error cases. Its strict validator checks exact fields, fixed market/evidence references and family splits; the corresponding JSON Schema is supplied. Fault injection is labelled local simulation. `fault_mcp` is a real stdio MCP test-server source to exercise client timeouts/tool errors/malformed successful payloads; run it only in the owned test harness.

`research_metrics` exposes exact fact/evidence agreement, conflicting citations, same-input pairwise decision consistency and transparent text-structure measurements. Clarity counts are explicitly not a substitute for the qualitative rubric. An evidence claim uses `{fact, value, evidence_ids}`, with references resolving to `{id, facts}`. Conflicting evidence is retained as a conflict, never counted as supported.

`feedback.BoundFeedbackStore` is the application integration API. Unlike the earlier unbound teaching store, it verifies an existing exact run/output pair, authenticates a practice reviewer against a separately configured token mapping, and persists corrections without changing prior output or approving orders. Display comments/corrections as text. The earlier `quality.FeedbackStore` remains a narrowly scoped backward-compatible unit exercise, not the app route.

`checkpoints.Checkpoints` persists PREPARED then WRITE_INTENT before dispatch. Reconciliation checks the actual ledger request ID/digest and marks a matching order COMMITTED. A missing order after WRITE_INTENT stays UNRESOLVED because an old writer could still commit. No silent replay or fake settlement is permitted.

### Worked recovery exercise (commands supplied, not run here)

```sh
# Use a new empty scratch directory. The first command intentionally exits 73.
PYTHONPATH=projects/08-mcp-trading-floor python3 -m evaluation_lab.checkpoint_demo prepare-and-crash --ledger /tmp/academy-recovery-new/paper.sqlite --checkpoint /tmp/academy-recovery-new/checkpoint.sqlite
PYTHONPATH=projects/08-mcp-trading-floor python3 -m evaluation_lab.checkpoint_demo reconcile --ledger /tmp/academy-recovery-new/paper.sqlite --checkpoint /tmp/academy-recovery-new/checkpoint.sqlite
```

Create that scratch directory first. Expected result on a fresh account is one order, cash 9373.75, ACA position 5 and COMMITTED reconciliation with `dispatch_allowed:false`. The result must be observed, not copied from this expected answer. A second reconciliation must retain exactly the same balance/order count. For a WRITE_INTENT without an order, expected state is UNRESOLVED until the old writer is independently fenced or its result found.
