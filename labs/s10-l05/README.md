# s10-l05: Add Report Export and Email Delivery

Inspect real Markdown/HTML/JSON exports and hashes. With an explicitly configured account and budget send an exact-approved report to a course-owned local sink, then repeat its idempotency key.

Current implementation, relative to `projects/03-deep-research/`:

- research_lab/exports_v2.py
- research_lab/transports.py:SmtpDelivery

Run the relevant tests for your checkout and retain actual output. A shared regression result does not verify this lesson's optional model, browser or deployment steps.

Still required:

- actual approved course-owned local SMTP receipt

Follow the [student setup and live-integration guide](../../projects/03-deep-research/docs/student-guide.md) for executable commands, prerequisites, expected results and explicit paid-run consent. Read `projects/03-deep-research/docs/semantic-repair-stages09-10-v2.md` for the current workflow contracts. Fixture tests do not establish live model/search, browser, SMTP or deployment outcomes.
