# Local validation scope — 12 November 2026

The Academy reference kit has been exercised locally in several distinct scopes:

- The dependency-free suite tests the eight project cores, negative cases, learner utilities and exercises. CI discovers both shared and project-local tests.
- Actual installed SDK checks covered nine Python framework families, including a real local A2A client/server exchange. Sixteen SDK tests executed; unrelated environment skips were not counted as passes.
- Mastra passed the actual TypeScript compiler and four deterministic workflow tests. The generated factory's Mastra scaffold also passed its compiler check.
- The browser project exercised genuine Chromium extraction on an owned local page, LangGraph SQLite close/reopen/resume, real Gradio construction and Deep Agents construction.
- The capstone exercised real MCP protocol calls, a local Qdrant collection, local HTTP routes, the React browser interface and a Gradio browser callback. The prices and research corpus remained explicitly synthetic.
- The digital twin used real PDF extraction, and the sales/research examples constructed actual typed SDK agents, tools, managers and handoffs. These checks did not invoke a provider model.

The checks found concrete compatibility bugs: a SQLite thread ownership issue, a changed Deep Agents backend API and missing Node types in a Mastra configuration. Those were corrected and the affected checks rerun. Earlier failures remain part of the Studio evidence rather than being presented as uninterrupted success.

These checks establish the stated local software behaviors. They do not certify live provider output, a deployed public application, a complete human study, or independent approval of every lesson. Required model runs, authentic screen captures, Docker execution where specified, and lesson-specific material/visual acceptance remain separate work.

The official Playwright MCP server was observed to read an owned `file://` test sentinel. Do not assume its URL options provide an operating-system filesystem sandbox. The Academy facade rejects disallowed direct navigation before dispatch, but untrusted browsing additionally requires isolated filesystem and network controls. The teaching examples should use owned local fixture pages until those boundaries have been verified for the intended environment.

Use each lesson's acceptance criteria and preserve the distinction between an expected result and an actually observed result.
