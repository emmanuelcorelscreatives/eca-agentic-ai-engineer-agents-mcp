# Framework decision record and final portfolio assessment

## Stage 30 lesson 16 — Choosing the right agent framework

Choose an implementation by the application constraints you can test, not by the number of framework names in the diagram. Reuse the course `frameworks/` adapters as concrete candidates, and preserve their actual runtime status. An imported class or package installation is not proof that a model run succeeded.

Score each candidate from 0–2 using retained evidence, or mark **not evaluated**. Do not turn missing evidence into a zero or a passing score.

| Criterion | Reproducible capstone experiment | Evidence to retain |
|---|---|---|
| Control | Can a rejected risk decision halt before paper execution? | rejected proposal, actual trace, unchanged ledger |
| State | Can an interrupted approved workflow recover without buying twice? | persisted database, same request ID, first and retried results |
| Tool boundary | Can a model request an unadvertised approval tool? | discovered schemas and actual denied invocation |
| Typed outputs | How is a malformed quantity or unsupported citation handled? | raw response plus actual validation error |
| Interoperability | Can the candidate use the same stdio/HTTP MCP capabilities? | real initialize/discovery/call transcript |
| Human review | Does approval bind to the exact proposal/version? | proposal digest and one-use approval record |
| Observability | Can one proposal be followed through model/tool/approval stages? | parent-child trace with unknown and failed outcomes retained |
| Deployment | Does the application restart with the same ledger and no secrets in logs? | image/source identity, restart proof, redaction test |
| Maintenance | Is required behavior covered by the repository tests? | pinned dependency versions and actual regression results |

**Exercise:** compare one explicit Python orchestration baseline with two course framework adapters. Keep the exact same fixture, tool schema and risk limits. Record the candidate source path and version, an actual successful and failed workflow, differences in state ownership, and any unavailable integration. Explain your selection in a one-page architecture decision record.

**Worked reasoning:** a candidate that produces fluent research but allows model output to bypass deterministic rejection fails the capstone boundary. A candidate that requires application-owned approval can still be appropriate if the application makes that boundary explicit and tests it. Distinguish features implemented by a framework from controls implemented by your application. The course reference keeps approval and ledger rules in ordinary Python so switching an orchestration adapter does not change account policy.

## Stage 30 lesson 17 — Ten engineering principles

1. Define observable outcomes before choosing agents: a valid evidence-linked proposal is a contract; “intelligent trading” is not.
2. Keep model authority bounded: language output cannot grant approval or rewrite a deterministic risk decision.
3. Treat tool results and retrieved content as data: a webpage instruction does not become a developer instruction.
4. Preserve evidence lineage: every displayed claim references an actual retained source, with synthetic fixtures labeled.
5. Use typed interfaces: parse and validate quantities, prices, citations and state transitions before acting.
6. Make side effects idempotent: retries preserve request identity and return the existing result.
7. Make uncertainty visible: a missing response or deployment record is unknown, not a fabricated success.
8. Put humans at meaningful decision boundaries: approval identifies the exact proposal and cannot be reused silently.
9. Measure the real application: report observed latency, real usage metadata and documented cost assumptions separately.
10. Prefer the simplest architecture that meets tested requirements: add another agent or service only when its responsibility and failure handling are clear.

**Exercise:** annotate one actual capstone trace with all applicable principles. For each principle give the code path, the test proving it and a failure that would violate it. A principle without evidence is an improvement item rather than a completed portfolio claim.

## Stage 30 lesson 18 — Career and portfolio roadmap

Prepare a public portfolio using only original synthetic data and approved public assets. Never publish API keys, private account screenshots, source transcripts containing personal information or paid-provider access tokens.

A credible capstone case study contains:

- Problem and scope: educational paper trading with fictional companies and no brokerage execution.
- Architecture: ownership of model calls, MCP transport, memory, deterministic risk, human approval and ledger.
- A reproducible quick start tied to a source revision and tested dependencies.
- Actual evidence: tests, one rejected proposal, an approved paper fill, an idempotent retry and a trace.
- Evaluation: real measured results and explicit limitations; keep model-judge scores separate from accounting correctness.
- Operations: storage, secrets, authentication, restart/recovery, and the exact boundary between a localhost prototype and a hosted system.
- Reflection: one concrete design mistake, how evidence exposed it, and the scoped correction.

**Exercise:** write three short project descriptions for an engineering role, a consulting engagement and a product proposal. Each description must name the user problem, your actual contribution, a measurable observed result and a limitation. Do not claim employment, certification, revenue, production usage or financial returns that have not occurred.

**Worked example:** “Built a synthetic paper-trading teaching application with MCP research tools, Decimal accounting and explicit human approval. Demonstrated that repeated request IDs return the original fill without an additional purchase. The localhost deployment has not been evaluated for public multi-tenant use.” This is a verifiable engineering statement; “built a profitable autonomous trading system” is unsupported by this project.

## Stage 30 lesson 19 — Completion and next steps

Submit the eight project repositories or their coherent course subdirectories, the final source revision, actual test results, demonstration records, exercise solutions and a limitations log. For each project identify which components are deterministic fixtures, which really invoke a model, which depend on credentials and which remain untested.

A submission is complete when a reviewer can follow its documented commands from a clean environment, inspect the original sample data, reproduce the stated outputs, and trace every claimed observation to evidence. If the hosted deployment or a model experiment was not performed, say so and scope the presentation accordingly; do not invent a completion certificate or successful deployment.

**Final exercise:** conduct a peer handoff. The reviewer starts without your local database or shell environment, uses the documented sample inputs, reproduces one accepted and one rejected workflow, then records a mismatch or confirms the exact tested claim. Keep the handoff report separate from automated test output and from the course video production pipeline.
