"""s02-l07 companion. Place beside examples/ in the course repository root.
Default/--fixture: offline synthetic exchange. --live: one explicitly opted-in
provider request using private process configuration, with no automatic retry.
"""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "examples" / "stages02-04"))
from foundations import Budget, FakeModel, text_call

PROMPT = "Write one friendly sentence welcoming a new student to Cedar Academy."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true", help="Offline synthetic exchange (default)")
    mode.add_argument("--live", action="store_true", help="Authorize one configured provider request")
    args = parser.parse_args()
    budget = Budget(1)
    if not args.live:
        model = FakeModel([{"content": "Hello academy"}])
        answer = text_call(model, PROMPT, budget)
        print("OFFLINE SYNTHETIC — predetermined response; no provider request")
        print("fixture_answer:", answer)
        print("recorded_request:", json.dumps(model.requests, ensure_ascii=False))
        print("local_attempts:", budget.calls)
        return 0

    from stage02_configuration import load_configuration, ObservedCompatibleModel, ModelBoundaryError
    try:
        config = load_configuration()
    except ValueError:
        print(json.dumps({"status": "boundary", "category": "configuration", "local_attempts": 0}))
        return 1
    model = ObservedCompatibleModel(config, allow_live=True)
    budget.charge()
    try:
        observation = model.observe([{"role": "user", "content": PROMPT}])
    except ModelBoundaryError as error:
        print(json.dumps({"status": "boundary", "category": error.category, "local_attempts": budget.calls}))
        return 1
    print(json.dumps({"status": "observed", "answer": observation.message.get("content"),
                      "model": observation.model, "provider_request_id": observation.provider_request_id,
                      "input_tokens": observation.input_tokens, "output_tokens": observation.output_tokens,
                      "usage_status": observation.usage_status, "local_attempts": budget.calls}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
