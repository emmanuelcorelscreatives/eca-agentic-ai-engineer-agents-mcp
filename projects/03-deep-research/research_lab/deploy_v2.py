"""Deployment factory. Startup validates configured secrets without logging values."""
import os
from pathlib import Path

def create_app():
    from fastapi import FastAPI
    import gradio as gr
    from openai import AsyncOpenAI
    from agents import OpenAIResponsesModel
    from .sdk_v2 import build_team
    from .brave_search import BraveSearch
    from .interface_v2 import build_ui
    for key in ('ACADEMY_MODEL','OPENAI_API_KEY','BRAVE_SEARCH_API_KEY','ACADEMY_SOURCE_REVISION'):
        if not os.environ.get(key):raise RuntimeError('required deployment setting absent: '+key)
    if os.environ.get('ACADEMY_MODE')!='live':raise RuntimeError('this deployment explicitly requires live mode; do not label fixture runs as live')
    root=Path(os.environ.get('ACADEMY_STATE_DIR','/state'))
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    client=AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'],max_retries=0)
    team=build_team(OpenAIResponsesModel(model=os.environ['ACADEMY_MODEL'],openai_client=client))
    backend=BraveSearch(os.environ['BRAVE_SEARCH_API_KEY'],enabled=True)
    manifest={'source_revision':os.environ['ACADEMY_SOURCE_REVISION'],'source_ids':[],
              'model':os.environ['ACADEMY_MODEL'],'provider':backend.identity}
    app=FastAPI()
    @app.get('/healthz')
    def health():return {'status':'ready','mode':'configured-live','external_provider_health':'not probed'}
    @app.on_event('shutdown')
    async def shutdown():await client.close()
    return gr.mount_gradio_app(app,build_ui(backend,team.plan,team.analyze,root,manifest),path='/research')
