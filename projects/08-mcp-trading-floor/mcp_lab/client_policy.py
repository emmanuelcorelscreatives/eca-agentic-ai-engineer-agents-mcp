"""Host policy narrows discovered tools independently of server capability support."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ReadOnlyHost:
    session: object
    allowed_tools: frozenset[str] = frozenset({"read_text_file", "list_directory", "list_allowed_directories"})

    async def discovery(self):
        available = await self.session.list_tools()
        return [tool for tool in available.tools if tool.name in self.allowed_tools]

    async def call(self, name: str, arguments: dict):
        if name not in self.allowed_tools:
            raise PermissionError("Host policy denies this tool")
        return await self.session.call_tool(name, arguments)
