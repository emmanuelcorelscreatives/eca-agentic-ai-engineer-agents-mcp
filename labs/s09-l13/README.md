# s09-l13: Handle Missing, Conflicting and Insufficient Evidence

Require the system to identify uncertainty, compare conflicting sources and avoid invented conclusions.

## Exercise

Evaluate no-source, single-source, contradictory-date, broken-link and prompt-injection cases; request targeted follow-up only when a justified budget remains.

Read projects/03-deep-research/research_lab/evidence.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
