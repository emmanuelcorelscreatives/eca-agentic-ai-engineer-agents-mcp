# s09-l05: Build the Web Search Agent

Execute searches, collect relevant results and return normalized source records.

## Exercise

Normalize fixture results and simulate errors offline, then execute one authorized real-provider query against the approved research question. Retain the actual query, provider, timestamp, response and normalized source records; inspect the observed results before creating the walkthrough.

Read projects/03-deep-research/research_lab/search.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
