# LangChain Agent Patterns

> Self-contained, **deployable** agents built with LangChain (`create_agent`), LangGraph, and Deep Agents (`create_deep_agent`). Current API as of June 2026.

Each folder under [`examples/`](examples/) is an independent agent — copy it out, install, run, and deploy on its own.

## Agents

| Folder | Stack | What it does |
|--------|-------|--------------|
| [`examples/release-notes-agent/`](examples/release-notes-agent/) | Deep Agents | Commit log → house-style release notes. Planning + on-disk skill. CLI + `langgraph.json`. |
| [`examples/lead-lifecycle-agent/`](examples/lead-lifecycle-agent/) | Deep Agent + LangGraph workflow | Lead-qualification Deep Agent (per-lead memory + BANT skill + learning loop) chained to an engagement agent. Container-deployable; Supabase/Postgres memory via env. |
| [`examples/deep-research-agent/`](examples/deep-research-agent/) | Deep Agents | Orchestrator + parallel research subagents, `tavily_search` + `think_tool`. **MIT port of [`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents)** — see its `ATTRIBUTION.md`. |
| [`examples/text-to-sql-agent/`](examples/text-to-sql-agent/) | Deep Agents | NL → SQL on the Chinook DB: planning + skills + `AGENTS.md` memory. **MIT port** — see its `ATTRIBUTION.md`. |

Each folder ships its own `README.md` with setup, run, and deploy steps.

## Quick start

```bash
export ANTHROPIC_API_KEY=...          # or DEEP_AGENT_MODEL for another provider
cd examples/release-notes-agent
pip install -e .                       # or: uv sync
python agent.py                        # run the CLI
langgraph dev                          # or serve via langgraph.json
```

## Deploy

Each agent is deployable on **LangGraph Platform / self-host** (`langgraph.json`), and
`lead-lifecycle-agent/` includes a `Dockerfile`:

```bash
cd examples/lead-lifecycle-agent
docker build -t lead-lifecycle-agent .
docker run --rm -p 8000:8000 --env-file .env lead-lifecycle-agent
```

## Reference docs & snippets

This repo is **deployable code only**. The conceptual guides (LangChain / LangGraph /
Deep Agents) and single-file pattern snippets that accompany these agents are maintained
separately. Authoritative source: **[docs.langchain.com/oss/python](https://docs.langchain.com/oss/python)**.

## License & attribution

`examples/deep-research-agent/` and `examples/text-to-sql-agent/` are faithful ports of
examples from [`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents)
(MIT License, © LangChain, Inc.), pinned to commit `a98f0df`; each ships an `ATTRIBUTION.md`
with the full license text. Upstream model ids (`claude-sonnet-4-5`) are preserved in the
ports; our own agents default to `claude-sonnet-4-6`.

## Version compatibility

| Package | Version |
|---------|---------|
| langchain | 1.x |
| langgraph | 1.x |
| deepagents | 0.4.x (verified on 0.4.2) |

**Last updated**: 2026-06-16
