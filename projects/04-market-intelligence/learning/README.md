# Academy market debate: stages 11–12

This isolated teaching package supplements the market screener. Its retailer and every metric are fictional. The offline command validates configuration and searches the fixed pack; it never creates fake model arguments.

```sh
cd projects/04-market-intelligence/learning
PYTHONPATH=src python3 -m academy_market_debate.main --facts fixtures/retailer-facts.json
```

Use [uv setup](docs/s11-l03.md) and the [entry point guide](docs/s11-l09.md) for optional paid provider execution in the dedicated environment. The offline command above needs no SDK or credentials. Shell examples use POSIX syntax; in PowerShell set `$env:PYTHONPATH = "src"` before running the Python command. See [runtime checks and limitations](docs/runtime-evidence.md) for test commands and historical version observations.

## Stage 11

| Lesson | Guide | Exercise | Worked reasoning |
| --- | --- | --- | --- |
| 01: Framework fit | [Guide](docs/s11-l01.md) | [Exercise](exercises/s11-l01.md) | [Solution](solutions/s11-l01.md) |
| 02: Abstractions | [Guide](docs/s11-l02.md) | [Exercise](exercises/s11-l02.md) | [Solution](solutions/s11-l02.md) |
| 03: Install with uv | [Guide](docs/s11-l03.md) | [Exercise](exercises/s11-l03.md) | [Solution](solutions/s11-l03.md) |
| 04: Generate a starter | [Guide](docs/s11-l04.md) | [Exercise](exercises/s11-l04.md) | [Solution](solutions/s11-l04.md) |
| 05: Project structure | [Guide](docs/s11-l05.md) | [Exercise](exercises/s11-l05.md) | [Solution](solutions/s11-l05.md) |
| 06: YAML configuration | [Guide](docs/s11-l06.md) | [Exercise](exercises/s11-l06.md) | [Solution](solutions/s11-l06.md) |
| 07: Python crew configuration | [Guide](docs/s11-l07.md) | [Exercise](exercises/s11-l07.md) | [Solution](solutions/s11-l07.md) |
| 08: Debate crew | [Guide](docs/s11-l08.md) | [Exercise](exercises/s11-l08.md) | [Solution](solutions/s11-l08.md) |
| 09: Entry point | [Guide](docs/s11-l09.md) | [Exercise](exercises/s11-l09.md) | [Solution](solutions/s11-l09.md) |
| 10: Run and inspect | [Guide](docs/s11-l10.md) | [Exercise](exercises/s11-l10.md) | [Solution](solutions/s11-l10.md) |

## Stage 12

| Lesson | Guide | Exercise | Worked reasoning |
| --- | --- | --- | --- |
| 01: Five-step design | [Guide](docs/s12-l01.md) | [Exercise](exercises/s12-l01.md) | [Solution](solutions/s12-l01.md) |
| 02: Roles and goals | [Guide](docs/s12-l02.md) | [Exercise](exercises/s12-l02.md) | [Solution](solutions/s12-l02.md) |
| 03: Measurable outputs | [Guide](docs/s12-l03.md) | [Exercise](exercises/s12-l03.md) | [Solution](solutions/s12-l03.md) |
| 04: Task context | [Guide](docs/s12-l04.md) | [Exercise](exercises/s12-l04.md) | [Solution](solutions/s12-l04.md) |
| 05: External research | [Guide](docs/s12-l05.md) | [Exercise](exercises/s12-l05.md) | [Solution](solutions/s12-l05.md) |
| 06: Custom tools | [Guide](docs/s12-l06.md) | [Exercise](exercises/s12-l06.md) | [Solution](solutions/s12-l06.md) |
| 07: Input/result validation | [Guide](docs/s12-l07.md) | [Exercise](exercises/s12-l07.md) | [Solution](solutions/s12-l07.md) |
| 08: Pydantic outputs | [Guide](docs/s12-l08.md) | [Exercise](exercises/s12-l08.md) | [Solution](solutions/s12-l08.md) |
| 09: Execution processes | [Guide](docs/s12-l09.md) | [Exercise](exercises/s12-l09.md) | [Solution](solutions/s12-l09.md) |
| 10: Memory and shared context | [Guide](docs/s12-l10.md) | [Exercise](exercises/s12-l10.md) | [Solution](solutions/s12-l10.md) |

Then continue to the [stage 13 screener](../README.md) and [advanced handbook](../advanced/HANDBOOK.md). The workbook's live-execution acceptance criteria are separate from these offline exercises: a manual argument or configuration check is not a completed model debate.

## Boundaries

The six-call shared fact tool budget is enforced in Python; iteration and timeout settings are additionally configured on agents. They are not a hard total provider cost ceiling. Use only authorized accounts and choose a finite provider budget before opting in. `memory=False` prevents implicit default vector-memory provider calls; explicit task context is still passed. The optional memory demonstration requires its own explicit embedder/model authorization. No live provider debate or real memory backend result is supplied; record actual outputs or failures from your own optional run rather than assuming success.

## Official references verified 2026-11-12

- https://docs.crewai.com/v1.15.40/en/concepts/flows
- https://docs.crewai.com/v1.15.40/en/concepts/tasks
- https://docs.crewai.com/v1.15.40/en/concepts/tools
- https://docs.crewai.com/v1.15.40/en/concepts/crews
- https://docs.crewai.com/v1.15.40/en/concepts/memory

These references support the APIs, not an assertion that this environment has run the SDK.

## Optional extensions and their limits

[External research](docs/s12-l05.md) uses bounded official-document HTTPS retrieval with typed queries, source normalization and a separate researcher/reviewer CrewAI adapter. It is not research about the fictional retailer. [Memory integration](docs/s12-l10.md) adds an opt-in scoped framework-memory variant while retaining the default memory-disabled debate. These optional integrations need their own runtime verification; historical installation or constructor checks do not establish that retrieval, provider execution or memory recall/reset succeeded. Keep absent, failed and unknown outcomes explicit. See the [application boundaries](docs/stages11-12-coherence.md).
