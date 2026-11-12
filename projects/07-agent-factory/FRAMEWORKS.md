# Genuine AutoGen factory-agent adapter

The optional `autogen_adapter.py` creates four actual AutoGen `AssistantAgent` instances in a `RoundRobinGroupChat`: requirements analyst, architect, developer and reviewer. It uses the supplied model client and makes a bounded four-turn proposal pass. It does not execute proposed code, mistake prose for a test receipt, or promote a reviewer opinion into production approval.

Install `autogen-agentchat` and `autogen-ext[openai]` in a dedicated environment and record the exact installed versions. Configure a real supported model name through your environment. Example, deliberately opt-in and potentially billable:

```python
import asyncio
import json
import os
from pathlib import Path
from autogen_ext.models.openai import OpenAIChatCompletionClient
from factory import AgentSpec
from autogen_adapter import propose

async def main():
    spec = AgentSpec.from_json(json.loads(Path('examples/text_helper.json').read_text()))
    client = OpenAIChatCompletionClient(model=os.environ['ACADEMY_FACTORY_MODEL'])
    try:
        result = await propose(spec, client)
        Path('actual-agent-proposal.json').write_text(json.dumps(result, indent=2))
    finally:
        await client.close()

asyncio.run(main())
```

`OPENAI_API_KEY` belongs in the local environment, never committed or placed in screenshots. Configure a client compatible with your actual account/provider. No provider/model identity is fabricated by this adapter.

The deterministic factory remains the trusted fixed-template validation path. Arbitrary developer proposals need independent review and a separate genuine containment executor before testing. A temporary directory alone is insufficient for untrusted code. The generated project's Docker recipe demonstrates one bounded deployment path; no Docker run is claimed here.

Primary documentation checked 2026-11-12:

- [AutoGen team creation and model client](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
- [AutoGen human interaction and bounded team turns](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html)

No live model call or installed-SDK integration test was run in the baseline environment. This is executable adapter source with documented runtime prerequisites, not a claimed successful AutoGen experiment. Microsoft Agent Framework is taught separately and is not silently presented as the same package/API.
