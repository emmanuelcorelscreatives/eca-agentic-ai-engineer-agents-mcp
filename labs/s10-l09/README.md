# s10-l09: Add Retries and Failure Recovery

Recover from failed searches, malformed outputs, provider errors and interrupted research tasks.

## Exercise

Implement a retry classifier, bounded exponential backoff with jitter and explicit terminal failure states.
Checkpoint completed research steps and use idempotency keys for external delivery.
Exercise: resume after an injected search failure without repeating already committed work.

Read projects/03-deep-research/research_lab/runtime.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
