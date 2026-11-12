"""Central-owner Stage 25 Docker bridge; never a model-supplied tool.

The owner key and evidence directory stay outside the untrusted mounted workspace.
Two real bounded containers execute generated tests and independent acceptance.
An owner HMAC authenticates actual host-collected receipts; a container's boolean
or a self-consistent JSON SHA cannot substitute for that owner signature.
No Docker/image build/provider execution occurs on import or construction.
"""
from __future__ import annotations
import asyncio
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import uuid
from advanced import canonical,sha
from docker_validate import execute,plan

MAX_FILES=200
MAX_BYTES=8_000_000


def _write_new(path,value):
    with path.open('xb') as stream:
        stream.write(canonical(value)+b'\n');stream.flush();os.fsync(stream.fileno())
    fd=os.open(path.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def _read_tree(workspace):
    workspace=Path(workspace)
    if not workspace.is_absolute() or workspace.resolve()!=workspace or not workspace.is_dir():
        raise ValueError('real absolute workspace required')
    paths=sorted(workspace.rglob('*'))
    files={};size=0
    for path in paths:
        if path.is_symlink() or not(path.is_dir() or path.is_file()):raise ValueError('symlink/special workspace entry')
        if not path.is_file():continue
        if len(files)>=MAX_FILES:raise ValueError('too many generated files')
        size+=path.stat().st_size
        if size>MAX_BYTES:raise ValueError('generated artifact bytes exceed limit')
        files[str(path.relative_to(workspace))]=path.read_text(encoding='utf-8')
    artifacts={p:c for p,c in files.items() if not p.startswith('acceptance/')}
    acceptance={p:c for p,c in files.items() if p.startswith('acceptance/')}
    if not acceptance or not any(p.startswith('acceptance/test') and p.endswith('.py') for p in acceptance):
        raise ValueError('immutable independent acceptance suite missing')
    return artifacts,acceptance,{p:sha(c.encode()) for p,c in files.items()}


def _key(path):
    path=Path(path)
    if not path.is_absolute() or path.resolve()!=path or path.is_symlink():raise ValueError('owner key must be real absolute path')
    info=path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)&0o077:
        raise PermissionError('owner key requires same-user private regular file')
    value=path.read_bytes()
    if len(value)<32:raise ValueError('owner key requires at least 32 random bytes')
    return value


