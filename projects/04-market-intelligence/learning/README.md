# Academy market debate: stages 11–12

This isolated teaching package supplements the market screener. Its retailer and every metric are fictional. The offline command validates configuration and searches the fixed pack; it never creates fake model arguments.

```sh
cd projects/04-market-intelligence/learning
PYTHONPATH=src python3 -m academy_market_debate.main --facts fixtures/retailer-facts.json
```

Use `docs/s11-l03.md` for uv setup and `docs/s11-l09.md` for explicitly paid provider execution. The committed `uv.lock` was actually resolved and checked with uv 0.13.8, then installed successfully into a new isolated environment using `uv sync --frozen --extra crewai`. Observed versions: Python 3.12.3, CrewAI 1.15.40 and Pydantic 2.12.5. All 20 lesson docs have exercises and worked reasoning. Offline tests live at repository `tests/test_market_learning.py`.

## Boundaries

The six-call shared fact tool budget is enforced in Python; iteration and timeout settings are additionally configured on agents. They are not a hard total provider cost ceiling. The production governor must separately authorize live use. `memory=False` prevents implicit default vector-memory provider calls; explicit task context is still passed. The optional memory demonstration requires its own explicit embedder/model authorization. Actual network-denied SDK construction passed for sequential/hierarchical crews, custom tools and Pydantic output. The real Flow event engine passed with an explicitly substituted deterministic worker; this is scheduling evidence, not provider output. A genuine disposable starter was generated with `crewai create crew academy_practice --skip-provider --classic` under network isolation; its actual file inventory was retained separately. Live provider debate and real memory backend remain unexecuted pending separate evidence.

## Official references verified 2026-11-12

- https://docs.crewai.com/v1.15.40/en/concepts/flows
- https://docs.crewai.com/v1.15.40/en/concepts/tasks
- https://docs.crewai.com/v1.15.40/en/concepts/tools
- https://docs.crewai.com/v1.15.40/en/concepts/crews
- https://docs.crewai.com/v1.15.40/en/concepts/memory

These references support the APIs, not an assertion that this environment has run the SDK.
