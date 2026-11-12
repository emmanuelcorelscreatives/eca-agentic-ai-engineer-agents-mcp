"""Actual SDK lifecycle/trace instrumentation. No provider call on import.

The export is a local copy of genuine SDK span identifiers and lifecycle callbacks,
not a claim that OpenAI hosted telemetry was uploaded or accepted.
"""
from __future__ import annotations

from collections import defaultdict
import json
import os
from pathlib import Path
import threading
import time

from agents import RunHooks
from agents.tracing import TracingProcessor


def usage_fields(usage):
    """Missing counters remain None; do not turn unavailable provider usage into zero."""
    return {key: getattr(usage, key, None) if usage is not None else None
            for key in ('requests', 'input_tokens', 'output_tokens', 'total_tokens')}


class ObservationHooks(RunHooks):
    def __init__(self):
        self.events = []
        self.calls = []
        self._active = defaultdict(list)

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        call = {'agent': agent.name, 'started_monotonic': time.perf_counter(),
                'status': 'started', 'duration_seconds': None, 'usage': usage_fields(None),
                'response_id': None}
        self.calls.append(call)
        self._active[(id(context), agent.name)].append(call)

    async def on_llm_end(self, context, agent, response):
        pending = self._active[(id(context), agent.name)]
        if not pending:
            # Diagnostics must not turn a completed model call into a failed lesson.
            # Retain the missing-start limitation instead of inventing elapsed time.
            self.calls.append({'agent': agent.name, 'status': 'complete_start_unobserved',
                               'duration_seconds': None,
                               'usage': usage_fields(getattr(response, 'usage', None)),
                               'response_id': getattr(response, 'response_id', None)})
            return
        call = pending.pop(0)
        call.update(status='complete', duration_seconds=time.perf_counter() - call['started_monotonic'],
                    usage=usage_fields(getattr(response, 'usage', None)),
                    response_id=getattr(response, 'response_id', None))

    async def on_tool_start(self, context, agent, tool):
        self.events.append({'kind': 'tool_start', 'agent': agent.name, 'tool': tool.name,
                            'tool_call_id': getattr(context, 'tool_call_id', None)})

    async def on_tool_end(self, context, agent, tool, result):
        self.events.append({'kind': 'tool_end', 'agent': agent.name, 'tool': tool.name,
                            'tool_call_id': getattr(context, 'tool_call_id', None)})

    async def on_handoff(self, context, from_agent, to_agent):
        self.events.append({'kind': 'handoff', 'from_agent': from_agent.name, 'to_agent': to_agent.name})

    async def on_agent_end(self, context, agent, output):
        # Never copy arbitrary final text into debugging telemetry.
        self.events.append({'kind': 'agent_final', 'agent': agent.name})

    def export(self):
        return {'origin': 'actual-sdk-lifecycle-callbacks',
                'calls': [{k: v for k, v in row.items() if k != 'started_monotonic'}
                          for row in self.calls], 'events': list(self.events)}


class LocalSDKTraceProcessor(TracingProcessor):
    """Thread-safe, redacted local span collector with no HTTP exporter."""
    def __init__(self):
        self._lock = threading.Lock()
        self.traces = []
        self.spans = []

    def on_trace_start(self, trace):
        pass

    def on_trace_end(self, trace):
        exported = trace.export()
        if exported is not None:
            with self._lock:
                self.traces.append({key: exported.get(key) for key in ('id', 'workflow_name')})

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        exported = span.export()
        if exported is None:
            return
        # Reject arbitrary input/output/error text even if a caller changed SDK privacy settings.
        data = exported.get('span_data') or {}
        row = {key: exported.get(key) for key in
               ('trace_id', 'id', 'parent_id', 'started_at', 'ended_at')}
        row['span_data'] = {key: data[key] for key in
                            ('type', 'name', 'model', 'from_agent', 'to_agent', 'usage') if key in data}
        row['error_present'] = exported.get('error') is not None
        with self._lock:
            self.spans.append(row)

    def shutdown(self):
        pass

    def force_flush(self):
        pass

    def write(self, path: str | Path):
        with self._lock:
            payload = {'origin': 'actual-sdk-span-exports-local-only',
                       'hosted_upload_proven': False, 'traces': self.traces, 'spans': self.spans}
            body = json.dumps(payload, indent=2, allow_nan=False) + '\n'
        # Fail rather than erase prior run evidence. Keep the learner's synthetic session private.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(body)


def complete_lineage_observed(events):
    """Inspect actual callbacks; instructions alone never prove delegation occurred."""
    inventory = [i for i, row in enumerate(events) if row.get('kind') == 'tool_end'
                 and row.get('tool') == 'ask_inventory']
    policy = [i for i, row in enumerate(events) if row.get('kind') == 'tool_end'
              and row.get('tool') == 'ask_policy']
    transfers = [i for i, row in enumerate(events) if row.get('kind') == 'handoff'
                 and row.get('to_agent') == 'Delivery synthesizer']
    shipping = [i for i, row in enumerate(events) if row.get('kind') == 'tool_end'
                and row.get('tool') == 'shipping']
    final = [i for i, row in enumerate(events) if row.get('kind') == 'agent_final'
             and row.get('agent') == 'Delivery synthesizer']
    return bool(inventory and policy and transfers and shipping and final
                and max(inventory[0], policy[0]) < transfers[0] < shipping[-1] < final[-1])
