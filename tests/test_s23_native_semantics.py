"""Real SDK runtime tests with an explicitly scripted, zero-provider client.

Execute only in the centrally admitted Microsoft 1.16.1 SDK environment.
No test result is asserted by this authored file's existence.
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
if os.environ.get("ECA_FRAMEWORK_FAMILY") != "microsoft":
    raise unittest.SkipTest("Select the genuine Microsoft SDK environment; a skip is not a pass")
from agent_framework import BaseChatClient, ChatResponse, Content, Message, AgentSession, FunctionInvocationLayer, ChatMiddlewareLayer
from examples.s23_microsoft_native import (
    Ticket, Decision, Escalation, ApprovalLedger, Telemetry, build_specialist,
    build_workflow, decide, save_session, load_session, tools_for,
)


class ScriptedClient(FunctionInvocationLayer, ChatMiddlewareLayer, BaseChatClient):
    """Explicit test double for model outputs; framework/tool/graph are genuine."""
    def __init__(self, replies):
        super().__init__()
        self.replies = list(replies)
        self.inputs = []

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        if stream:
            raise NotImplementedError("This fixture tests non-streaming only")
        self.inputs.append(list(messages))
        reply = self.replies.pop(0)
        content = reply if isinstance(reply, list) else [Content.from_text(reply)]
        return ChatResponse(messages=[Message(role="assistant", contents=content)],
                            response_id=f"scripted-{len(self.inputs)}")


def ticket(category="damaged"):
    return Ticket(ticket_id="T-ACADEMY-1", category=category, product_id="P-KEY", message="Synthetic exercise")


def output(category="damaged"):
    return Decision(ticket_id="T-ACADEMY-1", category=category,
                    recommendation="Review synthetic policy", held=False).model_dump_json()


class NativeSemantics(unittest.IsolatedAsyncioTestCase):
    async def test_schema_and_identity(self):
        with self.assertRaises(ValueError):
            Ticket(ticket_id="X", category="invented", product_id="P", message="x")
        for reply in ['{}', '{"ticket_id":"wrong","category":"damaged","recommendation":"x","held":false}']:
            agent = build_specialist(ScriptedClient([reply]), "damage", Telemetry(), ApprovalLedger())
            with self.assertRaises(Exception):
                await decide(agent, ticket())
        agent = build_specialist(ScriptedClient([output()]), "damage", Telemetry(), ApprovalLedger())
        self.assertEqual((await decide(agent, ticket())).ticket_id, "T-ACADEMY-1")

    async def test_native_tool_validation_rejects_before_effect(self):
        ledger = ApprovalLedger()
        escalation = tools_for(ledger)[1]
        with self.assertRaises(Exception):
            await escalation.invoke(arguments={"ticket_id": "T-ACADEMY-1"})
        self.assertEqual(ledger.effects, [])

    async def test_exact_approval_in_native_invocation_loop(self):
        approved = Escalation(ticket_id="T-ACADEMY-1", draft="Exact draft")
        for grant, draft, success in [(False, "Exact draft", False),
                                     (True, "Changed draft", False), (True, "Exact draft", True)]:
            ledger, telemetry = ApprovalLedger(), Telemetry()
            if grant:
                ledger.approve(approved, "Academy reviewer")
            call = Content.from_function_call("call-1", "record_escalation",
                    arguments={"ticket_id": approved.ticket_id, "draft": draft})
            client = ScriptedClient([[call], output()])
            agent = build_specialist(client, "damage", telemetry, ledger)
            if success:
                await decide(agent, ticket())
                self.assertEqual(len(ledger.effects), 1)
                # Even direct native-tool invocation cannot replay the consumed grant.
                with self.assertRaises(Exception):
                    await tools_for(ledger)[1].invoke(arguments=approved.model_dump())
            else:
                with self.assertRaises(Exception):
                    await decide(agent, ticket())
                self.assertEqual(ledger.effects, [])
            self.assertIn("tool", {event["phase"] for event in telemetry.events})

    async def test_native_graph_both_routes_and_held_ambiguity(self):
        for category in ["damaged", "delivery", "unknown"]:
            clients = {}
            def factory(name):
                clients[name] = ScriptedClient([output(category)])
                return clients[name]
            workflow = build_workflow(factory)
            events = await workflow.run(ticket(category))
            results = events.get_outputs()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].category, category)
            if category == "unknown":
                self.assertTrue(results[0].held)
                self.assertEqual(sum(len(c.inputs) for c in clients.values()), 0)
            else:
                selected = "damage" if category == "damaged" else "delivery"
                self.assertEqual(len(clients[selected].inputs), 1)
                self.assertEqual(len(clients["review"].inputs), 1)
                rendered = " ".join(m.text for m in clients["review"].inputs[0])
                self.assertIn("Research to independently review", rendered)

    async def test_native_session_history_cold_process_and_owner_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            client = ScriptedClient([output(), output()])
            agent = build_specialist(client, "damage", Telemetry(), ApprovalLedger())
            session = AgentSession()
            await decide(agent, ticket(), session)
            save_session(path, "student-A", session)
            with self.assertRaises(ValueError):
                load_session(path, "student-B")
            code = ('import sys; from pathlib import Path; '
                    'from examples.s23_microsoft_native import load_session; '
                    's=load_session(Path(sys.argv[1]),"student-A"); '
                    'print(s.session_id); assert s.state')
            completed = subprocess.run([sys.executable, "-c", code, str(path)],
                                       capture_output=True, text=True, check=True)
            self.assertEqual(completed.stdout.strip(), session.session_id)
            restored = load_session(path, "student-A")
            await decide(agent, ticket(), restored)
            self.assertGreater(len(client.inputs[1]), len(client.inputs[0]))
            fresh = AgentSession()
            self.assertEqual(fresh.state, {})

    async def test_real_middleware_correlation_timings_and_secret_redaction(self):
        secret = "CANARY-DO-NOT-LOG"
        telemetry = Telemetry(correlation=f"case-{secret}", secrets=[secret])
        agent = build_specialist(ScriptedClient([output()]), "damage", telemetry, ApprovalLedger())
        await decide(agent, ticket())
        self.assertTrue({"agent", "model"} <= {e["phase"] for e in telemetry.events})
        self.assertTrue(all(e["duration_ns"] >= 0 for e in telemetry.events))
        self.assertNotIn(secret, json.dumps(telemetry.events))
        self.assertEqual(len({e["correlation"] for e in telemetry.events}), 1)
        failing = build_specialist(ScriptedClient([]), "damage", telemetry, ApprovalLedger())
        with self.assertRaises(Exception):
            await decide(failing, ticket())
        self.assertTrue(any(e["outcome"] == "error" for e in telemetry.events))



# Additional real tool-output observation is deliberately separate from model intelligence.
class PolicyToolRuntime(unittest.IsolatedAsyncioTestCase):
    async def test_native_readonly_tool_invocation_has_observed_result(self):
        telemetry, ledger = Telemetry(), ApprovalLedger()
        client = ScriptedClient([[Content.from_function_call("lookup-1", "policy_lookup",
                                 arguments={"product_id": "P-KEY"})], output()])
        agent = build_specialist(client, "damage", telemetry, ledger)
        await decide(agent, ticket())
        tool_messages = [m for m in client.inputs[1] if m.role == "tool"]
        self.assertTrue(tool_messages)
        self.assertIn("POL-KEY-1", str([m.to_dict() for m in tool_messages]))
        self.assertEqual(ledger.effects, [])

if __name__ == "__main__":
    unittest.main()
