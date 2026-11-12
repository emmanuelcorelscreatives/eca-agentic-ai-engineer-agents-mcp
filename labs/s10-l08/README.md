# s10-l08: Analyze Traces, Latency and Token Usage

Use execution records to find slow, expensive or unreliable parts of the workflow.

## Exercise

Record run/step IDs, parent step, start/end timestamps, provider-reported token usage and outcome.
Use labeled synthetic traces for arithmetic exercises; capture a separate genuine run for any operational demonstration.
Exercise: identify the slowest step and estimate which optimization is supported by measured evidence.

Read projects/03-deep-research/research_lab/runtime.py, projects/03-deep-research/research_lab/evaluation.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
