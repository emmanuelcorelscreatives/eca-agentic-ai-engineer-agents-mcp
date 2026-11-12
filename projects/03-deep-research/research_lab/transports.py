"""Opt-in standard-library transports. Not used by the default offline lab."""
import asyncio
import json
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("search endpoint redirects are disabled")

class JsonSearchTransport:
    """POST to an administrator-selected HTTPS service implementing the lab contract.

    Request: {query, limit}. Response: {records: [id,title,url,text,topic,value,...]}.
    This is not a claim that an arbitrary commercial provider uses this schema;
    configure an appropriate server-side adapter for your actual search provider.
    """
    def __init__(self, endpoint, token, *, enabled=False, opener=None):
        parsed=urlparse(endpoint)
        if not enabled or parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("explicit opt-in and HTTPS endpoint required")
        if not token or any(c in token for c in "\r\n"):
            raise ValueError("separate bearer credential required")
        self.endpoint, self.token = endpoint, token
        self.opener=opener or build_opener(NoRedirect())
    def request(self, query):
        data=json.dumps({"query":query,"limit":10}).encode()
        req=Request(self.endpoint,data=data,method='POST',headers={
            'Content-Type':'application/json','Authorization':'Bearer '+self.token})
        with self.opener.open(req,timeout=15) as response:
            raw=response.read(1_000_001)
        if len(raw)>1_000_000: raise ValueError("search response too large")
        payload=json.loads(raw)
        rows=payload.get('records')
        if not isinstance(rows,list) or len(rows)>10: raise ValueError("bounded records list required")
        return rows
    async def __call__(self, query):
        return await asyncio.to_thread(self.request,query)

class SmtpDelivery:
    """Use only via reporting.deliver_approved. No automatic delivery retry."""
    def __init__(self, host, port, sender, username, password, *, enabled=False, factory=None):
        if not enabled or not host or port!=465:
            raise ValueError("explicit opt-in and implicit TLS port 465 required")
        if '@' not in sender or any(c in sender for c in "\r\n"):
            raise ValueError("valid sender required")
        self.host,self.port,self.sender=host,port,sender
        self.username,self.password=username,password
        self.factory=factory or smtplib.SMTP_SSL
    def __call__(self, recipient, report):
        if '@' not in recipient or any(c in recipient for c in "\r\n"):
            raise ValueError("valid recipient required")
        message=EmailMessage();message['From']=self.sender;message['To']=recipient
        message['Subject']='Academy research report';message.set_content(report)
        with self.factory(self.host,self.port,timeout=15,context=ssl.create_default_context()) as smtp:
            smtp.login(self.username,self.password)
            refused=smtp.send_message(message)
        if refused: raise RuntimeError("mail server refused recipient")
        return {'status':'accepted_by_configured_mail_server','delivered_to_inbox':None}
