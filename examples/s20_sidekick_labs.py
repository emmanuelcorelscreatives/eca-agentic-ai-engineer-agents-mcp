"""Actual bounded offline Sidekick exercises; optional SDK labs stay separate."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'projects/06-browser-sidekick/sidekick.py'
spec=importlib.util.spec_from_file_location('s20_sidekick',path)
side=importlib.util.module_from_spec(spec);sys.modules[spec.name]=side;spec.loader.exec_module(side)

def run_case(case):
    with tempfile.TemporaryDirectory(prefix='academy-s20-') as directory:
        database=Path(directory)/'tasks.sqlite'
        store=side.TaskStore(database)
        browser=side.FixtureBrowser(path.parent/'fixtures')
        try:
            if case=='research':
                task=store.create('Find actual values in synthetic fixture',[side.Step('extract','workshops.html',criterion='workshop dates and prices present')])
                store.advance(task,browser)
                result=store.checklist(task)[0]['result']
                assert '2030-04-12' in result and 'USD 45' in result
                return {'status':'passed','observation':result,'provenance':'actual local HTML extraction; synthetic dataset'}
            if case=='approval':
                task=store.create('Save an explicitly approved local finding',[side.Step('save','finding.md',value='Synthetic workshop price: USD 30',criterion='file saved')])
                tools=side.ArtifactTools(browser,Path(directory)/'artifacts')
                assert store.advance(task,tools)=='awaiting_approval'
                assert not (Path(directory)/'artifacts/finding.md').exists()
                store.decide(task,0,'approve'); store.advance(task,tools)
                assert (Path(directory)/'artifacts/finding.md').read_text()=='Synthetic workshop price: USD 30'
                return {'status':'passed','observation':'no file before approval; exact approved file after approval'}
            if case=='recovery':
                task=store.create('Read across process-style reopen',[side.Step('extract','workshops.html',criterion='content present')])
                store.advance(task,browser);store.close();store=side.TaskStore(database)
                assert store.advance(task,browser)=='complete'
                events=store.db.execute('SELECT event FROM trace WHERE task=?',(task,)).fetchall()
                assert [row[0] for row in events]==['complete']
                return {'status':'passed','observation':'completed task resumed without duplicate extraction','events':[row[0] for row in events]}
            if case=='edit-reject':
                task=store.create('Review a proposed message',[side.Step('message','sandbox',value='draft A',criterion='message receipt')])
                store.decide(task,0,'approve')
                store.decide(task,0,'edit',side.Step('message','sandbox',value='draft B',criterion='message receipt'))
                assert store.advance(task,browser)=='awaiting_approval'
                store.decide(task,0,'reject');assert store.advance(task,browser)=='rejected'
                return {'status':'passed','observation':'edited payload required fresh approval; rejection stopped dispatch'}
            if case=='unknown':
                task=store.create('Investigate uncertain submission',[side.Step('submit','sandbox',criterion='receipt')])
                with store.db:store.db.execute("UPDATE step SET state='executing' WHERE task=?",(task,))
                assert store.advance(task,browser)=='executing'
                return {'status':'passed','observation':'uncertain action retained; no automatic replay'}
            raise ValueError('unknown case')
        finally:store.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('case',choices=['research','approval','recovery','edit-reject','unknown'])
    print(json.dumps(run_case(parser.parse_args().case),indent=2))
