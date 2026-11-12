"""Server-owned exact-session run exports. Never accept a browser-supplied path."""
import hashlib
import json
from pathlib import Path
import secrets
import threading
from .contracts_v2 import validate_report
from .pipeline_v2 import digest
from .exports_v2 import export

class RunExports:
    def __init__(self,root):
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.runs={};self.lock=threading.RLock()
    def _owned(self,token,session):
        if not isinstance(session,str) or not session:raise ValueError('current server session required')
        record=self.runs.get(token)
        if record is None or record['session']!=session:raise PermissionError('run does not belong to this session')
        directory=record['directory']
        if directory.is_symlink() or directory.resolve()!=directory or directory.parent!=self.root:
            raise PermissionError('run directory identity changed')
        return record
    def create(self,session):
        if not isinstance(session,str) or not session:raise ValueError('current server session required')
        with self.lock:
            token=secrets.token_urlsafe(32);directory=self.root/('run-'+secrets.token_hex(24))
            directory.mkdir(mode=0o700)
            self.runs[token]={'session':session,'directory':directory,'complete':False}
            return token,directory
    def finish(self,token,session,bundle):
        with self.lock:
            record=self._owned(token,session);validate_report(bundle['report'],bundle['evidence'])
            checkpoint=record['directory']/'state-v2.json'
            if checkpoint.is_symlink():raise PermissionError('checkpoint cannot be a symlink')
            state=json.loads(checkpoint.read_text())
            writing=state['steps'].get('writing',{})
            if state['identity']!=bundle['identity'] or writing.get('status')!='COMPLETE' or writing.get('result_sha256')!=digest(bundle['report']):
                raise ValueError('only the exact completed own-run report can be exported')
            output=record['directory']/'exports'
            if output.exists():raise ValueError('export already finalized; reuse original manifest')
            manifest=export(bundle,output) # SAME CLI export boundary, not an invented second renderer
            record.update(complete=True,manifest=manifest,output=output,
                          state_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest())
    def download_paths(self,token,session):
        with self.lock:
            record=self._owned(token,session)
            if not record['complete']:raise ValueError('research must complete before export')
            checkpoint=record['directory']/'state-v2.json'
            if checkpoint.is_symlink() or hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=record['state_sha256']:
                raise ValueError('completed run state changed')
            output=record['output']
            if output.is_symlink() or output.resolve()!=output:raise PermissionError('export directory changed')
            for name,expected in record['manifest'].items():
                path=output/name
                if path.is_symlink() or path.resolve().parent!=output or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
                    raise ValueError('own export bytes/identity changed')
            manifest_path=output/'sha256.json'
            if manifest_path.is_symlink() or json.loads(manifest_path.read_text())!=record['manifest']:
                raise ValueError('export manifest changed')
            return [str(output/name) for name in ('report.md','report.html','research.json','sha256.json')]
