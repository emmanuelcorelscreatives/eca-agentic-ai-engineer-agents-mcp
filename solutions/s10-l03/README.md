# s10-l03: Stream Research Progress to the User

An async generator streams actual events, closes pending tasks on cancellation and does not expose hidden reasoning.

Current implementation, relative to `projects/03-deep-research/`:

- research_lab/interface_v2.py:stream_research
- research_lab/pipeline_v2.py

Central QA executed 23 scoped semantic regression tests with zero skips; this is neither a lesson-specific live observation nor independent material/visual/production approval. Historical v1 demo outputs remain historical.

Still required:

- genuine browser progress/cancel observations

See `projects/03-deep-research/docs/semantic-repair-stages09-10-v2.md` for the finite actual capstone and exact evidence boundaries. No author-made live call, browser run, SMTP send or deployment is claimed.
