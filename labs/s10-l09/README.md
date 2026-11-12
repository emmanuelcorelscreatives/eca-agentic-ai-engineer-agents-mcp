# s10-l09: Selective known-failure recovery

Use `research_lab/pipeline_v3.py` and `recovery_v3.py` in projects/03-deep-research.
Inject one positively returned malformed search response or known HTTP response after
another branch commits. A distinct reader binds one authorization to the old attempt,
unchanged inputs, actual failure evidence and a new attempt ID. Resume the SAME journal.

Demonstrate the failed branch alone being attempted again, completed siblings reused,
all original raw failures retained, and a three-total-attempt ceiling. Repeat with an
UNKNOWN timeout: no authorization may replay it. Do not discard the run or reset history.

New tests are authored in tests/test_stage10_recovery_export_v3.py; central QA owns
execution. Prior23-test evidence does not certify this delta. See the v3 project doc.
