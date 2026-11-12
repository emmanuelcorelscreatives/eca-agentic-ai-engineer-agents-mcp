"""Real installed SDK and subprocess transport tests, without a model provider."""
import asyncio
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import urllib.error

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.types import CreateMessageResult, TextContent
except ModuleNotFoundError as exc:
    if exc.name == "mcp":
        raise unittest.SkipTest("Optional SDK integration requires mcp_lab/requirements.txt") from exc
    raise

LAB = Path(__file__).resolve().parents[1] / "projects/08-mcp-trading-floor/mcp_lab"
TOKEN = "course-only-test-token-0123456789"


async def sampler(context, params):
    # A deterministic host policy callback, NOT a claim of real model inference.
    if params.maxTokens > 80:
        raise ValueError("Sampling token policy exceeded")
    return CreateMessageResult(role="assistant", content=TextContent(type="text", text="Deterministic host sampling fixture"), model="deterministic-course-fixture", stopReason="endTurn")


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_discovery_calls_resources_prompts_sampling_errors(self):
        server = StdioServerParameters(command=sys.executable, args=[str(LAB / "server.py")])
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write, sampling_callback=sampler) as session:
                initialized = await session.initialize()
                self.assertTrue(initialized.protocolVersion)
                self.assertIsNotNone(initialized.capabilities.tools)
                self.assertIsNotNone(initialized.capabilities.resources)
                self.assertIsNotNone(initialized.capabilities.prompts)
                tools = await session.list_tools()
                names = {t.name for t in tools.tools}
                self.assertEqual(names, {"quote", "read_course_file", "sampled_summary"})
                self.assertNotIn("execute_order", names)
                quote = await session.call_tool("quote", {"symbol": "ACME", "quantity": 2})
                self.assertFalse(quote.isError)
                self.assertEqual(json.loads(quote.content[0].text)["price_cents"], 1200)
                invalid = await session.call_tool("quote", {"symbol": "ACME", "quantity": "bad"})
                self.assertTrue(invalid.isError)
                denied = await session.call_tool("read_course_file", {"path": "../../secrets.txt"})
                self.assertEqual(json.loads(denied.content[0].text)["error"]["code"], "PERMISSION_DENIED")
                absent = await session.call_tool("read_course_file", {"path": "absent.md"})
                self.assertEqual(json.loads(absent.content[0].text)["error"]["code"], "NOT_FOUND")
                unsupported = await session.call_tool("missing_tool", {})
                self.assertTrue(unsupported.isError)
                resources = await session.list_resources()
                self.assertEqual([str(x.uri) for x in resources.resources], ["academy://handbook"])
                content = await session.read_resource("academy://handbook")
                self.assertEqual(content.contents[0].text, (LAB / "fixtures/handbook.md").read_text())
                prompts = await session.list_prompts()
                self.assertEqual(prompts.prompts[0].name, "research_brief")
                prompt = await session.get_prompt("research_brief", {"symbol": "NOVA"})
                self.assertIn("NOVA", prompt.messages[0].content.text)
                sampling = await session.call_tool("sampled_summary", {"topic": "least privilege"})
                self.assertIn("Deterministic host sampling fixture", sampling.content[0].text)
                self.assertEqual(importlib.metadata.version("mcp"), "1.26.0")

    async def test_streamable_http_auth_and_real_session(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        env = dict(os.environ, ACADEMY_MCP_TRANSPORT="http", ACADEMY_MCP_TOKEN=TOKEN, ACADEMY_MCP_PORT=str(port))
        process = subprocess.Popen([sys.executable, str(LAB / "server.py")], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            url = f"http://127.0.0.1:{port}/mcp"
            ready = False
            for _ in range(100):
                if process.poll() is not None:
                    self.fail("HTTP server terminated: " + process.stderr.read().decode())
                try:
                    await asyncio.to_thread(urllib.request.urlopen, url, timeout=1)
                except urllib.error.HTTPError as exc:
                    self.assertEqual(exc.code, 401)
                    ready = True
                    break
                except OSError:
                    await asyncio.sleep(.05)
            self.assertTrue(ready, "HTTP startup timed out")
            async with streamablehttp_client(url, headers={"Authorization": "Bearer " + TOKEN}) as (read, write, session_id):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("quote", {"symbol": "NOVA", "quantity": 1})
                    self.assertEqual(json.loads(result.content[0].text)["price_cents"], 850)
                    self.assertIsNotNone(session_id())
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            process.stderr.close()

    async def test_official_node_filesystem(self):
        script = LAB / "node-filesystem/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js"
        if not script.is_file():
            self.skipTest("Run npm ci in mcp_lab/node-filesystem for the named Node integration")
        with tempfile.TemporaryDirectory() as temp:
            allowed = Path(temp) / "academy"
            allowed.mkdir()
            (allowed / "lesson.txt").write_text("Original Academy synthetic course fixture")
            denied_file = Path(temp) / "outside.txt"
            denied_file.write_text("Not in authorized root")
            server = StdioServerParameters(command="node", args=[str(script), str(allowed)])
            async with stdio_client(server) as (read, write):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    self.assertIsNotNone(initialized.capabilities.tools)
                    names = {tool.name for tool in (await session.list_tools()).tools}
                    self.assertIn("read_text_file", names)
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("academy_mcp_host_policy", LAB / "client_policy.py")
                    policy = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = policy
                    spec.loader.exec_module(policy)
                    host = policy.ReadOnlyHost(session)
                    visible = {tool.name for tool in await host.discovery()}
                    self.assertIn("read_text_file", visible)
                    self.assertNotIn("write_file", visible)
                    with self.assertRaises(PermissionError):
                        await host.call("write_file", {"path": str(allowed / "blocked.txt"), "content": "not allowed"})
                    self.assertFalse((allowed / "blocked.txt").exists())
                    content = await session.call_tool("read_text_file", {"path": str(allowed / "lesson.txt")})
                    self.assertFalse(content.isError)
                    self.assertIn("Original Academy", content.content[0].text)
                    denied = await session.call_tool("read_text_file", {"path": str(denied_file)})
                    self.assertTrue(denied.isError)
                    self.assertNotIn("Not in authorized root", denied.content[0].text)

    def test_root_symlink_escape(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("course_mcp_lab", LAB / "server.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            root.mkdir()
            secret = Path(temp) / "secret.txt"
            secret.write_text("not part of course")
            (root / "escape.txt").symlink_to(secret)
            module.ROOT = root
            with self.assertRaises(PermissionError):
                module.read_allowed("escape.txt")
            with self.assertRaises(PermissionError):
                module.read_allowed(str(secret))


if __name__ == "__main__":
    unittest.main()
