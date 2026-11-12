"""Explicit whole-workflow Docker launcher and finite host model mailbox.

No model transport is selected automatically. The operator supplies a trusted
callback, executed in a bounded child, and a preloaded immutable image digest.
"""
from __future__ import annotations
import hashlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import time
import uuid
import zipfile

MAX_FILE = 1048576
MAX_CALLS = 9


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def read_json(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_FILE:
            raise ValueError('ordinary bounded single-link JSON required')
        raw = os.read(fd, MAX_FILE + 1)
        if len(raw) > MAX_FILE: raise ValueError('file limit')
        def unique_pairs(items):
            result = {}
            for key, value in items:
                if key in result: raise ValueError('duplicate JSON key')
                result[key] = value
            return result
        def finite_only(value):
            raise ValueError('nonfinite JSON constant: ' + value)
        def finite_float(value):
            import math
            number = float(value)
            if not math.isfinite(number): raise ValueError('nonfinite JSON number')
            return number
        return json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=finite_only,
                          parse_float=finite_float)
    finally:
        os.close(fd)


def write_json(path, value):
    raw = canonical(value)
    if len(raw) > MAX_FILE: raise ValueError('file limit')
    path = Path(path)
    temporary = path.with_name('.pending-' + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        try:
            remaining = memoryview(raw)
            while remaining:
                written = os.write(fd, remaining)
                if written <= 0: raise OSError('short JSON write made no progress')
                remaining = remaining[written:]
            os.fsync(fd)
        finally:
            os.close(fd)
        # Linux atomic no-replace rename: readers never see partial JSON and
        # prior reservations/responses can never be silently overwritten.
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(temporary), -100, os.fsencode(path), 1) != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error), str(path))
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        try: temporary.unlink()
        except FileNotFoundError: pass


def _directory(path):
    path = Path(path).absolute()
    if path != path.resolve(strict=True) or not path.is_dir() or ',' in str(path) or '\n' in str(path):
        raise ValueError('canonical mount directory required')
    return path


def docker_argv(image, inputs, mailbox, name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/:~-]*@sha256:[0-9a-f]{64}', image):
        raise ValueError('preloaded digest-pinned image required')
    if not re.fullmatch(r'eca-whole-[0-9a-f]{32}', name): raise ValueError('invalid owner')
    inputs, mailbox = _directory(inputs), _directory(mailbox)
    if inputs == mailbox or inputs in mailbox.parents or mailbox in inputs.parents:
        raise ValueError('disjoint mount roots required')
    # A fresh operator-owned, size-limited tmpfs is mandatory. A normal directory
    # on a large disk is refused: generated code must not fill the host filesystem.
    fs = os.statvfs(mailbox)
    if fs.f_blocks * fs.f_frsize > 16 * 1024 * 1024:
        raise ValueError('mailbox requires a dedicated tmpfs of at most 16 MiB')
    if any(mailbox.iterdir()): raise ValueError('fresh empty mailbox required')
    return ['docker', 'run', '--name', name, '--label', 'eca.whole.owner=' + name,
            '--rm', '--pull=never', '--log-driver=none', '--network=none', '--read-only',
            '--cap-drop=ALL', '--cap-add=SETUID', '--cap-add=SETGID',
            '--security-opt=no-new-privileges', '--user=0:0',
            '--memory=768m', '--memory-swap=768m', '--cpus=2', '--pids-limit=64',
            '--ulimit=nofile=128:128', '--ulimit=fsize=1048576:1048576',
            '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777',
            '--tmpfs', '/work:rw,nosuid,nodev,size=128m,mode=1777',
            '--mount', 'type=bind,source=' + str(inputs) + ',target=/inputs,readonly',
            '--mount', 'type=bind,source=' + str(mailbox) + ',target=/mailbox',
            '--workdir=/work', '--env=HOME=/tmp', '--env=PYTHONDONTWRITEBYTECODE=1',
            image, 'python', '-B', '/opt/engineering/container_entrypoint.py']


def _provider_child(callback, request, destination):
    os.setsid()
    null = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null, 1)
        os.dup2(null, 2)
    finally: os.close(null)
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE, MAX_FILE))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    response = callback(request)
    write_json(destination, response)


class HostBroker:
    """At most one attempt per ordinal; reserve before calling, never retry.

    Callback receives a validated request and must return the actual response
    envelope. It must not fabricate request IDs, raw responses or model names.
    """
    def __init__(self, mailbox, callback, max_calls=MAX_CALLS):
        if type(max_calls) is not int or not 4 <= max_calls <= MAX_CALLS:
            raise ValueError('invalid call budget')
        self.root = _directory(mailbox)
        self.callback = callback
        self.max_calls = max_calls
        self.used = set()

    def poll(self):
        ordinal = len(self.used) + 1
        if ordinal > self.max_calls: return False
        request_path = self.root / ('request-%02d.json' % ordinal)
        if not request_path.exists(): return False
        request = read_json(request_path)
        required = {'schema', 'role', 'payload', 'input_sha', 'ordinal', 'request_sha'}
        if set(request) != required or request['schema'] != 1 or request['ordinal'] != ordinal:
            raise ValueError('invalid mailbox request')
        if request['role'] not in ('product_manager', 'architect', 'developer', 'quality_assurance'):
            raise ValueError('unknown role')
        if not isinstance(request['payload'], dict) or len(canonical(request['payload'])) > 750000:
            raise ValueError('invalid payload size')
        if not re.fullmatch('[0-9a-f]{64}', request['input_sha']): raise ValueError('invalid input digest')
        if hashlib.sha256(canonical(request['payload'])).hexdigest() != request['input_sha']:
            raise ValueError('payload digest mismatch')
        payload = {key: value for key, value in request.items() if key != 'request_sha'}
        if hashlib.sha256(canonical(payload)).hexdigest() != request['request_sha']:
            raise ValueError('request digest mismatch')
        # Reservation survives uncertain outcomes in this retained file. A new
        # launcher cannot silently reuse this mailbox, even after interruption.
        write_json(self.root / ('reserved-%02d.json' % ordinal), request)
        self.used.add(ordinal)
        destination = self.root / ('provider-%02d.json' % ordinal)
        child = multiprocessing.get_context('fork').Process(
            target=_provider_child, args=(self.callback, request, destination))
        child.start()
        child.join(60)
        timed_out = child.is_alive()
        # Also reap provider transport descendants after normal completion.
        try: os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        if timed_out:
            child.join(5)
            raise TimeoutError('provider outcome UNKNOWN; reserved attempt must not be replayed')
        if child.exitcode != 0: raise RuntimeError('provider outcome UNKNOWN; inspect reservation')
        response = read_json(destination)
        write_json(self.root / ('response-%02d.json' % ordinal),
                   {'request_sha': request['request_sha'], 'response': response})
        return True


