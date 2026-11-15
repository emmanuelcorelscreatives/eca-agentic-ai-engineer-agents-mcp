# V3 local deployment exercise

This serves the current `research_lab.deploy_v3` application at `/research`, with
server-session-owned downloads. It is **not** the offline fixture UI. Submitting a
research question makes real, potentially paid OpenAI and Brave requests. Choose
accounts, model, permissions and budget before submission. Never use a live request
as an automated smoke test.

## Prerequisites and supplied lock

Use Docker on your own learning machine and the **repository root** as the initial
working directory. The image uses Python 3.12, the exact direct inputs in
[`requirements.in`](requirements.in) and the supplied transitive-hash
[`requirements.lock`](requirements.lock). A lock is present; do not regenerate it
merely because an older exercise describes resolution as unfinished. Its presence
does not prove successful dependency installation, image startup or live behavior.
The older `deployment/research/` v2 Dockerfile is not this exercise's entrypoint.

Build with the project directory, not the repository root, as context:

```sh
docker build -f projects/03-deep-research/deployment/research-v3/Dockerfile \
  -t eca-research-v3:local projects/03-deep-research
```

If package/hash resolution fails, retain the actual error. Do not remove hash checking
or silently substitute versions. Review dependency changes in a separate environment.

## Private settings and state

Copy the unpopulated [environment template](../research/env.example) to a private
location outside the checkout, then edit it locally without printing its contents:

```sh
install -d -m 700 "$HOME/.config/eca-research"
install -m 600 projects/03-deep-research/deployment/research/env.example \
  "$HOME/.config/eca-research/env"
```

Set `ACADEMY_MODE=live`, your `ACADEMY_MODEL`, `OPENAI_API_KEY`, `BRAVE_SEARCH_API_KEY`,
`ACADEMY_SOURCE_REVISION` (the reviewed source version actually used) and
`ACADEMY_STATE_DIR=/state`. Do not commit, screenshot or paste the populated file.
Secret values must not appear in shell arguments. The template alone cannot start a
configured app; empty required settings cause startup refusal.

The container runs as UID 10001. Create a **new exercise-only** private named volume
and set ownership using this image, without touching any existing run's state:

```sh
docker volume create eca-research-v3-state
docker run --rm --network none --user 0 \
  --mount source=eca-research-v3-state,target=/state \
  --entrypoint python eca-research-v3:local \
  -c "import os; os.chown('/state', 10001, 10001); os.chmod('/state', 0o700)"
```

If that volume name already belongs to an existing exercise/run, reuse its original
ownership and data rather than reinitializing it. Do not discard a journal to evade
an UNKNOWN provider outcome. Reports, raw responses and state may contain private
material; the volume must not be shared publicly or mounted as broad Gradio paths.

## Local-only startup and checks

```sh
docker run --rm --name eca-research-v3 -p 127.0.0.1:7860:7860 \
  --read-only --tmpfs /tmp:rw,nosuid,size=256m \
  --cap-drop ALL --security-opt no-new-privileges \
  --env-file "$HOME/.config/eca-research/env" \
  --mount source=eca-research-v3-state,target=/state \
  eca-research-v3:local
```

Keep that terminal open; use a second terminal for the health check:

```sh
curl --fail http://127.0.0.1:7860/healthz
```

Expected health fields are `status: ready`, `mode: configured-live` and
`external_provider_health: not probed`. This is local configuration readiness, not
successful model/search access. Open `http://127.0.0.1:7860/research` in your browser.
Keep binding local. A remote deployment additionally needs authenticated TLS, access
controls, resource limits and a deliberate private-data retention policy; this guide
does not claim those services have been deployed for you.

Only after choosing the spend, submit one finite question. Record any actual failure
honestly; a timeout/cancellation may leave UNKNOWN, which must not replay automatically.
After a successful completed run, use **Prepare my completed report downloads** to
obtain `report.md`, `report.html`, `research.json` and `sha256.json`. Check the manifest
hashes against the downloaded report bytes and trace a finding back to its source.

Use a genuinely separate browser session to verify it cannot retrieve the first
session's opaque run token; an unfinished run must not export. The offline cases in
[`test_stage10_recovery_export_v3.py`](../../tests/test_stage10_recovery_export_v3.py)
demonstrate foreign-token/tamper refusal without making paid calls. Do not give a
browser arbitrary filesystem paths or publish private raw reports as test evidence.

Record build, startup, health, provider results, browser behavior and download results
separately. None is established merely by the existence of this guide, a lock, a UI
constructor or fixture tests. Preserve state when stopping the exercise container.
