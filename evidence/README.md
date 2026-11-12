# Recording actual course evidence

A lesson's evidence must show what actually ran at a specific repository commit. Offline fixture tests, SDK import tests, real model runs, browser captures and deployment checks are distinct evidence classes. A passing offline exercise does not certify the others.

For each practical, record:

1. Stable lesson ID, repository commit, operating system and dependency versions.
2. The exact commands and inputs, with credentials and personal data removed.
3. Actual exit codes, returned values or visible application observations.
4. Whether data is synthetic, locally observed, retrieved from a cited source or returned by a real model call.
5. Known failures, unexecuted steps and remaining acceptance criteria.

Use an evidence file such as `s01-l02-observation.md` in your own workspace. Do not populate it with invented expected output. The exercise's expected result belongs in its solution or acceptance criteria, and must be labeled as expected until observed.

For n8n, retain the real imported workflow execution and the actual model/tool/decision path. The exported workflow and offline JavaScript tests in this repository establish authoring and local logic only; they are not proof of an n8n model execution. Each manual workflow run can incur one model request. Keep retries disabled and review the configured account and budget first.

Screenshots should show the actual application screen, without decorative devices or narration subtitles. Never include private browser tabs, tokens, personal workbooks or customer data. Student portfolio evidence should contain only the Academy fixtures or information the student explicitly intends to publish.

The repository's GitHub Actions log reports the suite that actually ran for its commit. Additional Studio build receipts are operational records and are not silently promoted into public live-provider observations.
