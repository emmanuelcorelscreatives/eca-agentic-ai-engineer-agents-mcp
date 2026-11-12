"""Real loopback Gradio workspace over the complete persisted Sidekick pipeline.

Authoring status: this revised integrated UI awaits central browser/SDK QA.
``--model provider:model`` explicitly configures native planning; without it the
visible mode is a deterministic fixture. No silent model-to-fixture fallback.
Owned screenshots/artifacts are returned inline after exact session+SHA checks,
never through a broadly exposed filesystem download directory.
"""
import base64
import html
import json
from pathlib import Path
from advanced import SessionController
from pipeline import NativePlanner, SidekickApplication
from sandbox_server import Sandbox
from sidekick import Step


def build_ui(database:Path,sandbox:Sandbox,*,model=None,workspace_root=None,executable_path=None,application=None):
    import gradio as gr
    root=Path(workspace_root or database.parent/'sidekick-workspaces')
    app=application or SidekickApplication(database,root,sandbox,
                     NativePlanner(model) if model is not None else None,
                     executable_path=executable_path)

    def tasks(token):
        with app.control._store() as store:
            rows=store.db.execute('SELECT task FROM sidekick_owner WHERE owner_hash=? ORDER BY rowid DESC',
                                  (app.control._owner(token),)).fetchall()
        return [row['task'] for row in rows]

    def present(token,task):
        snapshot=app.snapshot(token,task)
        first=next((r for r in snapshot['steps'] if r['state']!='complete'),None)
        proposal=json.loads(first['payload']) if first else {}
        captures=[r for r in snapshot['observations'] if r.get('screenshot')]
        image='<p>No browser action has produced a screenshot yet.</p>'
        if captures:
            latest=captures[-1]
            path=app.owned_file(token,task,latest['screenshot'],latest['screenshot_sha256'])
            encoded=base64.b64encode(path.read_bytes()).decode('ascii')
            image='<img alt="Actual owned Playwright browser viewport" style="max-width:100%" src="data:image/png;base64,'+encoded+'">'
        links=[]
        for item in snapshot['observations']:
            if item.get('artifact'):
                path=app.owned_file(token,task,item['artifact'],item['body_sha256'])
                encoded=base64.b64encode(path.read_bytes()).decode('ascii')
                links.append('<li><a download="'+html.escape(path.name,quote=True)+'" href="data:application/octet-stream;base64,'+encoded+'">'+html.escape(path.name)+'</a> SHA256 '+html.escape(item['body_sha256'])+'</li>')
        files='<ul>'+''.join(links)+'</ul>' if links else '<p>No approved artifacts written yet.</p>'
        final={'objective':snapshot['objective'],'status':snapshot['status'],
               'evaluation':snapshot['evaluation'],'complete_steps':snapshot['complete'],'total_steps':snapshot['total'],
               'meaning':'Completion means the original plan predicates have observed attributable evidence; it does not certify arbitrary untested claims.'}
        # Raw data, current evidence and current approval are separate views, not generated progress prose.
        return (snapshot,(first['number'] if first else -1),(first['revision'] if first else ''),
                json.dumps(proposal,indent=2),image,files,final,app.export_trace(token,task))

    def create(objective,token):
        task=app.create(token,objective)
        return (task,gr.update(choices=tasks(token),value=task),*present(token,task))
    def select(task,token): return (task,*present(token,task))
    def recover(secret):
        app.control._owner(secret)
        owned=tasks(secret)
        return secret,gr.update(choices=owned,value=owned[0] if owned else None)
    def advance(task,token):
        app.advance(token,task)
        return present(token,task)
    def revise(task,token):
        app.revise(token,task)
        return present(token,task)
    def decision(task,number,revision,payload,token,choice):
        displayed=Step(**json.loads(payload))
        if choice=='approve' and displayed.digest()!=revision:
            raise ValueError('Save the edited proposal before approving its new revision')
        app.decide(token,task,int(number),revision,choice,displayed if choice=='edit' else None)
        return present(token,task)

    with gr.Blocks(title='Academy Browser Task Sidekick') as demo:
        gr.Markdown('# Academy Browser Task Sidekick\nPlanning mode: **'+app.planner.mode+'**. Consequential actions always require a separate exact approval.')
        session=gr.State(value=SessionController.session)
        task=gr.State(value='');revision=gr.State(value='');number=gr.State(value=-1)
        objective=gr.Textbox(label='Task objective',value='Compare Academy Python and SQL workshops; prepare a synthetic Python workshop request and preserve an evidence report.')
        create_button=gr.Button('Plan new task')
        selector=gr.Dropdown(label='Your persisted tasks',choices=[])
        with gr.Accordion('Restore a previously owned lab session',open=False):
            recovery=gr.Textbox(label='Your private session recovery secret (at least 32 characters)',type='password')
            recover_button=gr.Button('Use this private session')
            gr.Markdown('For restart demonstrations, set and retain your own private recovery secret before creating a task. Never publish that secret or another account’s data.')
        progress=gr.JSON(label='Durable checklist and observed evidence')
        browser=gr.HTML(label='Actual browser update')
        proposal=gr.Code(label='Exact proposed action; edits require saving and fresh approval',language='json')
        with gr.Row():
            run_button=gr.Button('Advance one bounded browser/tool step')
            revise_button=gr.Button('Request one bounded revision (when available)')
        with gr.Row():
            approve=gr.Button('Approve exact displayed action')
            edit=gr.Button('Save edited proposal (not approval)')
            reject=gr.Button('Reject')
        artifacts=gr.HTML(label='Owned approved artifacts')
        final=gr.JSON(label='Final result and evidence-based evaluation')
        trace=gr.JSON(label='Redacted run trace / intervention / timing evidence')
        outputs=[progress,number,revision,proposal,browser,artifacts,final,trace]
        create_button.click(create,[objective,session],[task,selector,*outputs])
        selector.change(select,[selector,session],[task,*outputs])
        recover_button.click(recover,[recovery],[session,selector])
        run_button.click(advance,[task,session],outputs)
        revise_button.click(revise,[task,session],outputs)
        def fixed_decision(choice):
            def callback(t,n,r,p,s):return decision(t,n,r,p,s,choice)
            return callback
        for button,choice in ((approve,'approve'),(edit,'edit'),(reject,'reject')):
            # Bind a fixed server-owned decision, never accept an action kind from a client.
            button.click(fixed_decision(choice),[task,number,revision,proposal,session],outputs)
        gr.Markdown('Loopback Academy sandbox only. Unsupported upload, download, message and destructive browser tools fail closed. No public or authenticated-user deployment is claimed.')
    return demo


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,default=Path('sidekick-ui.sqlite'))
    parser.add_argument('--workspace-root',type=Path,default=Path('sidekick-workspaces'))
    parser.add_argument('--port',type=int,default=7860)
    parser.add_argument('--model',help='Explicit LangChain provider:model; real calls use configured provider credentials')
    parser.add_argument('--browser-executable',help='Optional exact installed Chromium executable')
    args=parser.parse_args()
    model=None
    if args.model:
        from langchain.chat_models import init_chat_model
        model=init_chat_model(args.model,max_retries=0,timeout=30)
    with Sandbox() as sandbox:
        build_ui(args.database,sandbox,model=model,workspace_root=args.workspace_root,
                 executable_path=args.browser_executable).queue(default_concurrency_limit=1).launch(
            server_name='127.0.0.1',server_port=args.port,share=False,strict_cors=True)
