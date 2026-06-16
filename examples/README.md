# Examples

Two kinds of examples:

1. **Deployable agents** (subfolders) — self-contained projects you can copy out and run/deploy on their own (code + `pyproject.toml` + `.env.example` + README, and `langgraph.json` where applicable).
2. **Single-file pattern demos** (`*.py`) — one file per pattern, illustrative snippets.

```bash
pip install -U langchain "langchain[anthropic]" langgraph
pip install -U deepagents      # for the deep-agent folders
export ANTHROPIC_API_KEY=...
```

## Deployable agents

| Folder | Stack | What it does |
|--------|-------|--------------|
| [`release-notes-agent/`](release-notes-agent/) | Deep Agents (`create_deep_agent`) | Commit log → house-style release notes. Planning + on-disk skill via `FilesystemBackend`. CLI + `langgraph.json`. **Ours.** |
| [`deep-research-agent/`](deep-research-agent/) | Deep Agents | Multi-step web research: orchestrator + parallel `research-agent` subagents, `tavily_search` + `think_tool`. **Port of `langchain-ai/deepagents` (MIT)** — see its `ATTRIBUTION.md`. |
| [`text-to-sql-agent/`](text-to-sql-agent/) | Deep Agents | NL → SQL on the Chinook DB: planning + skills + `AGENTS.md` memory + `FilesystemBackend`. **Port of `langchain-ai/deepagents` (MIT)** — see its `ATTRIBUTION.md`. |

Each folder has its own README with setup, run, and deploy steps.

## Single-file pattern demos

### Single agent
| File | Pattern |
|------|---------|
| `basic_agent.py` | ReAct — tools + interactive loop |
| `agent_with_memory.py` | ReAct + `InMemorySaver` checkpointer |
| `streaming_agent.py` | ReAct + streaming |
| `rag_agent.py` | RAG retrieval tool |

### Multi-agent
| File | Pattern |
|------|---------|
| `supervisor_multi_agent.py` | Subagents (agent-as-tool) |
| `swarm_multi_agent.py` | Handoffs (`Command.PARENT`), checkpointed |

### Custom LangGraph reasoning patterns
| File | Pattern |
|------|---------|
| `langgraph_plan_and_execute.py` | Plan-and-Execute |
| `langgraph_reflection.py` | Reflection loop |
| `langgraph_rewoo.py` | ReWOO |
| `langgraph_lats.py` | LATS (Monte Carlo Tree Search) |

## Attribution

`deep-research-agent/` and `text-to-sql-agent/` are faithful ports of examples from
[`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents) (MIT License,
Copyright © LangChain, Inc.), pinned to commit `a98f0df`. Each folder's `ATTRIBUTION.md`
carries the full license text and provenance. Their model ids are upstream's
(`claude-sonnet-4-5`); the rest of this repo defaults to `claude-sonnet-4-6`.
