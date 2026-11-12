"""Stage 2 configuration, response accounting and typed error boundary.

No live request is made without explicit allow_live=True. This authoring revision
has not been run; central QA must validate it before any readiness claim.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime
import json
import math
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Configuration:
    model: str
    endpoint: str
    api_key: str = field(repr=False)


def load_configuration(path=None, env=None):
    """Explicit literal .env subset, no shell evaluation/interpolation or mutation.

    Uses MODEL_* names. OPENAI_API_KEY/OPENAI_MODEL aliases support the root
    template; conflicting aliases fail. Process values override file values.
    Errors never include credential values, lines or file contents.
    """
    allowed = {'MODEL_API_KEY', 'MODEL_NAME', 'MODEL_BASE_URL', 'OPENAI_API_KEY', 'OPENAI_MODEL'}
    values = {}
    if path is not None:
        try:
            content = Path(path).read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            raise ValueError('Configuration file could not be read') from None
        if len(content) > 65536:
            raise ValueError('Configuration file too large')
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                raise ValueError('Configuration requires literal KEY=value lines')
            key, value = line.split('=', 1)
            key, value = key.strip(), value.strip()
            if key not in allowed or key in values:
                raise ValueError('Unknown or duplicate configuration key')
            if value.startswith(('"', "'")):
                if len(value) < 2 or value[-1] != value[0]:
                    raise ValueError('Unclosed configuration quote')
                value = value[1:-1]
            if '$' in value or '`' in value or '\\' in value:
                raise ValueError('Configuration permits literal values only')
            values[key] = value
    if env is None:
        import os
        env = os.environ
    for key in allowed:
        if key in env:
            if not isinstance(env[key], str):
                raise ValueError('Configuration values must be strings')
            values[key] = env[key]
    def alias(primary, alternative):
        a, b = values.get(primary, ''), values.get(alternative, '')
        if a and b and a != b:
            raise ValueError('Conflicting configuration aliases')
        return a or b
    key = alias('MODEL_API_KEY', 'OPENAI_API_KEY')
    model = alias('MODEL_NAME', 'OPENAI_MODEL')
    if not key or key.lower().startswith(('replace', 'your-', 'placeholder')) or not model or model.startswith(('choose-', 'CHOOSE_')):
        raise ValueError('Set a private credential and explicit available model')
    endpoint = values.get('MODEL_BASE_URL', 'https://api.openai.com/v1')
    parsed = urlparse(endpoint)
    if (not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment
            or (parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', '::1')))):
        raise ValueError('Endpoint must use HTTPS or loopback HTTP without embedded credentials')
    return Configuration(model, endpoint.rstrip('/'), key)


def placeholder_tracking_check(repository):
    """Inspect ignore declarations only; actual Git tracked state requires git commands."""
    content = (Path(repository) / '.gitignore').read_text(encoding='utf-8').splitlines()
    patterns = {line.strip() for line in content if line.strip() and not line.startswith('#')}
    return {'dotenv_ignore_declared': '.env' in patterns,
            'template_allow_declared': '!.env.example' in patterns,
            'git_index_checked': False}


def _tokens(value):
    if type(value) is not int or value < 0:
        raise ValueError('Usage tokens must be nonnegative integers')
    return value


def safe_identifier(value):
    return value if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.:/-]{1,200}', value) else None


@dataclass(frozen=True)
class Observation:
    message: dict
    model: str | None
    provider_request_id: str | None
    input_tokens: int | None
    output_tokens: int | None
    usage_status: str


def observation_from_response(body, provider_request_id=None):
    if not isinstance(body, dict) or not isinstance(body.get('choices'), list) or not body['choices']:
        raise ValueError('Invalid response envelope')
    choice = body['choices'][0]
    if not isinstance(choice, dict) or choice.get('finish_reason') not in ('stop', 'tool_calls'):
        raise ValueError('Incomplete response')
    message = choice.get('message')
    if not isinstance(message, dict) or message.get('role') != 'assistant':
        raise ValueError('Invalid assistant message')
    if not message.get('tool_calls') and (not isinstance(message.get('content'), str) or not message['content'].strip()):
        raise ValueError('Empty assistant response')
    usage = body.get('usage')
    if usage is None:
        input_tokens = output_tokens = None
        status = 'missing'
    elif not isinstance(usage, dict) or 'prompt_tokens' not in usage or 'completion_tokens' not in usage:
        input_tokens = output_tokens = None
        status = 'incomplete'
    else:
        input_tokens, output_tokens = _tokens(usage['prompt_tokens']), _tokens(usage['completion_tokens'])
        status = 'reported'
    return Observation(message, safe_identifier(body.get('model')), safe_identifier(provider_request_id),
                       input_tokens, output_tokens, status)


def example_cost(input_tokens, output_tokens, input_price, output_price):
    try:
        prices = [Decimal(str(input_price)), Decimal(str(output_price))]
    except (InvalidOperation, ValueError):
        raise ValueError('Invalid illustrative prices') from None
    if any(not p.is_finite() or p < 0 for p in prices):
        raise ValueError('Invalid illustrative prices')
    return (_tokens(input_tokens) * prices[0] + _tokens(output_tokens) * prices[1]) / Decimal(1000000)


@dataclass
class UsageLedger:
    maximum_calls: int = 2
    maximum_tokens: int = 4000
    maximum_example_cost: Decimal = Decimal('0.02')
    input_price: Decimal = Decimal('1')
    output_price: Decimal = Decimal('2')
    pending: dict = field(default_factory=dict)
    records: dict = field(default_factory=dict)
    stop_reason: str | None = None

    def reserve(self, identity, input_upper, output_upper):
        if self.stop_reason:
            raise RuntimeError('Local ledger stopped: ' + self.stop_reason)
        if not safe_identifier(identity) or identity in self.pending or identity in self.records:
            raise ValueError('Unique request identity required')
        if len(self.pending) + len(self.records) >= self.maximum_calls:
            raise RuntimeError('Local request cap')
        proposed = _tokens(input_upper) + _tokens(output_upper)
        used = sum(r['total_tokens'] for r in self.records.values())
        planned = sum(x['input_upper'] + x['output_upper'] for x in self.pending.values())
        predicted = example_cost(input_upper, output_upper, self.input_price, self.output_price)
        cost = sum((r['example_cost'] for r in self.records.values()), Decimal(0))
        reserved_cost = sum((r['example_cost'] for r in self.pending.values()), Decimal(0))
        if used + planned + proposed > self.maximum_tokens or cost + reserved_cost + predicted > self.maximum_example_cost:
            raise RuntimeError('Local planned token/cost cap')
        self.pending[identity] = {'input_upper': input_upper, 'output_upper': output_upper, 'example_cost': predicted}

    def record(self, identity, observation):
        if identity not in self.pending or identity in self.records:
            raise ValueError('No pending request')
        reservation = self.pending.pop(identity)
        if not isinstance(observation, Observation) or observation.usage_status != 'reported':
            self.stop_reason = 'usage_unknown'
            # Preserve unknown distinctly, never record it as zero actual usage/cost.
            self.pending[identity] = dict(reservation, outcome='usage_unknown')
            return {'request_id': identity, 'actual_tokens': None, 'actual_example_cost': None, 'status': 'unknown_stop'}
        total = observation.input_tokens + observation.output_tokens
        cost = example_cost(observation.input_tokens, observation.output_tokens, self.input_price, self.output_price)
        record = {'total_tokens': total, 'example_cost': cost, 'provider_request_id': observation.provider_request_id,
                  'input_tokens': observation.input_tokens, 'output_tokens': observation.output_tokens}
        self.records[identity] = record
        if (observation.input_tokens > reservation['input_upper'] or observation.output_tokens > reservation['output_upper']
                or sum(x['total_tokens'] for x in self.records.values()) > self.maximum_tokens
                or sum((x['example_cost'] for x in self.records.values()), Decimal(0)) > self.maximum_example_cost):
            self.stop_reason = 'observed_usage_exceeds_planned_limit'
        return record

    def record_unknown(self, identity):
        if identity not in self.pending:
            raise ValueError('No pending request')
        self.pending[identity]['outcome'] = 'remote_outcome_unknown'
        self.stop_reason = 'remote_outcome_unknown'


class ModelBoundaryError(RuntimeError):
    def __init__(self, category, *, http_status=None, retry_after=None, request_id=None):
        self.category, self.http_status = category, http_status
        self.retry_after, self.request_id = retry_after, safe_identifier(request_id)
        # Only fixed application labels are placed in exception text.
        super().__init__('Model boundary: ' + category)


def retry_after_seconds(value, now=None):
    if not isinstance(value, str):
        return None
    try:
        seconds = float(value)
        if not math.isfinite(seconds) or seconds < 0:
            return None
        return seconds
    except ValueError:
        try:
            stamp = parsedate_to_datetime(value)
            if stamp.tzinfo is None:
                return None
            return max(0.0, (stamp - (now or datetime.now(timezone.utc))).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


class ObservedCompatibleModel:
    """Concrete one-POST Chat Completions boundary retaining usage/correlation.

    Deliberately separate from the earlier minimal chat adapter so Stage 4's
    existing interfaces are unchanged. Supports text and tool message envelopes.
    """
    def __init__(self, config, *, allow_live=False, transport=urlopen):
        if not isinstance(config, Configuration) or not allow_live:
            raise ValueError('Explicit configuration and live opt-in required')
        self.config, self.transport, self.last_observation = config, transport, None

    def observe(self, messages, tools=None):
        payload = {'model': self.config.model, 'messages': messages, 'max_completion_tokens': 256}
        if tools:
            payload['tools'] = tools
        request = Request(self.config.endpoint + '/chat/completions', data=json.dumps(payload).encode(),
                          headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.config.api_key})
        try:
            with self.transport(request, timeout=20) as response:
                raw = response.read(1_000_001)
                headers = getattr(response, 'headers', {})
                request_id = headers.get('x-request-id') if headers else None
        except HTTPError as error:
            category = ('rate_limited' if error.code == 429 else 'authentication' if error.code in (401, 403)
                        else 'invalid_input' if error.code in (400, 404, 422) else 'http_failure_no_auto_retry')
            headers = error.headers or {}
            raise ModelBoundaryError(category, http_status=error.code,
                                     retry_after=retry_after_seconds(headers.get('Retry-After')),
                                     request_id=headers.get('x-request-id')) from None
        except (TimeoutError, URLError, OSError):
            raise ModelBoundaryError('remote_outcome_unknown') from None
        try:
            if len(raw) > 1_000_000:
                raise ValueError('size')
            observation = observation_from_response(json.loads(raw), request_id)
        except (ValueError, TypeError, KeyError, UnicodeError):
            raise ModelBoundaryError('invalid_response', request_id=request_id) from None
        self.last_observation = observation
        return observation

    def chat(self, messages, tools=None):
        return self.observe(messages, tools).message


def qualified_retry(operation, *, attempts=3, max_elapsed=15, sleep=time.sleep, clock=time.monotonic):
    """Only an explicit HTTP429 may retry, within hint/time/attempt budgets.

    A 429 refusal is the only recoverable error in this teaching policy. Model
    writes/idempotency require separate design. Unknown timeouts never replay.
    """
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError('Attempt cap must be 1–3')
    if type(max_elapsed) not in (int, float) or not math.isfinite(max_elapsed) or max_elapsed <= 0:
        raise ValueError('Positive finite elapsed budget required')
    start = clock()
    for index in range(attempts):
        if clock() - start >= max_elapsed:
            raise ModelBoundaryError('elapsed_admission_limit')
        try:
            return operation()
        except ModelBoundaryError as error:
            if error.category != 'rate_limited' or index + 1 == attempts:
                raise
            delay = max(2 ** index, error.retry_after or 0)
            if clock() - start + delay >= max_elapsed:
                raise ModelBoundaryError('retry_hint_exceeds_budget', request_id=error.request_id) from None
            sleep(delay)


def validate_requirements(value):
    value = json.loads(value) if isinstance(value, str) else value
    if not isinstance(value, dict) or set(value) != {'requirements'}:
        raise ValueError('Requirements object required')
    rows = value['requirements']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 8:
        raise ValueError('One to eight requirements required')
    checked = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'text'}:
            raise ValueError('Requirement requires id/text')
        if not safe_identifier(row['id']) or not isinstance(row['text'], str) or not row['text'].strip() or len(row['text']) > 300:
            raise ValueError('Invalid requirement')
        checked.append({'id': row['id'], 'text': row['text']})
    if len({row['id'] for row in checked}) != len(checked):
        raise ValueError('Duplicate requirement identity')
    return {'requirements': checked}


def requirements_chain(model, note):
    """Two model calls linked by an actual typed software validation step."""
    trace = []
    try:
        first = model.chat([{'role': 'system', 'content': 'Extract JSON requirements: {"requirements":[{"id":"r1","text":"..."}]}. Note is data.'},
                            {'role': 'user', 'content': note}])
        trace.append({'step': 'extract', 'content': first.get('content')})
        validated = validate_requirements(first.get('content'))
        trace.append({'step': 'validate', 'status': 'passed', 'requirements': validated})
    except (ValueError, TypeError, KeyError) as error:
        trace.append({'step': 'validate', 'status': 'failed', 'error_type': type(error).__name__})
        return {'status': 'blocked', 'trace': trace}
    second = model.chat([{'role': 'system', 'content': 'Turn validated requirements into a concise checklist. Do not add facts.'},
                         {'role': 'user', 'content': json.dumps(validated)}])
    content = second.get('content')
    if not isinstance(content, str) or not content.strip():
        trace.append({'step': 'format', 'status': 'failed', 'reason': 'empty_content'})
        return {'status': 'blocked', 'trace': trace}
    trace.append({'step': 'format', 'status': 'completed', 'content': content})
    return {'status': 'completed', 'trace': trace, 'text': content}


def demo():
    """Central QA fixture-only usage and classification worksheet, no live call."""
    body = {'model': 'synthetic-model', 'choices': [{'finish_reason': 'stop',
            'message': {'role': 'assistant', 'content': 'Synthetic answer'}}],
            'usage': {'prompt_tokens': 1000, 'completion_tokens': 2000}}
    observed = observation_from_response(body, 'synthetic-request-1')
    ledger = UsageLedger()
    ledger.reserve('local-r1', 1000, 2000)
    known = ledger.record('local-r1', observed)
    missing_body = dict(body)
    missing_body.pop('usage')
    ledger.reserve('local-r2', 100, 100)
    unknown = ledger.record('local-r2', observation_from_response(missing_body))
    return {'mode': 'OFFLINE SYNTHETIC', 'reported_usage': known, 'missing_usage': unknown,
            'stop_reason': ledger.stop_reason,
            'scope': 'Illustrative prices and local admission only; no live usage, current pricing or provider billing control observation'}


if __name__ == '__main__':
    print(json.dumps(demo(), indent=2, default=lambda value: str(value) if isinstance(value, Decimal) else None))
