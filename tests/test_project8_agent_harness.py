"""Host-control tests are explicitly separate from optional real MCP sessions.

These source-authored tests have no import-time SDK dependency or provider call.
The central QA owner must execute them and record the actual outcomes.
"""
import asyncio
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest

PROJECT = Path(__file__).resolve().parents[1] / "projects/08-mcp-trading-floor"
spec = importlib.util.spec_from_file_location("academy_project8_agent_harness", PROJECT / "agent_harness.py")
h = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = h
spec.loader.exec_module(h)


def fixture_validator(arguments, schema):
    """A fixture validator for control-flow tests, NOT JSON Schema evidence."""
    if set(arguments) != {"query"} or not isinstance(arguments["query"], str):
        raise h.HostError("SCHEMA_INVALID", "Expected fixture query string")


class SessionFixture:
    """Labeled SDK-shape double. Actual transport test is a separate method."""
    def __init__(self, *, delayed=False, failure=False, binary=False):
        self.calls = []
        self.delayed, self.failure, self.binary = delayed, failure, binary

    async def list_tools(self):
        return NS(tools=[NS(name="lookup", inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}),
                         NS(name="write_report", inputSchema={"type": "object"})])

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if self.delayed:
            await asyncio.sleep(10)
        if self.failure:
            raise ConnectionError("FAKE_SECRET_CANARY_MUST_NOT_BE_IN_TRACE")
        return {"isError": False, "content": [{"type": "text", "text": "Observed fixture evidence"}]}

    async def list_resources(self):
        return NS(resources=[NS(uri="academy://guide")])

    async def read_resource(self, uri):
        return NS(contents=[NS(blob="AA==") if self.binary else NS(text="Exact original course guide")])

    async def list_prompts(self):
        return NS(prompts=[NS(name="brief", arguments=[NS(name="topic", required=True)])])

    async def get_prompt(self, name, arguments):
        return {"messages": [{"role": "user", "content": {"type": "text", "text": "Research " + arguments["topic"]}}]}


class SequenceProvider:
    """Deterministic action fixture; never labeled an AI observation."""
    def __init__(self, actions):
        self.actions, self.inputs = iter(actions), []

    async def next_action(self, messages, tools):
        self.inputs.append((messages, tools))
        return next(self.actions)


