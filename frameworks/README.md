# Optional framework recipes

These companions teach the framework-specific APIs used in the original course curriculum. The eight projects and lesson workbooks supply the larger applications. A small arithmetic recipe does **not** demonstrate all the advanced memory, MCP, team, persistence, evaluation or deployment objectives in its stage.

Official documentation and package registries were checked on **2026-11-12**. `registry-versions.json` records exact observed package versions and Python requirements; `catalog.json` maps each recipe to its original stages. These are documentation-aligned examples with **offline tests only**, not claims of a successful live SDK/provider integration. Provider account permissions, model availability and evolving SDK behavior still need the separately recorded practical run.

## Work in separate environments

Use Python **3.11 or 3.12**. Install one framework at a time, with a separate virtual environment. Do not install these dependencies in Studio or overwrite the core course environment. From the repository root, for example:

```sh
python3.11 -m venv .venv-openai-agents
. .venv-openai-agents/bin/activate
python -m pip install -r frameworks/requirements/openai-agents.txt
python -m pip freeze > openai-agents-local-lock.txt
```

On PowerShell, activate with `.venv-openai-agents\Scripts\Activate.ps1`. Exact top-level pins are supplied; transitive dependencies are resolved at installation time. Save the local lock and `python --version` with your lab evidence. These files are not a fully resolved cross-platform lock. Read current framework release/migration notes before upgrading. Do not mix old AutoGen 0.2 examples with the pinned AgentChat package. The present Pydantic AI and ADK major versions may differ from older tutorials.

Use an available provider model identifier in `COURSE_MODEL`; do not copy an unrelated deployment name or infer account access. Set credentials privately in your terminal. Do not commit keys, Azure CLI caches or `.env` files. API-backed recipes require `--run` before their imports or requests occur. A model call may incur charges; nothing was sent while preparing this kit. Tool functions only calculate local fixture values and do not place orders, send email or trade.

## Recipe commands and primary references

### OpenAI Agents SDK — stages 6, 7, 8, 9, 10

Agent, Runner, function tools and specialist handoff. API-backed execution not run.

