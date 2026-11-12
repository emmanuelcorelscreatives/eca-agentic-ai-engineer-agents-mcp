"""Explicit configuration; importing reads no secrets and opens no database."""
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Settings:
    database: str
    retention_days: int = 30
    request_limit_per_minute: int = 30
    notification_mode: str = 'local_outbox'
    public_bind: bool = False
    auth_username: str = ''
    auth_password: str = ''
    live_model_enabled: bool = False
    model: str = ''
    def __post_init__(self):
        if self.retention_days<1 or self.request_limit_per_minute<1:raise ValueError('positive retention and rate limit required')
        if self.notification_mode not in ('local_outbox','dry_run'):raise ValueError('unconfigured external notification mode')
        if self.public_bind and (not self.auth_username or len(self.auth_password)<16):raise ValueError('public bind requires explicit username and strong configured password')
        if type(self.live_model_enabled) is not bool or (self.live_model_enabled and not self.model):raise ValueError('live model enablement requires an explicit model')
    @classmethod
    def from_env(cls,environ=None):
        env=os.environ if environ is None else environ
        return cls(database=env.get('TWIN_DATABASE',str(Path.home()/'.local/share/academy-twin/twin.sqlite')),retention_days=int(env.get('TWIN_RETENTION_DAYS','30')),request_limit_per_minute=int(env.get('TWIN_RATE_LIMIT','30')),notification_mode=env.get('TWIN_NOTIFICATION_MODE','local_outbox'),public_bind=env.get('TWIN_PUBLIC_BIND','false').lower()=='true',auth_username=env.get('TWIN_AUTH_USERNAME',''),auth_password=env.get('TWIN_AUTH_PASSWORD',''),live_model_enabled=env.get('TWIN_LIVE_MODEL_ENABLED','false').lower()=='true',model=env.get('ACADEMY_MODEL',''))


def profile_path():
    """Source checkout and installed-wheel fixtures resolve to the same data bytes."""
    local=Path(__file__).parent/'fixtures/profile.json'
    if local.is_file():return local
    from importlib.resources import files
    return files('twin_data').joinpath('profile.json')


def evaluation_path():
    local=Path(__file__).parent/'data/evaluation/professional-questions.jsonl'
    if local.is_file():return local
    from importlib.resources import files
    return files('twin_data').joinpath('professional-questions.jsonl')
