# Reference solution: s10-l05

Provide a runnable reference solution and explanation for the named exercise; do not mark it tested until actual execution evidence is retained.

Implementation: projects/03-deep-research/research_lab/reporting.py.

The supplied run produces a real offline report with unresolved cost conflict, exact source excerpts and unknown dates; it does not assert a winner. Inspect exported research.json and sha256.json. For a negative case, use an empty FixtureSearch corpus; quality.decision must be insufficient_evidence. The test suite covers invalid dependencies, invented citations, request-mismatched recovery and unknown-outcome non-retry.

Optional UI/browser, live search, actual provider tokens, real email and hosted deployment observations require separate execution and are not claimed by these offline fixtures.