def verified_delivery(mailbox, result, allow_offline_fixture=False):
    """Bind a successful result to the newly published whole-crew archive."""
    if type(allow_offline_fixture) is not bool: raise ValueError('explicit fixture option required')
    fixture = result.get('status') == 'OFFLINE_TEST_DOUBLE_PASS'
    if result.get('passed') is not True or result.get('status') not in ('ACTUAL_TEAM_RUN_AWAITING_INDEPENDENT_ACCEPTANCE', 'OFFLINE_TEST_DOUBLE_PASS'):
        raise ValueError('successful whole-team result required')
    if fixture and not allow_offline_fixture: raise ValueError('fixture delivery is not production evidence')
    receipt = read_json(Path(mailbox) / 'delivery-receipt.json')
    if receipt.get('manifest', {}).get('resultSha256') != hashlib.sha256(canonical(result)).hexdigest():
        raise ValueError('delivery receipt is not bound to this whole-team result')
    expected_status = 'OFFLINE_FIXTURE_NOT_PRODUCTION' if fixture else 'ACTUAL_RESULT_AWAITING_INDEPENDENT_ACCEPTANCE'
    if receipt['manifest'].get('deliveryStatus') != expected_status:
        raise ValueError('delivery provenance class mismatch')
    path = Path(mailbox) / 'delivery.zip'
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_FILE:
            raise ValueError('ordinary bounded delivery archive required')
        with os.fdopen(os.dup(fd), 'rb') as handle: raw = handle.read(MAX_FILE + 1)
    finally: os.close(fd)
    if len(raw) != receipt.get('sizeBytes') or hashlib.sha256(raw).hexdigest() != receipt.get('archiveSha256'):
        raise ValueError('delivery archive differs from its exact published receipt')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or sum(info.file_size for info in infos) > 4194304:
            raise ValueError('bounded unique delivery inventory required')
        manifest = json.loads(archive.read('.eca/delivery-manifest.json'))
        if manifest != receipt['manifest'] or json.loads(archive.read('.eca/whole-team-result.json')) != result:
            raise ValueError('archive metadata belongs to a different whole-team result')
        if set(names) != set(manifest['memberSha256']) | {'.eca/delivery-manifest.json'}:
            raise ValueError('delivery member inventory differs from its manifest')
        for name, expected in manifest['memberSha256'].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError('delivery member bytes differ from the manifest')
    return {**receipt, 'hostPath': str(path), 'independentAcceptanceRequired': True}


def launch(image, inputs, mailbox, callback, seconds=420):
    """Run all four roles inside one container; provider I/O stays on host.

    No shell, image pull/build, nested Docker socket, broad cleanup or automatic
    retry. Returned success requires actual zero exit and a retained result.
    """
    if type(seconds) is not int or not 30 <= seconds <= 900: raise ValueError('invalid timeout')
    owner = 'eca-whole-' + uuid.uuid4().hex
    argv = docker_argv(image, inputs, mailbox, owner)
    broker = HostBroker(mailbox, callback)
    proc = None
    started = time.monotonic()
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                env={'PATH': os.defpath}, start_new_session=True)
        while proc.poll() is None:
            if time.monotonic() - started > seconds: raise TimeoutError('whole-crew deadline')
            broker.poll()
            time.sleep(0.05)
        if proc.returncode != 0: raise RuntimeError('container failed; retain mailbox evidence')
        result = read_json(Path(mailbox) / 'result.json')
        delivery = verified_delivery(mailbox, result) if result.get('passed') is True else None
        return {'execution': 'whole-crew-docker', 'image': image, 'owner': owner,
                'returncode': proc.returncode, 'provider_attempts': len(broker.used), 'result': result,
                'delivery': delivery}
    finally:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
        # Exact owned name only. Failure remains an exception, not success.
        rm = subprocess.run(['docker', 'rm', '-f', owner], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=10, env={'PATH': os.defpath})
        if rm.returncode:
            import tempfile
            def cap_log():
                import resource
                resource.setrlimit(resource.RLIMIT_FSIZE, (8192, 8192))
            with tempfile.TemporaryFile() as errors:
                inspect = subprocess.run(['docker', 'container', 'inspect', owner], stdout=subprocess.DEVNULL,
                                         stderr=errors, timeout=5, env={'PATH': os.defpath}, preexec_fn=cap_log)
                errors.seek(0)
                if inspect.returncode != 1 or b'No such container' not in errors.read(8192):
                    raise RuntimeError('owned-container cleanup unconfirmed')
