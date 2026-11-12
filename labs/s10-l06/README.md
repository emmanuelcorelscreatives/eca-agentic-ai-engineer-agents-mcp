# s10-l06: Create a Research Evaluation Dataset

Build representative questions and expected quality criteria for repeatable system testing.

## Exercise

Create at least 12 clearly labeled Academy-authored cases spanning narrow facts, comparisons, time-sensitive topics, conflicting evidence and insufficient evidence.
Store case_id, question, source expectations, coverage checklist, expected refusal/uncertainty behavior and rubric version; avoid an asserted single correct long-form report.
Exercise: add two cases and justify why their quality criteria are observable.

Read projects/03-deep-research/data/s10-evaluation-cases.json.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
