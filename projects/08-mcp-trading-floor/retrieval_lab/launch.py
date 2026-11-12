"""Explicit existing-server launch selection, never a model-controlled command."""
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
import json
import os
from .core import RetrievalError

@dataclass(frozen=True)
class OfficialServerPaths:
    fetch_python: Path
    playwright_cli: Path
    chromium: Path
    workspace: Path

    def browser_arguments(self,output_directory):
        package=self.playwright_cli.parent/'package.json'
        data=json.loads(package.read_text())
        if data.get('name')!='@playwright/mcp' or data.get('version')!='0.0.54':
            raise RetrievalError('unexpected existing Playwright server distribution/version')
        if not self.chromium.is_file(): raise RetrievalError('explicit approved browser executable required')
        return [str(self.playwright_cli),'--headless','--isolated','--block-service-workers',
                '--executable-path',str(self.chromium),'--output-dir',str(output_directory)]

@asynccontextmanager
async def existing_session(command,args,workspace,environment=None):
    """Use real SDK stdio. Caller owns finite process/namespace/filesystem sandbox.

    Exact package locks and launch manifest are recorded by the parent QA runner.
    No personal credentials are forwarded by this function. SDK's normal basic
    platform environment still applies; browser isolation must use --isolated.
    """
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    work=Path(workspace).resolve(strict=True)
    if not work.is_dir(): raise RetrievalError('existing owned workspace required')
    forwarded={'PATH':os.defpath,'LANG':'C.UTF-8','PYTHONNOUSERSITE':'1'}
    allowed={'ACADEMY_SUBJECT','ACADEMY_TENANT','ACADEMY_PERMISSIONS','ACADEMY_QDRANT_URL','ACADEMY_SEARCH_ENDPOINT','ACADEMY_FETCH_ORIGINS'}
    if any(key not in allowed for key in (environment or {})): raise RetrievalError('unapproved environment field')
    forwarded.update(environment or {})
    async with stdio_client(StdioServerParameters(command=str(command),args=list(args),cwd=str(work),env=forwarded)) as streams:
        async with ClientSession(*streams) as client:
            await client.initialize()
            yield client
