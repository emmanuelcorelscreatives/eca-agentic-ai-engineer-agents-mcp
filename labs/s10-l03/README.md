# s10-l03: Stream Research Progress to the User

Display planning, searching, analysis and writing status while the research run executes.

## Exercise

Define run_id, sequence, phase and public_message for planning/searching/analysis/writing/completed/failed events.
Implement a generator that streams events while orchestration runs and closes cleanly on completion/cancellation.
Exercise: add a source-fetch progress event and handle browser disconnects.

Read projects/03-deep-research/research_lab/interface.py, projects/03-deep-research/research_lab/runtime.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
