# s09-l11: Manage Parallel Research Tasks

Run independent research branches concurrently while preserving task and source attribution.

## Exercise

Run independent fixture search tasks with concurrency two; inject one failure and compare deterministic merged output against serial execution.

Read projects/03-deep-research/research_lab/search.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
