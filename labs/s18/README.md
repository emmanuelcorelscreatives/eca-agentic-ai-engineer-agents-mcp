# Stage 18 practicals

These lesson handouts map the original stage plan to actual executable code. Read each lesson recording gate before writing observed-result narration.

Offline suite:

```sh
python -m unittest discover -s tests -p test_stages16_19.py -v
```

The 18 standard-library tests exercise real local behavior, including SQLite process restart and local HTTP serving. Four opt-in SDK tests require installed compatible packages:

```sh
COURSE_SDK_OFFLINE=1 python -m unittest discover -s tests -p test_stages16_19.py -v
```

Those tests use a clearly labeled deterministic fixture chat model, never a live model. Real provider observations, LangSmith traces, MCP/browser runs and PostgreSQL runtime each require their own retained evidence.

## Retained actual SDK proof

The shared isolated runtime actually passed all 22 tests: 18 local standard-library behavior tests and four genuine SDK integration tests (LangChain agent/tool/middleware, LangGraph routes/history, SqliteSaver interrupt/reopen/resume/fork, DeepAgent construction). The test chat model is explicitly deterministic and makes no provider calls. Tested pins are in `examples/s16/requirements-tested.txt`.

Provider observations, LangSmith, PostgreSQL, MCP end-to-end and Stage19 browser-specific runtime are separate outstanding gates. See the full material mapping for exact scope.
