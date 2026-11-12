"""Explicit bounded Docker execution. Import and planning never start Docker.

Use a separately approved digest-pinned image containing locked dependencies.
This wrapper does NOT run arbitrary Dockerfiles or allow build-network access.
A genuine successful receipt is required before describing Docker as verified.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import time
import uuid


def plan(workspace: Path, image: str, *, seconds=30):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}',image):
        raise ValueError('digest-pinned image required')
    workspace = Path(workspace)
    if not workspace.is_absolute() or workspace.resolve() != workspace or ',' in str(workspace) or workspace.is_symlink() or not workspace.is_dir():
        raise ValueError('absolute real workspace required')
    if not 1 <= seconds <= 120: raise ValueError('timeout must be 1..120 seconds')
    if any(p.is_symlink() or (not p.is_dir() and not p.is_file()) for p in workspace.rglob('*')):
        raise ValueError('symlinks and special files forbidden')
    if not (workspace/'test_agent.py').is_file(): raise ValueError('required acceptance suite missing')
    inventory = {str(p.relative_to(workspace)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(workspace.rglob('*')) if p.is_file()}
    name = 'academy-factory-'+uuid.uuid4().hex
    # No host socket, credentials, ports, Dockerfile, host environment, or writable bind mounts.
    command = ['docker','run','--name',name,'--pull','never','--network','none','--read-only',
        '--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges',
        '--memory','256m','--memory-swap','256m','--cpus','1','--pids-limit','64',
        '--ulimit','nofile=64:64','--log-driver','none',
        '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=16m',
        '--mount',f'type=bind,source={workspace},target=/app,readonly',
        '--workdir','/app','--entrypoint','python',image,'-I','-B','-m','unittest',
        'discover','-s','/app','-p','test_agent.py','-v']
    return {'command':command,'name':name,'timeout_seconds':seconds,'inventory':inventory,
            'status':'PLANNED_NOT_EXECUTED','image':image}


def execute(workspace, image, evidence, *, explicitly_authorized=False, seconds=30):
    if not explicitly_authorized: raise PermissionError('explicit Docker execution authorization required')
    prepared = plan(Path(workspace),image,seconds=seconds)
    evidence = Path(evidence)
    if evidence.exists(): raise FileExistsError('fresh evidence directory required')
    evidence.mkdir(parents=False)
    (evidence/'plan.json').write_text(json.dumps(prepared,indent=2))
    # Bounded stream, not capture_output: an infinite-printing generated test cannot fill host RAM.
    process = subprocess.Popen(prepared['command'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent'},start_new_session=True)
    selector = selectors.DefaultSelector(); selector.register(process.stdout,selectors.EVENT_READ)
    deadline = time.monotonic()+seconds; total=0; failure=None
    try:
        with (evidence/'container.log').open('wb') as log:
            while selector.get_map():
                if time.monotonic() >= deadline: failure='timeout'; break
                events = selector.select(timeout=min(.2,max(0,deadline-time.monotonic())))
                for key,_ in events:
                    data=os.read(key.fileobj.fileno(),8192)
                    if not data: selector.unregister(key.fileobj); continue
                    total += len(data)
                    if total > 1_000_000: failure='output-limit'; break
                    log.write(data)
                if failure: break
        if failure: process.terminate()
        try: code=process.wait(timeout=3)
        except subprocess.TimeoutExpired: process.kill(); code=process.wait(timeout=3)
    finally:
        selector.close(); process.stdout.close()
        # Remove ONLY the exact owned name, even after CLI timeout; retain cleanup evidence.
        cleanup = subprocess.run(['docker','rm','-f',prepared['name']],capture_output=True,text=True,timeout=10,
                                  env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent'})
        (evidence/'cleanup.json').write_text(json.dumps({'returncode':cleanup.returncode,
            'stdout':cleanup.stdout[:4096],'stderr':cleanup.stderr[:4096]}))
    current = plan(Path(workspace),image,seconds=seconds)['inventory']
    result={'passed':code == 0 and failure is None and current == prepared['inventory'],
            'kind':'docker-executed','returncode':code,'failure':failure,
            'stdout':(evidence/'container.log').read_text(errors='replace'),'stderr':'',
            'image':image,'inventory':prepared['inventory'],'cleanup_returncode':cleanup.returncode,
            'limitation':'One actual container test run, not a complete security certification.'}
    if cleanup.returncode: result['passed']=False; result['failure']='owned-container-cleanup-unconfirmed'
    (evidence/'result.json').write_text(json.dumps(result,indent=2))
    return result
