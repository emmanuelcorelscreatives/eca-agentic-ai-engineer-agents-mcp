"""Bounded READ retries; uncertain writes require explicit reconciliation."""
import time

class UnknownWriteOutcome(RuntimeError): pass

def classify(exc, *, operation):
    if operation not in {'read', 'write'}: raise ValueError('read/write required')
    if isinstance(exc, (ValueError, TypeError, PermissionError)):
        return 'permanent'
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return 'retryable_read' if operation == 'read' else 'unknown_write'
    return 'escalate'


def retry_read(operation, *, attempts=3, deadline_seconds=5, backoff_seconds=0.1,
               sleep=time.sleep, clock=time.monotonic):
    if type(attempts) is not int or attempts < 1 or deadline_seconds <= 0 or backoff_seconds < 0:
        raise ValueError('invalid retry policy')
    started = clock()
    for attempt in range(attempts):
        if clock() - started >= deadline_seconds: raise TimeoutError('read deadline elapsed')
        try: return operation()
        except Exception as exc:
            if classify(exc, operation='read') != 'retryable_read' or attempt + 1 == attempts:
                raise
            delay = backoff_seconds * (2 ** attempt)
            if clock() - started + delay >= deadline_seconds: raise TimeoutError('read deadline elapsed') from exc
            sleep(delay)


def write_once(operation):
    try: return operation()
    except Exception as exc:
        if classify(exc, operation='write') == 'unknown_write':
            raise UnknownWriteOutcome('Reconcile by durable request ID before deciding whether to retry') from exc
        raise
