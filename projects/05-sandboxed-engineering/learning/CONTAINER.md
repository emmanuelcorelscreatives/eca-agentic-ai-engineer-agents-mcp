# Whole engineering crew in Docker

This entrypoint executes product management, architecture, development, QA,
context handoffs and bounded repairs **inside one owned container**. The default
provider wrapper constructs actual CrewAI Agent/Task/Crew objects with its
bounded BaseLLM bridge; generic role names alone are not CrewAI execution. Only model
transport crosses the boundary: a finite host broker reads typed file requests
and returns actual response envelopes. It never executes generated source.

This is an **optional advanced Linux/Python-3.12 extension**, not a prerequisite
for the [offline notebook](WORKED-EXAMPLE.md). Source and mocked tests do not prove
that Docker, uv, CrewAI or a provider works in your environment. Do not run any
container or paid request until the prerequisites below are met and you opt in.

## Prerequisites and offline preparation

From this directory, independently inspect these files and semantic_team.py.
The real `uv.lock` is already supplied: check it, do not replace it with a new
resolution simply to run the example. The project uses Python 3.12 with the explicitly
pinned `crewai==1.15.40` runtime. The generated expense application remains
standard-library-only; the orchestrator has real SDK dependencies. You need the
full transitive lock and a prepopulated,
bounded offline wheel/cache inventory. `uv sync --frozen --offline --no-dev`
must genuinely install those locked dependencies into the prepared image; an
empty cache must fail rather than silently fetch them. uv remains an actual
tool copied from an independently pinned image.

The build context must contain the separately reviewed `offline-cache/`
directory copied from an actual successful uv resolution; retain its full file
inventory, hashes, size limit and provenance. No fabricated cache or unbounded
host cache mount is used. The Dockerfile copies only that explicit cache and
uses `UV_PYTHON_DOWNLOADS=never`. Runtime PATH selects the actual synchronized
`.venv/bin/python`, so SDK imports cannot accidentally run on the base Python.

Supply PYTHON_IMAGE and UV_IMAGE as independently verified digest-pinned local
images. Build only after their contents and origin have been reviewed,
with network disabled and no package downloads. Record the resulting immutable
image digest. Runtime `docker_argv` refuses tags and always uses `--pull=never`.
The launcher does not build or pull anything.

Have the lab administrator provision one new learner-owned mailbox tmpfs, at most
16 MiB, mode 0700, and arrange its eventual owned cleanup. No host mount commands
are part of this exercise; the launcher never runs arbitrary mount commands.
Put only request.json in a
separate read-only input directory, with title and product_request strings.
Do not bind the repository root, home directories, credentials, Docker socket,
existing course files, or other users' files.

The caller supplies `container_launch.launch(image, inputs, mailbox, callback)`.
Inside the container, `CrewAIRoleProvider(MailboxProvider(), evidence_store)`
wraps each typed role request in actual CrewAI execution. Preserve separate
actual broker-response and framework-output lineage; SDK construction alone
does not prove a completed role, and a role cannot cause additional unbudgeted
model calls. Check that exact adapter and its call limit in your environment.
The trusted callback receives schema/role/payload/input_sha/ordinal/request_sha
and returns the exact semantic_team response envelope. It owns provider access
and must retain the real request ID, model identity and raw response. Requests
are reserved before transport, at most nine are made by the crew, and timeouts
remain UNKNOWN without retries. A used mailbox cannot be silently reused.

### Preparation recipe in an isolated lab

The lab/instructor must supply: a working Docker daemon you are allowed to use;
locally present Python-3.12 and uv images with actual repository digests; a reviewed
uv-format `offline-cache/` containing every artifact needed by this exact lock;
and a fresh dedicated mailbox as described above. The cache is **not** committed,
and a random wheel folder is not a substitute for a uv cache. Request these
resources if absent; do not download packages, mount host filesystems or silently
enable networking to work around a missing prerequisite.

The following commands are a recipe for that separately prepared lab, not commands
that the offline activities run. Work in an isolated copy of `learning/` containing
only the needed source, Dockerfile, pyproject, lock and supplied cache. From there:

```sh
UV_CACHE_DIR="$PWD/offline-cache" UV_PYTHON_DOWNLOADS=never uv lock --check --offline
UV_CACHE_DIR="$PWD/offline-cache" UV_PYTHON_DOWNLOADS=never uv sync --frozen --offline --no-dev
```

Stop on missing Python, wheels or lock incompatibility; never fall back to online
sync. This installs orchestrator dependencies into that copy's `.venv`, not the
generated expense app. Record actual output and review the cache's file inventory
and size. Set `PYTHON_IMAGE` and `UV_IMAGE` locally to the actual preloaded
`name@sha256:...` identities; these are image names, never credentials. Then:

```sh
docker build --network=none --pull=false --build-arg PYTHON_IMAGE="$PYTHON_IMAGE" --build-arg UV_IMAGE="$UV_IMAGE" -t eca-engineering-lab .
docker image inspect eca-engineering-lab
```

The launcher accepts a real locally addressable **repository digest**, not the
build tag or an untested string made from an image ID. If this lab cannot assign
and resolve that digest locally without pulling, stop and ask the lab administrator
to provision a suitable image; do not relax `--pull=never`. Inspect whether source,
SDK imports and runtime Python actually match this build before live use.

