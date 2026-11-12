# Stage 13 — Evidence-first market intelligence practicals

This stage uses **fictional** Cedar, Maple and Pine. Their scenario date is 2026-01-01;
it is a teaching-data label, not an observation of real markets. Existing `market.py`,
`companies.json`, `synthetic-ledger.json`, `crewai_adapter.py` and these advanced tools
form one application rather than fourteen unrelated examples.

Run from the repository root:

```sh
python3 projects/04-market-intelligence/advanced/research_lab.py --output-dir /tmp/eca-market-stage13
python3 -m unittest discover -s tests -p 'test_market_advanced.py' -v
```

The semantic extension adds `advanced/full_report.py --output-dir NEW_DIRECTORY`
for one report containing the financial ranking **and** all business/product/competition
profiles and dated sector signals. The new commands and semantic tests are authored
pending central QA; the earlier eight-test receipt does not certify these new bytes.

`research_lab.py` executes actual fixture validation and writes JSON, Markdown and the
full evidence registry. A new output directory is required; historical results are not
overwritten. No provider or network operation occurs. For optional live framework
execution use the separately pinned CrewAI environment and:

```sh
python projects/04-market-intelligence/advanced/live_research.py --run-live \
  --model PROVIDER/MODEL --trace /tmp/eca-market-live-task-trace.jsonl
```

This is an actual hierarchical CrewAI configuration with four specialists and a manager.
Task callbacks retain **real SDK task outputs only after execution**. The custom memory
tool serves only validated structured research bound to exact source and criteria hashes;
CrewAI embedding memory is disabled, so no hidden embedding-provider call is introduced.
The manager's intermediate provider reasoning is not asserted by a task-output callback.
Live runs require an approved external budget/governor; `max_iter=6` and `max_rpm=10` are
iteration/rate controls, not a guaranteed total API-token cost ceiling. A run whose outcome
is unknown must not be blindly replayed. Free-text summaries require human evidence review.

## 1. Scope, responsibilities and deliverable

Four specialist roles own company facts, sector context, deterministic screening and
risk/evidence review; a hierarchical manager coordinates them. The report must show all
three companies exactly once, each rule, source locator, uncertainty and concentration
risk. **Exercise:** label “Cedar's real stock will rise” as supported or unsupported.
**Solution:** unsupported; this fixture contains neither real prices nor forecasting data.

## 2. Structured research models

`market.Company`/`Criteria` and advanced `Evidence` distinguish null from zero, preserve
fraction units and reject non-finite values. Evidence dates parse as actual ISO dates.
**Exercise:** replace Pine's missing margin with zero. **Solution:** reject the inference;
null is unknown and zero would claim a measured margin. Use the missingness test.

## 3. Company research agent

The real adapter's `fictional_company_research` tool supplies complete approved records.
`review_numeric_claims` resolves every non-null metric to a company-specific ledger item.
`research_sources.json` additionally supplies company business models, named products,
competitive positioning and explicit limitations. `FixtureResearchAdapter.company`
returns typed `CompanyResearch` with dated `SourceDocument` citations: Cedar's CSV
reporting product versus fictional Rook's connectors; Maple's repairable warehouse
scanner versus fictional North's initial prices; Pine's small advisory engagements
versus fictional Elm's broad programmes. These are authored scenario facts, not real
company observations. Each product and competitor claim is carried with its source
extract; a source belonging to another company fails validation.
**Exercise:** change Cedar's growth to .9. **Solution:** ledger reconciliation rejects it;
no LLM confidence or unsupported citation rescues the number. An actual SDK/provider
run is separately required before narrating an observed live research result.

## 4. Market analysis agent

`FixtureResearchAdapter.market` supplies dated fictional conditions and numerical
signals with source extracts: software planned-evaluation share 24/40 and cost-index
change 100→108; hardware orders 100→95 and component lead time 4→6 weeks; services
inquiries 80→92. The adapter checks every supplied ratio/change and source attribution.
The actual market analyst has the `dated_market_conditions` tool and company task
context, so it can compare demand, costs and supply pressures within this synthetic
scenario. Sampling and causality uncertainties remain explicit. `sector_context` is
only the older no-live-evidence helper; it does not replace the new scenario data.
**Exercise:** infer a hardware industry boom from Maple alone. **Solution:** retain an
uncertainty; one fictional company is not market evidence.

