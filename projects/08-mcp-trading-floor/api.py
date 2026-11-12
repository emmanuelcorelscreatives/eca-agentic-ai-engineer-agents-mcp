"""Local synthetic course API with separate operator and reviewer capabilities."""
from dataclasses import asdict
import os
import secrets
import json
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from trading_floor import TradingFloor, Proposal

app=FastAPI(title='Academy synthetic paper trading')
DATABASE=os.environ.get('ACADEMY_PAPER_DB','paper.sqlite')

def feedback_database():return os.environ.get('ACADEMY_FEEDBACK_DB',DATABASE+'.feedback.sqlite')

class Order(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    symbol:str=Field(min_length=1,max_length=10)
    quantity:int=Field(gt=0,le=10000)
    side:str='BUY'

class Execution(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    proposal:dict
    request_id:str=Field(min_length=1,max_length=100)

class Review(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    proposal:dict
    action:str
    reason:str=''

def authorized(token:str|None,*,reviewer=False):
    key='ACADEMY_REVIEW_TOKEN' if reviewer else 'ACADEMY_LOCAL_TOKEN'
    expected=os.environ.get(key,'')
    if not expected or not token or not secrets.compare_digest(expected,token):
        raise HTTPException(401,'local reviewer token required' if reviewer else 'local course token required')
    if reviewer and secrets.compare_digest(expected,os.environ.get('ACADEMY_LOCAL_TOKEN','')):
        raise HTTPException(403,'reviewer and operator tokens must differ')

def reviewable_result(result:dict,run_id:str)->dict:
    from evaluation_lab.feedback import BoundFeedbackStore
    store=BoundFeedbackStore(feedback_database())
    try:
        output=json.dumps(result,sort_keys=True)
        output_sha256=store.register_output(run_id,output)
        return {**result,'feedback':{'run_id':run_id,'output_sha256':output_sha256,'reviewable_output':output}}
    finally:store.close()

@app.get('/health')
def health():return {'status':'ok','mode':'synthetic-paper-only'}

@app.get('/state')
def state():
    floor=TradingFloor(DATABASE)
    try:return {'portfolio':floor.state(),'trace':floor.history(),'proposals':floor.proposal_history(),'transactions':floor.transactions()}
    finally:floor.close()

@app.get('/research/{symbol}')
def research(symbol:str):
    floor=TradingFloor(DATABASE)
    try:return floor.research(symbol)
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    finally:floor.close()

@app.post('/proposals')
def propose(order:Order,x_academy_token:str|None=Header(default=None)):
    authorized(x_academy_token)
    floor=TradingFloor(DATABASE)
    try:
        p=floor.propose(order.symbol,order.quantity,order.side)
        result={'proposal':asdict(p),'risk':floor.risk(p),'next_state':'AWAITING_HUMAN_APPROVAL'}
        # Proposal risk can change with account revision; each exact version gets its own run ID.
        return reviewable_result(result,'proposal:'+p.digest()+':'+str(result['risk']['account_revision']))
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    finally:floor.close()

@app.post('/reviews')
def review(body:Review,x_academy_review_token:str|None=Header(default=None)):
    authorized(x_academy_review_token,reviewer=True)
    floor=TradingFloor(DATABASE)
    try:
        p=Proposal(**body.proposal)
        reviewer=os.environ.get('ACADEMY_REVIEWER_NAME','academy-local-reviewer')
        if body.action=='APPROVE':return {'status':'APPROVED','risk':floor.approve(p,reviewer)}
        if body.action=='REJECT':return floor.reject(p,reviewer,body.reason)
        raise ValueError('action must be APPROVE or REJECT')
    except (ValueError,TypeError) as exc:raise HTTPException(422,str(exc)) from exc
    finally:floor.close()

@app.post('/execute')
def execute(body:Execution,x_academy_token:str|None=Header(default=None)):
    authorized(x_academy_token)
    floor=TradingFloor(DATABASE)
    try:
        result=floor.execute(Proposal(**body.proposal),body.request_id)
        return reviewable_result(result,'order:'+body.request_id)
    except (ValueError,TypeError) as exc:raise HTTPException(422,str(exc)) from exc
    finally:floor.close()

class Feedback(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    submission_id:str=Field(min_length=1,max_length=100)
    run_id:str=Field(min_length=1,max_length=120)
    output_sha256:str=Field(min_length=64,max_length=64)
    rating:int=Field(ge=1,le=5)
    comment:str=Field(min_length=1,max_length=4000)
    correction:str|None=None

@app.post('/feedback')
def feedback(body:Feedback,x_academy_review_token:str|None=Header(default=None)):
    authorized(x_academy_review_token,reviewer=True)
    from evaluation_lab.feedback import BoundFeedbackStore
    store=BoundFeedbackStore(feedback_database())
    try:
        reviewer=os.environ.get('ACADEMY_REVIEWER_NAME','academy-local-reviewer')
        return store.submit(**body.model_dump(),reviewer=reviewer,token=x_academy_review_token,
                            reviewer_tokens={reviewer:os.environ['ACADEMY_REVIEW_TOKEN']})
    except (ValueError,PermissionError) as exc:raise HTTPException(422,str(exc)) from exc
    finally:store.close()

@app.get('/feedback')
def feedback_report(x_academy_token:str|None=Header(default=None)):
    authorized(x_academy_token)
    from evaluation_lab.feedback import BoundFeedbackStore
    store=BoundFeedbackStore(feedback_database())
    try:return store.report()
    finally:store.close()
