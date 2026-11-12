# s10-l02: Build the Deep Research Gradio Interface

Create an interface for entering research questions and viewing the completed report.

## Exercise

Provide a question field, submit control, status area and report viewer.
Validate empty/oversized input; use an explicit fixture mode for deterministic offline testing.
Exercise: add a report title and source list without changing the orchestration interface.

Read projects/03-deep-research/research_lab/interface.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
