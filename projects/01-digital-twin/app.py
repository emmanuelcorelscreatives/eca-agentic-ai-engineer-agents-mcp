"""Optional local Gradio UI; profile and contacts remain local. No model calls."""
import json
from pathlib import Path
from twin import DigitalTwin


def build_app():
    import gradio as gr
    sections = json.loads((Path(__file__).parent/'fixtures/profile.json').read_text())['sections']
    # A fresh DB per handler avoids sharing SQLite connections across UI threads.
    def chat(message, history):
        twin = DigitalTwin(sections)
        try:
            result = twin.answer(message)
            return result['answer'] + "\n\nSources: " + (', '.join(result['citations']) or 'none')
        finally:
            twin.db.close()
    with gr.Blocks() as app:
        gr.Markdown('# Fictional professional digital twin\nApproved synthetic profile excerpts; no live language model.')
        gr.ChatInterface(fn=chat)
    return app

if __name__ == '__main__':
    build_app().launch(server_name='127.0.0.1', share=False)
