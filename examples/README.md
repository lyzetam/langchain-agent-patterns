# Examples

Runnable agent examples, one file per pattern. All default to `model="anthropic:claude-sonnet-4-6"` and read the key from `ANTHROPIC_API_KEY` (or set `DEEP_AGENT_MODEL` / the relevant provider key).

```bash
pip install -U langchain "langchain[anthropic]" langgraph
pip install -U deepagents      # only for deepagent_release_notes.py
export ANTHROPIC_API_KEY=...
```

## Single agent

| File | Pattern | Notes |
|------|---------|-------|
| `basic_agent.py` | ReAct | Tools + interactive loop |
| `agent_with_memory.py` | ReAct + memory | `InMemorySaver` checkpointer + `thread_id` |
| `streaming_agent.py` | ReAct + streaming | `stream_mode=["updates","messages"]` |
| `rag_agent.py` | RAG | Retrieval tool + `content_and_artifact` |

## Multi-agent

| File | Pattern | Notes |
|------|---------|-------|
| `supervisor_multi_agent.py` | Subagents (agent-as-tool) | Coordinator + `task` registry |
| `swarm_multi_agent.py` | Handoffs | `StateGraph` + `Command(graph=Command.PARENT)`, checkpointed |

## Deep Agents

| File | Pattern | Notes |
|------|---------|-------|
| `deepagent_release_notes.py` | `create_deep_agent` | Planning + custom tool + on-demand skill. Supports `--repo PATH` to read a real git log. |

The deep agent's on-demand skill lives in [`skills/release-notes/SKILL.md`](skills/release-notes/SKILL.md).

```bash
python deepagent_release_notes.py                              # bundled sample commits
python deepagent_release_notes.py --repo /path/to/repo --version 1.2.0
```

## Custom LangGraph reasoning patterns

| File | Pattern |
|------|---------|
| `langgraph_plan_and_execute.py` | Plan-and-Execute (planner → executor → replanner) |
| `langgraph_reflection.py` | Reflection (generate → reflect loop) |
| `langgraph_rewoo.py` | ReWOO (plan → batch tool exec → solve) |
| `langgraph_lats.py` | LATS (Monte Carlo Tree Search) |

## Sample outputs

Captured from live runs — see [`outputs/`](outputs/):

| Output | From |
|--------|------|
| [`outputs/deepagent_release_notes.md`](outputs/deepagent_release_notes.md) | `deepagent_release_notes.py` (both modes) |
