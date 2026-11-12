"""Integrated private-local UI. Paid SDK and actual owned SMTP each require opt-in."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from sales import Prospect
from application import SalesApplication


def build_app(*, allow_sdk=False, model=None, sink=None, database=None, export_directory=None):
    import gradio as gr
    private = Path(tempfile.mkdtemp(prefix='academy-sales-v2-'))
    controller = SalesApplication(database or str(private/'drafts.sqlite'), allow_sdk=allow_sdk,
        model=model, sink=sink, export_directory=export_directory or private/'exports')
    prospect = Prospect(**json.loads((Path(__file__).parent/'fixtures/prospect.json').read_text())['prospect'])

    def fields(result):
        row = result.get('preview', {})
        return (result.get('draft_id'), row.get('recipient', ''), row.get('subject', ''),
                row.get('body', ''), row.get('revision'), row.get('payload_hash', ''), result)

    async def create(mode):
        return fields(await controller.create(prospect, mode))

    def action(ident, recipient, subject, body, revision, shown_hash, choice):
        if choice in {'approve', 'submit-owned-sink'}:
            current = controller.action(ident, 'preview')
            # Approval is of what the user sees, not merely hidden stale state.
            if (recipient, subject, body, revision) != (current['recipient'], current['subject'], current['body'], current['revision']):
                raise PermissionError('Save edits and refresh exact preview before approval')
        result = controller.action(ident, choice, recipient=recipient, subject=subject, body=body,
                                   expected_revision=revision, expected_hash=shown_hash)
        row = controller.action(ident, 'preview')
        return row['recipient'], row['subject'], row['body'], row['revision'], row['payload_hash'], result

    with gr.Blocks() as app:
        gr.Markdown('# Academy sales team\nSynthetic data only. A local human must approve the exact recipient, subject, body and revision. SMTP submits only to an explicitly owned loopback sink. Manager/handoff observations do not silently become drafts. This local UI is not authenticated production deployment.')
        ident = gr.State(None)
        mode = gr.Dropdown(['deterministic', 'sdk-sequential', 'sdk-manager', 'sdk-handoff'], value='deterministic', label='Generation mode; SDK modes can incur charges when enabled')
        recipient = gr.Textbox(label='Recipient')
        subject = gr.Textbox(label='Subject')
        body = gr.Textbox(label='Body; stored canonical LF text includes final newline', lines=8)
        revision = gr.Number(label='Revision', interactive=False, precision=0)
        shown_hash = gr.Textbox(label='Exact preview hash', interactive=False)
        report = gr.JSON(label='Actual operational result; mechanical checks are not model quality approval')
        gr.Button('Generate or observe selected workflow').click(create, inputs=mode, outputs=[ident, recipient, subject, body, revision, shown_hash, report])
        for label, choice in [('Save edit; revoke approval', 'edit'), ('Approve exact preview', 'approve'),
                              ('Reject', 'reject'), ('Refresh preview', 'preview'), ('Submit approved to owned SMTP sink', 'submit-owned-sink')]:
            gr.Button(label).click(lambda i,r,s,b,v,h,c=choice: action(i,r,s,b,v,h,c),
                inputs=[ident,recipient,subject,body,revision,shown_hash], outputs=[recipient,subject,body,revision,shown_hash,report])
        artifact = gr.File(label='Download local operational/evaluation report')
        gr.Button('Export current trace, evaluation and approval history').click(lambda i: controller.export(i, prospect), inputs=ident, outputs=artifact)
    app.academy_controller = controller
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-sdk', action='store_true')
    parser.add_argument('--owned-sink-port', type=int)
    parser.add_argument('--acknowledge-owned-sink', action='store_true')
    args = parser.parse_args()
    sink = None
    if args.owned_sink_port:
        from transport import OwnedSinkSMTP
        sink = OwnedSinkSMTP(args.owned_sink_port, ownership_acknowledged=args.acknowledge_owned_sink)
    if args.allow_sdk and (not os.environ.get('OPENAI_API_KEY') or not os.environ.get('ACADEMY_MODEL')):
        parser.error('SDK mode requires OPENAI_API_KEY and explicit ACADEMY_MODEL')
    build_app(allow_sdk=args.allow_sdk, model=os.environ.get('ACADEMY_MODEL'), sink=sink).launch(server_name='127.0.0.1', share=False)
