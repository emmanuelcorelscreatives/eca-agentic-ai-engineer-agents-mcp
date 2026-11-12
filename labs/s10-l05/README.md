# s10-l05: Add Report Export and Email Delivery

Allow users to export completed reports and send approved copies through configured tools.

## Exercise

Produce Markdown and HTML exports with references and stable UTF-8 content.
Use a local mail sink by default; require an explicit approval action and configured recipient before external send.
Exercise: add an export filename sanitizer and show delivery status without exposing credentials.

Read projects/03-deep-research/research_lab/reporting.py.

Run `python3 examples/stages09-10/run_research.py --export /tmp/academy-research-lab` from the repository root. Run `python3 -m unittest discover -s projects/03-deep-research/tests -p test_stages_09_10.py`. Change one fixture in a temporary copy and demonstrate the relevant failure path. Retain actual terminal output and mark synthetic observations explicitly.
