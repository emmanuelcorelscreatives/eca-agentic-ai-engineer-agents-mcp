# s10-l04: Display Plans, Sources and Agent Activity

Present useful execution information without exposing private internal reasoning.

## Exercise

Display a concise task plan, source URLs and factual tool/agent status.
Use an allowlisted public schema; exclude hidden reasoning, API keys, private prompts and raw provider payloads.
Exercise: add a duration column to the agent-activity view using actual recorded timestamps.

Read projects/03-deep-research/research_lab/interface.py, projects/03-deep-research/research_lab/runtime.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
