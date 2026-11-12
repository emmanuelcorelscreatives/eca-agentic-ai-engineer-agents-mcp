"""Course-owned file capabilities and Docker-only command execution.

These controls reduce accidental damage; containers share the host kernel and are
not a production boundary for actively hostile code. No host Python/shell runner.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import time
import uuid


class FileTools:
    """Descriptor-relative operations; symlink ancestors are never followed.

    Workspace directory is owned by the operator. Do not grant another host
    process permission to rename or hard-link its ancestors during a run.
    """
    def __init__(self, root: Path, writable=("src",), max_bytes=65536):
        self.root = Path(root).absolute()
        if self.root != self.root.resolve(strict=True) or self.root.is_symlink(): raise ValueError("symlink workspace")
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        if not writable or any('/' in p or p in ('', '.', '..') for p in writable):
            os.close(self.fd); raise ValueError("explicit top-level write scopes required")
        if type(max_bytes) is not int or not 0 < max_bytes <= 1048576:
            os.close(self.fd); raise ValueError("invalid file quota")
        self.writable, self.max_bytes = tuple(writable), max_bytes

    def close(self):
        if self.fd is not None: os.close(self.fd); self.fd = None
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _parent(self, name, write=False):
        if not isinstance(name, str) or '\\' in name or '\x00' in name:
            raise ValueError("invalid path")
        parts = name.split('/')
        if not name or name.startswith('/') or any(p in ('', '.', '..') for p in parts):
            raise ValueError("relative canonical path required")
        if write and (parts[0] not in self.writable or len(parts) < 2):
            raise PermissionError("read-only scope")
        current = os.dup(self.fd)
        try:
            for part in parts[:-1]:
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
                os.close(current); current = nxt
            return current, parts[-1]
        except BaseException:
            os.close(current); raise

    def read(self, name):
        parent, leaf = self._parent(name)
        try:
            fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            try:
                import stat
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("only unlinked ordinary workspace files")
                with os.fdopen(os.dup(fd), 'rb') as handle: data = handle.read(self.max_bytes + 1)
                if len(data) > self.max_bytes: raise ValueError("file quota exceeded")
                return data.decode('utf-8')
            finally: os.close(fd)
        finally: os.close(parent)

    def write(self, name, content, expected_sha256=None):
        if not isinstance(content, str): raise ValueError("UTF-8 text required")
        data = content.encode('utf-8')
        if len(data) > self.max_bytes: raise ValueError("file quota exceeded")
        parent, leaf = self._parent(name, write=True)
        temp = '.eca-' + uuid.uuid4().hex
        try:
            if expected_sha256 is not None:
                old = self.read(name).encode()
                if hashlib.sha256(old).hexdigest() != expected_sha256:
                    raise ValueError("stale source")
            else:
                try: os.stat(leaf, dir_fd=parent, follow_symlinks=False)
                except FileNotFoundError: pass
                else: raise FileExistsError("replacement requires exact old hash")
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=parent)
            try:
                with os.fdopen(os.dup(fd), 'wb') as handle:
                    handle.write(data); handle.flush(); os.fsync(handle.fileno())
            finally: os.close(fd)
            os.replace(temp, leaf, src_dir_fd=parent, dst_dir_fd=parent)
            os.fsync(parent)
            return hashlib.sha256(data).hexdigest()
        finally:
            try: os.unlink(temp, dir_fd=parent)
            except FileNotFoundError: pass
            os.close(parent)

    def list(self, directory):
        parent, leaf = self._parent(directory)
        try:
            fd = os.open(leaf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try: return sorted(os.listdir(fd))
            finally: os.close(fd)
        finally: os.close(parent)


# Fixed command identities, never model-supplied argv, package names or shell text.
COMMANDS = {
    'uv-version': ('uv', '--version'),
    'uv-venv': ('uv', 'venv', '--offline', '/tmp/eca-venv'),
    'uv-lock-check': ('uv', 'lock', '--check', '--offline'),
    'uv-sync': ('uv', 'sync', '--frozen', '--offline', '--no-dev'),
    'app': ('python', '-B', 'src/expense_app.py'),
    'tests': ('python', '-B', '-m', 'unittest', 'discover', '-s', '/tests', '-v'),
}

@dataclass(frozen=True)
class Policy:
    image: str
    seconds: int = 20
    memory_mb: int = 256
    cpus: int = 1
    pids: int = 64
    output_bytes: int = 16384
    def __post_init__(self):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/:~-]*@sha256:[0-9a-f]{64}', self.image):
            raise ValueError('preloaded digest-pinned image required')
        for value, low, high in ((self.seconds, 1, 60), (self.memory_mb, 64, 512),
                                 (self.cpus, 1, 2), (self.pids, 16, 128),
                                 (self.output_bytes, 128, 1048576)):
            if type(value) is not int or not low <= value <= high: raise ValueError('quota out of bounds')


def docker_command(policy, workspace, tests, command_id, owner):
    if command_id not in COMMANDS: raise ValueError('command not allowlisted')
    if not re.fullmatch(r'eca-learning-[a-f0-9]{32}', owner): raise ValueError('invalid owned container name')
    paths = []
    for path in (workspace, tests):
        original = Path(path).absolute()
        resolved = original.resolve(strict=True)
        if original != resolved or not resolved.is_dir() or ',' in str(resolved) or '\n' in str(resolved):
            raise ValueError('canonical ordinary mount directory required')
        paths.append(str(resolved))
    # All source and tests mounted readonly. Dependency environment is ephemeral;
    # uv commands cannot modify lockfiles in /workspace, intentionally failing if stale.
    return ['docker', 'run', '--name', owner, '--label', 'eca.learning.owner=' + owner,
            '--rm', '--pull=never', '--log-driver=none', '--network=none', '--read-only', '--cap-drop=ALL',
            '--security-opt=no-new-privileges', '--user=65534:65534',
            '--memory=' + str(policy.memory_mb) + 'm', '--memory-swap=' + str(policy.memory_mb) + 'm',
            '--cpus=' + str(policy.cpus), '--pids-limit=' + str(policy.pids),
            '--ulimit=nofile=128:128', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m',
            '--mount', 'type=bind,source=' + paths[0] + ',target=/workspace,readonly',
            '--mount', 'type=bind,source=' + paths[1] + ',target=/tests,readonly',
            '--workdir=/workspace', '--env=HOME=/tmp', '--env=UV_PROJECT_ENVIRONMENT=/tmp/eca-venv',
            policy.image, *COMMANDS[command_id]]


def execute(policy, workspace, tests, command_id):
    """Explicit opt-in Docker operation. Never called by offline unit tests.

    Spool capped process output to disk rather than unbounded host RAM. Docker's
    client is stopped on timeout; the exact owned container is removed in finally.
    No broad container cleanup, pulls, host env/credentials, shell or retries.
    """
    owner = 'eca-learning-' + uuid.uuid4().hex
    argv = docker_command(policy, workspace, tests, command_id, owner)
    result = dict(run_id=owner, command_id=command_id, argv=argv, policy=asdict(policy),
                  execution='docker', returncode=None, timed_out=False, infrastructure_error=None,
                  stdout='', stderr='', truncated=False, cleanup_confirmed=False)
    start = time.monotonic()
    # RLIMIT_FSIZE caps logs on Linux; no unbounded communicate/capture_output.
    def limits():
        import resource
        resource.setrlimit(resource.RLIMIT_FSIZE, (policy.output_bytes, policy.output_bytes))
    try:
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            try:
                proc = subprocess.Popen(argv, stdout=out, stderr=err, env={'PATH': os.defpath},
                                        start_new_session=True, preexec_fn=limits)
                try: result['returncode'] = proc.wait(timeout=policy.seconds)
                except subprocess.TimeoutExpired:
                    result['timed_out'] = True
                    import signal
                    os.killpg(proc.pid, signal.SIGKILL); proc.wait(timeout=5)
            except OSError as exc: result['infrastructure_error'] = type(exc).__name__ + ': ' + str(exc)
            for key, handle in (('stdout', out), ('stderr', err)):
                handle.seek(0); raw = handle.read(policy.output_bytes)
                result[key] = raw.decode('utf-8', errors='replace')
                result['truncated'] |= len(raw) == policy.output_bytes
    finally:
        try:
            cleanup = subprocess.run(['docker', 'rm', '-f', owner], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, timeout=10, env={'PATH': os.defpath})
            if cleanup.returncode == 0: result['cleanup_confirmed'] = True
            else:
                check = subprocess.run(['docker', 'container', 'inspect', owner], capture_output=True,
                                       timeout=5, env={'PATH': os.defpath})
                result['cleanup_confirmed'] = check.returncode == 1 and b'No such container' in check.stderr
        except (OSError, subprocess.TimeoutExpired): pass
    result['elapsed_seconds'] = round(time.monotonic() - start, 6)
    result['passed'] = (result['returncode'] == 0 and not result['timed_out']
                        and not result['truncated'] and not result['infrastructure_error']
                        and result['cleanup_confirmed'])
    return result
