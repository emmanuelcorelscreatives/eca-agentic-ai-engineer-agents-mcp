"""Per-session progressive MCP catalogue with dispatch-time authorization."""
from dataclasses import dataclass
import inspect
from .core import RetrievalError

@dataclass(frozen=True)
class ToolSpec:
    name: str
    capability: str
    permission: str
    description: str
    schema: dict
    handler: object

class ProgressiveRouter:
    """One router per authenticated session/process; no cross-session global state.

    Permission supplier is trusted host state, never model-supplied tool arguments.
    Discovering once cannot bypass subsequent permission revocation.
    """
    def __init__(self,specs,permissions):
        self.specs={item.name:item for item in specs}
        if len(self.specs)!=len(specs): raise RetrievalError('duplicate tool names')
        self.permissions=permissions;self.exposed=set()
    def _permitted(self,spec): return spec.permission in self.permissions()
    @staticmethod
    def _discover_descriptor():
        return {'name':'discover_capability','description':'Reveal authorized specialists for a named capability; does not grant permissions.',
                'inputSchema':{'type':'object','properties':{'capability':{'type':'string','maxLength':60}},'required':['capability'],'additionalProperties':False}}
    def descriptors(self):
        return [self._discover_descriptor()]+[
            {'name':spec.name,'description':spec.description,'inputSchema':spec.schema}
            for spec in sorted(self.specs.values(),key=lambda s:s.name)
            if spec.name in self.exposed and self._permitted(spec)]
    def discover(self,capability):
        if not isinstance(capability,str): raise RetrievalError('capability must be a string')
        candidates=[spec for spec in self.specs.values() if spec.capability==capability]
        if not candidates: raise RetrievalError('unknown capability')
        allowed=[spec.name for spec in candidates if self._permitted(spec)]
        if not allowed: raise PermissionError('capability not authorized')
        self.exposed.update(allowed)
        return {'capability':capability,'revealed':sorted(allowed),'tools':self.descriptors()}
    async def dispatch(self,name,arguments):
        import jsonschema
        if name=='discover_capability':
            jsonschema.validate(arguments,self._discover_descriptor()['inputSchema'])
            return self.discover(arguments['capability'])
        spec=self.specs.get(name)
        if spec is None or name not in self.exposed or not self._permitted(spec):
            raise PermissionError('tool is unknown, hidden, or revoked')
        jsonschema.validate(arguments,spec.schema)
        result=spec.handler(**arguments)
        return await result if inspect.isawaitable(result) else result
