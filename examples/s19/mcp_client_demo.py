"""Inspect the owned synthetic browser fixture through a real local MCP session."""
import argparse
import asyncio
import json
from pathlib import Path
import sys


async def inspect_fixture():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from examples.s19.browser_research import fixture_server

    root = Path(__file__).resolve().parents[2]
    with fixture_server() as origin:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(root / 'examples/s19/browser_research.py'), '--mcp', '--origin', origin],
        )
        async with stdio_client(parameters) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = [tool.name for tool in tools.tools]
                if names != ['inspect_page']:
                    raise RuntimeError('Unexpected browser fixture tool discovery')
                result = await session.call_tool('inspect_page', {'path': '/docs.html'})
                if result.isError:
                    raise RuntimeError('Browser fixture tool returned an error; no successful observation claimed')
                return {'scope': 'owned synthetic fixture, no model call',
                        'tools': [tool.model_dump(mode='json') for tool in tools.tools],
                        'result': result.model_dump(mode='json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        result = asyncio.run(asyncio.wait_for(inspect_fixture(), timeout=30))
    except ModuleNotFoundError as error:
        raise SystemExit('Install the browser optional requirements and official MCP SDK in a separate environment; missing module: ' + str(error.name)) from None
    except TimeoutError:
        raise SystemExit('Local MCP/browser exercise timed out; no successful tool result claimed') from None
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
