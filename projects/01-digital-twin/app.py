"""Actual Gradio responses, visible progress and consented contact actions."""
import asyncio
import json
import uuid
from config import Settings,profile_path
from service import TwinService
from prompts import IDENTITY


def build_app(settings=None):
    import gradio as gr
    settings=settings or Settings.from_env()
    sections=json.loads(profile_path().read_text())['sections']
    service=TwinService(sections,settings)
    def chat(message,history,session='local-cli'):
        yield 'Retrieving approved professional information…'
        try:
            if settings.live_model_enabled:
                clean_history=[{'role':row['role'],'content':row['content']} for row in history if isinstance(row,dict) and row.get('role') in ('user','assistant') and isinstance(row.get('content'),str)]
                result=asyncio.run(service.answer_with_model(session,message,clean_history))
                if 'model_answer' in result:
                    answer=result['model_answer']['answer'];citations=result['model_answer']['cited_section_ids']
                else:answer=result['answer'];citations=result['citations']
            else:
                result=service.answer(session,message);answer=result['answer'];citations=result['citations']
            yield answer+'\n\nSources: '+(', '.join(citations) or 'none')
        except (ValueError,PermissionError) as error:yield 'Request not completed: '+str(error)
        except Exception as error:yield 'Request failed ('+type(error).__name__+'). No contact action was performed.'
    def contact(session,call_id,name,email,message,opportunity,consent):
        if not call_id:call_id=uuid.uuid4().hex
        for event in service.contact_events(session,call_id,name,email,message,consent,opportunity):yield call_id,event
    def question(session,call_id,question_text,consent):
        if not call_id:call_id=uuid.uuid4().hex
        try:return call_id,service.capture_question(session,call_id,question_text,consent)
        except (ValueError,PermissionError) as error:return call_id,{'status':'rejected','error':str(error)}
    with gr.Blocks() as app:
        mode='Configured live grounded model' if settings.live_model_enabled else 'Deterministic approved-excerpt baseline'
        gr.Markdown('# Professional Digital Twin\n'+IDENTITY+'\n'+mode+'. No external send is implied.')
        session=gr.State(value=lambda:uuid.uuid4().hex)
        gr.ChatInterface(fn=chat,additional_inputs=[session])
        call_id=gr.State(value='');question_id=gr.State(value='')
        gr.Markdown('## Contact the representative\nSubmitting stores this request for the configured retention period. A local outbox records notification intent; no external delivery is configured by default.')
        name=gr.Textbox(label='Name');email=gr.Textbox(label='Email');message=gr.Textbox(label='Message',lines=4);opportunity=gr.Textbox(label='Opportunity or project details')
        consent=gr.Checkbox(label=f'I consent to storing these contact details for up to {settings.retention_days} days.',value=False)
        checklist=gr.JSON(label='Action checklist and actual receipt')
        gr.Button('Submit contact request').click(contact,inputs=[session,call_id,name,email,message,opportunity,consent],outputs=[call_id,checklist])
        gr.Button('Start another contact request').click(lambda:('',False),outputs=[call_id,consent])
        question_text=gr.Textbox(label='Question to save for the representative')
        question_consent=gr.Checkbox(label='I consent to storing this question.',value=False)
        question_status=gr.JSON(label='Question receipt')
        gr.Button('Save question').click(question,inputs=[session,question_id,question_text,question_consent],outputs=[question_id,question_status])
        gr.Button('Start another saved question').click(lambda:('',False),outputs=[question_id,question_consent])
    app.academy_service=service
    return app


def main():
    settings=Settings.from_env();app=build_app(settings)
    auth=(settings.auth_username,settings.auth_password) if settings.public_bind else None
    app.launch(server_name='0.0.0.0' if settings.public_bind else '127.0.0.1',share=False,auth=auth)

if __name__=='__main__':main()