class HarnessTests(unittest.IsolatedAsyncioTestCase):
    async def registry(self, sessions=None, allowed=None, **kwargs):
        registry = h.MCPRegistry(sessions or {"files": SessionFixture()}, allowed if allowed is not None else {"files::lookup"}, schema_validator=fixture_validator, **kwargs)
        await registry.discover()
        return registry

    async def test_cross_server_collision_and_exact_routing(self):
        files, fetch = SessionFixture(), SessionFixture()
        registry = await self.registry({"files": files, "fetch": fetch}, {"files::lookup", "fetch::lookup"})
        self.assertEqual({d["name"] for d in registry.descriptors()}, {"files::lookup", "fetch::lookup"})
        result = await registry.dispatch("fetch::lookup", {"query": "course product"})
        self.assertEqual(result.status, "ok")
        self.assertEqual(files.calls, [])
        self.assertEqual(fetch.calls, [("lookup", {"query": "course product"})])

    async def test_bad_arguments_unknown_hidden_and_revoked_zero_calls(self):
        session = SessionFixture()
        registry = await self.registry({"files": session})
        invalid = await registry.dispatch("files::lookup", {"query": 3})
        self.assertEqual(invalid.error_code, "SCHEMA_INVALID")
        for name in ("files::write_report", "files::new_tool", "lookup"):
            self.assertEqual((await registry.dispatch(name, {"query": "x"})).error_code, "PERMISSION_DENIED")
        registry.revoke("files::lookup")
        self.assertEqual((await registry.dispatch("files::lookup", {"query": "x"})).error_code, "PERMISSION_DENIED")
        self.assertEqual(session.calls, [])

    async def test_progressive_lists_are_role_local_and_calls_enforced(self):
        shared = SessionFixture()
        first = await self.registry({"files": shared}, set())
        second = await self.registry({"files": shared}, set())
        self.assertEqual(first.descriptors(), ())
        with self.assertRaises(h.HostError):
            first.expose("files::lookup")
        first.expose("files::lookup", host_authorized=True)
        self.assertEqual(len(first.descriptors()), 1)
        self.assertEqual(second.descriptors(), ())
        self.assertEqual((await second.dispatch("files::lookup", {"query": "x"})).error_code, "PERMISSION_DENIED")

    async def test_resource_exact_text_unknown_binary_and_unsupported(self):
        registry = await self.registry(allowed_resources={("files", "academy://guide"), ("files", "academy://absent")})
        self.assertEqual(await registry.read_resource("files", "academy://guide"), "Exact original course guide")
        with self.assertRaises(h.HostError) as unknown:
            await registry.read_resource("files", "academy://absent")
        self.assertEqual(unknown.exception.code, "RESOURCE_UNKNOWN")
        registry.sessions["files"].binary = True
        with self.assertRaises(h.HostError) as binary:
            await registry.read_resource("files", "academy://guide")
        self.assertEqual(binary.exception.code, "RESOURCE_NON_TEXT")
        registry.sessions["files"] = object()
        with self.assertRaises(h.HostError) as unsupported:
            await registry.read_resource("files", "academy://guide")
        self.assertEqual(unsupported.exception.code, "RESOURCE_UNSUPPORTED_OR_FAILED")

    async def test_prompt_supplied_arguments_missing_unknown_no_permissions(self):
        registry = await self.registry(allowed_prompts={("files", "brief"), ("files", "absent")})
        before = registry.descriptors()
        prompt = await registry.get_prompt("files", "brief", {"topic": "synthetic markets"})
        self.assertIn("synthetic markets", prompt[0]["content"]["text"])
        with self.assertRaises(h.HostError) as missing:
            await registry.get_prompt("files", "brief", {})
        self.assertEqual(missing.exception.code, "PROMPT_ARGUMENT_INVALID")
        with self.assertRaises(h.HostError) as unknown:
            await registry.get_prompt("files", "absent", {})
        self.assertEqual(unknown.exception.code, "PROMPT_UNKNOWN")
        self.assertEqual(before, registry.descriptors())
        self.assertEqual(registry.sessions["files"].calls, [])

    async def test_concurrent_call_ids_latency_and_no_secret_exception_trace(self):
        registry = await self.registry({"one": SessionFixture(), "two": SessionFixture(failure=True)}, {"one::lookup", "two::lookup"})
        results = await asyncio.gather(registry.dispatch("one::lookup", {"query": "PRIVATE_QUERY_CANARY"}), registry.dispatch("two::lookup", {"query": "other"}))
        self.assertEqual([row.status for row in results], ["ok", "error"])
        self.assertNotEqual(results[0].call_id, results[1].call_id)
        terminal = [row for row in registry.trace if row["event"] == "end"]
        self.assertEqual(len(terminal), 2)
        self.assertTrue(all(row["latency_ms"] >= 0 for row in terminal))
        self.assertNotIn("PRIVATE_QUERY_CANARY", str(registry.trace))
        self.assertNotIn("FAKE_SECRET_CANARY", str(registry.trace))

    async def test_timeout_is_bounded_and_no_retry(self):
        session = SessionFixture(delayed=True)
        registry = await self.registry({"files": session})
        result = await registry.dispatch("files::lookup", {"query": "x"}, .01)
        self.assertEqual(result.error_code, "TIMEOUT")
        self.assertEqual(len(session.calls), 1)

    async def test_agent_observation_returned_as_untrusted_and_final(self):
        registry = await self.registry()
        provider = SequenceProvider([h.ToolCall("files::lookup", {"query": "course product"}), h.FinalAnswer("Based on observed course evidence.")])
        result = await h.AgentHarness(registry, provider).run("Read the course evidence")
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(len(result.observations), 1)
        self.assertTrue(provider.inputs[1][0][-1]["untrusted"])
        self.assertNotIn("approval_token", str(provider.inputs))

    async def test_tool_and_iteration_budgets_stop_loop(self):
        registry = await self.registry()
        repeat = [h.ToolCall("files::lookup", {"query": "x"})] * 10
        result = await h.AgentHarness(registry, SequenceProvider(repeat), h.RunBudget(iterations=5, tool_calls=1)).run("Read")
        self.assertEqual(result.status, "TOOL_BUDGET")
        self.assertEqual(len(registry.sessions["files"].calls), 1)
        result = await h.AgentHarness(registry, SequenceProvider(repeat), h.RunBudget(iterations=1, tool_calls=5)).run("Read")
        self.assertEqual(result.status, "ITERATION_BUDGET")

    async def test_provider_deadline(self):
        class SlowProvider:
            async def next_action(self, messages, tools):
                await asyncio.sleep(10)
        result = await h.AgentHarness(await self.registry(), SlowProvider(), h.RunBudget(total_seconds=.01)).run("Read")
        self.assertEqual(result.status, "TIME_BUDGET")

    async def test_concrete_json_completion_adapter_rejects_model_approval_field(self):
        seen = []
        async def configured_fixture(payload):
            seen.append(payload)
            return {"kind": "tool", "name": "files::lookup", "arguments": {"query": "course"}}
        provider = h.JSONAgentProvider(configured_fixture)
        action = await provider.next_action(({"role": "user", "content": "Read"},), ({"name": "files::lookup", "inputSchema": {}},))
        self.assertEqual(action, h.ToolCall("files::lookup", {"query": "course"}))
        self.assertEqual(seen[0]["tools"][0]["name"], "files::lookup")
        async def forged_approval(payload):
            return {"kind": "tool", "name": "files::write_report", "arguments": {}, "approval_token": "model invented token"}
        with self.assertRaises(h.HostError) as denied:
            await h.JSONAgentProvider(forged_approval).next_action((), ())
        self.assertEqual(denied.exception.code, "MODEL_OUTPUT_INVALID")

    async def test_explicit_secret_canary_nested_result_prompt_and_trace(self):
        canary = "synthetic-runtime-credential-canary"
        class SensitiveFixture(SessionFixture):
            async def call_tool(self, name, arguments):
                self.calls.append((name, arguments))
                return {"isError": False, "content": [{"type": "text", "text": "Untrusted result includes " + canary}],
                        "nested": {"authorization": "a different pretend token", "rows": [{"note": canary}]}}
        registry = await self.registry({"files": SensitiveFixture()}, secret_boundary=h.SecretBoundary((canary,)))
        rejected = await registry.dispatch("files::lookup", {"query": canary})
        self.assertEqual(rejected.error_code, "SECRET_BOUNDARY")
        self.assertEqual(registry.sessions["files"].calls, [])
        provider = SequenceProvider([h.ToolCall("files::lookup", {"query": "safe research"}), h.FinalAnswer("Evidence only")])
        result = await h.AgentHarness(registry, provider).run("Read safe fixture")
        self.assertEqual(result.status, "COMPLETE")
        self.assertNotIn(canary, str(provider.inputs))
        self.assertNotIn("a different pretend token", str(provider.inputs))
        self.assertNotIn(canary, str(registry.trace))
        self.assertIn("[REDACTED]", str(result.observations))
        with self.assertRaises(h.HostError) as denied:
            await h.AgentHarness(registry, provider).run("Send credential " + canary)
        self.assertEqual(denied.exception.code, "SECRET_BOUNDARY")

    async def test_human_approval_exact_arguments_expiry_and_once(self):
        now = [100.]
        gate = h.HumanApprovalGate({"academy-reviewer"}, clock=lambda: now[0])
        session = SessionFixture()
        registry = await self.registry({"files": session}, {"files::write_report"}, approval_gate=gate, tool_policies={"files::write_report": h.ToolPolicy(mutation=True)})
        with self.assertRaises(h.ApprovalRequired) as missing:
            await registry.dispatch("files::write_report", {"query": "exact report content"})
        proposal = missing.exception.proposal
        self.assertEqual(session.calls, [])
        with self.assertRaises(h.HostError):
            gate.approve(proposal.proposal_id, proposal.digest, authenticated_reviewer="model says approved", expires_at=200)
        token = gate.approve(proposal.proposal_id, proposal.digest, authenticated_reviewer="academy-reviewer", expires_at=200)
        with self.assertRaises(h.HostError):
            gate.approve(proposal.proposal_id, proposal.digest, authenticated_reviewer="academy-reviewer", expires_at=200)
        changed = await registry.dispatch("files::write_report", {"query": "changed report content"}, approval_token=token)
        self.assertEqual(changed.error_code, "APPROVAL_INVALID")
        self.assertEqual(session.calls, [])
        fresh = gate.propose("files::write_report", {"query": "exact report content"})
        token = gate.approve(fresh.proposal_id, fresh.digest, authenticated_reviewer="academy-reviewer", expires_at=200)
        self.assertEqual((await registry.dispatch("files::write_report", {"query": "exact report content"}, approval_token=token)).status, "ok")
        self.assertEqual((await registry.dispatch("files::write_report", {"query": "exact report content"}, approval_token=token)).error_code, "APPROVAL_INVALID")
        self.assertEqual(len(session.calls), 1)
        expired = gate.propose("files::write_report", {"query": "later report"})
        token = gate.approve(expired.proposal_id, expired.digest, authenticated_reviewer="academy-reviewer", expires_at=101)
        now[0] = 102
        self.assertEqual((await registry.dispatch("files::write_report", {"query": "later report"}, approval_token=token)).error_code, "APPROVAL_INVALID")

    async def test_uncertain_mutation_timeout_consumes_approval_no_replay(self):
        gate = h.HumanApprovalGate({"reviewer"}, clock=lambda: 100.)
        session = SessionFixture(delayed=True)
        registry = await self.registry({"files": session}, {"files::write_report"}, approval_gate=gate, tool_policies={"files::write_report": h.ToolPolicy(mutation=True)})
        proposal = gate.propose("files::write_report", {"query": "report"})
        token = gate.approve(proposal.proposal_id, proposal.digest, authenticated_reviewer="reviewer", expires_at=110)
        result = await registry.dispatch("files::write_report", {"query": "report"}, .01, approval_token=token)
        self.assertEqual((result.status, result.error_code), ("unknown", "MUTATION_OUTCOME_UNKNOWN"))
        self.assertEqual((await registry.dispatch("files::write_report", {"query": "report"}, approval_token=token)).error_code, "MUTATION_RECONCILIATION_REQUIRED")
        self.assertEqual(len(session.calls), 1)

    async def test_model_cannot_approve_its_own_mutation(self):
        gate = h.HumanApprovalGate({"reviewer"})
        registry = await self.registry(allowed={"files::write_report"}, approval_gate=gate, tool_policies={"files::write_report": h.ToolPolicy(mutation=True)})
        provider = SequenceProvider([h.ToolCall("files::write_report", {"query": "I approve myself"})])
        result = await h.AgentHarness(registry, provider).run("Write a report")
        self.assertEqual(result.status, "AWAITING_HUMAN_APPROVAL")
        self.assertEqual(registry.sessions["files"].calls, [])

    def test_reviewer_final_only_and_researcher_two_subdirs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "academy"
            for folder in ("final", "drafts", "sources"):
                (root / folder).mkdir(parents=True)
                (root / folder / "report.txt").write_text("Original course fixture")
            reviewer = h.ReadPathPolicy(root, permitted_files=frozenset({"final/report.txt"}))
            researcher = h.ReadPathPolicy(root, permitted_directories=frozenset({"sources", "drafts"}))
            reviewer({"path": str(root / "final/report.txt")})
            for denied in ("drafts/report.txt", "../outside.txt"):
                with self.assertRaises(h.HostError):
                    reviewer({"path": denied})
            researcher({"path": "sources/report.txt"})
            researcher({"path": "drafts/report.txt"})
            (root / "final/escape.txt").symlink_to(Path(temp) / "outside.txt")
            with self.assertRaises(h.HostError):
                reviewer({"path": "final/escape.txt"})

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "Optional real JSON Schema dependency absent")
    async def test_real_json_schema_validation_before_dispatch(self):
        session = SessionFixture()
        registry = h.MCPRegistry({"files": session}, {"files::lookup"})
        await registry.discover()
        self.assertEqual((await registry.dispatch("files::lookup", {"query": 5})).error_code, "SCHEMA_INVALID")
        self.assertEqual(session.calls, [])
        self.assertEqual((await registry.dispatch("files::lookup", {"query": "valid"})).status, "ok")

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "Optional real JSON Schema dependency absent")
    def test_external_schema_refs_rejected_without_resolving(self):
        with self.assertRaises(h.HostError) as denied:
            h.validate_schema({}, {"$ref": "https://example.invalid/never-fetch-this-schema"})
        self.assertEqual(denied.exception.code, "SCHEMA_UNSAFE")

    async def test_denied_proposal_has_no_usable_approval(self):
        gate = h.HumanApprovalGate({"reviewer"}, clock=lambda: 100.)
        proposal = gate.propose("files::write_report", {"path": "final/report.txt", "content": "Original report"})
        gate.deny(proposal.proposal_id, authenticated_reviewer="reviewer")
        with self.assertRaises(h.HostError):
            gate.approve(proposal.proposal_id, proposal.digest, authenticated_reviewer="reviewer", expires_at=110.)

    @unittest.skipUnless(importlib.util.find_spec("mcp") and importlib.util.find_spec("jsonschema"), "Optional actual SDK integration requires project8 runtime")
    async def test_actual_stdio_registry_tool_resource_and_prompt(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        server = StdioServerParameters(command=sys.executable, args=[str(PROJECT / "mcp_lab/server.py")])
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                registry = h.MCPRegistry({"lab": session}, {"lab::quote"}, allowed_resources={("lab", "academy://handbook")}, allowed_prompts={("lab", "research_brief")})
                await registry.discover()
                self.assertEqual((await registry.dispatch("lab::quote", {"symbol": "ACME", "quantity": "bad"})).error_code, "SCHEMA_INVALID")
                observed = await registry.dispatch("lab::quote", {"symbol": "ACME", "quantity": 1})
                self.assertEqual(observed.status, "ok")
                self.assertIn("synthetic", str(observed.data))
                self.assertEqual(await registry.read_resource("lab", "academy://handbook"), (PROJECT / "mcp_lab/fixtures/handbook.md").read_text())
                messages = await registry.get_prompt("lab", "research_brief", {"symbol": "ACME"})
                self.assertIn("ACME", str(messages))

    @unittest.skipUnless(importlib.util.find_spec("mcp") and importlib.util.find_spec("jsonschema"), "Optional actual SDK integration requires project8 runtime")
    async def test_actual_official_filesystem_approved_write_exact_bytes(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        node_server = PROJECT / "mcp_lab/node-filesystem/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js"
        if not node_server.is_file():
            self.skipTest("Official Node filesystem dependency absent")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            destination = root / "approved-report.txt"
            arguments = {"path": str(destination), "content": "Original Academy report: synthetic evidence only.\n"}
            gate = h.HumanApprovalGate({"course-reviewer"}, clock=lambda: 100.)
            server = StdioServerParameters(command="node", args=[str(node_server), str(root)])
            async with stdio_client(server) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    registry = h.MCPRegistry({"sandbox": session}, {"sandbox::write_file"}, approval_gate=gate,
                                             tool_policies={"sandbox::write_file": h.ToolPolicy(mutation=True, argument_check=h.ReadPathPolicy(root, permitted_files=frozenset({destination.name})))})
                    await registry.discover()
                    with self.assertRaises(h.ApprovalRequired) as pending:
                        await registry.dispatch("sandbox::write_file", arguments)
                    self.assertFalse(destination.exists())
                    proposal = pending.exception.proposal
                    token = gate.approve(proposal.proposal_id, proposal.digest, authenticated_reviewer="course-reviewer", expires_at=110.)
                    observed = await registry.dispatch("sandbox::write_file", arguments, approval_token=token)
                    self.assertEqual(observed.status, "ok")
                    self.assertEqual(destination.read_text(), arguments["content"])
                    destination.write_text("A later independent human edit")
                    denied = await registry.dispatch("sandbox::write_file", arguments, approval_token=token)
                    self.assertEqual(denied.error_code, "APPROVAL_INVALID")
                    self.assertEqual(destination.read_text(), "A later independent human edit")


if __name__ == "__main__":
    unittest.main()
