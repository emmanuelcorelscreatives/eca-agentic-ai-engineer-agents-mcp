# Stage 19: Browser Automation and Deep Agents

The original browser primitives remain in `examples/s19/browser_research.py`. The connected native harness is `examples/s19/native_harness.py`. It combines actual Playwright read tools with native Deep Agents planning, filesystem tools, skills, specialist task delegation and SQLite checkpoint continuation.

This is an owned, invented Academy documentation website. Searching its index is not an internet search. No personal browser profile is opened and browser routes allow GET requests only. The dedicated virtual filesystem is a path boundary; run it in a centrally provisioned sandbox for process isolation.

## Central QA commands

These commands are authored for the central QA owner. No successful execution is implied by their presence.

```sh
python -m unittest discover -s tests -p test_s19_native_harness.py -v
RUN_S19_NATIVE_SDK=1 python -m unittest discover -s tests -p test_s19_native_harness.py -v
```

The second command uses a scripted model through the actual SDK and Chromium, and starts two separate processes with the same SQLite checkpointer. This tests orchestration contracts, not provider intelligence. A native skill body sentinel fails the scripted run if unrelated calendar instructions appear in model input. Source mutation, workspace mutation, request failure and durable call budgets are negative cases.

## Genuine configured-model exercise

Central QA must separately authorize provider requests, configure credentials outside the repository and install the pinned course environment (Deep Agents 0.7.36, Playwright/Chromium, LangChain OpenAI and langgraph-checkpoint-sqlite). Choose a fresh dedicated workspace and an explicitly permitted model:

```sh
python -m examples.s19.native_harness --workspace /tmp/academy-s19-unique --model YOUR_PERMITTED_MODEL --phase start
# Let the first process exit. Inspect the real checkpoint, notes, report and evidence.
python -m examples.s19.native_harness --workspace /tmp/academy-s19-unique --model YOUR_PERMITTED_MODEL --phase resume
```

`start` should return an actual HITL interruption. `resume` approves continuation of that exact pending tool, not correctness of its answer. The SQLite graph state is not copied into a new workflow. Model, source bytes, thread, budget and output artifact hashes must match. Any mismatch blocks continuation and requires an explicit new run; no silent reset, retry or result reuse occurs. The new fixture server can have a different port after restart; retained evidence keeps the original observed URL and SHA.

The default durable browser budget is 12 total calls, including failures and unknown outcomes; it persists across both processes. Agent model limits are parent 14, researcher 6 and critic 4 per invocation, plus a 60-step graph recursion bound. Those limits are not a universal money cap. No provider transport retry is enabled. The deterministic evaluator reports individual contract facts and gaps; it neither repairs missing evidence nor approves content automatically.

Keep raw terminal output, environment versions, process IDs, source/artifact hashes, SQLite database, evidence ledger and actual captures. A provider refusal, missing tool, incomplete report or exhausted budget is a failed/held exercise, never a synthetic positive.

## Official references

- https://docs.langchain.com/oss/python/deepagents/skills
- https://docs.langchain.com/oss/python/deepagents/subagents
- https://docs.langchain.com/oss/python/deepagents/backends
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/deepagents/human-in-the-loop

These materials are implementation input, not production or render approval. Independent central QA must inspect actual evidence before footage is recorded.
