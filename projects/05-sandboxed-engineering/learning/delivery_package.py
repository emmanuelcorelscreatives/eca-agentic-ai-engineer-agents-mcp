"""Package the exact completed whole-crew result, never the legacy fixed template.

Author-only implementation pending first central QA. No generated code executes
here. Actual tool validation is a prerequisite; independent source/material review
remains necessary even after this ZIP is produced.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
import stat
import tempfile
import zipfile
from semantic_team import (ACCEPTANCE_TESTS,CRITERIA,FILES,consume,sha,validate_files,
                           validate_requirements,validate_architecture,validate_receipt)

MAX_RESULT_BYTES=1_048_576
MAX_TOTAL_BYTES=4_194_304
MAX_ARCHIVE_BYTES=1_048_576


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def _strict_json(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('duplicate completion JSON key')
            result[key]=value
        return result
    def number(value):
        import math
        parsed=float(value)
        if not math.isfinite(parsed):raise ValueError('nonfinite completion number')
        return parsed
    return json.loads(raw,object_pairs_hook=pairs,parse_float=number,
                      parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite completion JSON')))


def _completion_bytes(evidence_dir,result):
    root=Path(evidence_dir)
    if root.absolute()!=root.resolve(strict=True) or not root.is_dir():raise ValueError('canonical evidence directory required')
    entries=list(root.iterdir())
    if len(entries)>256:raise ValueError('bounded evidence inventory required')
    matches=[p for p in entries if p.name.endswith('-completion.json')]
    if len(matches)!=1:raise ValueError('exact one retained completion event required')
    fd=os.open(matches[0],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>MAX_RESULT_BYTES:
            raise ValueError('ordinary bounded completion evidence required')
        with os.fdopen(os.dup(fd),'rb') as handle:raw=handle.read(MAX_RESULT_BYTES+1)
    finally:os.close(fd)
    if len(raw)>MAX_RESULT_BYTES or _strict_json(raw)!=result:raise ValueError('completion event does not bind exact result')
    return raw


def _validated_members(result,evidence_dir,allow_offline_fixture=False):
    if type(allow_offline_fixture) is not bool:raise ValueError('explicit fixture option required')
    if not isinstance(result,dict):raise ValueError('typed whole-team result required')
    status=result.get('status')
    offline=status=='OFFLINE_TEST_DOUBLE_PASS'
    if result.get('passed') is not True or status not in ('ACTUAL_TEAM_RUN_AWAITING_INDEPENDENT_ACCEPTANCE','OFFLINE_TEST_DOUBLE_PASS'):
        raise ValueError('successful complete whole-team result required')
    if offline and not allow_offline_fixture:raise ValueError('offline fixture delivery is not a production package')
    raw=_canonical(result)
    if len(raw)>MAX_RESULT_BYTES:raise ValueError('result size limit')
    completion=_completion_bytes(evidence_dir,result)
    files=validate_files(result['files'])
    if set(files)!=FILES:raise ValueError('source scope mismatch')
    artifacts=result['artifacts']
    if set(artifacts)!={'requirements','architecture','implementation','qa_plan'}:raise ValueError('exact typed role artifacts required')
    requirements=validate_requirements(consume(artifacts['requirements'],'product_manager',1))
    validate_architecture(consume(artifacts['architecture'],'architect',1),requirements)
    revision=artifacts['implementation'].get('revision')
    if type(revision) is not int or not 1<=revision<=3:raise ValueError('bounded implementation revision required')
    if consume(artifacts['implementation'],'developer',revision)!=files:raise ValueError('final source differs from developer artifact')
    qa_plan=consume(artifacts['qa_plan'],'quality_assurance',1)
    if set(qa_plan)!={'tests','coverage'} or set(qa_plan['coverage'])!=CRITERIA:raise ValueError('QA coverage mismatch')
    if not isinstance(qa_plan['tests'],str) or len(qa_plan['tests'].encode())>20000:raise ValueError('QA test quota')
    attempts=result['attempts']
    if not isinstance(attempts,list) or not 1<=len(attempts)<=3:raise ValueError('bounded actual test attempts required')
    if revision!=len(attempts):raise ValueError('source revisions and test attempts disagree')
    last=attempts[-1];receipt=last['receipt']
    if last['source_sha256']!=sha(files) or last['receipt_sha256']!=sha(receipt):raise ValueError('final receipt/source binding mismatch')
    validate_receipt(receipt,files,qa_plan['tests'])
    if receipt['passed'] is not True or not all(receipt['observations'].values()):raise ValueError('unpassed observations cannot be packaged')
    if not offline and receipt['execution']!='inside-owned-container':raise ValueError('real container execution required')
    matrix=result['acceptance_matrix']
    if set(matrix)!=CRITERIA or any(row!={'passed':True,'receipt_sha256':sha(receipt)} for row in matrix.values()):
        raise ValueError('acceptance matrix not bound to final observation')
    calls=result['calls']
    if not isinstance(calls,list) or not 5<=len(calls)<=9 or len({c['request_id'] for c in calls})!=len(calls):
        raise ValueError('exact bounded unique model-call lineage required')
    expected_roles={'requirements':'product_manager','architecture':'architect','implementation':'developer',
                    'test-plan':'quality_assurance','review':'quality_assurance','repair':'developer'}
    for call in calls:
        if set(call)!={'role','stage','request_id','response_sha256'} or expected_roles.get(call['stage'])!=call['role']:
            raise ValueError('role call lineage mismatch')
        if not isinstance(call['request_id'],str) or not call['request_id'] or not re.fullmatch(r'[a-f0-9]{64}',call['response_sha256']):
            raise ValueError('actual response lineage required')
    if any(artifact['response_sha256'] not in {c['response_sha256'] for c in calls} for artifact in artifacts.values()):
        raise ValueError('artifact producer missing from retained call lineage')
    for index,attempt in enumerate(attempts):
        if attempt['attempt']!=index or attempt['receipt_sha256']!=sha(attempt['receipt']):
            raise ValueError('historical attempt receipt was altered')
    members={name:body.encode() for name,body in files.items()}
    members['test_course_acceptance.py']=ACCEPTANCE_TESTS.encode()
    members['test_independent_qa.py']=qa_plan['tests'].encode()
    members['.eca/whole-team-result.json']=raw+b'\n'
    members['.eca/original-completion-event.json']=completion
    manifest={'schemaVersion':1,'deliveryStatus':'OFFLINE_FIXTURE_NOT_PRODUCTION' if offline else 'ACTUAL_RESULT_AWAITING_INDEPENDENT_ACCEPTANCE',
              'resultSha256':sha(result),'sourceSha256':sha(files),'finalReceiptSha256':sha(receipt),
              'memberSha256':{name:hashlib.sha256(body).hexdigest() for name,body in sorted(members.items())},
              'independentAcceptanceRequired':True,'generatedCodeExecutedByPackager':False}
    members['.eca/delivery-manifest.json']=_canonical(manifest)+b'\n'
    if len({name.casefold() for name in members})!=len(members):raise ValueError('archive path collision')
    if any(name.startswith('/') or '..' in name.split('/') or '\\' in name for name in members):raise ValueError('unsafe archive path')
    if sum(len(body) for body in members.values())>MAX_TOTAL_BYTES:raise ValueError('archive uncompressed quota')
    return members,manifest


def package_delivery(result,destination,evidence_dir,allow_offline_fixture=False):
    members,manifest=_validated_members(result,evidence_dir,allow_offline_fixture)
    destination=Path(destination)
    parent=destination.parent
    if parent.absolute()!=parent.resolve(strict=True) or not parent.is_dir():raise ValueError('canonical destination directory required')
    if destination.suffix.lower()!='.zip' or destination.name in ('','.', '..'):raise ValueError('ZIP destination required')
    if destination.exists() or destination.is_symlink():raise FileExistsError('new archive destination required')
    fd,temporary_name=tempfile.mkstemp(prefix='.eca-delivery-',suffix='.zip',dir=parent)
    temporary=Path(temporary_name);os.close(fd)
    try:
        with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for name,body in sorted(members.items()):archive.writestr(name,body)
        if temporary.stat().st_size>MAX_ARCHIVE_BYTES:raise ValueError('compressed archive quota')
        with zipfile.ZipFile(temporary) as archive:
            if len(archive.namelist())!=len(members) or set(archive.namelist())!=set(members):raise ValueError('archive inventory mismatch')
            if archive.testzip() is not None:raise ValueError('archive CRC failure')
            for name,expected in members.items():
                if archive.read(name)!=expected:raise ValueError('archive member differs from actual source/evidence')
        with temporary.open('rb') as handle:os.fsync(handle.fileno())
        # Same-filesystem hard-link publishes a complete archive atomically and
        # fails if another writer won the destination. No overwrite fallback.
        os.link(temporary,destination,follow_symlinks=False)
        directory=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(directory)
        finally:os.close(directory)
        return {'path':str(destination),'sizeBytes':destination.stat().st_size,
                'archiveSha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
                'manifest':manifest,'independentAcceptanceRequired':True}
    finally:
        try:temporary.unlink()
        except FileNotFoundError:pass
