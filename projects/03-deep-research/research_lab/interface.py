"""Optional real Gradio UI: installed separately; no external calls by default."""
import asyncio
import json
from .runtime import run
from .reporting import markdown
from .search import FixtureSearch

def progress(question, records):
    from queue import Queue
    from threading import Thread
    messages = Queue()
    def worker():
        try:
            bundle = asyncio.run(run(question, FixtureSearch(records),
                                     event_callback=lambda event: messages.put(("event", event))))
            messages.put(("result", bundle))
        except Exception as error:
            messages.put(("error", error))
    thread = Thread(target=worker, daemon=True)
    thread.start()
    while True:
        kind, value = messages.get()
        if kind == "event":
            yield json.dumps(value), "", ""
        elif kind == "error":
            thread.join()
            raise value
        else:
            thread.join()
            yield "Complete", markdown(value), json.dumps(value, indent=2)
            return

def build_ui(records):
    try: import gradio as gr
    except ImportError as error: raise RuntimeError("Install requirements-optional.txt for Gradio") from error
    with gr.Blocks(title="Academy Deep Research — synthetic offline lab") as demo:
        gr.Markdown("# Deep Research Lab\nAcademy synthetic corpus. No live search or real email delivery.")
        question = gr.Textbox(label="Research question", value="Community workshop scheduling")
        submit = gr.Button("Research")
        status = gr.Textbox(label="Operational status")
        report = gr.Markdown()
        bundle = gr.Code(label="Sources, plan and activity bundle", language="json")
        submit.click(lambda q: progress(q, records), inputs=question, outputs=[status, report, bundle])
    return demo
