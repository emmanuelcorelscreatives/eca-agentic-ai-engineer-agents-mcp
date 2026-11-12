"""Optional local human approval UI; simulated delivery only."""
import json
import tempfile
from pathlib import Path
from sales import Prospect,SalesTeam


def build_app():
    import gradio as gr
    # Separate local temporary DB, never in a public course fixture directory.
    database=str(Path(tempfile.mkdtemp(prefix='academy-sales-'))/'drafts.sqlite')
    prospect=Prospect(**json.loads((Path(__file__).parent/'fixtures/prospect.json').read_text())['prospect'])
    def create():
        team=SalesTeam(database)
        try:
            ident=team.create_draft(prospect);row=team.draft(ident)
            return ident,row['subject'],row['body'],'Draft: requires human review'
        finally:team.db.close()
    def action(ident,subject,body,choice):
        team=SalesTeam(database)
        try:
            if choice=='edit':team.edit(ident,subject,body);return 'Edited; previous approval revoked'
            if choice=='approve':
                row=team.draft(ident)
                if row['subject']!=subject or row['body']!=body:return 'Save edits before approving the displayed exact message'
                team.approve(ident,'Local UI human');return 'Approved exact stored payload; no message sent'
            if choice=='reject':
                with team.db:team.db.execute("UPDATE drafts SET status='rejected',approved_hash=NULL,approver=NULL WHERE id=? AND status!='simulated_delivery'",(ident,))
                return 'Rejected; no message sent'
            return json.dumps(team.deliver(ident))
        except (ValueError,KeyError,PermissionError) as error:return str(error)
        finally:team.db.close()
    with gr.Blocks() as app:
        gr.Markdown('# Sales practice approval queue\nFictional prospect. Delivery is simulated only.')
        ident=gr.State(None);subject=gr.Textbox(label='Subject');body=gr.Textbox(label='Body',lines=8);status=gr.Textbox(label='Status',interactive=False)
        gr.Button('Create draft').click(create,outputs=[ident,subject,body,status])
        for label,choice in [('Save edits','edit'),('Approve exact draft','approve'),('Reject','reject'),('Simulate approved delivery','deliver')]:
            gr.Button(label).click(lambda i,s,b,c=choice:action(i,s,b,c),inputs=[ident,subject,body],outputs=status)
    return app
if __name__=='__main__':build_app().launch(server_name='127.0.0.1',share=False)
