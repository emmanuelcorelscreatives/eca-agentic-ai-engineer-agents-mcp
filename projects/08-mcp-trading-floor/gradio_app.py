"""Optional Gradio research dashboard; proposals do not constitute approval."""
import json
import gradio as gr
from trading_floor import TradingFloor

def inspect(symbol, quantity):
    floor=TradingFloor()
    try:
        research=floor.research(symbol)
        proposal=floor.propose(symbol,int(quantity))
        return research, floor.risk(proposal), floor.state()
    except ValueError as exc: return {'error':str(exc)}, {}, {}
    finally: floor.close()

with gr.Blocks() as demo:
    gr.Markdown('# Academy paper-trading research\nSynthetic fixtures only. No live execution. Human approval remains in the local CLI.')
    symbol=gr.Dropdown(['ACA','LAB','EDU'],value='ACA',label='Synthetic company')
    quantity=gr.Number(value=5,precision=0,label='Whole shares')
    run=gr.Button('Research and check proposal')
    research=gr.JSON(label='Evidence'); risk=gr.JSON(label='Deterministic risk'); state=gr.JSON(label='Initial simulated portfolio')
    run.click(inspect,[symbol,quantity],[research,risk,state])

if __name__ == '__main__': demo.launch(server_name='127.0.0.1',share=False)
