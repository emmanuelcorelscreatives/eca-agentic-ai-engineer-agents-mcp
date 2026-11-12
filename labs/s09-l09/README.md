# s09-l09: Add Structured Research Outputs

Define validated schemas for plans, searches, evidence records, sections and final reports.

## Exercise

Validate valid records, missing required fields, invalid enum values, dangling references and an incompatible schema version.

Read projects/03-deep-research/research_lab/planning.py, projects/03-deep-research/research_lab/evidence.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
