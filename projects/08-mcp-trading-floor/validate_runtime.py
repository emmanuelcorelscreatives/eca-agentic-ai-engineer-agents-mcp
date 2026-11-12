"""Actual optional HTTP/browser smoke tests; no model or public account calls."""
from pathlib import Path
import argparse
import contextlib
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent

def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); return sock.getsockname()[1]

def request(base,path,body=None,token=None):
    headers={'Content-Type':'application/json'}
    if token: headers['X-Academy-Token']=token
    req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body else None,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=10) as response:
            return response.status,json.loads(response.read())
    except urllib.error.HTTPError as exc: return exc.code,json.loads(exc.read())

def wait_http(url,process):
    deadline=time.monotonic()+40
    while time.monotonic()<deadline:
        if process.poll() is not None: raise RuntimeError('server exited during startup')
        try:
            with urllib.request.urlopen(url,timeout=2) as response:
                if response.status==200: return
        except (OSError,urllib.error.URLError): time.sleep(.2)
    raise TimeoutError(url)

@contextlib.contextmanager
def process(command,env,cwd,log):
    with log.open('wb') as output:
        p=subprocess.Popen(command,cwd=cwd,env=env,stdout=output,stderr=subprocess.STDOUT)
        try: yield p
        finally:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)

def validate(output:Path,chrome:str):
    output.mkdir(parents=True,exist_ok=True)
    checks=[]
    with tempfile.TemporaryDirectory(prefix='academy-paper-runtime-') as temporary:
        database=Path(temporary)/'paper.sqlite'
        env={**os.environ,'ACADEMY_PAPER_DB':str(database),'ACADEMY_LOCAL_TOKEN':'synthetic-local-test-token'}
        api_port=port(); ui_port=port(); gradio_port=port(); base=f'http://127.0.0.1:{api_port}'
        with process([sys.executable,'-m','uvicorn','api:app','--host','127.0.0.1','--port',str(api_port)],env,ROOT,output/'api.log') as api:
            wait_http(base+'/state',api)
            assert request(base,'/state')[1]['portfolio']['cash']=='10000.00';checks.append('actual HTTP initial account')
            payload={'symbol':'ACA','quantity':5,'side':'BUY'}
            assert request(base,'/proposals',payload)[0]==401;checks.append('actual HTTP missing token rejected')
            status,proposal=request(base,'/proposals',payload,env['ACADEMY_LOCAL_TOKEN']);assert status==200
            assert proposal['risk']['allowed'];checks.append('actual HTTP typed proposal')
            assert request(base,'/proposals',{**payload,'quantity':True},env['ACADEMY_LOCAL_TOKEN'])[0]==422;checks.append('actual Pydantic bool quantity rejection')
            order={'proposal':proposal['proposal'],'request_id':'runtime-smoke-001'}
            assert request(base,'/execute',order,env['ACADEMY_LOCAL_TOKEN'])[0]==422;checks.append('actual HTTP unapproved execution rejected')
            from trading_floor import TradingFloor,Proposal
            floor=TradingFloor(str(database))
            try:floor.approve(Proposal(**proposal['proposal']),'explicit local test reviewer')
            finally:floor.close()
            status,first=request(base,'/execute',order,env['ACADEMY_LOCAL_TOKEN']);assert status==200 and first['cash']=='9373.75'
            assert request(base,'/execute',order,env['ACADEMY_LOCAL_TOKEN'])[1]==first;checks.append('actual HTTP approved transaction and idempotent retry')
            from playwright.sync_api import sync_playwright
            # Use built frontend preview, with an explicit proxy to this isolated API.
            config=Path(temporary)/'preview.config.mjs'
            config.write_text('export default {preview:{proxy:{"/api":{target:'+json.dumps(base)+',rewrite:p=>p.replace(/^\\/api/,"")}}}};')
            vite=ROOT/'frontend/node_modules/vite/bin/vite.js'
            with process(['node',str(vite),'preview','--host','127.0.0.1','--port',str(ui_port),'--strictPort','--config',str(config)],env,ROOT/'frontend',output/'react.log') as ui:
                wait_http(f'http://127.0.0.1:{ui_port}',ui)
                with sync_playwright() as pw:
                    browser=pw.chromium.launch(executable_path=chrome,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
                    try:
                        page=browser.new_page(viewport={'width':1280,'height':900})
                        page.goto(f'http://127.0.0.1:{ui_port}')
                        page.get_by_label('Local course token').fill(env['ACADEMY_LOCAL_TOKEN'])
                        page.get_by_role('button',name='Research and propose').click()
                        page.wait_for_function('document.querySelector("pre").textContent.includes("fixture-aca-001")')
                        checks.append('actual React browser proposal interaction')
                        page.get_by_role('button',name='Read portfolio and trace').click()
                        page.wait_for_function('document.querySelector("pre").textContent.includes("9373.75")')
                        page.get_by_label('Local course token').fill('')
                        page.screenshot(path=str(output/'react-dashboard.png'),full_page=True)
                        checks.append('actual React browser committed portfolio and trace')
                    finally:browser.close()
            gradio_env={**env,'GRADIO_SERVER_PORT':str(gradio_port),'GRADIO_ANALYTICS_ENABLED':'False'}
            with process([sys.executable,'gradio_app.py'],gradio_env,ROOT,output/'gradio.log') as gui:
                wait_http(f'http://127.0.0.1:{gradio_port}/config',gui)
                with sync_playwright() as pw:
                    browser=pw.chromium.launch(executable_path=chrome,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
                    try:
                        page=browser.new_page(viewport={'width':1280,'height':900})
                        page.goto(f'http://127.0.0.1:{gradio_port}')
                        page.get_by_role('button',name='Research and check proposal').click()
                        page.wait_for_function('document.body.textContent.includes("fixture-aca-001")')
                        page.screenshot(path=str(output/'gradio-dashboard.png'),full_page=True)
                        checks.append('actual Gradio browser research/risk callback')
                    finally:browser.close()
    result={'status':'PASS','checks':checks,'model_calls':0,'public_account_mutations':0,'screenshots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('*.png')}}
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--chrome',required=True)
    args=parser.parse_args()
    validate(args.output,args.chrome)
