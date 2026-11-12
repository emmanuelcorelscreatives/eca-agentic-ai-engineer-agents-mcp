# Genuine Mastra Studio, owned local environment

Authoring instructions only; no Studio startup/capture/provider result is claimed.

Use the exact package lock admitted by central QA. From this directory run
`npm ci`, `npm run check`, then `npm test` only inside the admitted SDK helper.
Set `COURSE_MODEL` to an explicitly approved provider/model. Load a dedicated
Academy credential using the operator's secret environment mechanism, never a
command-line argument, screen-visible `.env`, shell tracing, or a shared account
profile. Inspect variable **names**, not values. `src/mastra/index.ts` registers
one actual triage agent and the deterministic fixture workflow; MCP exercises
have a separate bounded lifecycle in `withMcpAgent`.

Start `npm run dev -- --help` for the pinned CLI's actual supported flags, then
bind Studio to localhost in a controlled browser session. Do not assume a CLI
flag or advertise a listening URL until observed. Retain the actual startup
log, CLI version, PID/birth identity, local listener and clean shutdown receipt.
Never expose this development UI to the public network.

First inspect and run the deterministic workflow with `T-001`, then the failure
case `T-999`. Preserve actual run IDs, executed steps and exception details.
Only after separately approved model budget, run the Agent with an explicit
resource and thread ID; capture actual tool input/output and trace. Do not label
workflow-only execution as an LLM-generated response. Use a new Academy thread
and clean browser profile; avoid existing user data and credentials. End the
owned server using its verified process handle and confirm listener cleanup.

The native Memory test reopens a real LibSQL database and exercises two isolated
resources without any provider call. It proves persistence/storage boundaries,
not a model's ability to interpret a remembered follow-up; that needs a genuine
bounded two-turn `agent.generate` observation with actual structured-output
validation. Do not substitute generated screenshots for Studio captures.

## Stable dataset location in the actual Studio bundle

Mastra moves modules into `.mastra/output/index.mjs`; module-relative lookup
therefore does not locate the original repository dataset. Start every package
command from `examples/s24_mastra`, as the commands above require. The loader
resolves `../../data/s24_articles.json` from that **working directory**, not the
bundled module URL. Alternate launchers must set `COURSE_REPOSITORY_ROOT` to the
absolute root of the same frozen Academy repository. This variable is a path,
not a credential; do not print other environment values. Relative root overrides
fail before reading the dataset.

The loader verifies full fixture SHA256
`3e2f8e8bb583e9855112adda091f3189009928967dd22787c607d1769ef4d645`.
No copy into `.mastra` or runtime-only untracked fixture is permitted. Preserve
the original failed startup log. Central QA must repeat typecheck/tests and
actual Studio startup with the current source, retaining the resolved fixture
path/SHA, PID/listener and final shutdown proof; this edit itself is not a startup
PASS.
