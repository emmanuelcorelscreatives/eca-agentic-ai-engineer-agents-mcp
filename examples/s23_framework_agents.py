"""Genuine AutoGen AgentChat and Microsoft Agent Framework constructors.
Run evidence, SDK persistence and workflow integration are separately pending.
"""
import os
from examples.s22_policy import PolicyService

def policy_lookup(product_id: str) -> dict:
    """Read policy for an exact synthetic product ID."""
    return PolicyService().lookup(product_id)

def build_autogen(model):
    if not model:
        raise ValueError('Explicit model ID required')
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    client = OpenAIChatCompletionClient(model=model)
    agent = AssistantAgent('academy_policy', model_client=client, tools=[policy_lookup],
        system_message='Draft ticket triage using policy_lookup. Never send an escalation.',
        reflect_on_tool_use=True)
    return agent, client

async def save_autogen(agent, path):
    from examples.s23_workflow import save_state
    save_state(path, {'framework':'autogen-agentchat', 'state':await agent.save_state()})

async def restore_autogen(agent, path):
    from examples.s23_workflow import load_state
    envelope=load_state(path)
    if envelope['framework'] != 'autogen-agentchat':
        raise ValueError('Wrong framework state')
    await agent.load_state(envelope['state'])

def build_microsoft(client):
    """Client is an actual configured model client; caller owns credential lifecycle."""
    from agent_framework import Agent
    return Agent(client=client, instructions='Draft synthetic ticket triage using policy_lookup. Never send it.',
        tools=[policy_lookup])

async def live_autogen(ticket_text):
    if os.environ.get('ACADEMY_ALLOW_LIVE') != '1':
        raise ValueError('Set ACADEMY_ALLOW_LIVE=1 for one explicitly budgeted run')
    model=os.environ.get('COURSE_MODEL','')
    agent, client=build_autogen(model)
    try:
        return await agent.run(task=ticket_text)
    finally:
        await client.close()
