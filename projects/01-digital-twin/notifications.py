"""Explicit notification adapters; no environment-triggered network delivery.

The default records a local dry run only. Supplying a callable does not authorize
external delivery: an external adapter also requires allow_external=True at the
individual dispatch. External failures are UNKNOWN, never retryable by this API.
"""
from dataclasses import dataclass
from typing import Callable, Mapping, Any


@dataclass(frozen=True)
class NotificationAdapter:
    name: str
    send: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    external: bool = True

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip() or not callable(self.send):
            raise ValueError('adapter requires a name and callable send function')
        if type(self.external) is not bool:
            raise ValueError('external must be an explicit boolean')


def _dry_run(payload):
    return {'status': 'dry_run', 'delivery': 'not_sent', 'payload': dict(payload)}


LOCAL_DRY_RUN = NotificationAdapter('local-dry-run', _dry_run, external=False)
