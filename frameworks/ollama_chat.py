"""Stage 4: direct localhost Ollama chat; explicit --run, no remote URL override."""
import json
from urllib.request import Request, urlopen
from frameworks.common import require_run

def request_body(model: str) -> dict:
    if not model or len(model) > 200 or any(c.isspace() for c in model):
        raise ValueError("a local installed model tag is required")
    return {"model": model, "stream": False, "messages": [{"role": "user", "content": "Explain tool calling in two sentences."}]}

def main():
    env = require_run("OLLAMA_MODEL")
    body = json.dumps(request_body(env["OLLAMA_MODEL"])).encode()
    request = Request("http://127.0.0.1:11434/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=120) as response:
        result = json.load(response)
    if not result.get("done") or not isinstance(result.get("message", {}).get("content"), str):
        raise RuntimeError("unexpected or incomplete Ollama response")
    print(result["message"]["content"])

if __name__ == "__main__":
    main()