## 5. Screening and ranking

`market.screen` uses growth >= threshold, margin >= threshold, debt <= threshold; equality
passes. Scores sum three equally weighted Boolean rules; missing value/evidence earns no
credit. Ties sort by symbol. **Exercise:** growth threshold .20. **Solution:** Cedar and
Pine both score 2, Cedar first by symbol; Maple scores 1. No fact changes.

## 6. Risk and evidence reviewer

Use `review_numeric_claims` before a report and `evaluate` after assembly. The latter
rejects changed profiles, risks, company coverage or criteria against the authoritative
reference. **Exercise:** cite Pine's growth evidence for Cedar. **Solution:** reject the
misattributed company even if the citation exists. Free-text business assertions outside
the fixture are unsupported and must be removed or held for real source review.

## 7. Replaceable data adapters

`market.ResearchSource`/`FixtureSource` cover numeric company records. The additional
`ResearchAdapter` protocol has typed company and market methods, implemented by
`FixtureResearchAdapter`. Each returns exactly one of `success(value)`,
`absent(reason)` or `error(reason)`. An absent sector is not zero growth; an unavailable
source is not a successful empty research result. Malformed source dates, duplicate
IDs, company/sector citation swaps and unreconciled signal arithmetic become error
results. A replacement adapter must preserve those contracts. A live
adapter must additionally bind source permission, timestamp, rate limit and unavailable
response semantics. **Exercise:** rename a fixture adapter “live”. **Solution:** a name
changes no provenance; preserve fictional status until real authorized data exists.

## 8. Reusable calculations

`ratio` rejects missing, non-finite and zero-denominator inputs. `fraction` requires an
explicit percent/fraction unit. Ledger tests independently recompute each financial ratio.
**Exercise:** normalize 18 percent. **Solution:** .18; 18 as a fraction means 1800%, so
never silently guess units. A ratio error is not a zero observation.

## 9. User-defined criteria

Use the CLI's three explicit thresholds or `Criteria`. Every report records accepted
criteria; threshold changes do not mutate company facts. Unsupported operators and
weights are not silently accepted. **Exercise:** set minimum margin .20. **Solution:**
Cedar's equality passes; Pine remains unknown; Maple fails the margin rule.

## 10. Validated memory and context

`ResearchMemory` keys canonical source identity plus criteria, validates exact report
content before storing and returns independent copies. `live_research` adds this as a
real custom CrewAI tool to each specialist, alongside explicit prior-task context.
**Exercise:** update the ledger or thresholds. **Solution:** source/criteria keys change,
so old scores miss the cache. This demonstrates custom validated memory, not a claim
that built-in embedding memory has executed.

## 11. Hierarchical manager and correction

The actual adapter uses `Process.hierarchical` and `manager_llm`. The manager receives
four scoped specialist agents; task context carries dependencies. A correction means
requesting supporting source or rejecting a changed report, never accepting fabricated
metrics. **Exercise:** remove a required source. **Solution:** expose uncertainty and
hold unsupported output. Retain actual task callbacks and provider receipts for a live
demo; do not synthesize a manager/delegation/correction trace from a sequential mock.

## 12. Structured profiles

Every profile includes identity, sector, score, checks, risks and uncertainties. Markdown
is generated directly from the same JSON; HTML, pipe and newline characters in text are
escaped. **Exercise:** compare Pine JSON and Markdown. **Solution:** both show unknown
margin, 2/3 score and the same missing-profitability risk; no guessed value is inserted.

## 13. Final report

The executable produces `report.json`, `report.md` and `evidence.json`. Every non-null
metric points to the same ledger-backed evidence. **Exercise:** omit Maple to make the
report look stronger. **Solution:** `evaluate` fails coverage; selection criteria must
be explicit, consistent and preserved in the deliverable.

## 14. Evaluation

The suite injects numerical tampering, wrong-company citations, missingness errors,
invalid dates/units, cache changes and report-field omissions. **Exercise:** score a
candidate that duplicates the leading company. **Solution:** fail unique company
coverage and exact profile comparison. Offline correctness is actual fixture proof;
it is not a claim that CrewAI/provider execution, live market research or investment
performance has been verified.