class CentralDockerOwner:
    """Construct only in the centrally admitted owner, with its private HMAC key.

    `validate` and `verify` match run_factory's async callback boundary. The owner
    must prepare a reviewed digest-pinned image with real locked dependencies
    separately; this class never builds/pulls an image or grants build network.
    """
    def __init__(self,*,image,evidence_root,key_path,explicitly_authorized=False,seconds=30):
        if not explicitly_authorized:raise PermissionError('central Docker execution must be explicitly authorized')
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}',image):
            raise ValueError('approved digest-pinned image required')
        if not 1<=seconds<=120:raise ValueError('bounded per-suite timeout required')
        self.root=Path(evidence_root)
        if not self.root.is_absolute() or self.root.resolve()!=self.root or not self.root.is_dir():raise ValueError('existing private owner evidence root required')
        info=self.root.stat()
        if info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)&0o077:raise PermissionError('owner evidence directory must be private')
        self.key_path=Path(key_path);self.secret=_key(self.key_path)
        self.image=image;self.seconds=seconds

    def _context(self,workspace,prepared):
        workspace=Path(workspace)
        for private in (self.root,self.key_path):
            if private==workspace or workspace in private.parents or private in workspace.parents:
                raise ValueError('owner key/evidence and workspace must be disjoint')
        artifacts,acceptance,inventory=_read_tree(workspace)
        if not isinstance(prepared,dict) or prepared.get('artifact_sha256')!=sha(artifacts) or prepared.get('acceptance_sha256')!=sha(acceptance):
            raise ValueError('actual artifact/independent acceptance differs from prepared hashes')
        plan(workspace,self.image,seconds=self.seconds,suite='generated')
        plan(workspace,self.image,seconds=self.seconds,suite='independent')
        return {'workspace':str(workspace),'artifact_sha256':sha(artifacts),'acceptance_sha256':sha(acceptance),
                'inventory':inventory,'image':self.image,'seconds_per_suite':self.seconds}

    async def validate(self,workspace,prepared):
        # Docker is blocking; the central owner's admitted coordinator owns this thread.
        return await asyncio.to_thread(self._execute,Path(workspace),prepared)

    def _execute(self,workspace,prepared):
        context=self._context(workspace,prepared)
        # Workspace relocation must not reset the once budget for identical inputs.
        once=self.root/('once-'+sha({k:context[k] for k in ('artifact_sha256','acceptance_sha256','image')}))
        # An existing reservation, including unknown interrupted execution, is NEVER replayed.
        once.mkdir(mode=0o700)
        _write_new(once/'request.json',context)
        _write_new(once/'EXECUTION-UNKNOWN.json',{'status':'UNKNOWN_UNTIL_OWNER_RECEIPT','replay_allowed':False})
        # Engine observation occurs outside the untrusted container, with no provider networking.
        image_result=subprocess.run(['docker','image','inspect',self.image,'--format','{{json .}}'],
            capture_output=True,text=True,timeout=10,env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent'})
        _write_new(once/'image-inspect.json',{'returncode':image_result.returncode,
            'stdout':image_result.stdout,'stderr':image_result.stderr})
        if image_result.returncode:raise RuntimeError('approved image is not locally inspectable; no pull attempted')
        image=json.loads(image_result.stdout)
        if self.image not in image.get('RepoDigests',[]):raise ValueError('actual image digest not confirmed by owner engine')
        results=[]
        for suite in ('generated','independent'):
            if self._context(workspace,prepared)!=context:raise ValueError('workspace changed before suite')
            result=execute(workspace,self.image,once/suite,explicitly_authorized=True,seconds=self.seconds,suite=suite)
            if result.get('cleanup_returncode')!=0:raise RuntimeError('owned cleanup unresolved; no further suite or repair authorized')
            if result.get('kind')!='docker-executed' or result.get('actually_started') is not True or result.get('suite_completed') is not True:
                _write_new(once/(suite+'-nonrepairable-outcome.json'),{'status':'INFRASTRUCTURE_OR_RUNTIME_UNRESOLVED',
                    'model_repair_allowed':False,'actual_result':result})
                raise RuntimeError('actual completed test execution not proven; infrastructure/timeout/unknown is not a model repair input')
            if result.get('image_config_id')!=image.get('Id'):
                raise ValueError('owned container actually used a different image config')
            results.append(result)
        if self._context(workspace,prepared)!=context:raise ValueError('workspace changed during validation')
        observed={}
        for path in sorted(once.rglob('*')):
            if path.is_file():observed[str(path.relative_to(once))]=hashlib.sha256(path.read_bytes()).hexdigest()
        receipt_id=uuid.uuid4().hex
        receipt={'kind':'docker-executed','artifact_sha256':context['artifact_sha256'],
            'acceptance_sha256':context['acceptance_sha256'],'image_digest':self.image.rsplit('@',1)[1],
            'image_config_id':image.get('Id'),'run_id':receipt_id,
            'passed':all(r['passed'] and r['returncode']==0 for r in results),
            'returncode':next((r['returncode'] for r in results if r['returncode']!=0),0),
            'stdout':'\n'.join('SUITE '+r['suite']+'\n'+r['stdout'] for r in results),
            'stderr':'\n'.join(r['stderr'] for r in results),
            'suite_results':[{'suite':r['suite'],'passed':r['passed'],'returncode':r['returncode'],
                'cleanup_returncode':r['cleanup_returncode'],'failure':r['failure'],
                'container_id':r['container_id'],'actually_started':r['actually_started'],
                'suite_completed':r['suite_completed']} for r in results],
            'owner_evidence_sha256':sha(observed),
            'limitation':'Two actual constrained test processes; not full security certification or model-quality proof.'}
        # Failed timeout/output-limit outcomes must be nonzero for pipeline repair.
        if not receipt['passed'] and receipt['returncode']==0:receipt['returncode']=1
        receipt['receipt_sha256']=sha(receipt)
        signed={'context':context,'once_directory':once.name,'receipt':receipt,'evidence':observed}
        envelope={'signed':signed,'owner_hmac_sha256':hmac.new(self.secret,canonical(signed),hashlib.sha256).hexdigest()}
        _write_new(self.root/(receipt_id+'.owner-receipt.json'),envelope)
        return receipt

    async def verify(self,workspace,prepared,receipt):
        """Authenticate owner signature AND retained real execution/log/image hashes."""
        try:
            run_id=receipt['run_id']
            if not re.fullmatch(r'[a-f0-9]{32}',run_id):return False
            envelope=json.loads((self.root/(run_id+'.owner-receipt.json')).read_text())
            signed=envelope['signed']
            expected=hmac.new(self.secret,canonical(signed),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected,envelope['owner_hmac_sha256']):return False
            if signed['receipt']!=receipt or signed['context']!=self._context(workspace,prepared):return False
            if receipt['receipt_sha256']!=sha({k:v for k,v in receipt.items() if k!='receipt_sha256'}):return False
            if receipt['owner_evidence_sha256']!=sha(signed['evidence']):return False
            if not re.fullmatch(r'once-[a-f0-9]{64}',signed['once_directory']):return False
            once=self.root/signed['once_directory']
            for relative_name,digest in signed['evidence'].items():
                path=once/relative_name
                if path.resolve()!=path or once not in path.parents or not path.is_file():return False
                if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:return False
            suites=receipt['suite_results']
            return [r['suite'] for r in suites]==['generated','independent'] and all(
                r['cleanup_returncode']==0 and r['actually_started'] is True and r['suite_completed'] is True for r in suites)
        except (KeyError,TypeError,ValueError,OSError,json.JSONDecodeError):
            return False
