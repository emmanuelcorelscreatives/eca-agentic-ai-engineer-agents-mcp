"""Genuine A2A SDK server: local stock skill, no model/provider calls.
Optional SDK APIs require compatibility verification before teaching captures.
"""
from examples.s21_inventory import lookup_stock

def make_app():
    from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentInterface
    from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
    from starlette.applications import Starlette
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import InMemoryTaskStore
    from a2a.server.agent_execution import AgentExecutor, RequestContext
    from a2a.server.events import EventQueue
    from a2a.helpers import new_text_message, get_message_text
    import json
    class InventoryExecutor(AgentExecutor):
        async def execute(self, context: RequestContext, event_queue: EventQueue):
            sku = get_message_text(context.message).strip()
            await event_queue.enqueue_event(new_text_message(json.dumps(lookup_stock(sku))))
        async def cancel(self, context: RequestContext, event_queue: EventQueue):
            raise NotImplementedError('This immediate read-only capability does not expose cancellation')
    card = AgentCard(name='Academy Inventory', description='Read-only synthetic SKU stock lookup',
        supported_interfaces=[AgentInterface(protocol_binding='JSONRPC',url='http://127.0.0.1:8765/',protocol_version='1.0')], version='1.0.0',
        default_input_modes=['text/plain'], default_output_modes=['text/plain'],
        capabilities=AgentCapabilities(streaming=False, extended_agent_card=False),
        skills=[AgentSkill(id='stock-check', name='Check stock', description='Exact SKU lookup',
            tags=['inventory'], examples=['ECA-KEY-01'])])
    handler=DefaultRequestHandler(agent_executor=InventoryExecutor(), task_store=InMemoryTaskStore(), agent_card=card)
    return Starlette(routes=[*create_agent_card_routes(card), *create_jsonrpc_routes(handler,'/')])
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(make_app(), host='127.0.0.1', port=8765)
