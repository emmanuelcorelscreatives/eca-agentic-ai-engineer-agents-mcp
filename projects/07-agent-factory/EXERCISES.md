# Exercises

1. Build the sample app and record the actual generated test count and CLI output.
2. Change the enabled tools to `['uppercase']`. Generate a new app. Verify `word_count` is rejected.
3. Put `../escape` in the name, add a `shell` tool, or select `autogen`. Explain and verify each refusal.
4. Change the purpose to contain a Python-looking string. Inspect `agent.py` and confirm the text remains documentation/data rather than executable code.
5. Deliberately break a generated test in an in-memory `render` result and call `validate_generated`. Confirm the factory reports actual failure rather than writing an approval receipt.
6. Explain the distinction between a temporary working directory and a security boundary. Run Docker only on an authorized host and retain the actual build/run output.
7. Design a framework adapter protocol with `render(spec)` and adapter-specific acceptance tests. Do not label an adapter operational until its dependencies, real execution and failure paths have been tested.
8. Repair one deliberately introduced deterministic tool defect, preserve the failed source and actual failure diagnostics, then generate a new successful receipt. The baseline does not write a validation receipt on failure. Keep the failed directory unchanged; follow [solution 8](SOLUTIONS.md#8-retain-a-tool-failure-and-repair-it).

For the additional typed catalog/model exercises, follow the [Stage 25 guide](MODEL-PIPELINE-AUTHORING.md) and the [offline catalog solution](SOLUTIONS.md#offline-catalog-worked-example). The catalog schema is different from the text-helper schema above. In s25-l07, submit the specialist's `instructions.json`; `instructions.md` belongs to the legacy baseline. Paid model calls and Docker execution are separate, explicitly opt-in exercises, not prerequisites for these offline examples.
