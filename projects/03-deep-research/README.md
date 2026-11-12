# Project 3: Deep Research Intelligence Team

Curriculum: Stage 9, lessons 1–13, with Stage 10 application/evaluation follow-up. This deterministic reference performs bounded parallel retrieval over a **synthetic local corpus**, preserves citations, identifies conflicting claim values and renders a report. It performs no live search, model call or external factual verification.

```sh
python3 projects/03-deep-research/research.py
python3 projects/03-deep-research/research.py "galactic asteroid mineral royalties"
```

The first report must preserve both **45 minutes** and **70 minutes** as a conflict, noting source excerpts and scope. It must not average them into an invented result. The second should report insufficient evidence. Fixture `.txt` files are the corresponding invented practice source documents; JSON contains the normalized evidence records.

## Practical build sequence

1. Define the research question, deliverable and completion criteria. `plan` exposes a deterministic starting plan, not generated hidden reasoning.
2. Inspect the three query branches and `ThreadPoolExecutor(max_workers=3)`. Results are deduplicated by stable source identifier with deterministic final ordering.
3. Add a new local source and normalize title, location, published date, claim, value and excerpt.
4. Inspect claim/value groups. Different values remain explicit alternatives with citations. Shared values are supported by this corpus only, never declared universal truth.
5. Expand report sections and include missing evidence, source-date limitations and an assessment of comparability.
6. Optional separate live adapters may provide search/model reasoning and a Gradio UI. Pin the chosen actual search provider/SDK and framework versions; credentials remain in environment variables outside the repository. Preserve fetched source snapshots, access times, exact excerpts and per-query attribution. Untrusted web content must not control tools or override application instructions.
7. Add evaluation fixtures for contradictory, duplicated, irrelevant, stale and absent sources. A live adapter must pass the same citation/no-invention tests before deployment.

## Exercises and solutions

- **Conflict:** explain 45 versus 70. Solution: the first excludes validation, the second includes it. Keep both values and their conditions; the system does not establish that either source is wrong.
- **Missing evidence:** research an unrelated topic. Solution: `insufficient_evidence`, empty findings, no invented references.
- **Duplicate source IDs:** insert another record with an existing ID. Solution: fail loudly before parallel retrieval instead of silently overwriting evidence.
- **Concurrency:** compare max_workers 1 and 3. Solution: identical report output; concurrency changes scheduling, not attribution or conclusions.
- **Causal overreach:** ask whether automation caused improvement. Solution: the three-report fictional pilot has no controlled evidence of causality; record that gap rather than claim success.

The limited lexical search and exact claim-key grouping are deliberately visible baseline constraints. More intelligent planning and semantic evidence analysis must be evaluated explicitly when optional live agents are added.

## Implemented optional SDK adapter

`agents_adapter.py` implements actual `Agent`, `Runner.run`, typed Pydantic outputs and bounded turns. Install `requirements-optional.txt` in a separate virtual environment, then run `python3 agents_adapter.py --live` from this project directory after setting `OPENAI_API_KEY` and `ACADEMY_MODEL`. This makes paid requests. It was syntax-checked and exercised with a fake runner for orchestration, **not executed against a live provider**. The underlying SDK may retry transient requests according to its own settings; do not infer request-count guarantees from max_turns. No secrets are printed by this script, and tracing is disabled.

Official API references checked 2026-11-12: [SDK overview](https://developers.openai.com/api/docs/guides/agents/sdk), [quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart?lang=python), [agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents). Version ranges are compatibility constraints, not a verified frozen deployment lock; resolve/pin in your environment and rerun tests before live use.

## Actual local runtime validation (2026-11-12)

A finite resource-governed validation environment installed OpenAI Agents SDK 0.24.0, Pydantic 2.14.3, Gradio 6.31.0 and pypdf 6.21.4. Actual SDK agent configurations and both twin/sales Gradio interfaces built successfully; pypdf extracted the synthetic resume. This proves imports/configuration and text extraction, not live model behavior or browser interaction. No model requests or UI servers were started. Reproduce in an isolated environment; retain version resolution and rerun the tests before deployment.
