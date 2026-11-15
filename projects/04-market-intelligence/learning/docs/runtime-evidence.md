# Reproducible runtime evidence

Run deterministic tests from repository root:

```sh
python3 -m unittest discover -s tests -p test_market_learning.py -v
python3 -m unittest discover -s tests -p test_market_learning_semantic.py -v
```

`test_market_learning.py` imports no SDK. It exercises fixture parsing, shared tool budgeting, context isolation/reset, citation validation and the real offline CLI without mocked model responses. `test_market_learning_semantic.py` checks external-source validation with deterministic transport doubles and authorization failures without making HTTP/provider calls. Its optional SDK checks skip when CrewAI is absent; a skip is not a pass of that integration. Transport doubles are not internet observations.

## Historical observations and remaining limits

The original isolated installation used uv 0.13.8, Python 3.12.3, CrewAI 1.15.40 and Pydantic 2.12.5. Network-denied SDK construction was checked for sequential/hierarchical crews, custom tools and Pydantic output. A Flow scheduling check used a substituted deterministic worker, not a model debate. A disposable `academy_practice` starter was generated with `crewai create crew academy_practice --skip-provider --classic`; its [file inventory](../fixtures/actual-cli-starter-inventory.json) records generation, not kickoff. These historical observations do not certify changed code or your environment. Use the [setup guide](s11-l03.md) to record your own versions.

A live run must save actual returned task outputs under a new output path, actual versions/model and your explicit provider budget. No live model execution, backend memory retrieval or subjective quality score can be inferred from constructor success. No live debate or memory-backend success is supplied here. Never replay an unknown provider outcome simply to fill missing evidence.
