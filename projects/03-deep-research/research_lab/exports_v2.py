"""Report exports and approved duplicate-key-aware local delivery ledger."""
import hashlib
import html
import json
import os
from pathlib import Path
from .interface_v2 import render_report
from .pipeline_v2 import digest
from .reporting import delivery_digest, deliver_approved

def export(bundle,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    markdown=render_report(bundle['report'])
    files={'report.md':markdown,'report.html':'<!doctype html><meta charset="utf-8"><title>Academy Research</title><pre>'+html.escape(markdown)+'</pre>',
           'research.json':json.dumps(bundle,sort_keys=True,indent=2)}
    hashes={}
    for name,content in files.items():
        path=directory/name;path.write_text(content);hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    (directory/'sha256.json').write_text(json.dumps(hashes,indent=2))
    return hashes

def deliver_once(recipient,report,approval,key,directory,adapter):
    """A prior IN_FLIGHT record is UNKNOWN and MUST NOT be retried automatically."""
    import fcntl
    root=Path(directory);root.mkdir(parents=True,exist_ok=True,mode=0o700)
    path=root/(digest(key)+'.json');lock=os.open(str(path)+'.lock',os.O_CREAT|os.O_RDWR,0o600)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        identity=delivery_digest(recipient,report)
        if approval!=identity:raise ValueError('exact recipient/report approval required')
        if path.exists():
            old=json.loads(path.read_text())
            if old['identity']!=identity:raise ValueError('idempotency key reused for different content')
            if old['status']=='COMPLETE':return old['result']
            raise RuntimeError('prior delivery outcome unknown; inspect original server receipt')
        def persist(value):
            temp=path.with_suffix('.tmp');fd=os.open(temp,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
            with os.fdopen(fd,'w') as handle:json.dump(value,handle);handle.flush();os.fsync(handle.fileno())
            os.replace(temp,path)
            directory_fd=os.open(root,os.O_DIRECTORY)
            try:os.fsync(directory_fd)
            finally:os.close(directory_fd)
        persist({'identity':identity,'status':'IN_FLIGHT'})
        result=deliver_approved(recipient,report,approval,adapter)
        persist({'identity':identity,'status':'COMPLETE','result':result})
        return result
    finally:os.close(lock)
