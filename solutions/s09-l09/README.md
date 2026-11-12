# Reference solution: s09-l09

A reference solution reports actionable field paths, rejects extra unsupported assertions and validates cross-record references after structural validation.

Implementation: projects/03-deep-research/research_lab/planning.py, projects/03-deep-research/research_lab/evidence.py.

The supplied run produces a real offline report with unresolved cost conflict, exact source excerpts and unknown dates; it does not assert a winner. Inspect exported research.json and sha256.json. For a negative case, use an empty FixtureSearch corpus; quality.decision must be insufficient_evidence. The test suite covers invalid dependencies, invented citations, request-mismatched recovery and unknown-outcome non-retry.

Optional UI/browser, live search, actual provider tokens, real email and hosted deployment observations require separate execution and are not claimed by these offline fixtures.
