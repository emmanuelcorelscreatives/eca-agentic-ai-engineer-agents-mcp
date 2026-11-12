"""Persistent local Gradio paper-trading dashboard; no real market or model calls."""
import json
import os
import secrets
import gradio as gr
from dataclasses import asdict
from trading_floor import TradingFloor,Proposal

DATABASE=os.environ.get('ACADEMY_PAPER_DB','paper.sqlite')

def inspect(symbol,quantity, database=None):
    # Optional explicit database keeps this callback reusable in isolated exercises.
    floor=TradingFloor(database or os.environ.get('ACADEMY_PAPER_DB',':memory:'))
    try:
        if isinstance(quantity,bool) or float(quantity)!=int(quantity):raise ValueError('whole-share quantity required')
        research=floor.research(symbol)
        proposal=floor.propose(symbol,int(quantity))
        return research,{**floor.risk(proposal),'proposal':asdict(proposal),'status':'AWAITING_HUMAN_APPROVAL'},floor.state()
    except ValueError as exc:return {'error':str(exc)},{},{}
    finally:floor.close()

def dashboard_state():
    floor=TradingFloor(DATABASE)
    try:return {'portfolio':floor.state(),'proposals':floor.proposal_history(),'transactions':floor.transactions(),
                'activity':floor.history(),'agent_status':'Local deterministic reference; no external model running'}
    finally:floor.close()

def review_and_execute(proposal_data,review_token,action):
    expected=os.environ.get('ACADEMY_REVIEW_TOKEN','')
    if not expected or not review_token or not secrets.compare_digest(expected,review_token):
        return {'error':'separate local reviewer token required'},dashboard_state()
    if secrets.compare_digest(expected,os.environ.get('ACADEMY_LOCAL_TOKEN','')):
        return {'error':'reviewer and operator tokens must differ'},dashboard_state()
    floor=TradingFloor(DATABASE)
    try:
        payload=json.loads(proposal_data) if isinstance(proposal_data,str) else proposal_data
        proposal=Proposal(**payload.get('proposal',payload))
        reviewer=os.environ.get('ACADEMY_REVIEWER_NAME','academy-local-reviewer')
        if action=='APPROVE':result={'status':'APPROVED','risk':floor.approve(proposal,reviewer)}
        elif action=='REJECT':result=floor.reject(proposal,reviewer,'Rejected by local course reviewer')
        else:raise ValueError('choose APPROVE or REJECT')
    except (ValueError,TypeError,json.JSONDecodeError) as exc:result={'error':str(exc)}
    finally:floor.close()
    return result,dashboard_state()

def execute_approved(proposal_data,request_id):
    floor=TradingFloor(DATABASE)
    try:
        payload=json.loads(proposal_data) if isinstance(proposal_data,str) else proposal_data
        proposal=Proposal(**payload.get('proposal',payload))
        result=floor.execute(proposal,request_id)
    except (ValueError,TypeError,json.JSONDecodeError) as exc:result={'error':str(exc)}
    finally:floor.close()
    return result,dashboard_state()

def build_dashboard():
    with gr.Blocks() as dashboard:
        gr.Markdown('# Academy paper-trading floor\nSynthetic fixtures only. Research, proposals, human review and persistent paper positions use one local database.')
        symbol=gr.Dropdown(['ACA','LAB','EDU'],value='ACA',label='Synthetic company')
        quantity=gr.Number(value=5,precision=0,label='Whole shares')
        run=gr.Button('Research and check proposal')
        research=gr.JSON(label='Evidence');proposal=gr.JSON(label='Proposal and deterministic risk');portfolio=gr.JSON(label='Portfolio')
        run.click(lambda s,q:inspect(s,q,DATABASE),[symbol,quantity],[research,proposal,portfolio])
        state=gr.JSON(label='Proposals, review state, activity and agent status')
        refresh=gr.Button('Refresh persistent state');refresh.click(dashboard_state,[],state)
        selected=gr.Textbox(label='Exact proposal JSON from the research result',lines=5)
        reviewer_token=gr.Textbox(label='Separate local reviewer token',type='password')
        action=gr.Dropdown(['APPROVE','REJECT'],value='APPROVE',label='Human review action')
        review=gr.Button('Record human review');result=gr.JSON(label='Action result')
        review.click(review_and_execute,[selected,reviewer_token,action],[result,state])
        request_id=gr.Textbox(label='Stable paper-order request ID',value='academy-order-001')
        execute=gr.Button('Execute already approved paper order')
        execute.click(execute_approved,[selected,request_id],[result,state])
        dashboard.load(dashboard_state,[],state)
    return dashboard

# Lazy construction keeps callback tests independent from framework UI registration.
demo=None
if __name__=='__main__':build_dashboard().launch(server_name='127.0.0.1',share=False)
