# Stages 02–04: environment, agent patterns and model boundaries

Run from the repository root with Python 3.11 or newer:

```sh
python3 examples/stages02-04/foundations.py
python3 -m unittest discover -s tests -p test_stages_02_04.py -v
```

Windows: use `py -3` in place of `python3` when appropriate. The demo and tests require only the standard library. All displayed model text, shop inventory and model comparisons are **synthetic fixtures**, never observations of a live model.

`foundations.py` contains inspectable building blocks; each lab identifies its function and exact exercises. `sdk_adapter.py` is a lazy optional OpenAI SDK adapter; `CompatibleModel` uses a concrete Chat Completions HTTP request and `OllamaModel` calls the actual local `/api/chat` endpoint. Each implements `chat(messages, tools=None)` so the same tool loop can use fixtures or an explicitly configured model. Tools are application executed: the model requests a call and the application validates the allowlisted function and arguments before returning its result.

For a real hosted run, obtain access independently, choose an available model, set a private `MODEL_API_KEY` environment variable, configure the intended endpoint, and explicitly use `allow_live=True`. `base_url`/endpoint should include `/v1` for typical compatible servers; no guarantee is made that a server supports every parameter. SDK optional installation: `python3 -m pip install openai` inside your isolated environment; this is not a pinned reproducibility claim. Do not use real customer data. Our adapter sets `max_retries=0`; a timeout may have completed remotely and must not trigger a blind paid replay. Local request/token limits are not provider billing caps.

For Ollama, install the real application from https://ollama.com, run `ollama pull YOUR_CHOSEN_MODEL`, verify with `ollama list`, then use `OllamaModel('YOUR_CHOSEN_MODEL', allow_live=True)`. Model downloads, local inference and hardware suitability were not tested in this material-authoring run. Ollama tool support varies by model. The native adapter's tool-call identity shape differs from OpenAI: use ordinary text calls with it until you add and test a dedicated tool-call normalization boundary; do not claim the OpenAI loop works unchanged with native Ollama tool payloads.

No `.env` is loaded automatically. Prefer process environment variables; if using an optional dotenv loader, keep `.env` ignored and invoke loading only at the application entrypoint. Do not paste credentials into notebooks, screenshots, exception logs or tracked files. `.env.example` is a placeholder-only local example under `data/s02/` and must be copied selectively, not populated in the public repository.

## Capture and evidence requirements

Windows, macOS, Cursor/VS Code, GitHub account operations, model dashboards, Ollama and live hosted model calls require actual learner/app execution. These authored labs are not proof those actions happened. Use genuine application windows for tutorials; neutral architecture diagrams are fine for concepts. No imitation vendor UI, decorative desktop props or baked subtitles. Retain redacted command versions, model identifier, timestamps, usage when supplied and observed errors. Never record Authorization headers. Complete the actual platform track available to you; the other platform remains an alternative exercise, not a fabricated capture.

## Reference contracts checked 2026-11-12

- Chat Completions: https://developers.openai.com/api/reference/resources/chat
- Ollama native chat: https://docs.ollama.com/api/chat
- OpenAI Python SDK: https://github.com/openai/openai-python

Hosted vs local comparisons and the framework landscape are decision exercises, not universal product rankings. Use current official documentation for installation and live provider pricing. Frameworks organize programs; model providers perform inference; MCP exposes tool/data protocols; tracing observes execution. None replaces permission boundaries, validation or human approval for consequential writes.
