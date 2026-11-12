# s09-l10: Coordinate the Research Team Through Code

Build a controlled orchestration flow that manages each research phase and its dependencies.

## Exercise

Run the full offline pipeline; interrupt after evidence capture and resume without rerunning successful searches.

Read projects/03-deep-research/research_lab/runtime.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
