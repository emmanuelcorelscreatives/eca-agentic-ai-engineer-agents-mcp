"""Current owned-session UI with usable exact-run report download control."""
import asyncio
import json
from .pipeline_v3 import run_research
from .interface_v2 import public_event, render_report
from .run_exports_v3 import RunExports

async def stream_owned(question,session,registry,backend,planner,analyst,manifest):
    token,directory=registry.create(session);queue=asyncio.Queue()
    task=asyncio.create_task(run_research(question,backend,planner,analyst,directory,
        input_manifest=manifest,callback=lambda event:queue.put_nowait(public_event(event))))
    events=[]
    try:
        while not task.done() or not queue.empty():
            try:
                event=await asyncio.wait_for(queue.get(),timeout=.1);events.append(event)
                yield json.dumps(events,indent=2),'',{},token
            except asyncio.TimeoutError:continue
        bundle=await task
        registry.finish(token,session,bundle)
        view={'plan':bundle['plan'],'sources':[{key:source[key] for key in
             ('id','title','url','published','retrieved','scope','content_kind')} for source in bundle['sources']],
             'uncertainties':bundle['analysis']['uncertainties']}
        yield json.dumps(events,indent=2),render_report(bundle['report']),view,token
    finally:
        if not task.done():task.cancel()
        await asyncio.gather(task,return_exceptions=True)

def build_ui(backend,planner,analyst,root,manifest):
    import gradio as gr
    registry=RunExports(root)
    async def submit(question,request:gr.Request):
        if not request.session_hash:raise ValueError('server session missing')
        async for row in stream_owned(question,request.session_hash,registry,backend,planner,analyst,manifest):yield row
    def downloads(token,request:gr.Request):
        return registry.download_paths(token,request.session_hash)
    with gr.Blocks(title='Academy Deep Research') as demo:
        gr.Markdown('# Deep Research\nSource excerpts are untrusted evidence. Download exports only after your own actual run completes.')
        question=gr.Textbox(label='Research question',max_lines=8)
        begin=gr.Button('Research');stop=gr.Button('Cancel')
        events=gr.Code(label='Actual operational spans',language='json')
        report=gr.Markdown();details=gr.JSON(label='Plan, source metadata and uncertainties')
        token=gr.State('')
        download=gr.Button('Prepare my completed report downloads')
        files=gr.File(label='My report exports',file_count='multiple',interactive=False)
        submission=begin.click(submit,inputs=question,outputs=[events,report,details,token])
        stop.click(fn=None,inputs=None,outputs=None,cancels=[submission])
        download.click(downloads,inputs=token,outputs=files)
    # Explicit Python-only handles enable meaningful central callback tests with actual Gradio.
    demo.academy_downloads=downloads
    demo.academy_registry=registry
    demo.academy_submit=submit
    return demo
