"""Optional genuine ADK package and runner. No provider call on import."""
import os
import sys
from examples.s21_inventory import lookup_stock, estimate_delivery, summarize_events

def build_agent(model=None, *, mcp=False):
    from google.adk.agents import Agent
    model = model or os.environ.get('GOOGLE_MODEL', '').strip()
    if not model:
        raise ValueError('Set GOOGLE_MODEL; provider credentials must be configured separately')
    tools = [lookup_stock, estimate_delivery]
    toolset = None
    if mcp:
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters
        toolset = McpToolset(connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command=sys.executable,
                args=['-m', 'examples.s21_mcp_inventory'])),
            tool_filter=['lookup_stock', 'estimate_delivery'])
        tools = [toolset]
    return Agent(name='academy_stock_support', model=model, tools=tools,
        instruction='Use inventory tools for stock and delivery. Never invent products or stock. '
        'Preferences belong only to the current session. Report tool errors honestly.'), toolset

async def run_turn(text, *, user_id, session_id, sessions, runner):
    """Caller owns the actual ADK session service, so state may span turns safely."""
    from google.genai import types
    events = []
    async for event in runner.run_async(user_id=user_id, session_id=session_id,
            new_message=types.Content(role='user', parts=[types.Part(text=text)])):
        events.append(event)
    return summarize_events(events)

async def live_demo():
    if '--run' not in sys.argv:
        raise ValueError('Explicit --run required; nothing sent')
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    agent, toolset = build_agent(mcp='--mcp' in sys.argv)
    service = InMemorySessionService()
    await service.create_session(app_name='academy_inventory', user_id='synthetic-user', session_id='demo-a')
    runner = Runner(agent=agent, app_name='academy_inventory', session_service=service)
    try:
        print(await run_turn('Check ECA-KEY-01 and delivery to AB12.',
            user_id='synthetic-user', session_id='demo-a', sessions=service, runner=runner))
    finally:
        if toolset is not None:
            await toolset.close()
if __name__ == '__main__':
    import asyncio
    asyncio.run(live_demo())
