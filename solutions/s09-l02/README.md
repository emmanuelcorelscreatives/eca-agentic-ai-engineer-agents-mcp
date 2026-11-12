# Reference solution: s09-l02

A reference responsibility matrix assigns each task one owner and gives source review authority to reject unsupported findings without overwriting evidence.

Implementation: projects/03-deep-research/research_lab/planning.py.

The supplied run produces a real offline report with unresolved cost conflict, exact source excerpts and unknown dates; it does not assert a winner. Inspect exported research.json and sha256.json. For a negative case, use an empty FixtureSearch corpus; quality.decision must be insufficient_evidence. The test suite covers invalid dependencies, invented citations, request-mismatched recovery and unknown-outcome non-retry.

Optional UI/browser, live search, actual provider tokens, real email and hosted deployment observations require separate execution and are not claimed by these offline fixtures.
