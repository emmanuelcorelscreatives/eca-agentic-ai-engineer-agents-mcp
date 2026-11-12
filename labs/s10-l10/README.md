# s10-l10: Deploy the Deep Research Application

Configure secrets, dependencies and hosting settings for a working deployment.

## Exercise

Pin verified dependencies and document local container startup, health checks, bind address, secret injection and persistent run storage.
Provide separate offline fixture and real-provider configurations; never include real credentials.
Exercise: deploy to an authorized course-owned test target and capture actual health/startup/report behavior.

Read projects/03-deep-research/docs/stages09-10-architecture.md.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
