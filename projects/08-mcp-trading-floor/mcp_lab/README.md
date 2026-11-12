# MCP protocol laboratory

This lab uses the **official Python MCP SDK 1.26.0**. It is distinct from the trading service adapter. The host owns model invocation and approval; the MCP server advertises capabilities and cannot execute trades.

```sh
python3 -m venv .venv
.venv/bin/pip install -r projects/08-mcp-trading-floor/mcp_lab/requirements.txt
.venv/bin/python -m unittest discover -s tests -p test_project8_mcp_protocol.py -v
```

Tests connect to actual subprocess stdio and loopback Streamable HTTP servers, initialize a session, discover tools/resources/prompts, validate inputs, read exact resource bytes and retrieve a parameterized prompt. The host sampling callback deliberately returns a deterministic fixture: this proves the sampling protocol round-trip, **not real model inference**. A tool's structured `ok:false` error is an application error; invalid SDK argument schemas produce MCP `isError`. Discovery grants no authorization.

## Boundaries

`ACADEMY_MCP_ROOT` contains only original course fixtures. Absolute paths, traversal and resolved symlink escapes are rejected; files must be UTF-8 and at most64KiB. Do not put personal files or secrets in this directory. Root containment is a course sandbox boundary, not protection against an adversary modifying its filesystem concurrently.

The HTTP example binds127.0.0.1 only. Set an unpredictable `ACADEMY_MCP_TOKEN` in the process environment, never a prompt/log/repository. Every HTTP request is checked before MCP handling. This operator-provisioned bearer-token teaching boundary is **not an implementation of MCP OAuth discovery, protected-resource metadata or delegated authorization**. Do not expose it publicly as an OAuth-compliant server. Deploy real TLS/authz using the official specification before remote use.

```sh
ACADEMY_MCP_TRANSPORT=http ACADEMY_MCP_PORT=8765 ACADEMY_MCP_TOKEN="$COURSE_LOCAL_TOKEN" .venv/bin/python projects/08-mcp-trading-floor/mcp_lab/server.py
```

## Exercises

1. Inspect actual initialize capabilities. Explain why `tools` support does not permit a trade.
2. Compare `read_course_file`, `academy://handbook` and `research_brief`. Retrieving a prompt does not execute it.
3. Add a denied sampling callback. Observe the tool failure and keep the host in control.
4. Create a symlink outside the fixture root and run the containment regression.
5. Try the HTTP route without a bearer token and record the real401 response.

## Instructor reference and remaining named integrations

Official SDK: https://github.com/modelcontextprotocol/python-sdk/tree/v1.x
Official Node filesystem server: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
Inspector: https://github.com/modelcontextprotocol/inspector
Playwright MCP: https://github.com/microsoft/playwright-mcp

The Node filesystem server must be launched with an explicitly created Academy-only root. Its advertised tools differ from this custom teaching server; it does not automatically provide this lab's resources/prompts. Inspector is a genuine GUI and needs its own actual browser capture; a passing SDK test is not an Inspector screenshot. Playwright MCP requires an isolated browser profile and a finite allowlisted course fixture, not the account's existing browser. These named integrations are marked separately in verification, never inferred from Python tests.

## Official Node filesystem integration

The separate `node-filesystem/package.json` pins the real `@modelcontextprotocol/server-filesystem` release2.3.0 read from npm metadata. Its lockfile freezes transitive dependencies after installation:

```sh
cd projects/08-mcp-trading-floor/mcp_lab/node-filesystem
npm ci
cd ../../../..
.venv/bin/python -m unittest discover -s tests -p test_project8_mcp_protocol.py -v
```

This existing server supports more operations than the course agent should receive. `client_policy.ReadOnlyHost` filters its discovered tools and rejects every call outside the read/list allowlist before transport. Students should still launch it with only a newly created Academy fixture root; host filtering and path containment are separate controls. No capability list makes untrusted server content authoritative instructions.

For Inspector, install a reviewed fixed Inspector version separately and launch it against the same explicit server command/root. Do not expose Inspector's development proxy publicly or disable its authentication. A capture must show the actual successful connection/capability list; protocol test evidence is not a substitute. Inspector/browser, fetch and Playwright named integrations remain untested here until separately recorded actual runs.
