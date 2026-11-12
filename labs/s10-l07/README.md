# s10-l07: Evaluate Source Quality and Report Completeness

Score evidence relevance, source diversity, coverage, organization and factual support.

## Exercise

Define a documented 0–4 scale per dimension and require source/section evidence for scores.
Prepare a strong and a deliberately flawed fixture report, with the flaws explicitly labeled.
Exercise: score a held-out report and explain one disagreement with a reference annotation.

Read projects/03-deep-research/research_lab/evaluation.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