Primary source: [OpenAI Agents SDK documentation](https://developers.openai.com/api/docs/guides/agents).

Install `frameworks/requirements/openai-agents.txt` in its own environment. 

```sh
python -m frameworks.openai_agents --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### CrewAI — stages 11, 12, 13, 14, 15

Sequential tasks, two agents and explicit context. Educational synthetic arithmetic, not live market analysis.

Primary source: [CrewAI documentation](https://docs.crewai.com/en/concepts/crews).

Install `frameworks/requirements/crewai.txt` in its own environment. 

```sh
python -m frameworks.crewai_crew --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### LangChain — stages 16, 18

Modern create_agent, not retired initialize_agent patterns.

Primary source: [LangChain documentation](https://docs.langchain.com/oss/python/langchain/quickstart).

Install `frameworks/requirements/langchain.txt` in its own environment. 

```sh
python -m frameworks.langchain_agent --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### LangGraph — stages 17, 18, 19, 20

Model-free graph, in-memory checkpoint, interrupt and fixture rejection. Persistence ends when the process exits.

Primary source: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/interrupts).

Install `frameworks/requirements/langgraph.txt` in its own environment. 

```sh
python -m frameworks.langgraph_state
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### Google ADK — stages 21

Factory for the root_agent CLI convention. ADK 2.x docs were checked; use isolated environments.

Primary source: [Google ADK documentation](https://adk.dev/get-started/python/).

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### AWS Strands — stages 22

Explicit Bedrock model and region. Local tool does not send orders. Requires actual AWS model access.

Primary source: [AWS Strands documentation](https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/).

Install `frameworks/requirements/strands.txt` in its own environment. 

```sh
python -m frameworks.strands_bedrock --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### Pydantic AI — stages 22

Typed dataclass dependencies and validated structured model output. Provider output is not pre-recorded here.

Primary source: [Pydantic AI documentation](https://pydantic.dev/docs/ai/core-concepts/dependencies/).

Install `frameworks/requirements/pydantic-ai.txt` in its own environment. 

```sh
python -m frameworks.pydantic_typed --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### AutoGen AgentChat — stages 23

AgentChat-era imports, distinct from older AutoGen 0.2. This does not assert all APIs migrate mechanically.

Primary source: [AutoGen AgentChat documentation](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html).

Install `frameworks/requirements/autogen.txt` in its own environment. 

```sh
python -m frameworks.autogen_agentchat --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### Microsoft Agent Framework — stages 23

FoundryChatClient plus explicit Azure CLI credential. Deployment name and project endpoint are user configuration.

Primary source: [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent).

Install `frameworks/requirements/microsoft.txt` in its own environment. 

```sh
python -m frameworks.microsoft_agent --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### Agno — stages 24

Explicit OpenAI model and local function tool. SDK and provider package installed separately in the isolated environment.

Primary source: [Agno documentation](https://docs.agno.com/agents/building-agents).

Install `frameworks/requirements/agno.txt` in its own environment. The isolated requirement file also pins the OpenAI provider client; save your resolved transitive lock. 

```sh
python -m frameworks.agno_agent --run
```

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### Mastra — stages 24

Typed createTool, integer cents and provider/model routing. Exact package pins are in its private package.json.

Primary source: [Mastra documentation](https://mastra.ai/docs/agents/overview).

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### n8n — stages 1

Importable manual-trigger/Code workflow. This foundation is deterministic; add an actual AI Agent node for the model-driven lesson.

Primary source: [n8n documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.code/).

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

### Ollama — stages 4

Fixed localhost endpoint, installed model tag, nonstreaming response. Requires a separately started local Ollama server.

Primary source: [Ollama documentation](https://docs.ollama.com/api/chat).

Evidence to retain: exact installed versions, command, input, actual response and any failure. Never label an expected response as an observed model result.

## Configuration by recipe

- OpenAI Agents, CrewAI, LangChain, Pydantic AI, AutoGen and Agno: `OPENAI_API_KEY` and `COURSE_MODEL`. AutoGen may need an explicit model capability declaration for an unknown custom model; consult its model-client documentation rather than pretending an unsupported model works.
- Strands: `AWS_REGION`, `BEDROCK_MODEL_ID` and separately configured AWS credentials, for example your authorized AWS profile. Verify Bedrock model entitlement. No credential is embedded.
- Microsoft Agent Framework: `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL` and an authorized `az login`. This recipe uses **AzureCliCredential**, matching the chosen explicit credential route; it does not probe arbitrary credential chains.
- ADK: `GOOGLE_MODEL` and `GOOGLE_API_KEY`, then create a throwaway ADK project with `adk create academy_order_agent`. In that generated project's `agent.py`, use `from frameworks.google_adk_agent import build_agent; root_agent = build_agent()`. Keep the repository root on `PYTHONPATH`, retain the generated `__init__.py`, and run `adk run academy_order_agent` or `adk web` from the project's parent directory. This is the real CLI route; the factory alone is not an observed agent run or A2A deployment.
- Ollama: install/start Ollama separately, pull an appropriate model, set `OLLAMA_MODEL` to that exact installed tag, then run `python -m frameworks.ollama_chat --run`. Its URL is fixed to `127.0.0.1:11434`; it does not expose your local server publicly.

## LangGraph checkpoint lab

After installing the isolated LangGraph requirements, run the graph without provider credentials. The `calculate` node creates `37.50` from `12.50 × 3`; `approval` interrupts with that actual computed value. The script resumes the same thread with a scripted **False**, so the disposition must be `rejected`. This is a deterministic test input, not evidence that a human approved anything. Try a new thread and manually choose a Boolean resume value. Inspect the stored state. Replace the in-memory saver with a supported durable saver only in the separate persistence lesson, documenting its schema and actual restart test.

## Mastra isolated TypeScript project

Use Node.js **22.13 or later** as required by the observed core package. From `frameworks/mastra`, run `npm install`, save the resulting lockfile, then `npm run check`. Set `OPENAI_API_KEY` and `COURSE_MODEL` before `npm run live`. The router uses `openai/<model>`; it is different from Pydantic AI's `openai:<model>` identifier. The tool's `execute` receives validated input directly. These npm install/typecheck/live commands were **not executed** while preparing this companion. Capture real output before using it as a tutorial result.

## n8n workflow lab

Import `n8n/order-workflow.json` into your own n8n workspace. It starts inactive and contains only a manual trigger and Code node; executing it should calculate `3750` cents from the visible fixture. No credentials, webhook, public URL or external write is configured. The preparation test actually evaluates this Code node with Node.js, but does not claim the workflow was imported into n8n.

For Stage 1 Lesson 2's **autonomous AI workflow**, use `examples/s01/first-workflow.n8n.json` and its accompanying practical instructions when available. To extend the arithmetic foundation separately in the real n8n editor: add an AI Agent node, connect a supported Chat Model with your own credentials, provide a fixture question and a read-only calculation tool, and execute it. Inspect the actual model/tool execution data and record the n8n version. The model chooses a tool; the arithmetic node alone does not. Keep any email/order action disconnected until the course's real human-approval step. The completed autonomous exercise requires that actual model execution; do not pass off the deterministic starter as its result.

## Further practical exercises

For every framework, use the same order fixture and compare tool arguments and returned total. Ask for an unknown price and confirm the agent does not invent a live quote. Test negative quantities against the local tool. Compare a single agent, explicit handoff and sequential workflow using the relevant complete project adapters. Add MCP only through the separately supplied course server and the framework's current official MCP integration; authenticate and constrain each external server rather than guessing transport behavior. Record real trace IDs only when produced by an actual run.
