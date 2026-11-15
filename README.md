# Agentic AI Engineer: The Complete AI Agents & MCP Course

Emmanuel Corels Academy · 30 stages · 362 lessons · eight portfolio projects

This repository is the course's shared practical workspace. It preserves the supplied curriculum's learning objectives and separates deterministic, executable engineering exercises from optional live model/framework integrations. Synthetic profiles, companies, prospects, web pages and market prices are fictional teaching data. An offline result is never presented as a live model response, web search, market observation or external delivery.

## Start locally

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python3 scripts/run_tests.py
python3 scripts/check_curriculum.py
```

On Windows, use `python` in place of `python3` after activating the environment. The core suite requires no credentials, paid APIs, email account or market account. Optional SDK tests report skips when their dependencies are absent; a skip is not a verified integration. Each project README gives its own demo, exercise and optional integration commands. Run optional frameworks in separate environments: their dependency and Python requirements can conflict. Never install every framework into one environment merely to run the core tests.

## Project progression

| Project | Stages | Practical directory |
|---|---|---|
| Professional Digital Twin Agent | 1–5 | [01-digital-twin](projects/01-digital-twin) |
| AI Sales Development Team | 6–8 | [02-sales-team](projects/02-sales-team) |
| Deep Research Intelligence Team | 9–10 | [03-deep-research](projects/03-deep-research) |
| Market Intelligence and Stock Screening Crew | 11–13 | [04-market-intelligence](projects/04-market-intelligence) |
| Sandboxed AI Engineering Team | 14–15 | [05-sandboxed-engineering](projects/05-sandboxed-engineering) |
| Browser Task Sidekick | 16–20 | [06-browser-sidekick](projects/06-browser-sidekick) |
| Agent Application Factory | 21–25 | [07-agent-factory](projects/07-agent-factory) |
| MCP-Powered AI Trading Floor | 26–30 | [08-mcp-trading-floor](projects/08-mcp-trading-floor) |

[The complete curriculum](curriculum/lessons.json) contains exact stage/lesson titles, objectives and suggested minutes. [Lesson workbooks](curriculum/workbooks) give lesson-specific practical tasks and acceptance criteria. [Framework recipes](frameworks) cover the named external SDKs. [The shared core](coursekit/core.py) implements a bounded tool loop, explicit argument validation, approval boundaries, SQLite sessions and cited-excerpt coverage.

## Find your lesson

Start with the [curriculum guide](curriculum/README.md), then open the workbook for [stages 1–10](curriculum/workbooks/stages-01-10.md), [stages 11–20](curriculum/workbooks/stages-11-20.md), or [stages 21–30](curriculum/workbooks/stages-21-30.md). Search for the lesson ID, such as `s20-l01`. Each entry identifies the practical, deliverable and acceptance criteria. The [material index](curriculum/materials.json) lists the supplied files for each lesson; it is navigation, not proof that a live integration has run. [Practice](practice/README.md) explains how to work through exercises rather than copying solutions.

## Results and completion

Record the command, revision, dependencies and actual result of your own runs. Keep expected outcomes separate from observations; fixtures and test doubles do not certify a live model, browser session or deployment. See [recording results](evidence/README.md) and the [completion rubric](curriculum/completion-rubric.md). CI reports only the tests actually run for its commit.

## Exercises and solutions

Each project includes a starting implementation, runnable fixture, exercises and reference solutions or acceptance checks. First run the reference demo and tests, then implement the exercises. Keep test data separate from personal documents. For the digital twin, substitute only professional information you explicitly intend to use. For sales, email remains a draft until separately approved. The trading floor is paper-only and uses fictional prices; it has no brokerage connector.

## Credentials and operational boundaries

Copy `.env.example` locally only if an optional adapter needs it. Do not commit API keys, browser sessions, personal resumes or customer data. Start external demos with a small explicit budget. The browser and coding projects restrict their training tasks to local fixture sites and isolated workspaces. Human approval is an application control; a model saying “approved” is not approval.

## Licence

Code and original synthetic fixtures are licensed under [MIT](LICENSE). External framework documentation and dependencies retain their own licences. The source PDF is an Academy curriculum source and is not redistributed here.
