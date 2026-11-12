# Stage10 lessons9–10: precise recovery/export delta, version3

This authored delta does not change the frozen stage9 packet or its23-test evidence.
Central QA must execute the NEW tests. Actual provider, browser and deployment evidence
remains pending. Existing v2 entry points and historical outputs retain their scope.

## Selective recovery of a positively known failure

`pipeline_v3.run_research` preserves the same run identity, journal and completed phase/
query results. `RecoveryJournal` accepts an explicit `recovery_authorizations` dictionary
and `executor_identity`. A distinct reviewer positively classifies the exact failed
attempt and binds an authorization to its complete SHA and unchanged input SHA.

One authorization has these exact fields:

- `step_name`: exact phase/query key, for example `search/task-a-counterevidence`.
- `old_attempt_sha256`: `pipeline_v2.digest` of the complete retained failed step.
- `input_sha256`: the exact original step input hash.
- `failure_kind`: `known_http_response`, `connection_refused`, or `known_malformed_response`.
- `evidence_sha256`: hash of retained actual `known_failure_evidence`, or the exact
  `raw_result` for a known malformed response.
- `reviewer_identity` and `executor_identity`: explicit distinct responsible identities.
- `reason`: concrete observed failure and bounded remedy.
- `new_attempt_id`: new unique identity for this single additional attempt.

The new attempt reuses exactly the same inputs. Old attempts and the full authorization
are retained in `attempt_history` in the same journal; nothing is discarded or silently
reclassified. Three total attempts is a hard bound. Completed sibling requests are
revalidated/reused; they are not rerun. A second failure needs another exact current
reviewed authorization, not automatic retry. Prior UNKNOWN/IN_FLIGHT, an unknown attempt
anywhere in history, changed inputs, forged/stale proof or exhausted attempts refuses
replay. The API never creates a new run to evade history.

Known HTTP errors retain the actual response code/body; connection refusal retains its
positive local failure classification. A returned malformed payload is retained before
validation. If SDK internals do not expose the positively returned malformed output,
it remains unknown rather than fabricating proof or retrying it. Central actual-provider
observations are not supplied by synthetic boundary tests.

## Usable own-run UI downloads

`interface_v3.build_ui` uses actual Gradio widgets and a download button returning
Markdown, HTML, JSON and SHA manifest files. Its async research callback obtains the
server-provided session hash; an opaque token identifies only that session's run.
No browser input may supply a filesystem path.

`RunExports.finish` binds the actual completed writing checkpoint, bundle identity and
report SHA, then calls the SAME `exports_v2.export` boundary used by CLI export. The
button rechecks server session ownership, unchanged completed state, fixed file names,
paths and hashes. A foreign session, unfinished run, changed output or symlink is
refused. Do not configure broad Gradio allowed_paths for the private state root.
No real UI/browser/export observation is claimed until central QA retains it.

## Exact dependency input and deployment exercise

`deployment/research-v3/requirements.in` and `pyproject.toml` pin the direct versions
already recorded in admitted key3 dist-info metadata. Reading metadata did not install
or execute anything. Parent owns actual transitive resolution, hashes and clean proof.
The Dockerfile requires a real central `requirements.lock`; no hashes were invented.
It starts `deploy_v3` with the real download-enabled UI. Secret injection, non-root
execution, private /state volume and authenticated TLS remain required.

Fresh-user exercise for central QA: start the actual clean locked deployment; observe
health; open two genuinely separate sessions; complete one finite admitted research
request; prepare and download that session's four real exports; compare hashes and
verify a foreign-session token cannot retrieve them. Retain actual receipts/results.
Do not substitute a fixture report, fake provider response or synthetic browser image
for required actual model/Brave/deployment observations.
