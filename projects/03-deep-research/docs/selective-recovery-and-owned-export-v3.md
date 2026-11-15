# Stage 10 lessons 9–10: selective recovery and owned exports

Use the [student guide](student-guide.md) for local tests and the
[v3 deployment exercise](../deployment/research-v3/README.md) for build/start steps.
The tests use synthetic boundary cases; they do not establish actual provider,
browser or deployed behavior. Existing v2 CLI entrypoints keep their separate scope.

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
it remains unknown rather than fabricating proof or retrying it. Actual-provider
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
Only a real completed run and browser download establish actual UI/export behavior.

## Exact dependency input and deployment exercise

`deployment/research-v3/requirements.in` and `pyproject.toml` pin direct versions;
the supplied `requirements.lock` records transitive versions and hashes. The Dockerfile
installs that existing lock with hash checking and starts `deploy_v3` with the
download-enabled UI. A committed lock is not successful installation or build proof.
Follow the [deployment guide](../deployment/research-v3/README.md) for the exact build
context, protected settings, non-root writable private state and localhost startup.
Remote exposure additionally requires authenticated TLS and access controls.

Student exercise: start the actual clean locked deployment; observe
health; open two genuinely separate sessions; complete one finite explicitly chosen research
request; prepare and download that session's four real exports; compare hashes and
verify a foreign-session token cannot retrieve them. Retain actual receipts/results.
Do not substitute a fixture report, fake provider response or synthetic browser image
for required actual model/Brave/deployment observations.
