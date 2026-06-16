# Examples

Each subfolder is a **self-contained, deployable agent** — copy it out and run/deploy on
its own (code + `pyproject.toml` + `.env.example` + README, and `langgraph.json` /
`Dockerfile` where applicable).

```bash
export ANTHROPIC_API_KEY=...
cd <agent-folder>
pip install -e .        # or: uv sync
```

| Folder | Stack | What it does |
|--------|-------|--------------|
| [`release-notes-agent/`](release-notes-agent/) | Deep Agents | Commit log → house-style release notes. Planning + on-disk skill. CLI + `langgraph.json`. **Ours.** |
| [`lead-lifecycle-agent/`](lead-lifecycle-agent/) | Deep Agent + LangGraph workflow | Lead-qualification Deep Agent (per-lead memory + BANT skill + learning loop) → engagement agent. Container-deployable; Supabase/Postgres memory via env. **Ours.** |
| [`deep-research-agent/`](deep-research-agent/) | Deep Agents | Orchestrator + parallel research subagents, `tavily_search` + `think_tool`. **MIT port of `langchain-ai/deepagents`** — see its `ATTRIBUTION.md`. |
| [`text-to-sql-agent/`](text-to-sql-agent/) | Deep Agents | NL → SQL on Chinook: planning + skills + `AGENTS.md` memory. **MIT port** — see its `ATTRIBUTION.md`. |

Conceptual guides and single-file pattern snippets are kept separately — see
[docs.langchain.com/oss/python](https://docs.langchain.com/oss/python).
