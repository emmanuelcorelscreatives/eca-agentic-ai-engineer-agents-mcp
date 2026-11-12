# Project 7 — Agent Application Factory

This runnable factory demonstrates Stage 25's typed specification → requirements → architecture → scaffolding → tests → validated project pipeline. Its baseline is an honest deterministic `stdlib` adapter. It does **not** fabricate AutoGen, model reasoning, code-review judgments or API results.

```sh
python3 factory.py examples/text_helper.json /tmp/academy-generated-text-helper
cd /tmp/academy-generated-text-helper
python3 -m unittest -v
python3 agent.py < request.json
```

Choose a new output directory on each run. A successful factory run has actually executed the generated application's tests before writing the final artifact set. Its `validation-receipt.json` records the command, actual exit code/stdout/stderr and SHA256 of every generated source/config/document file. For the supplied request, the real application returns `{"words": 2}`.

## Specification and architecture

`AgentSpec` requires purpose, users, tools, data, outputs and policies. Names are safe Python identifiers. Tools are the explicit typed `word_count` and `uppercase` implementations. The executable adapter permits only `stdlib` with local/Docker deployment; other framework values raise a clear error rather than pretending integration succeeded.

Requirements and architecture are serialized alongside code. Policy text remains data in documentation/instructions, not interpolated executable code. Structural review parses Python and verifies the expected artifact inventory and application imports. Actual behavioral tests reject forbidden tools and invalid input as well as checking enabled functionality.

The temporary-directory test runner uses Python isolated import mode and a 15-second timeout. **This is not an OS security sandbox and must not be used for untrusted generated code.** Only the factory's fixed validated templates may enter this runner. Docker configuration is supplied for the separate isolation lesson:

```sh
docker build -t academy-text-helper /tmp/academy-generated-text-helper
docker run --rm -i --network none --read-only --cap-drop ALL --security-opt no-new-privileges academy-text-helper < /tmp/academy-generated-text-helper/request.json
```

Building the Python base image may require network access. The runtime command blocks network, uses a nonroot user and a read-only filesystem. These Docker commands are instructions, **not a claim that Docker was executed during the offline unit-test run**.

## Curriculum extensions

Use the same typed specification and executable acceptance tests to add a genuine framework adapter. Each adapter must produce its own real imports, dependencies, entry point and smoke tests; do not simply relabel the stdlib implementation. Replaceable adapter design does not mean every framework is already implemented.

For the bounded repair-loop lesson: retain the failed receipt, diagnose the exact failed assertion, produce one explicit changed template patch, generate into a fresh directory and rerun all generated tests. No automatic arbitrary-code rewrite/retry loop is currently shipped. No generated app should be launched until its actual validation passes.

See `EXERCISES.md` and `SOLUTIONS.md`. No API credentials or paid calls are needed for the baseline.
