"""Optional genuine Gradio Blocks UI, loopback only.

Install the pinned optional UI environment before running. Every callback uses a
server-side session token and persisted exact task ownership. A task-ID text field
is never an authorization mechanism. The sandbox and browser are server-owned.
This module alone does not establish a tested Gradio/browser integration run.
"""
from dataclasses import asdict
import json
from pathlib import Path
from advanced import SessionController, fixture_plan
from sandbox_server import ApprovedSandboxExecutor, Sandbox
from sidekick import Step


def build_ui(database: Path, sandbox: Sandbox):
    import gradio as gr
    controller = SessionController(database)
    factory = lambda store, task, origin: ApprovedSandboxExecutor(store, task, origin, sandbox.secret)

    def present(token, task):
        snapshot = controller.snapshot(token, task)
        first = next((r for r in snapshot['steps'] if r['state'] != 'complete'), None)
        proposal = json.loads(first['payload']) if first else {}
        return snapshot, (first['number'] if first else -1), (first['revision'] if first else ''), json.dumps(proposal, indent=2)

    def create(objective, submit, token):
        task = controller.create(token, fixture_plan(objective, sandbox.origin, submit))
        return (task, *present(token, task))
    def advance(task, token):
        controller.advance(token, task, factory)
        return present(token, task)
    def decision(task, number, revision, payload, token, choice):
        displayed = Step(**json.loads(payload))
        if choice == 'approve' and displayed.digest() != revision:
            raise ValueError('Save the edited proposal before approving its new revision')
        replacement = displayed if choice == 'edit' else None
        controller.decide(token, task, int(number), revision, choice, replacement)
        return present(token, task)

    with gr.Blocks(title='Academy Browser Task Sidekick') as demo:
        gr.Markdown('# Academy Browser Task Sidekick\nDeterministic sandbox lab. Native model-backed planning is a separately verified optional run.')
        session = gr.State(value=SessionController.session)
        task = gr.State(value='')
        revision = gr.State(value='')
        number = gr.State(value=-1)
        objective = gr.Textbox(label='Task objective', value='Compare Academy workshops')
        submit = gr.Checkbox(label='Include synthetic draft submission (requires approval)', value=False)
        create_button = gr.Button('Create task')
        progress = gr.JSON(label='Persisted progress and evidence')
        proposal = gr.Code(label='Exact current proposed action (edit before approval)', language='json')
        run_button = gr.Button('Advance one bounded step')
        with gr.Row():
            approve = gr.Button('Approve exact displayed action')
            edit = gr.Button('Save edited proposal (requires fresh approval)')
            reject = gr.Button('Reject')
        outputs = [progress, number, revision, proposal]
        create_button.click(create, [objective, submit, session], [task, *outputs])
        run_button.click(advance, [task, session], outputs)
        # Event lambdas close over a fixed action, never client-supplied authorization.
        approve.click(lambda t,n,r,p,s: decision(t,n,r,p,s,'approve'), [task, number, revision, proposal, session], outputs)
        edit.click(lambda t,n,r,p,s: decision(t,n,r,p,s,'edit'), [task, number, revision, proposal, session], outputs)
        reject.click(lambda t,n,r,p,s: decision(t,n,r,p,s,'reject'), [task, number, revision, proposal, session], outputs)
        gr.Markdown('The demonstration intentionally has no arbitrary file download or public deployment. Browser screenshots and owned artifact links require their separate capture/export integration; this UI does not claim those features.')
    return demo


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=Path('sidekick-ui.sqlite'))
    parser.add_argument('--port', type=int, default=7860)
    args = parser.parse_args()
    with Sandbox() as sandbox:
        build_ui(args.database, sandbox).queue(default_concurrency_limit=1).launch(
            server_name='127.0.0.1', server_port=args.port, share=False,
            show_api=False, strict_cors=True)
