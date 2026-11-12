"""Explicit selective recovery of positively known failures; never UNKNOWN replay."""
from copy import deepcopy
from .pipeline_v2 import Journal, digest, UnknownOutcome, RecordedFailure

MAX_TOTAL_ATTEMPTS=3
class RecoveryJournal(Journal):
    def __init__(self,directory,identity,*,authorizations=None,executor_identity=None):
        super().__init__(directory,identity)
        self.authorizations=authorizations or {}
        self.executor_identity=executor_identity
    def authorize_recovery(self,name,old,permit):
        required={'step_name','old_attempt_sha256','input_sha256','failure_kind','evidence_sha256',
                  'reviewer_identity','executor_identity','reason','new_attempt_id'}
        if not isinstance(permit,dict) or set(permit)!=required:raise ValueError('closed recovery authorization required')
        if old['status'] in ('IN_FLIGHT','UNKNOWN'):raise UnknownOutcome(name+': never recover by replay')
        if old['status'] not in ('FAILED','INVALID'):raise RecordedFailure('only known failed/invalid attempts are recoverable')
        if permit['step_name']!=name or permit['old_attempt_sha256']!=digest(old) or permit['input_sha256']!=old['input_sha256']:
            raise ValueError('recovery authorization does not bind exact prior attempt/input')
        if not self.executor_identity or permit['executor_identity']!=self.executor_identity:
            raise ValueError('explicit executing identity required')
        if not permit['reviewer_identity'] or permit['reviewer_identity']==self.executor_identity:
            raise ValueError('recovery needs a distinct positive-failure reviewer')
        for field in ('reason','new_attempt_id','evidence_sha256'):
            if not isinstance(permit[field],str) or not permit[field].strip():raise ValueError('recovery requires '+field)
        if len(permit['evidence_sha256'])!=64 or any(c not in '0123456789abcdef' for c in permit['evidence_sha256']):
            raise ValueError('reviewed positive-failure evidence SHA required')
        expected={'known_http_response':('FAILED','HTTPError'),
                  'connection_refused':('FAILED','ConnectionRefusedError'),
                  'known_malformed_response':('INVALID',old.get('error_type'))}
        pair=expected.get(permit['failure_kind'])
        if pair is None or (old['status'],old.get('error_type'))!=pair:
            raise ValueError('classification does not match actual retained failure')
        if permit['failure_kind']=='known_malformed_response':
            if 'raw_result' not in old or permit['evidence_sha256']!=digest(old['raw_result']):
                raise ValueError('malformed-output authorization must bind actual retained response')
        else:
            proof=old.get('known_failure_evidence')
            if proof is None or digest(proof)!=permit['evidence_sha256']:
                raise ValueError('known provider error needs retained actual failure evidence')
        history=self.state.get('attempt_history',{}).get(name,[])
        if any(item['attempt']['status'] in ('UNKNOWN','IN_FLIGHT') for item in history):
            raise UnknownOutcome('historical unknown attempt cannot be erased by a status change')
        if len(history)+1>=MAX_TOTAL_ATTEMPTS:raise RecordedFailure('three total attempts exhausted')
        used={item['authorization']['new_attempt_id'] for item in history}
        if permit['new_attempt_id'] in used or permit['new_attempt_id']==old.get('attempt_id'):
            raise ValueError('attempt identity must be new')
        return permit
    async def step(self,name,inputs,operation,validate,callback=None):
        existing=self.state['steps'].get(name);permit=None
        if existing and existing['status'] in ('FAILED','INVALID'):
            if digest(inputs)!=existing['input_sha256']:
                raise ValueError('selective recovery cannot change the original step inputs')
            supplied=self.authorizations.get(name)
            if supplied is None:return await super().step(name,inputs,operation,validate,callback)
            permit=self.authorize_recovery(name,existing,supplied)
            # Preserve the complete original attempt and authorization in the SAME journal.
            self.state.setdefault('attempt_history',{}).setdefault(name,[]).append({
                'attempt':deepcopy(existing),'authorization':deepcopy(permit),
                'authorization_sha256':digest(permit)})
            del self.state['steps'][name]
        async def retained_operation():
            entry=self.state['steps'][name]
            entry['attempt_id']=permit['new_attempt_id'] if permit else 'initial-'+entry['input_sha256'][:24]
            if permit:entry['recovery_authorization_sha256']=digest(permit)
            self.save()
            try:return await operation()
            except ConnectionRefusedError:
                entry['known_failure_evidence']={'kind':'connection_refused','request_started':False}
                self.save();raise
            except Exception as error:
                from urllib.error import HTTPError
                if isinstance(error,HTTPError):
                    # Preserve positively returned HTTP response, never invent a timeout receipt.
                    raw=error.read(1_000_001)
                    entry['known_failure_evidence']={'kind':'http_response','status':error.code,
                        'response_body_hex':raw[:1_000_000].hex(),'body_truncated':len(raw)>1_000_000}
                    self.save()
                raise
        return await super().step(name,inputs,retained_operation,validate,callback)
