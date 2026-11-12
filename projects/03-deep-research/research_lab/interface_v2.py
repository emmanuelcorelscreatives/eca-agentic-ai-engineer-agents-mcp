"""Real phase streaming with async cancellation and isolated per-submission state."""
import asyncio
import html
import json
from pathlib import Path
from tempfile import mkdtemp
from .pipeline_v2 import run_research

PUBLIC_EVENT_FIELDS=frozenset(('phase','status','span_id','parent_id','started_at','ended_at','duration_seconds','tokens','measurement'))
def public_event(event):return {key:value for key,value in event.items() if key in PUBLIC_EVENT_FIELDS}

def render_report(report):
    return '\n\n'.join(['# '+html.escape(report['title'])]+[
        '## '+html.escape(section['kind'])+'\n'+html.escape(section['text']) for section in report['sections']])

async def stream_research(question,backend,planner,analyst,root,manifest):
    # Each call gets a distinct directory even for the same question in another browser session.
    directory=mkdtemp(prefix='research-',dir=root);queue=asyncio.Queue()
    task=asyncio.create_task(run_research(question,backend,planner,analyst,directory,
         input_manifest=manifest,callback=lambda event:queue.put_nowait(public_event(event))))
    events=[]
    try:
        while not task.done() or not queue.empty():
            try:
                event=await asyncio.wait_for(queue.get(),timeout=.1)
                events.append(event)
                yield json.dumps(events,indent=2),'',{}
            except asyncio.TimeoutError:continue
        bundle=await task
        # Only public plan/source metadata/evidence is exposed; no private model reasoning or keys.
        view={'plan':bundle['plan'],'sources':[{key:source[key] for key in
              ('id','title','url','published','retrieved','scope','content_kind')} for source in bundle['sources']],
              'uncertainties':bundle['analysis']['uncertainties']}
        yield json.dumps(events,indent=2),render_report(bundle['report']),view
    finally:
        if not task.done():task.cancel()
        await asyncio.gather(task,return_exceptions=True)

def build_ui(backend,planner,analyst,root,manifest):
    import gradio as gr
    Path(root).mkdir(parents=True,exist_ok=True,mode=0o700)
    async def submit(question):
        async for row in stream_research(question,backend,planner,analyst,root,manifest):yield row
    with gr.Blocks(title='Academy Deep Research') as demo:
        gr.Markdown('# Deep Research\nLive-provider and synthetic modes must be labelled by the configured deployment. Source text is untrusted evidence, never instructions.')
        question=gr.Textbox(label='Research question',max_lines=8)
        begin=gr.Button('Research');stop=gr.Button('Cancel')
        events=gr.Code(label='Actual operational spans',language='json')
        report=gr.Markdown();details=gr.JSON(label='Plan, source metadata and uncertainties')
        submission=begin.click(submit,inputs=question,outputs=[events,report,details])
        stop.click(fn=None,inputs=None,outputs=None,cancels=[submission])
    return demo
