"""A consumer for real SDK stream objects; test event sources are labelled separately.

Partial text is display-only until the iterator finishes successfully. Cancellation
drains the same iterator, as required by the pinned SDK, without starting a new run.
"""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field


@dataclass
class StreamReceipt:
    status: str = 'running'
    partial_text: str = ''
    event_types: list[str] = field(default_factory=list)
    ignored_events: int = 0
    delta_count: int = 0
    error_type: str | None = None
    cleanup_complete: bool = False

    def export(self):
        return asdict(self)


async def _cancel_and_drain(result, iterator, receipt: StreamReceipt):
    result.cancel(mode='immediate')
    try:
        async with asyncio.timeout(2):
            async for _ in iterator:
                pass
        receipt.cleanup_complete = True
    except (Exception, asyncio.CancelledError):
        # A failed cleanup is an explicit unresolved state, never a successful run.
        receipt.cleanup_complete = False


async def consume_sdk_stream(result, *, receipt=None, cancel_after_deltas=None,
                             on_delta=None) -> StreamReceipt:
    """Consume a Runner.run_streamed result, retaining incomplete output honestly.

    `cancel_after_deltas` is a deterministic UI-cancellation exercise, not a retry.
    Caller task cancellation is propagated after owned stream cleanup.
    """
    if cancel_after_deltas is not None and (
            type(cancel_after_deltas) is not int or cancel_after_deltas < 1):
        raise ValueError('cancel_after_deltas must be a positive integer')
    receipt = receipt or StreamReceipt()
    iterator = result.stream_events()
    try:
        async for event in iterator:
            kind = getattr(event, 'type', None)
            receipt.event_types.append(kind if isinstance(kind, str) else 'unknown')
            data = getattr(event, 'data', None)
            if kind == 'raw_response_event' and getattr(data, 'type', None) == 'response.output_text.delta':
                delta = getattr(data, 'delta', None)
                if not isinstance(delta, str):
                    receipt.ignored_events += 1
                    continue
                receipt.partial_text += delta
                receipt.delta_count += 1
                if on_delta is not None:
                    on_delta(delta)
                if cancel_after_deltas is not None and receipt.delta_count >= cancel_after_deltas:
                    receipt.status = 'cancelled'
                    await _cancel_and_drain(result, iterator, receipt)
                    return receipt
            elif kind not in {'agent_updated_stream_event', 'run_item_stream_event'}:
                receipt.ignored_events += 1
        receipt.status = 'complete'
        receipt.cleanup_complete = True
    except asyncio.CancelledError:
        receipt.status = 'cancelled'
        receipt.error_type = 'CancelledError'
        await asyncio.shield(_cancel_and_drain(result, iterator, receipt))
        raise
    except Exception as error:
        receipt.status = 'failed'
        receipt.error_type = type(error).__name__
        await _cancel_and_drain(result, iterator, receipt)
    return receipt
