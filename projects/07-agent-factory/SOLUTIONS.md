# Solution guide

1. The sample app runs four generated tests: two enabled tools, forbidden tool and invalid input. The initial CLI output is `{"words": 2}`. Confirm these in your own receipt.
2. The generated `ALLOWED_TOOLS` tuple contains only `uppercase`; `run('word_count', 'hello')` raises `ValueError`.
3. Names use `[a-z][a-z0-9_]{2,39}`; tools use a closed allowlist; this baseline supports exactly the stdlib adapter. All three proposals fail before code execution.
4. Free text is serialized using JSON or written to Markdown. Executable code only receives the already validated tool-name tuple through a literal representation.
5. Generated tests run in a real subprocess. Nonzero return codes raise `ValueError` with actual stderr; no successful receipt is emitted.
6. A fresh directory prevents accidental file reuse but shares the host kernel, identity and network. Python `-I` controls imports; it is not arbitrary-code containment. The separate Docker runtime adds concrete process/network/filesystem controls and still requires host authorization.
7. Keep framework-specific rendering behind the typed specification. Include a real smoke execution for every declared adapter and reject unsupported frameworks. Never turn an optional dependency's absence into a fake success.
8. Correct the responsible fixed template, generate into a fresh path, execute every generated test and compare receipt file hashes. A changed receipt is evidence only of the tests actually run, not independent model review or universal correctness.
