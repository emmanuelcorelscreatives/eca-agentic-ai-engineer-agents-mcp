# Project 3: Deep Research Intelligence Team

Curriculum: Stage 9, lessons 1–13, and Stage 10, lessons 1–11. Start with the
[stage workbook](../../curriculum/workbooks/stages-01-10.md#stage-9), then use the
[student guide](docs/student-guide.md) for prerequisites, runnable steps and expected checks.

## Current learning route

All commands below run from the **repository root** with Python 3.11 or newer.
The fixture exercises and core tests need no credentials or third-party packages.

```sh
python3 examples/stages09-10/run_research.py
python3 -m unittest discover -s projects/03-deep-research/tests -v
```

The workshop demo should cite four synthetic records, retain the **30-credit versus
45-credit** cost conflict and report token usage as unavailable (`null`). It is a
fixed exercise for `Community workshop scheduling`, not a general research service:
other questions are rejected before retrieval. Default output uses no live search,
model, email or external factual verification. The optional
[offline UI setup](docs/student-guide.md#optional-offline-ui) uses the same fixture.

| Lessons | Implementation and student outcome |
|---|---|
| [s09-l01–l04](../../labs/s09-l01/README.md) | Scope the question and diagram roles; compare the fixed fixture plan with the question-driven SDK plan in `research_lab/sdk_v2.py`. |
| [s09-l05–l09](../../labs/s09-l05/README.md) | Inspect `brave_search.py`, `contracts_v2.py` and `pipeline_v2.py`; connect sources, exact excerpts, findings and report citations. Real Brave/SDK observations require opt-in paid setup. |
| [s09-l10–l13](../../labs/s09-l10/README.md) | Trace dependencies, bounded concurrency, deduplication and quality failures using the project tests. Distinguish fake transports from real source observations. |
| [s10-l01–l08](../../labs/s10-l01/README.md) | Follow modules, UI events, exports, evaluation cases and usage in the [student guide](docs/student-guide.md). |
| [s10-l09–l10](../../labs/s10-l09/README.md) | Study [selective recovery and owned exports](docs/selective-recovery-and-owned-export-v3.md), then follow the [v3 deployment exercise](deployment/research-v3/README.md). |
| [s10-l11](../../labs/s10-l11/README.md) | Use the [optional SDK/Brave capstone](docs/student-guide.md#optional-live-sdk-and-search) and mark any unobserved live/UI/deployment outcomes incomplete. |

The current live path is `capstone_v2.py` with the question-driven SDK planner and
analyst, concrete Brave adapter and v2 journal. The current deployable UI uses
`interface_v3.py` / `deploy_v3.py` with selective recovery and own-session exports.
Neither is executed by the fixture commands above. Keep provider credentials outside
the repository, and never discard state to replay an UNKNOWN paid operation.

## Legacy Cedar comparison exercise

`research.py` is a separate deterministic comparison over a **synthetic local corpus**.
It preserves citations, identifies conflicting claim values and renders a report.
It performs no live search, model call or external factual verification. It is not
the workshop data or the current SDK application.

```sh
python3 projects/03-deep-research/research.py
python3 projects/03-deep-research/research.py "galactic asteroid mineral royalties"
```

The first report must preserve both **45 minutes** and **70 minutes** as a conflict, noting source excerpts and scope. It must not average them into an invented result. The second should report insufficient evidence. Fixture `.txt` files are the corresponding invented practice source documents; JSON contains the normalized evidence records.

### Cedar build sequence

1. Define the research question, deliverable and completion criteria. `plan` exposes a deterministic starting plan, not generated hidden reasoning.
2. Inspect the three query branches and `ThreadPoolExecutor(max_workers=3)`. Results are deduplicated by stable source identifier with deterministic final ordering.
3. Add a new local source and normalize title, location, published date, claim, value and excerpt.
4. Inspect claim/value groups. Different values remain explicit alternatives with citations. Shared values are supported by this corpus only, never declared universal truth.
5. Expand report sections and include missing evidence, source-date limitations and an assessment of comparability.
6. Optional separate live adapters may provide search/model reasoning and a Gradio UI. Pin the chosen actual search provider/SDK and framework versions; credentials remain in environment variables outside the repository. Preserve fetched source snapshots, access times, exact excerpts and per-query attribution. Untrusted web content must not control tools or override application instructions.
7. Add evaluation fixtures for contradictory, duplicated, irrelevant, stale and absent sources. A live adapter must pass the same citation/no-invention tests before deployment.

### Cedar exercises and solutions

- **Conflict:** explain 45 versus 70. Solution: the first excludes validation, the second includes it. Keep both values and their conditions; the system does not establish that either source is wrong.
- **Missing evidence:** research an unrelated topic. Solution: `insufficient_evidence`, empty findings, no invented references.
- **Duplicate source IDs:** insert another record with an existing ID. Solution: fail loudly before parallel retrieval instead of silently overwriting evidence.
- **Concurrency:** compare max_workers 1 and 3. Solution: identical report output; concurrency changes scheduling, not attribution or conclusions.
- **Causal overreach:** ask whether automation caused improvement. Solution: the three-report fictional pilot has no controlled evidence of causality; record that gap rather than claim success.

The limited lexical search and exact claim-key grouping are deliberately visible baseline constraints. More intelligent planning and semantic evidence analysis must be evaluated explicitly when optional live agents are added.

### Legacy optional SDK adapter

`agents_adapter.py` implements actual `Agent`, `Runner.run`, typed Pydantic outputs and bounded turns. Install `requirements-optional.txt` in a separate virtual environment, then run `python3 agents_adapter.py --live` from this project directory after setting `OPENAI_API_KEY` and `ACADEMY_MODEL`. This makes paid requests. It was syntax-checked and exercised with a fake runner for orchestration, **not executed against a live provider**. The underlying SDK may retry transient requests according to its own settings; do not infer request-count guarantees from max_turns. No secrets are printed by this script, and tracing is disabled.

Official API references checked 2026-11-12: [SDK overview](https://developers.openai.com/api/docs/guides/agents/sdk), [quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart?lang=python), [agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents). Version ranges are compatibility constraints, not a verified frozen deployment lock; resolve/pin in your environment and rerun tests before live use.

## Validation limits

Fixture tests and fake transports check local orchestration, contracts and failure
handling; they do not certify model quality, actual Brave results, browser behavior,
SMTP delivery or deployment. Optional Gradio tests skip when Gradio is absent. Treat
imports, a committed lock and a ready health endpoint as separate from real research
or a successful browser download, and record only outcomes you actually observe.
