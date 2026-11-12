# s10-l01: Refactor the Research System into Python Modules

Separate agents, schemas, tools, orchestration, configuration and interface logic into maintainable components.

## Exercise

Move the Stage 9 working research fixture into modules without changing report fields.
Keep provider clients behind an injected interface and load secrets only in config.
Exercise: extract one tool and replace direct network access with a fixture-backed implementation.

Read projects/03-deep-research/research_lab/__init__.py, projects/03-deep-research/docs/stages09-10-architecture.md.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
