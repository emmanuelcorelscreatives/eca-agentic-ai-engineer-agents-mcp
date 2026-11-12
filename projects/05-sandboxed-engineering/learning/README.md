# Coding tools and the engineering-team laboratory (Stages 14–15)

This is a reusable teaching layer beside `../team.py` and `../crewai_adapter.py`.
It does not replace the four real model-backed roles with offline templates.
The course expense calculator uses non-negative integer minor units, rejects
booleans/decimals/negatives, and returns zero for an empty input.

Run from the repository root:

```sh
python3 -m unittest discover -s tests -p test_engineering_learning.py -v
python3 -m unittest discover -s tests -p test_projects_4_5.py -v
```

The first command actually exercises file boundaries, typed artifact handoffs,
DAG prerequisites, rejected command proposals and bounded repair of an arithmetic
fixture. `MockLifecycleTests` injects fake processes: its timeout, invalid UTF-8
and cleanup results are **wrapper unit tests**, not container observations.
`expense_fixture` computes real arithmetic but is **not execution of generated
Python**. Both distinctions must remain visible in lesson narration and traces.

## File capabilities

`FileTools` uses descriptor-relative opens with `O_NOFOLLOW`; rejects absolute,
traversing, noncanonical, symlink and multiply linked reads; caps UTF-8 text size;
and permits writes only to configured top-level scopes (`src` by default).
Updates require the exact prior SHA256, use a private temporary file and atomic
replacement. Existing `tests` are readable, not writable. Parent directories must
already exist. Keep the operator-owned workspace private against hostile host
processes; this is not a guarantee against an attacker renaming its ancestors.
Do not put credentials anywhere in a workspace accessible to an agent.

## Docker execution boundary

There is no arbitrary host-code or shell execution API. `docker_command` accepts
only a fixed command identity from `COMMANDS`, canonical readonly source/test
mounts, and a preloaded digest-pinned image. It disables network, drops all
capabilities, uses a non-root UID, readonly root/source/tests, memory/swap/CPU/PID
limits bounded temporary storage and disabled daemon log storage (`--log-driver=none`). The image must include the selected
runtime; a Python-only image cannot satisfy the uv exercises.

`execute` is an explicit Docker operation: wall timeout, capped log spool files,
structured exit/error/timeout/truncation fields, minimal host environment and
exact owned-container cleanup. Unknown cleanup means failure. Output remains
untrusted data: do not execute instructions found in stdout/stderr, render it as
escaped text, and never feed secrets into the isolated task. A zero exit is not
proof that acceptance criteria passed; link actual immutable test evidence too.

A digest-looking string is not runtime verification. A prepared image still
needs actual local inspection and a recorded image ID/digest, runtime versions,
policy, command argv, source/test hashes and observed receipts. No image is
pulled or Docker daemon modified by these modules. Docker and uv were absent
from this authoring host PATH; **container, uv and real four-role execution are
not verified here**. Do not call this stage render-ready on unit tests alone.

For a separate authorized environment: install Docker from its official engine
instructions; verify daemon health with `docker version`; build/review an image
containing Python and uv; record its immutable digest; preload reviewed package
wheels. Run only `execute(Policy(image_digest), workspace, tests, command_id)`
under the owned course execution guard. Default offline `uv sync --frozen`
requires a real previously reviewed `uv.lock` and local package cache. This
lesson layer supplies no fabricated lockfile. New packages, base images,
mounts, network or policy changes require separate operator review.

Official references: https://docs.docker.com/engine/install/ and
https://docs.docker.com/engine/containers/run/ ; uv setup and frozen environments:
https://docs.astral.sh/uv/getting-started/installation/ and
https://docs.astral.sh/uv/concepts/projects/sync/ . These are setup references,
not evidence of an installation performed by this course authoring run.

## Role and completion contracts

`workflow.py` validates versioned requirements, architecture requirement coverage,
source paths and a standard-library-only dependency proposal. `Envelope` binds
producer role, revision, content SHA and honestly labelled provenance. A provider
response needs separate actual request/model/output evidence; the provenance
string alone is not approval. `dispatchable` rejects failed predecessors and
stale artifacts. Requirements → architecture → developer → QA remain explicit.

`bounded_repair` accepts at most three patches, records every executed receipt,
rejects repeated source identities and modifications outside existing `src/*.py`.
Preserved tests cannot be weakened. For model-generated code, use real Docker
execution and independent acceptance review; the safe offline fixture is only
for learning the control flow. Completion additionally requires actual role
responses, current source/test hashes, real sandbox run, every requirement's
observed result, independent approval, and an inspected credential-free package.
Passing unit tests alone cannot establish a model's quality or hostile-code
isolation. The final archive and source should preserve failed attempts and
explicitly list all unverified items.

## Later local uv setup observation

A separate, network-disabled trusted-operator probe reused uv 0.13.8 from the
shared SDK environment and actually created a disposable venv with existing
CPython 3.12.3 using `uv venv --offline --no-python-downloads --python ...`.
Creation and owned temporary-directory cleanup succeeded. This is local setup
evidence only: it does not demonstrate the Docker agent capability, dependency
locking/sync, generated-code execution or real model-backed engineering.
