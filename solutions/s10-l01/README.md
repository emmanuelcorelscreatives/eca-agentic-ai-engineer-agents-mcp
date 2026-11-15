# s10-l01: Refactor the Research System into Python Modules

Schemas, agents, provider adapter, orchestration, quality, UI and deployment are separate; live execution requires the explicit capstone entry point.

Current implementation, relative to `projects/03-deep-research/`:

- research_lab/contracts_v2.py
- research_lab/sdk_v2.py
- research_lab/pipeline_v2.py
- research_lab/interface_v2.py

Run the relevant tests for your checkout and retain actual output. A shared regression result does not verify this lesson's optional model, browser or deployment steps.

Still required:

- actual lesson-specific results and your review against the acceptance criteria

Follow the [student setup and live-integration guide](../../projects/03-deep-research/docs/student-guide.md) for executable commands, prerequisites, expected results and explicit paid-run consent. Read `projects/03-deep-research/docs/semantic-repair-stages09-10-v2.md` for the current workflow contracts. Fixture tests do not establish live model/search, browser, SMTP or deployment outcomes.
