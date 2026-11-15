# Browser and integrated Sidekick labs

Use Python 3.11+. These shell blocks use Linux/macOS syntax. On Windows use a writable local exercise directory, `python` when that is your Python 3 command, and `.venv-browser\Scripts\Activate.ps1` instead of the activation command. Run multiline Python examples from a disposable `.py` file when your shell does not support heredocs. Never commit databases, session secrets, virtual environments or browser profiles.

## Optional environment

Start at the repository root. This environment is separate from other course frameworks:

```sh
cd projects/06-browser-sidekick
python3 -m venv .venv-browser
. .venv-browser/bin/activate
python3 -m pip install -r requirements-optional.txt
python3 -m playwright install chromium
mkdir -p .course-state
```

The requirement files supply the course SDK pins, not a guarantee that installation works on every platform. If Chromium reports missing OS libraries, use an already supported local environment or the platform's documented browser prerequisites; do not automatically change a managed host. No provider key is needed for the foundation, MCP read lab or integrated fixture. Installing dependencies and running browser exercises are optional; the standard-library demo needs neither.

## Browser foundation

In terminal A, from `projects/06-browser-sidekick`:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory fixtures
```

In terminal B, change to the **same project directory**, activate `.venv-browser`, then run:

```sh
python3 - <<'PY'
from sidekick import PlaywrightBrowser, Step
browser = PlaywrightBrowser('http://127.0.0.1:8765')
print(browser.execute(Step('extract', 'workshops.html', criterion='workshop dates and prices')))
print(browser.requests)
PY
```

Expected page values: Agent Foundations / 2030-04-12 / USD 30 and Browser Tools / 2030-04-19 / USD 45. The adapter creates and closes an actual Chromium browser; it cannot submit forms. Its request log contains only method, origin and allow/abort outcome. Stop only your terminal A fixture server when finished. This does not exercise the integrated UI, model planning or MCP.

For a Stage 19 documentation-page screenshot, activate the environment and return to the repository root (`cd ../..` from the project directory):

```sh
python3 -m examples.s19.browser_research --browser-screenshot projects/06-browser-sidekick/.course-state/documentation.png
```

This command starts and closes its own loopback fixture. Inspect the actual saved PNG and printed records. These are synthetic Academy documentation records, not workshop bookings or external web search. The shared `test_stages16_19.py` command checks infrastructure; it is not a replacement for this browser exercise.

## Integrated fixture workspace

From the project directory with `.venv-browser` activated:

```sh
python3 ui_gradio.py --database .course-state/tasks.sqlite --workspace-root .course-state/workspaces --port 7860
```

Open `http://127.0.0.1:7860` yourself. Expected mode: **deterministic-fixture**. It plans a fixed local workflow, but browser observations are obtained through real Chromium. The catalogue here contains Python $40 and SQL $35, not the foundation catalogue.

1. Before creating a task, expand **Restore a previously owned lab session**, enter your own private secret of at least 32 characters and click **Use this private session**. Retain it privately; it is the ownership handle for restart exercises.
2. Keep the supplied synthetic objective and click **Plan new task**. Inspect the task ID, proposed action and checklist. In fixture mode, changing the objective does not make this fixed planner understand arbitrary tasks.
3. Click **Advance one bounded browser/tool step**. Inspect the genuine browser view and source observations. Advance again to reach a held synthetic draft submission; confirm there has been no submission before exact approval.
4. Inspect the exact proposal. **Save edited proposal (not approval)** invalidates prior approval; **Reject** cancels without an effect. For the successful reference path, use the unchanged synthetic proposal and **Approve exact displayed action**, then advance. Review and separately approve the report save when it becomes pending.
5. Inspect final evaluation and the owned artifact link. Completion concerns the plan's observed predicates, not arbitrary semantic truth of the objective. Do not claim a model wrote the fixed fixture report.
6. Stop only your UI process. Restart with exactly the same command, restore the same private session and select the saved task. The persisted sandbox uses its original port and receipts. Pending read/approval steps can continue; expired approvals fail closed and are not automatically renewed. Inspect that failure rather than modifying saved state to bypass expiry. Completed steps and `executing` unknown outcomes must not be replayed.

If startup reports an occupied saved port, investigate your own other fixture instance; do not pick a different port for the existing task or stop unrelated services. Older task databases lacking sandbox identity are inspection-only for this purpose: preserve them and use a fresh database for new tasks. Losing the private recovery secret does not grant permission to reset ownership. A closed process releases its port, but an interrupted unknown action still requires investigation.

### Optional configured-model planning

Only after choosing your own provider/model, external credential setup and a small budget, replace the UI command with:

```sh
python3 ui_gradio.py --database .course-state/native-tasks.sqlite --workspace-root .course-state/native-workspaces --model provider:model --port 7860
```

Replace `provider:model` with an actually configured supported model; it is a placeholder, not a supplied free account. Requests may incur costs. No retry or fixture fallback follows a native error. A timeout/unknown planning outcome must be reconciled rather than resubmitted. Specialists cannot grant action approval. This guide does not claim that provider responses or UI interactions have been executed successfully.

## Browser through MCP

Use a separate environment for this read-only protocol exercise. From the project directory:

```sh
python3 -m venv .venv-mcp
. .venv-mcp/bin/activate
python3 -m pip install -r requirements-browser-mcp.txt
python3 -m playwright install chromium
cd ../..
```

Run the following from the repository root. The client owns its fixture origin and stdio server lifecycle; it requires no separately running server on port 8765 and opens no personal browser profile:

```sh
python3 - <<'PY'
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from examples.s19.browser_research import fixture_server

async def inspect(origin):
    parameters = StdioServerParameters(command=sys.executable, args=[
        '-m', 'examples.s19.browser_research', '--mcp', '--origin', origin])
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([tool.name for tool in tools.tools])
            result = await session.call_tool('inspect_page', {'path': '/docs.html'})
            if result.isError:
                raise RuntimeError('MCP fixture read failed; inspect the actual error locally')
            print(result.content)

with fixture_server() as origin:
    asyncio.run(inspect(origin))
PY
```

Expected discovery includes `inspect_page`; a successful call returns the observed local documentation view and records. Do not invent an example successful reply if dependencies, browser launch or protocol calls fail. Context managers close the client, child server and fixture. The MCP entrypoint delegates synchronous Playwright work to a worker outside the async event loop. Direct HTTP/Playwright reads and an MCP server construction are not this client discovery/call proof.

## Stage 16 native invoke/stream starting point

With `.venv-browser` activated and the current directory at the repository root, the provider-free SDK fixture tests are:

```sh
COURSE_SDK_OFFLINE=1 python3 -m unittest discover -s tests -p test_s16_native_features.py -v
```

They use a deterministic SDK model, not a provider. For the separate configured-provider exercise, configure credentials outside the repository and use an explicitly chosen model and budget. This example makes **two potentially paid requests** (invoke and stream); do not run it merely to check installation:

```python
from langchain.chat_models import init_chat_model
from examples.s16.native_features import invoke_and_stream

model = init_chat_model('provider:model', max_retries=0, timeout=30)
result = invoke_and_stream(model, 'Explain why a local fixture is not an external web search.')
print(result['invoked'].content)
print(result['streamed'].content)
```

Use real returned `AIMessage`/`AIMessageChunk` observations. Independent request text need not match. Preserve an interrupted or empty stream as failure rather than fabricating a complete response. See [framework examples](FRAMEWORKS.md) for the separate LangGraph checkpoint/approval integration.
