# Exercises

1. Build the sample app and record the actual generated test count and CLI output.
2. Change the enabled tools to `['uppercase']`. Generate a new app. Verify `word_count` is rejected.
3. Put `../escape` in the name, add a `shell` tool, or select `autogen`. Explain and verify each refusal.
4. Change the purpose to contain a Python-looking string. Inspect `agent.py` and confirm the text remains documentation/data rather than executable code.
5. Deliberately break a generated test in an in-memory `render` result and call `validate_generated`. Confirm the factory reports actual failure rather than writing an approval receipt.
6. Explain the distinction between a temporary working directory and a security boundary. Run Docker only on an authorized host and retain the actual build/run output.
7. Design a framework adapter protocol with `render(spec)` and adapter-specific acceptance tests. Do not label an adapter operational until its dependencies, real execution and failure paths have been tested.
8. Repair one deliberately introduced deterministic tool defect, preserve the failed receipt and generate a new successful receipt. Keep the original directory unchanged.
