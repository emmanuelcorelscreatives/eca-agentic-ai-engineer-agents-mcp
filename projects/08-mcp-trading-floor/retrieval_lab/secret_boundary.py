"""Explicit fake-canary teaching boundary; keep real credentials outside sources."""
import re

class SecretBoundary:
    def __init__(self,secrets=()):
        self.secrets=tuple(sorted((x for x in secrets if isinstance(x,str) and x),key=len,reverse=True))
    def clean(self,value):
        if isinstance(value,str):
            for secret in self.secrets: value=value.replace(secret,'[REDACTED]')
            value=re.sub(r'(?i)\b(bearer\s+)[A-Za-z0-9._~+/-]+=*',r'\1[REDACTED]',value)
            value=re.sub(r'(?i)(\b(?:api[_-]?key|access[_-]?token|password|secret)\s*[=:]\s*)[^\s,;]+',r'\1[REDACTED]',value)
            return value
        if isinstance(value,dict):
            return {key:('[REDACTED]' if re.fullmatch(r'(?i)authorization|cookie|password|secret|api[_-]?key|access[_-]?token',str(key)) else self.clean(item)) for key,item in value.items()}
        if isinstance(value,list): return [self.clean(item) for item in value]
        if isinstance(value,tuple): return tuple(self.clean(item) for item in value)
        return value
