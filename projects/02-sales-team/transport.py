"""Actual SMTP to an explicitly owned loopback teaching sink only, never Internet mail."""
from dataclasses import dataclass
from email.message import EmailMessage
from email.policy import SMTP
import smtplib
import hmac
import re


def verify_received_payload_hash(message, expected_hash):
    """Verify a parsed SMTP header while ignoring surrounding RFC folding WSP only.

    Header folding can put whitespace before an intact hex token. Internal whitespace,
    duplicate headers, malformed hex and a different valid digest remain failures.
    This verifies transport evidence; it never grants or changes message approval.
    """
    values = message.get_all('X-Academy-Payload-SHA256', [])
    if len(values) != 1 or not isinstance(expected_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_hash):
        raise ValueError('one payload hash header and exact expected SHA256 required')
    received = str(values[0]).strip(' \t\r\n')
    if not re.fullmatch(r'[0-9a-f]{64}', received) or not hmac.compare_digest(received, expected_hash):
        raise ValueError('received payload hash differs from exact approved payload')
    return received


@dataclass(frozen=True)
class OwnedSinkSMTP:
    port: int
    host: str = '127.0.0.1'
    ownership_acknowledged: bool = False
    timeout: float = 5.0

    def __post_init__(self):
        if self.host not in {'127.0.0.1', '::1'}:
            raise ValueError('Only literal loopback owned sinks are allowed')
        if self.ownership_acknowledged is not True or type(self.port) is not int or not 1024 <= self.port <= 65535:
            raise ValueError('Explicit ownership acknowledgement and unprivileged sink port required')
        if not 0 < self.timeout <= 30:
            raise ValueError('Bounded timeout required')

    def send(self, payload, message_id):
        message = EmailMessage(policy=SMTP)
        message['From'] = 'academy-practice@example.invalid'
        message['To'] = payload['recipient']
        message['Subject'] = payload['subject']
        message['Message-ID'] = message_id
        message['X-Academy-Revision'] = str(payload['revision'])
        message['X-Academy-Payload-SHA256'] = payload['payload_hash']
        message.set_content(payload['body'], charset='utf-8', cte='quoted-printable')
        # SMTP's 250 DATA response means accepted by this sink, not real-world delivery.
        with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as smtp:
            refused = smtp.send_message(message)
            if refused:
                raise RuntimeError('recipient refused by owned sink')
        return {'outcome': 'accepted_by_owned_smtp_sink', 'message_id': message_id,
                'host': self.host, 'port': self.port, 'external_messages_sent': 0}
