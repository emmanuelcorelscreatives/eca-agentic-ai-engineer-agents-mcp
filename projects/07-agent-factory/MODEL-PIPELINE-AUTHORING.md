# Stage 25: typed catalog and model-pipeline guide

Start with the [README path table](README.md#stage-25-choose-the-right-path) and [offline catalog solution](SOLUTIONS.md#offline-catalog-worked-example). The stdlib text helper and catalog factory have different schemas. `factory.AgentSpec` accepts `examples/text_helper.json`; the advanced `TypedSpec` accepts [templates/catalog_research-spec.json](templates/catalog_research-spec.json). Do not pass the legacy word-count schema to `Pipeline.analyze`.

The local catalog example needs no optional packages or model account. It demonstrates fixed tools and tests, **not** generative requirements, architecture or code. Real specialist proposals are optional, potentially billable exercises with additional prerequisites below.

## Setup and offline checks

Use Python 3.12 in a Linux/supported POSIX environment for the advanced call ledger (`fcntl`). On Windows, use a suitable POSIX environment for this path; the baseline text helper does not require it. Start these commands from the repository root:

```sh
python3 -m venv .venv-factory
. .venv-factory/bin/activate
python -m pip install -r frameworks/requirements/autogen.txt
python -m pip check
cd projects/07-agent-factory
python -c "from model_schemas import RequirementsProposal; from autogen_agentchat.agents import AssistantAgent; print('Typed dependencies available')"
python -m unittest -v test_advanced.py
python -m unittest discover -s tests -v
```

Installation downloads packages; it does not authorize or make a model call. The existing manifest pins the direct AutoGen dependencies; record `python --version` and `python -m pip freeze` in your local exercise notes, not credentials. Resolving packages is not a verified SDK/model integration or a transitive release lock.

Expected offline checks: **14** advanced contract tests; **15** nested tests (8 Docker-boundary and 7 typed-pipeline checks). Without Pydantic, the latter seven skip: `OK (skipped=7)` means the typed path is **not verified**. Do not treat skips as success. These tests use fixed templates, offline backend fixtures and mocked/planned Docker operations; neither command requests a provider or runs Docker.

## Optional real requirements specialist

Only after explicitly approving an account, compatible model, spend limit and a single request, save the following as your own `requirements_example.py` in the project directory and run `python requirements_example.py`. Set `ACADEMY_FACTORY_MODEL` and your provider's required credential in the local environment without printing, committing or capturing the credential. This OpenAI-compatible client example is not a claim that every provider/model supports structured outputs.

```python
import asyncio
from importlib.metadata import version
import json
import os
from pathlib import Path
from advanced import TypedSpec
from autogen_ext.models.openai import OpenAIChatCompletionClient
from model_pipeline import AutoGenBackend, Pipeline

async def main():
    if input('Potentially billable: type CALL to authorize one requirements request: ') != 'CALL':
        return
    spec = TypedSpec.parse(json.loads(Path('templates/catalog_research-spec.json').read_text()))
    root = Path('student-work/model-requirements').resolve()
    root.parent.mkdir(exist_ok=True)
    root.mkdir()
    (root / 'spec.json').write_bytes(spec.encoded)
    model = os.environ['ACADEMY_FACTORY_MODEL']
    (root / 'runtime.json').write_text(json.dumps({
        'model': model, 'spec_sha256': spec.digest,
        'autogen-agentchat': version('autogen-agentchat'),
        'autogen-ext': version('autogen-ext'), 'pydantic': version('pydantic'),
    }, indent=2) + '\n')
    client = OpenAIChatCompletionClient(model=model, max_retries=0)
    try:
        pipeline = Pipeline(root, AutoGenBackend(client), max_calls=1, timeout=90)
        requirements = await pipeline.analyze(spec)
        print(requirements.model_dump_json(indent=2))
    finally:
        await client.close()

asyncio.run(main())
```

Expected shape, **not a supplied model answer**: `RequirementsProposal` binds `spec_sha256` to this exact spec and lists requirement IDs, source fields, measurable criteria and acceptance-test names. Inspect actual `requirements/raw-response.json` and `validated-proposal.json` in that workspace. Real output may be invalid, unresolved or fail; keep it honestly. A valid proposal still does not prove generated code or working tools.

Each proposal reserves its once key before submission and saves raw responses before validation. Failure, timeout or a missing receipt leaves UNKNOWN. Do not rerun by deleting the reservation, using a new key/directory, or enabling transport retries. Reconcile the original request and retained response first. The confirmation and one-call budget do not guarantee a dollar ceiling: confirm the actual model/account limits separately. Never execute proposed source on the host.

## Continue the exercise using the existing APIs

`model_schemas.py` defines closed Pydantic handoffs. `AutoGenBackend` uses structured AutoGen specialists without execution tools. The interfaces below are already supplied; the student must provide the application-specific acceptance and authorized execution/launch integration, not assume a turnkey deployment is included.

| Stage | Existing interface | What to inspect or supply |
| --- | --- | --- |
| Requirements | `Pipeline.analyze(spec)` | Actual typed proposal bound to the catalog spec |
| Architecture | `Pipeline.design(spec, requirements, approval)` | Human decision bound to the exact requirements; typed components and framework |
| Generation | `Pipeline.generate(spec, requirements, design, requirements_approval, architecture_approval)` | Five specialist passes; fresh files and graph; no implicit execution |
| Instructions (s25-l07) | `InstructionProposal` inside generation | **`instructions.json`**, with role, goals, allowed_tools, policies, refusal, escalation and untrusted_data; Markdown is optional |
| Review | `Pipeline.inspect(spec, requirements, files, diagnostics)` | Static diagnostics plus actual reviewer findings over exact source |
| Repair | `Pipeline.repair(...)` | Actual retained failure, explicit non-test scope and at most two patches; acceptance/tests remain unchanged |
| Validate/release | `run_factory(...)` | Caller-owned human decisions, independent acceptance, authorized sandbox and receipt verification |
| Launch | `launch_validated(files, release, central_launch=..., verify_launch_receipt=...)` | Separately implemented owned-container launch/cleanup and authenticated actual result |

The legacy [FRAMEWORKS.md](FRAMEWORKS.md) example uses a four-turn text-helper proposal team. It is not interchangeable with these catalog specialist calls. The [native Agno/Mastra scaffolds](adapters/frameworks.py) remain optional SDK source; they need real dependency locks and observed SDK/provider behavior before integration claims.

## Validation and launch extension contract

Before calling `run_factory`, provide a human-approved catalog spec (`advanced.approve`), an independently written nonempty `acceptance/test_*.py` suite and the following callbacks. These are exercise implementations; no placeholder callback should return a fabricated success.

- `approve_handoff(stage, proposal)` returns the real human decision: `artifact_sha256`, nonempty `reviewer`, `decision='approved'`, bound to that exact typed proposal. Do not auto-approve model prose.
- `sandbox_validate(workspace, prepared)` and `verify_sandbox_receipt(workspace, prepared, receipt)` may use the existing authorized `docker_bridge.CentralDockerOwner.validate` / `.verify` pair. Review the class setup: a separately reviewed **digest-pinned, locally available** image with locked dependencies, a private owner evidence directory and private same-user key disjoint from the generated workspace, and explicit Docker authorization. `docker_validate.plan` is inspection only; it does not execute.
- `approve_release(context)` returns an actual final human decision bound to `artifact_sha256`; generated tests do not replace independent acceptance. SHA identity alone does not authenticate a Docker receipt.
- Supply `allowed_repair_files` explicitly and a repair budget of 0–2. Preserve real failures and UNKNOWN outcomes; do not retry infrastructure failures as code repairs.

No arbitrary generated code is imported or executed on the host. Python isolated mode and a temporary directory are **not a security sandbox**. Docker validation requires its actual daemon/image and authorized resource/network policy; record a blocker if unavailable. Never bypass that requirement with a mocked receipt or the offline template runner.

A successful `run_factory` returns `release-gates-satisfied` with **`launch_performed: false`**. To complete s25-l15, implement and call the separate `launch_validated` boundary only after real validation. `central_launch(files, release)` must start only the validated exact artifact in the authorized containment environment and retain its real result and owned cleanup; `verify_launch_receipt(receipt, release)` must authenticate that result, not merely hash caller-provided JSON. The expected receipt includes `kind='docker-agent-launch'`, the exact `artifact_sha256` and `owned_cleanup_confirmed=true`. No ready-made launch callback is shipped. This integration remains a student extension, not an observed application output.

Keep model reasoning, local fixture contracts, actual container tests and observed launch results separate in the portfolio. A correct limitation/blocker is better than an invented completed run. Use the [workbook](../../curriculum/workbooks/stages-21-30.md) for the unchanged lesson topics; for s25-l07 use `instructions.json` as documented above.
