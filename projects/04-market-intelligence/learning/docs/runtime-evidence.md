# Reproducible runtime evidence

Run deterministic tests from repository root:

```sh
python3 -m unittest discover -s tests -p test_market_learning.py -v
```

No SDK is imported by those tests. They exercise actual fixture parsing, shared tool budgeting, context isolation/reset, citation validation and the real offline CLI. The test suite does not use mocked model responses.

The separate maintained SDK local-check script, when run under its isolated runtime, constructs actual Agent/Task/Crew/Pydantic/tool objects with the network denied. Its Flow test executes real @start/@listen scheduling while substituting the debate worker; that is event-engine evidence, never a model debate observation. A placeholder key is used solely to satisfy constructor validation and is not a real credential.

A live run must save actual returned task outputs under a new output path, actual versions/model and the approved external quota. No live model execution, backend memory retrieval, generated starter or subjective quality score can be inferred from constructor success. Never replay an unknown provider outcome simply to fill missing evidence.
