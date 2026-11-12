"""Optional localhost course API. Human approval is deliberately outside model tools."""
from dataclasses import asdict
import os
import secrets
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from trading_floor import TradingFloor, Proposal

app = FastAPI(title='Academy synthetic paper trading')
DATABASE = os.environ.get('ACADEMY_PAPER_DB', 'paper.sqlite')

class Order(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    symbol: str = Field(min_length=1, max_length=10)
    quantity: int = Field(gt=0, le=10000)
    side: str = 'BUY'

class Execution(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    proposal: dict
    request_id: str = Field(min_length=1, max_length=100)

def authorized(token: str | None):
    expected = os.environ.get('ACADEMY_LOCAL_TOKEN', '')
    if not expected or not token or not secrets.compare_digest(expected, token):
        raise HTTPException(401, 'local course token required')

@app.get('/state')
def state():
    floor = TradingFloor(DATABASE)
    try: return {'portfolio': floor.state(), 'trace': floor.history()}
    finally: floor.close()

@app.post('/proposals')
def propose(order: Order, x_academy_token: str | None = Header(default=None)):
    authorized(x_academy_token)
    floor = TradingFloor(DATABASE)
    try:
        p = floor.propose(order.symbol, order.quantity, order.side)
        return {'proposal': asdict(p), 'risk': floor.risk(p)}
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    finally: floor.close()

@app.post('/execute')
def execute(body: Execution, x_academy_token: str | None = Header(default=None)):
    authorized(x_academy_token)
    floor = TradingFloor(DATABASE)
    try: return floor.execute(Proposal(**body.proposal), body.request_id)
    except (ValueError, TypeError) as exc: raise HTTPException(422, str(exc)) from exc
    finally: floor.close()
