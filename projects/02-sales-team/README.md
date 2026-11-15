# Project 2: AI Sales Development Team

Build research → strategy → writing → review → exact human approval → simulated delivery. Start with a deterministic, offline state machine; then connect the optional SDK specialists and local Gradio interface. Cedar Library/Jordan Lee and Pine Community Workshop/Avery Morgan are fictional. Their `.invalid` addresses are not real mailboxes.

## Curriculum and prerequisites

- [Stage 6: SDK, async Python, tools and traces](../../curriculum/workbooks/stages-01-10.md#stage-6)
- [Stage 7: managers, handoffs and context](../../curriculum/workbooks/stages-01-10.md#stage-7)
- [Stage 8: sales team, lessons 1–14](../../curriculum/workbooks/stages-01-10.md#stage-8)
- [Worked solutions, capstone and scoring workflow](WORKED-SOLUTIONS.md)

Use Python 3 with `venv` support. The offline exercises use only the standard library; optional package compatibility must be checked in your environment. Commands below start in the repository root unless explicitly stated. No key, account or package install is needed for the first exercise.

## 1. Run the offline baseline

```sh
python3 projects/02-sales-team/sales.py
python3 projects/02-sales-team/sales.py --approve
python3 projects/02-sales-team/exercises.py
python3 -m unittest discover -s tests -p test_student_project_02.py -v
```

The first command prints an unsent draft, revision and payload hash. `--approve` records a practice reviewer and returns `delivery: simulated_only`, `external_messages_sent: 0`. Each CLI run uses a fresh in-memory database. The worked script checks all six exercises; it is not model execution or actual company research.

## 2. Try the optional local interface

Create an isolated environment from the repository root:

```sh
python3 -m venv .venv-sales
. .venv-sales/bin/activate
python3 -m pip install -r projects/02-sales-team/requirements-optional.txt
python3 projects/02-sales-team/app.py
```

No key or SMTP sink is required. Open the loopback URL printed by Gradio; public sharing is disabled. Choose `deterministic`, generate, inspect recipient/subject/body/revision/hash, save any edits, approve the exact preview, then select **Simulate approved delivery; no email**. Download the draft report. A second simulation must refuse. This is an offline approval/UI walkthrough, not proof of SDK-generated outreach.

The database and reports are temporary practice state. Reviewer names are labels, not authenticated identities. Never deploy this as a public multi-user approval service. SDK dropdown choices refuse unless server-side SDK opt-in and a model are configured. Owned SMTP submission refuses unless a sink was separately configured.

## 3. Connect the SDK deliberately

Set `OPENAI_API_KEY` and `ACADEMY_MODEL` privately in your environment; never paste secrets into files, screenshots, transcripts or repository commits. From this project directory:

```sh
cd projects/02-sales-team
python3 agents_adapter.py --live
```

**This makes paid model requests.** Both this CLI and the UI sequential mode use the same validated pipeline. Each output must retain prospect/company/campaign/evidence/revision identity; research, strategy and writer must also retain the source ID. CLI draft state is ephemeral, while the returned operational events retain actual intermediate outputs. A failed model review returns `revision_required`, never human approval.

For the SDK/UI capstone, return to the repository root and run:

```sh
cd ../..
python3 projects/02-sales-team/app.py --allow-sdk
```

Choose `sdk-sequential`, generate, review every factual claim against the fixture, edit if necessary, approve the exact preview, simulate and export. Edits clear approval. The model cannot approve or send. The SDK may retry transient requests internally; turn caps do not guarantee request counts. Tracing is disabled; exported operational records are not hosted traces or private reasoning.

`sdk-manager` and `sdk-handoff` are coordination observations, not sendable drafts. Use **Export selected manager/handoff observation** after running either. Inspect actual tool inputs/outputs and selected agents; if no revision or handoff occurred, record that absence rather than inventing it. See the [comparison exercise](WORKED-SOLUTIONS.md#manager-versus-handoff).

Version ranges in `requirements-optional.txt` are not a tested frozen lock. Import/construction checks, fake Runner tests, browser use and actual model behavior are different observations. This project does not claim live model or browser success merely from source code or a passing offline test.

## 4. Exercises and expected outcomes

Run `exercises.py` for the runnable [worked answers](WORKED-SOLUTIONS.md#six-worked-exercises); inspect its assertions, change one condition and explain the result.

1. Attempt delivery before approval: `PermissionError`, zero outbox rows.
2. Approve then edit the subject: `draft` status, cleared approval hash, a new approval required.
3. Add “guaranteed”: mechanical review fails and approval refuses. Try an invented revenue statement: explain why a word filter cannot verify truth; do not approve the invented claim.
4. Approve a corrected draft and simulate twice: one row, second attempt refused.
5. Create a second fictional prospect without a source ID: reject rather than invent evidence.
6. Build a typed reviewer-to-writer handoff carrying prospect/campaign/source IDs and a revision reason. A local record demonstrates the contract, not actual SDK delegation.

`models.py` provides the company/research/strategy/draft identity-graph exercise. `context_wire.py` validates the actual SDK handoff identity. `orchestration.py` defines manager tools and specialist handoffs. The sequential pipeline consumes actual upstream records; its deterministic baseline is not a substitute for observing live agent coordination when claiming that outcome.

## 5. Evaluate personalization and grounding

`fixtures/evaluation-cases.json` contains six authored emails for Cedar, with reference labels and rationales. `evaluations.py` keeps these labels separate from mechanical checks, including a worked false positive and false negative. Neither is a model score.

Use Cedar plus [the sparse Pine prospect](fixtures/prospect-sparse.json) in the [scoring walkthrough](WORKED-SOLUTIONS.md#score-two-prospects). Preserve actual outputs/run IDs, manually score all five rubric dimensions, and count failures. Offline worked samples must stay labeled `fixture-output`; never present them as actual agent results.

## Optional: actual owned-loopback SMTP, not external email

This is separate from simulated delivery and is unnecessary for the first capstone. Only use synthetic `.invalid` recipients and a listener you own. With the sales environment active, install the optional listener package, then run it in a dedicated terminal from the repository root:

```sh
python3 -m pip install -r projects/02-sales-team/requirements-smtp.txt
python3 -m aiosmtpd -n -l 127.0.0.1:8025
```

Use an unoccupied unprivileged port. If binding fails, stop and choose another port in both commands; do not kill or use someone else's listener. In a second terminal with the same environment active:

```sh
python3 projects/02-sales-team/app.py --owned-sink-port 8025 --acknowledge-owned-sink
```

Generate, review, approve, then choose **Submit approved to owned SMTP sink** exactly once. Compare the listener's printed synthetic recipient/subject/body, `Message-ID`, `X-Academy-Revision` and `X-Academy-Payload-SHA256` with the displayed preview and exported transport history. `transport.verify_received_payload_hash` validates a parsed header; canonical body text uses LF plus a final newline. Sink acceptance is not mailbox delivery. Stop both processes with Ctrl-C when finished. Keep captures private and synthetic.

Any transport exception or interrupted sending state is uncertain and held: inspect the same sink/message ID and reconcile before taking any action. Do not delete claims or replay unknown sends. `deliver(live=True)` stays prohibited; only the explicitly acknowledged loopback adapter can submit SMTP. External providers, recipient accounts and production approver authentication are not implemented here.
