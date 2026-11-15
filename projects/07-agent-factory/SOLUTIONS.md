# Solution guide

1. The sample app runs four generated tests: two enabled tools, forbidden tool and invalid input. The initial CLI output is `{"words": 2}`. Confirm these in your own receipt.
2. The generated `ALLOWED_TOOLS` tuple contains only `uppercase`; `run('word_count', 'hello')` raises `ValueError`.
3. Names use `[a-z][a-z0-9_]{2,39}`; tools use a closed allowlist; this baseline supports exactly the stdlib adapter. All three proposals fail before code execution.
4. Free text is serialized using JSON or written to Markdown. Executable code only receives the already validated tool-name tuple through a literal representation.
5. Generated tests run in a real subprocess. Nonzero return codes raise `ValueError` with actual stderr; no successful receipt is emitted.
6. A fresh directory prevents accidental file reuse but shares the host kernel, identity and network. Python `-I` controls imports; it is not arbitrary-code containment. The separate Docker runtime adds concrete process/network/filesystem controls and still requires host authorization.
7. Keep framework-specific rendering behind the typed specification. Include a real smoke execution for every declared adapter and reject unsupported frameworks. Never turn an optional dependency's absence into a fake success.
8. Correct the responsible fixed template, generate into a fresh path, execute every generated test and compare receipt file hashes. A changed receipt is evidence only of the tests actually run, not independent model review or universal correctness.

## Offline catalog worked example

From `projects/07-agent-factory`, run this Python example with Python 3.12 on a supported POSIX environment. It requires only the standard library. Use a new destination if you already ran it; existing output is never overwritten.

```python
import json
from pathlib import Path
import subprocess
import sys
from advanced import TypedSpec, approve, render_trusted, test_trusted_template, write_workspace

spec = TypedSpec.parse(json.loads(Path('templates/catalog_research-spec.json').read_text()))
approval = approve(spec, 'learner-human')
files = render_trusted(spec, approval)
result = test_trusted_template(spec, approval, files)
if not result['passed']:
    raise RuntimeError(result['stderr'])
destination = Path('student-work/catalog-example')
destination.parent.mkdir(exist_ok=True)
write_workspace(destination, files)
(destination / 'validation-receipt.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['stderr'])
subprocess.run(
    [sys.executable, '-B', 'agent.py'], cwd=destination,
    input=json.dumps({'tool': 'catalog_lookup', 'arguments': {'query': 'Engineering'}}),
    text=True, check=True,
)
```

Expected: **five** generated tests pass, followed by `{"matches": [{"id": "A001", "title": "Agent Engineering", "category": "AI"}]}`. Inspect `catalog.json` and the receipt in the new directory. `draft_notification` returns `delivered: false`; it does not send a message. This is a fixed local tool scaffold, not a model-generated research answer or a live framework run. The host validator accepts only byte-identical maintained catalog templates; do not pass arbitrary generated or edited source to it.

## 8. Retain a tool failure and repair it

From the project directory, run this Python example. It deliberately changes one known constant expression in the maintained text-helper template, retains the exact failed files and actual diagnostic, and restores the maintained template in a **different** directory. No on-disk repository template is edited. This narrow teaching mutation is not a runner for user-supplied or model-generated code.

```python
import difflib
import json
from pathlib import Path
from factory import AgentSpec, build, render, validate_generated

spec = AgentSpec.from_json(json.loads(Path('examples/text_helper.json').read_text()))
original = render(spec)
broken = dict(original)
needle = 'return {"words": len(text.split())}'
if original['agent.py'].count(needle) != 1:
    raise RuntimeError('The teaching template changed; inspect it before choosing a mutation')
broken['agent.py'] = original['agent.py'].replace(needle, 'return {"words": 0}')
root = Path('student-work/repair-example')
root.parent.mkdir(exist_ok=True)
root.mkdir()
failed = root / 'failed'
failed.mkdir()
for name, content in broken.items():
    (failed / name).write_text(content)
try:
    validate_generated(broken)
except ValueError as error:
    failure = {'status': 'failed', 'error_type': type(error).__name__, 'diagnostic': str(error)}
    (failed / 'failure-diagnostics.json').write_text(json.dumps(failure, indent=2) + '\n')
    print(failure['diagnostic'])
else:
    raise RuntimeError('The deliberate defect unexpectedly passed; no repair result is claimed')
receipt = build(spec, root / 'repaired')
diff = ''.join(difflib.unified_diff(
    broken['agent.py'].splitlines(keepends=True),
    original['agent.py'].splitlines(keepends=True),
    fromfile='failed/agent.py', tofile='repaired/agent.py',
))
(root / 'repair.diff').write_text(diff)
print(receipt['stderr'])
```

Expected first: the real `test_word_count` assertion fails (`0` versus `2`). Expected second: all **four** generated tests pass. `failed/failure-diagnostics.json` is explicitly an error record, not a success receipt; `repaired/validation-receipt.json` records the real successful tests and hashes. Compare `repair.diff`, both source files and the successful receipt. The failed directory remains unchanged after capture. Repeating the block refuses the existing destination; choose a new directory, not deletion or overwriting of the retained evidence.

The first attempt models the deliberate defect from exercises 5/8, not provider reasoning or arbitrary-code safety. Real model-generated or repaired code belongs in the separately authorized containment path described in the [typed pipeline guide](MODEL-PIPELINE-AUTHORING.md).
