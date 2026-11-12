"""Real ADK state tools and durable SQLite session service for Academy inventory.

No inference occurs here. Unprefixed keys stay session scoped: user:/app: keys
would intentionally broaden scope and are not used for shopping preferences.
"""
from pathlib import Path
from google.adk.tools import ToolContext
from examples.s21_inventory import lookup_stock
APP_NAME = 'academy_inventory'
USER_ID = 'synthetic-user'

def set_preference(sku: str, delivery_preference: str, tool_context: ToolContext) -> dict:
    """Remember a valid stock selection and bounded delivery preference in this session."""
    product=lookup_stock(sku)
    if not product['ok']:
        return product
    if delivery_preference not in {'standard','collection'}:
        return {'ok':False,'error':'invalid_delivery_preference'}
    tool_context.state['selected_sku']=sku
    tool_context.state['delivery_preference']=delivery_preference
    return {'ok':True,'selected_sku':sku,'delivery_preference':delivery_preference}

def get_preference(tool_context: ToolContext) -> dict:
    """Read the current session preference without reading other sessions."""
    return {'selected_sku':tool_context.state.get('selected_sku'),
            'delivery_preference':tool_context.state.get('delivery_preference')}

def durable_sessions(database_path: Path):
    """Use actual DatabaseSessionService with SQLite/aiosqlite, never an in-memory alias."""
    from google.adk.sessions import DatabaseSessionService
    path=Path(database_path).resolve()
    path.parent.mkdir(parents=True,exist_ok=True)
    return DatabaseSessionService(db_url='sqlite+aiosqlite:///'+str(path))

async def ensure_session(service, session_id: str):
    if not session_id or not session_id.isascii():
        raise ValueError('Use an explicit synthetic ASCII session ID')
    session=await service.get_session(app_name=APP_NAME,user_id=USER_ID,session_id=session_id)
    if session is None:
        session=await service.create_session(app_name=APP_NAME,user_id=USER_ID,session_id=session_id)
    return session

async def state_roundtrip(database_path: Path, session_id: str, *, preference=None):
    """Provider-free SDK persistence probe through an actual ADK state_delta event.

This is a storage demonstration, not an observed model decision. The live
multi-turn CLI below separately uses Runner and actual registered state tools.
"""
    from google.adk.events import Event, EventActions
    async with durable_sessions(database_path) as service:
        session=await ensure_session(service,session_id)
        if preference is not None:
            sku,delivery=preference
            if not lookup_stock(sku)['ok'] or delivery not in {'standard','collection'}:
                raise ValueError('Invalid preference')
            await service.append_event(session,Event(author='academy_preference_storage_probe',
                invocation_id='provider-free-storage-probe',
                actions=EventActions(state_delta={'selected_sku':sku,'delivery_preference':delivery})))
            session=await service.get_session(app_name=APP_NAME,user_id=USER_ID,session_id=session_id)
        return {'session_id':session.id,'state':session.state}

async def live_turns(database_path: Path, *, model=None):
    """Two actual model turns in A, separate B and persisted next-process state."""
    from google.adk.runners import Runner
    from examples.s21_adk import build_agent,run_turn
    async with durable_sessions(database_path) as service:
        for session_id in ('shopping-a','shopping-b'):
            await ensure_session(service,session_id)
        agent,toolset=build_agent(model)
        runner=Runner(agent=agent,app_name=APP_NAME,session_service=service)
        try:
            observed=[]
            for session_id,text in [('shopping-a','Remember ECA-KEY-01 with collection delivery using the preference tool.'),
                                    ('shopping-a','Read my remembered preference using the tool; what SKU and delivery did I select?'),
                                    ('shopping-b','Read my preference using the tool. If none is set, say so.')]:
                observed.append({'session_id':session_id,'request':text,'events':await run_turn(text,
                    user_id=USER_ID,session_id=session_id,sessions=service,runner=runner)})
            return observed
        finally:
            if toolset is not None: await toolset.close()

if __name__=='__main__':
    import argparse,asyncio,json
    parser=argparse.ArgumentParser();parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--session',default='shopping-a');parser.add_argument('--write',action='store_true')
    parser.add_argument('--live-model-turns',action='store_true');args=parser.parse_args()
    if args.live_model_turns:
        result=asyncio.run(live_turns(args.database))
    else:
        result=asyncio.run(state_roundtrip(args.database,args.session,
            preference=('ECA-KEY-01','collection') if args.write else None))
    print(json.dumps(result,sort_keys=True))
