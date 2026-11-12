# Project 4 — Market Intelligence and Stock Screening Crew

This runnable offline baseline supports Stage 13. Every company, metric and evidence
locator is a **fictional teaching fixture**. No prices, investment recommendations,
provider calls or real market-condition claims are made.

```sh
python3 projects/04-market-intelligence/market.py --output /tmp/eca-market-report.json
python3 projects/04-market-intelligence/market.py --min-growth .20
python3 -m unittest discover -s tests -p 'test_projects_4_5.py'
```

The research source returns typed company profiles. Analysis enumerates sectors and
explicitly declares absent live context. Screening applies three equal-weight rules;
a missing metric or its evidence earns zero, rather than being invented. The reviewer
reports unsupported metrics and preserves risk notes. Sorting is deterministic by
score, then symbol. The report includes each threshold, observed value and evidence
locator so a reader can reproduce every point.

Default expected ranking: Cedar 3/3, Pine 2/3, Maple 1/3. Pine's missing margin is an
uncertainty, not a zero margin observation. Fixture locators refer to the company records and documented formulas in
`synthetic-ledger.json`, not externally verified source documents. A test independently
recomputes all fixture metrics from that ledger.

## CrewAI extension (optional; not executed by the offline runner)

Implement researcher → market analyst → screener → evidence reviewer tasks with a
manager supervising corrections. Pass the complete structured profile list as task
context; store only validated profiles as memory. Wrap `FixtureSource` with a typed
CrewAI `BaseTool`, keep the deterministic `screen` function authoritative for scoring,
and require the final task to validate the same report schema. Install a pinned CrewAI
version in a separate environment and consult its official version-matching docs.
Network/provider adapters require explicit credentials and approval; this repository
makes no claim that a live crew has run. A new live adapter must supply provenance,
observation timestamps, permitted-source policy and error handling before comparison.

## Exercises and solutions

1. Raise minimum growth to .20. **Solution:** Cedar loses growth credit (2), Pine stays
   at 2, Maple stays 1; the symbol tie-break places Cedar first. Criteria change, not facts.
2. Remove Cedar's margin evidence. **Solution:** score becomes 2, one uncertainty is
   added; do not silently accept the unsupported metric.
3. Add negative cash flow as a risk. **Solution:** preserve it in `risks`; risk annotations
   do not change points unless a new explicit criterion is defined and tested.
4. Add a manager correction cycle. **Solution design:** ask the researcher to resolve
   missing evidence once, retain the first report, and record unresolved uncertainty if
   no approved evidence arrives. Never substitute an LLM's confidence for evidence.

## Implemented optional CrewAI adapter

`crewai_adapter.py` implements four real CrewAI agents, custom typed tools, explicit
task context, Pydantic final output and hierarchical manager orchestration. Task
context supplies shared research memory without a separate embedding provider.
It rejects any model-produced change to authoritative profiles or scores.

```sh
python3 -m venv /tmp/eca-market-live
/tmp/eca-market-live/bin/pip install -r projects/04-market-intelligence/requirements-live.txt
# Set provider credentials privately, then explicitly choose your configured model.
/tmp/eca-market-live/bin/python projects/04-market-intelligence/crewai_adapter.py --run-live --model PROVIDER/MODEL
```

This adapter was syntax-checked and its pure validation tested; SDK/provider
execution has not been performed. Installation and kickoff are explicit student
actions. Summary prose still requires human factual review; deterministic profile
validation does not prove all free-text claims. API reference (checked 2026-11-12):
[CrewAI crews](https://docs.crewai.com/v1.15.40/en/concepts/crews),
[custom tools](https://docs.crewai.com/v1.15.40/en/concepts/tools),
[hierarchical process](https://docs.crewai.com/v1.15.40/en/learn/hierarchical-process).
