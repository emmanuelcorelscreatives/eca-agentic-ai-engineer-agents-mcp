# Research lifecycle and teaching contracts

The question is a community-workshop scheduling investigation, with accessibility,
cost and operations branches. This package keeps facts, recommendations and unknowns
separate. `planning.ROLES` describes planner, searcher, analyst, reviewer and writer
handoffs. The writer consumes reviewed records and has no search or email authority.

The synthetic fixtures are Academy-authored and their example.invalid URLs are
identifiers, not web observations. Conflicting cost estimates intentionally remain
unresolved. Unknown dates remain null. The lab cannot certify a real product choice.

`make_plan` and `validate_plan` implement task DAG validation; `queries_for` provides
support and counterevidence searches; `parallel_search` admits at most eight bounded
read tasks and retains input order. `EvidenceStore` stores immutable exact excerpts
under SHA256 content IDs. Analysis groups conflicting values without picking a winner.
Reports include question, method, findings, limitations, recommendations and references.
Export preserves both the report and machine-readable source/evidence/activity bundle.

## Adapter and deployment boundaries

`LiveSearch` is a real async adapter interface accepting an explicitly enabled provider
transport. Supply a separately reviewed HTTPS search client. The adapter does not
follow arbitrary result URLs, embed credentials, retry rate limits or claim a fixture
is live. No live service or provider SDK was executed for these materials.

A concrete opt-in HTTPS JSON transport and TLS SMTP transport are implemented in
`research_lab/transports.py`; both are tested using fake transports and have never
contacted a live service. JSON search expects the documented Academy service contract,
not an invented claim about a commercial provider API. SMTP acceptance is distinct
from actual inbox delivery.

The optional Gradio interface is implemented in `research_lab/interface.py`. Install
`projects/03-deep-research/requirements-ui-stages09-10.txt` (a deployment lockfile is still required), then run:

```
python3 examples/stages09-10/run_research.py --ui
```

Binding is localhost and share=False. Deployment behind a reverse proxy needs actual
TLS, authentication, upload/size limits, retention rules and independent smoke testing.
Do not expose this teaching application directly to the public internet. The repository
does not claim a production deployment, live email or actual paid-model token measurements.

Operational progress reports phases only after those phases really execute; it does
not stream private reasoning. Token counts are null because the offline adapter has
none. Structural evaluation is a rubric aid, not an automatic factual-truth score.

Recovery uses request-bound durable JSON and rejects another question's checkpoint.
`bounded_retry` retries only a positively known connection refusal, up to three times.
Timeouts or unknown paid-provider outcomes propagate for investigation, never replay.
Email delivery requires an exact recipient/report digest; the demo outbox is simulated.
A real authenticated mail adapter and one actual approved delivery remain optional work.