### Input and host broker wiring

The separate canonical input directory contains only `request.json`:

```json
{"title":"Expense calculator","product_request":"Total non-negative integer minor units; reject negatives, decimals and booleans."}
```

The separate mailbox must be empty and be the fresh bounded tmpfs, not a normal
temporary directory on the host disk. Paths cannot be symlinks or overlapping
directories. Use `Path` objects for both directory arguments.

The transport callback is an explicit **learner/instructor integration task**.
This checkout does not supply an account-specific paid-provider client. It receives
`schema`, `role`, `payload`, `input_sha`, `ordinal`, `request_sha` and must return:

```text
role             = request['role']
input_sha256     = request['input_sha']
request_id       = actual provider request identifier
model            = actual provider model identifier
raw              = actual model response text containing the requested JSON
provenance       = 'actual-provider-response'
```

Only these six response keys are allowed. Bind every actual response to the
request, preserve private raw failures and never invent an identifier or convert
an offline double into real provenance. Keep credentials inside the host transport,
out of argv, input JSON, mailbox, generated files and logs. Review the provider's
actual usage/cost and data-sharing policy before opting in. A safe starting
callback is deliberately fail-closed:

```python
def provider_callback(request):
    raise RuntimeError('Provider transport is not configured; no request sent')
```

Do not launch with this callback expecting a result. Implement and review the
transport separately before a deliberate live run. After that opt-in, the host
invocation from this directory is:

```python
from pathlib import Path
from container_launch import launch

result = launch(
    image=prepared_repository_digest,
    inputs=Path(prepared_input_directory),
    mailbox=Path(prepared_empty_mailbox),
    callback=provider_callback,
)
```

The three `prepared_*` values are your actual provisioned lab values, not supplied
defaults. This call starts Docker and can spend provider credits; it is **not** an
offline example to run unchanged. At most nine broker requests are admitted; model
timeouts remain UNKNOWN and must not be replayed. Failure means retain the owned
mailbox and examine the reservation/output, not start a second run. A successful
return includes `execution`, `result` and `delivery`; inspect actual test attempts,
criterion observations, archive and matching receipt. The administrator must
coordinate cleanup of only the owned mailbox after retaining needed outputs.

## Boundary and limits

Runtime network is disabled; root filesystem read-only; work tmpfs 128 MiB;
temporary tmpfs 64 MiB; memory 768 MiB with equal swap limit; two CPU shares;
64 PIDs; fixed argv; finite overall deadline; finite per-provider deadline;
bounded JSON files and process output. The broker's size checks, path checks,
call budget and reserved records are enforced on the host.

The root orchestrator retains only SETUID/SETGID capabilities so generated
children can drop to UID/GID 65534 with no supplementary groups. Those children
cannot replace root-owned read-only source/tests or access the private mailbox.
No Docker socket or nested container command is available. Generated children
have 15-second wall and 10-second CPU deadlines, bounded logs, and their exact
process group is killed after each run. Container cleanup targets only its
random exact owner name and must be observed, not assumed.

The trusted runner records actual successful immutable acceptance test IDs:
empty and zero map to R1, sum to R2, invalid negative/decimal/bool to R3. All QA
and developer tests must also pass. These are functional observations, not a
proof against hostile Python: imported source can alter its interpreter's
runtime. Independent source review remains required. Containers share the host
kernel; do not describe this educational boundary as a hardened hostile-code
service.

## Review your optional live result

1. Run the local suites listed in [README.md](README.md#local-verification-map).
2. Inspect actual uv lock/check/sync and image build logs, image digest and source
   inventory. Run actual uv version/environment commands inside the image.
3. Execute one coherent authorized real-provider workflow through this launcher;
   retain every real response, four-role handoff, failing test source/output,
   any bounded repair and actual final acceptance observations.
4. Inspect finite output, no-network configuration, UID separation, immutable
   tests, mailbox limits, uncertain-call no-replay behavior and exact cleanup.
5. Independently review delivered files, dependency declarations, README and
   package inventory; perform fresh documented extraction/setup/tests inside the
   approved execution boundary, never unreviewed host execution. Test doubles are
   not live evidence.

No stdout or receipt should be published until private raw responses have been
reviewed for credentials and personal data.

## Exact generated delivery package

The default entrypoint now passes only a successful whole-team result and its
original completion event to `delivery_package.package_delivery`. It preserves the
exact generated source/docs/dependencies, immutable course and independent QA test
source, all typed artifacts, actual attempt receipts and acceptance matrix. Its
ZIP manifest records source/result/receipt/member hashes. It never substitutes the
older fixed template or executes generated code on the host.

The archive publishes atomically to the new `/mailbox/delivery.zip`; existing or
concurrently created paths are never overwritten. Paths, member inventory, CRC,
bytes and size quotas are checked. The host launcher requires the exact archive
and matching completion-bound receipt before returning a successful delivery.
Offline test-double packages require an explicit fixture flag and remain labelled
`OFFLINE_FIXTURE_NOT_PRODUCTION`; the production entrypoint does not enable it.

The local fixture-package tests are useful for learning archive checks, but they
do not establish real-provider delivery. For a real generated package, retain your
actual clean extraction/setup/test results and source review separately from the
offline notebook. No historical recording is required to use the notebook.
