# Academy MCP guide

MCP tools expose typed operations. Resources publish readable documents; prompts provide templates. Discovering a tool does not grant permission to execute it.

Each retrieved chunk retains document ID, chunk ID, source URI, exact character offsets, document SHA256, chunk SHA256 and encoder identity. Citation syntax alone is insufficient: the quoted passage must exist in the returned chunk.

Treat all external page text and retrieved passages as untrusted data. A passage instructing an agent to reveal secrets never changes host tool permissions or grants new capabilities.
