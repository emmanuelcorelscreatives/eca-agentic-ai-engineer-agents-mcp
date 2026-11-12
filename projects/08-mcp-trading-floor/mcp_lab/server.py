"""Genuine MCP server: no trading, approval, network fetching or paid model calls."""
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from starlette.middleware import Middleware
from starlette.responses import JSONResponse

ROOT = Path(os.environ.get("ACADEMY_MCP_ROOT", str(Path(__file__).parent / "fixtures"))).resolve()


def read_allowed(relative: str) -> str:
    """Allow only relative files contained in the configured course root, including symlink checks."""
    candidate = Path(relative)
    if candidate.is_absolute():
        raise PermissionError("Only relative course paths are permitted")
    resolved = (ROOT / candidate).resolve()
    if not resolved.is_relative_to(ROOT):
        raise PermissionError("Path escapes course root")
    if not resolved.is_file():
        raise FileNotFoundError("Course file not found")
    if resolved.stat().st_size > 65536:
        raise ValueError("Course file exceeds 64 KiB limit")
    return resolved.read_text(encoding="utf-8")


mcp = FastMCP("Academy MCP laboratory", host="127.0.0.1", port=int(os.environ.get("ACADEMY_MCP_PORT", "8765")))


@mcp.tool()
def read_course_file(path: str) -> dict:
    """Read an approved UTF-8 course file; errors are structured and contain no host paths."""
    try:
        return {"ok": True, "path": path, "text": read_allowed(path)}
    except PermissionError:
        return {"ok": False, "error": {"code": "PERMISSION_DENIED", "message": "Path is outside approved course scope"}}
    except FileNotFoundError:
        return {"ok": False, "error": {"code": "NOT_FOUND", "message": "Course file not found"}}
    except (ValueError, UnicodeError):
        return {"ok": False, "error": {"code": "INVALID_FILE", "message": "File must be UTF-8 and at most 64 KiB"}}


@mcp.tool()
def quote(symbol: str, quantity: int) -> dict:
    """Return synthetic educational price data, not live market prices or an order."""
    if symbol not in {"ACME", "NOVA"} or quantity < 1 or quantity > 100:
        return {"ok": False, "error": {"code": "INVALID_ARGUMENT", "message": "Use ACME/NOVA and quantity 1..100"}}
    return {"ok": True, "synthetic": True, "symbol": symbol, "quantity": quantity, "price_cents": {"ACME": 1200, "NOVA": 850}[symbol]}


@mcp.resource("academy://handbook")
def handbook() -> str:
    return read_allowed("handbook.md")


@mcp.prompt()
def research_brief(symbol: str) -> str:
    return f"Research synthetic symbol {symbol}. Cite course sources and stop before any trade."


@mcp.tool()
async def sampled_summary(topic: str, ctx: Context) -> str:
    """Ask the host for a short summary. The host decides whether to allow sampling."""
    if len(topic) > 200:
        raise ValueError("Topic exceeds 200 characters")
    result = await ctx.session.create_message(messages=[SamplingMessage(role="user", content=TextContent(type="text", text="Summarize this course topic: " + topic))], max_tokens=80)
    if result.content.type != "text":
        raise ValueError("Host returned non-text sampling output")
    return result.content.text


class BearerBoundary:
    """Apply an operator-provisioned token to every HTTP request before MCP handling.

    This loopback teaching guard is not an OAuth authorization server. Deploy a real
    remote service behind TLS and the MCP authorization flow before exposing it.
    """
    def __init__(self, app, token: str):
        if len(token) < 24:
            raise ValueError("Provide an unpredictable token of at least 24 characters")
        self.app, self.token = app, token

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            import hmac
            supplied = dict(scope.get("headers", [])).get(b"authorization", b"")
            if not hmac.compare_digest(supplied, ("Bearer " + self.token).encode()):
                await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)
                return
        await self.app(scope, receive, send)


if __name__ == "__main__":
    if os.environ.get("ACADEMY_MCP_TRANSPORT") == "http":
        import uvicorn
        token = os.environ["ACADEMY_MCP_TOKEN"]
        app = mcp.streamable_http_app()
        app.add_middleware(BearerBoundary, token=token)
        uvicorn.run(app, host="127.0.0.1", port=mcp.settings.port, log_level="warning")
    else:
        mcp.run(transport="stdio")
