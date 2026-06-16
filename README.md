# LangChain Agent Patterns

> Runnable examples and reference docs for building agents with **LangChain** (`create_agent`), **LangGraph** (StateGraph / Functional API), and **Deep Agents** (`create_deep_agent`) — current API as of June 2026.

## Repository layout

```
.
├── README.md                 # this file
├── docs/                     # reference documentation (no code)
│   ├── langchain-agents.md
│   ├── langgraph-deep-agents.md
│   ├── patterns-and-use-cases.md
│   ├── quick-reference.md
│   ├── reference-card.md
│   └── skills-reference.md
└── examples/                 # runnable code
    ├── README.md             # examples index
    ├── outputs/              # captured sample outputs
    ├── skills/               # on-demand SKILL.md files used by the deep agent
    └── *.py                  # one file per pattern
```

Documentation lives in [`docs/`](docs/); runnable code lives in [`examples/`](examples/); captured sample outputs live in [`examples/outputs/`](examples/outputs/).

## Documentation

| File | Covers |
|------|--------|
| [`docs/quick-reference.md`](docs/quick-reference.md) | Cheat sheet — fastest way in |
| [`docs/langchain-agents.md`](docs/langchain-agents.md) | `create_agent`, tools, memory, streaming, middleware |
| [`docs/langgraph-deep-agents.md`](docs/langgraph-deep-agents.md) | StateGraph API, nodes/edges, Deep Agents |
| [`docs/patterns-and-use-cases.md`](docs/patterns-and-use-cases.md) | Pattern comparison & use cases |
| [`docs/skills-reference.md`](docs/skills-reference.md) | The `/`-command scaffolders behind these examples |
| [`docs/reference-card.md`](docs/reference-card.md) | One-page reference card |

## Examples

See [`examples/README.md`](examples/README.md) for the full index. Highlights:

| File | Pattern |
|------|---------|
| `examples/basic_agent.py` | Single agent (ReAct) with tools |
| `examples/agent_with_memory.py` | Agent + checkpointer memory |
| `examples/rag_agent.py` | Retrieval-augmented agent |
| `examples/supervisor_multi_agent.py` | Multi-agent — Subagents (agent-as-tool) |
| `examples/swarm_multi_agent.py` | Multi-agent — Handoffs (`Command.PARENT`) |
| `examples/deepagent_release_notes.py` | **Deep Agents** — planning + on-demand skill |
| `examples/langgraph_{plan_and_execute,reflection,rewoo,lats}.py` | Custom LangGraph reasoning patterns |

**Sample outputs** from real runs are in [`examples/outputs/`](examples/outputs/) — e.g. [`deepagent_release_notes.md`](examples/outputs/deepagent_release_notes.md).

## Quick start

```bash
pip install -U langchain "langchain[anthropic]" langgraph   # core
pip install -U deepagents                                   # for the Deep Agents example

export ANTHROPIC_API_KEY=...        # or OPENAI_API_KEY / GOOGLE_API_KEY, etc.
```

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results: {query}"

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    system_prompt="You are a helpful assistant.",
)
print(agent.invoke({"messages": [{"role": "user", "content": "Hello!"}]})["messages"][-1].content)
```

Run the Deep Agents sample against its bundled commits, or against any real repo:

```bash
cd examples
python deepagent_release_notes.py                              # bundled sample commits
python deepagent_release_notes.py --repo /path/to/repo --version 1.2.0
```

## Choosing an approach

```
Single agent, model + tools loop?            → create_agent          (basic_agent.py)
Batteries-included (plan/memory/subagents)?  → Deep Agents           (deepagent_release_notes.py)
Explicit control flow / deterministic stages?→ LangGraph             (langgraph_*.py)
Multiple specialized agents?
  ├── Centralized coordinator                → Subagents             (supervisor_multi_agent.py)
  ├── Peer control transfer                  → Handoffs              (swarm_multi_agent.py)
  ├── Classify then dispatch                 → Router
  └── Bespoke pipeline                        → Custom workflow
```

## Version compatibility

| Package | Version |
|---------|---------|
| langchain | 1.x |
| langgraph | 1.x |
| deepagents | 0.4.x (examples verified on 0.4.2) |

## License

Compiled from official LangChain sources for educational use.
