# Whole engineering crew in Docker

This entrypoint executes product management, architecture, development, QA,
context handoffs and bounded repairs **inside one owned container**. The default
provider wrapper constructs actual CrewAI Agent/Task/Crew objects with its
bounded BaseLLM bridge; generic role names alone are not CrewAI execution. Only model
transport crosses the boundary: a finite host broker reads typed file requests
and returns actual response envelopes. It never executes generated source.

Authoring status: code and tests are supplied; no test, image build, Docker run,
package installation or provider call was executed by this author. These files
are not proof of successful project completion.

## Reproducible preparation (central QA)

From this directory, independently inspect these files and semantic_team.py.
Resolve a real lock with `uv lock --offline`, retain its full bytes and hash, then
run `uv sync --frozen --offline --no-dev` and `uv lock --check --offline`.
No invented lock is committed. The project uses Python 3.12 with the explicitly
pinned `crewai==1.15.40` runtime. The generated expense application remains
standard-library-only; the orchestrator has real SDK dependencies. Central QA
must resolve and inspect the actual full transitive lock and prepopulate a
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
images. Build only after their full inventories and provenance are approved,
with network disabled and no package downloads. Record the resulting immutable
image digest. Runtime `docker_argv` refuses tags and always uses `--pull=never`.
The launcher does not build or pull anything.

Create one new operator-owned mailbox tmpfs, at most 16 MiB, mode 0700. Central
QA is responsible for mounting and later unmounting exactly that owned tmpfs;
the launcher never runs arbitrary mount commands. Put only request.json in a
separate read-only input directory, with title and product_request strings.
Do not bind the repository root, home directories, credentials, Docker socket,
existing course files, or other users' files.

The caller supplies `container_launch.launch(image, inputs, mailbox, callback)`.
Inside the container, `CrewAIRoleProvider(MailboxProvider(), evidence_store)`
wraps each typed role request in actual CrewAI execution. Preserve separate
actual broker-response and framework-output lineage; SDK construction alone
does not prove a completed role, and a role cannot cause additional unbudgeted
model calls. Central QA must exercise that exact adapter and its call limit.
The trusted callback receives schema/role/payload/input_sha/ordinal/request_sha
and returns the exact semantic_team response envelope. It owns provider access
and must retain the real request ID, model identity and raw response. Requests
are reserved before transport, at most nine are made by the crew, and timeouts
remain UNKNOWN without retries. A used mailbox cannot be silently reused.

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

## Required observed evidence before lesson approval

1. Run tests/test_engineering_whole_crew.py and the semantic-team contract tests.
2. Inspect actual uv lock/check/sync and image build logs, image digest and source
   inventory. Run actual uv version/environment commands inside the image.
3. Execute one coherent authorized real-provider workflow through this launcher;
   retain every real response, four-role handoff, failing test source/output,
   any bounded repair and actual final acceptance observations.
4. Inspect finite output, no-network configuration, UID separation, immutable
   tests, mailbox limits, uncertain-call no-replay behavior and exact cleanup.
5. Independently review delivered files, dependency declarations, README and
   package inventory; perform fresh documented extraction/setup/tests. Capture
   the actual Docker/uv/crew/test screens. Test doubles are not live evidence.

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

This bridge and its new tests are authored pending central QA. Neither the
historical template ZIP test nor previous 130-test receipt proves these new bytes.
Actual clean extraction/setup/testing and independent source/material review of a
genuine whole-crew package remain required before the practical is approved.
