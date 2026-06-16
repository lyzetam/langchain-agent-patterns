# LangChain Agents - Complete Documentation

> **Comprehensive documentation and examples for building production-grade AI agents with LangChain, LangGraph, LangSmith, and Deep Agents.**

---

## 📚 Documentation Files

### Core Documentation

| File | Description | Size |
|------|-------------|------|
| `langchain-agents-documentation.md` | Complete LangChain agent guide | 22KB |
| `langchain-quick-reference.md` | Quick reference cheat sheet | 6KB |
| `langgraph-deep-agents-documentation.md` | LangGraph & Deep Agents | 24KB |
| `langchain-patterns-use-cases.md` | Patterns comparison & use cases | 13KB |

### Total Documentation: ~65KB of comprehensive guides

---

## 🎯 What's Covered

### LangChain Agents
- ✅ Basic agent creation with `create_agent`
- ✅ Tool definition and management
- ✅ Memory & persistence (short-term & long-term)
- ✅ Streaming & real-time updates
- ✅ Human-in-the-loop patterns
- ✅ Middleware system

### LangGraph
- ✅ StateGraph API
- ✅ Nodes & Edges
- ✅ Conditional routing
- ✅ Map-Reduce with Send
- ✅ Command for dynamic control
- ✅ Subgraphs & parent navigation

### Deep Agents & Advanced Patterns
- ✅ ReAct (Reasoning + Acting)
- ✅ Plan-and-Execute
- ✅ Reflection & Self-Improvement
- ✅ ReWOO (Reasoning Without Observation)
- ✅ LATS (Language Agent Tree Search)

### Multi-Agent Systems
- ✅ Supervisor Pattern
- ✅ Swarm Pattern
- ✅ Subagents as Tools
- ✅ Router Pattern
- ✅ Custom Workflows

### LangSmith
- ✅ Automatic tracing
- ✅ Manual instrumentation
- ✅ Evaluation (offline & online)
- ✅ Datasets & experiments
- ✅ Human annotation queues

---

## 💻 Example Files

### Basic Examples
| File | Pattern | Description |
|------|---------|-------------|
| `examples/basic_agent.py` | ReAct | Simple agent with tools |
| `examples/agent_with_memory.py` | ReAct + Memory | Conversational agent with checkpoints |
| `examples/streaming_agent.py` | ReAct + Streaming | Real-time progress updates |
| `examples/rag_agent.py` | RAG + Agent | Retrieval-augmented generation |

### Advanced Examples
| File | Pattern | Description |
|------|---------|-------------|
| `examples/langgraph_plan_and_execute.py` | Plan-and-Execute | Multi-step planning agent |
| `examples/langgraph_reflection.py` | Reflection | Self-improving essay writer |
| `examples/langgraph_rewoo.py` | ReWOO | Efficient search agent |
| `examples/langgraph_lats.py` | LATS | Tree search reasoning |

### Multi-Agent Examples
| File | Pattern | Description |
|------|---------|-------------|
| `examples/supervisor_multi_agent.py` | Supervisor | Travel booking system |
| `examples/swarm_multi_agent.py` | Swarm | Code review specialists |

### Total Examples: 10 production-ready implementations

---

## 🏗️ Architecture Decision Guide

### When to Use Each Pattern

```
┌────────────────────────────────────────────────────────────────┐
│                    AGENT PATTERN SELECTION                      │
└────────────────────────────────────────────────────────────────┘

Single Task?
├── Yes
│   ├── Variable steps? ───────────→ ReAct
│   ├── Can plan ahead? ───────────→ Plan-and-Execute
│   ├── Quality critical? ─────────→ Reflection
│   ├── Search-heavy? ─────────────→ ReWOO
│   └── Optimize decisions? ───────→ LATS
│
└── Multiple Domains?
    ├── Conversational? ───────────→ Swarm
    ├── Need parallelism? ─────────→ Supervisor
    ├── Strong isolation? ─────────→ Subagents
    └── Simple routing? ───────────→ Router
```

### Performance Quick Reference

| Pattern | Latency | Tokens | Parallel | Best For |
|---------|---------|--------|----------|----------|
| ReAct | Medium | Medium | No | General use |
| Plan-and-Execute | Higher | Lower | No | Multi-step |
| Reflection | Higher | Higher | No | Quality |
| ReWOO | Lower | Lower | No | Search |
| LATS | Highest | Highest | Yes | Optimization |
| Supervisor | Medium | Medium | Yes | Control |
| Swarm | Medium | Medium | No | Conversations |
| Subagents | Higher | Medium | Yes | Isolation |
| Router | Low | Low | Yes | Speed |

---

## 📖 Key Concepts

### State Management

```python
# Short-term memory (per conversation)
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

# Long-term memory (across conversations)
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()

# Compile with both
graph.compile(checkpointer=checkpointer, store=store)
```

### Streaming

```python
# Stream agent progress
for chunk in agent.stream(input, stream_mode="updates"):
    print(chunk)

# Stream LLM tokens
for token, metadata in agent.stream(input, stream_mode="messages"):
    print(token.content, end="")

# Multiple modes
for mode, chunk in agent.stream(input, stream_mode=["updates", "custom"]):
    print(f"{mode}: {chunk}")
```

### Multi-Agent Handoffs

```python
from langgraph.types import Command

def agent_a(state) -> Command[Literal["agent_b"]]:
    return Command(
        update={"messages": [response]},
        goto="agent_b",
        graph=Command.PARENT
    )
```

---

## 🚀 Getting Started

### Installation

```bash
# Basic installation
pip install -U langchain "langchain[openai]"

# For LangGraph
pip install -U langgraph

# For multi-agent systems
pip install langgraph-supervisor langgraph-swarm

# For persistence
pip install langgraph-checkpoint-sqlite  # or postgres
```

### Environment Setup

```bash
# Required for any provider
export OPENAI_API_KEY="..."
# or
export ANTHROPIC_API_KEY="..."

# For LangSmith tracing
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="..."
export LANGSMITH_PROJECT="my-project"
```

### Quick Start

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results: {query}"

agent = create_agent(
    model="gpt-4o",
    tools=[search],
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello!"}]
})
```

---

## 📊 Use Cases Covered

### Customer Support
- Triage → Specialist → Resolution
- Human escalation
- Conversation memory

### Code Generation
- Requirements → Code → Test → Fix
- Iterative improvement
- Multi-language support

### Research Assistant
- Query planning
- Information gathering
- Synthesis & verification

### Travel Booking
- Flight search
- Hotel booking
- Expense calculation
- Parallel execution

### Content Creation
- Outline generation
- Content writing
- Review & editing
- SEO optimization

---

## 🔗 Resources

### Official Documentation
- **LangChain**: https://python.langchain.com
- **LangGraph**: https://langchain-ai.github.io/langgraph
- **LangSmith**: https://docs.langchain.com/langsmith

### GitHub Repositories
- **LangChain**: https://github.com/langchain-ai/langchain
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **LangGraph Supervisor**: https://github.com/langchain-ai/langgraph-supervisor-py
- **LangGraph Swarm**: https://github.com/langchain-ai/langgraph-swarm-py

### Papers & Research
- **ReAct**: Reasoning + Acting (Yao et al., 2022)
- **Plan-and-Solve**: Multi-step planning
- **Reflexion**: Self-reflective agents (Shinn et al., 2023)
- **ReWOO**: Reasoning Without Observation (Xu et al., 2023)
- **LATS**: Language Agent Tree Search (Zhou et al., 2023)

---

## 📁 Repository Structure

```
agents/
├── README.md                                    # This file
├── langchain-agents-documentation.md           # Complete LangChain guide
├── langchain-quick-reference.md                # Quick cheat sheet
├── langgraph-deep-agents-documentation.md      # LangGraph & Deep Agents
├── langchain-patterns-use-cases.md             # Patterns comparison
└── examples/
    ├── basic_agent.py                          # Basic ReAct agent
    ├── agent_with_memory.py                    # Memory & persistence
    ├── streaming_agent.py                      # Real-time streaming
    ├── rag_agent.py                            # RAG implementation
    ├── supervisor_multi_agent.py               # Supervisor pattern
    ├── swarm_multi_agent.py                    # Swarm pattern
    ├── langgraph_plan_and_execute.py           # Plan-and-Execute
    ├── langgraph_reflection.py                 # Reflection pattern
    ├── langgraph_rewoo.py                      # ReWOO pattern
    └── langgraph_lats.py                       # LATS pattern
```

---

## 🎓 Learning Path

### Beginner
1. Read `langchain-quick-reference.md`
2. Run `examples/basic_agent.py`
3. Try `examples/agent_with_memory.py`
4. Add your own tools

### Intermediate
1. Read `langchain-agents-documentation.md`
2. Implement `examples/rag_agent.py`
3. Study `langgraph-deep-agents-documentation.md`
4. Build `langgraph_plan_and_execute.py`

### Advanced
1. Read `langchain-patterns-use-cases.md`
2. Implement multi-agent systems
3. Study `langgraph_lats.py`
4. Design custom architectures

---

## 🛠️ Best Practices

### Tool Design
- Clear, specific descriptions
- Include examples in docstrings
- Use `response_format="content_and_artifact"` for complex outputs

### State Management
- Use `add_messages` reducer for conversation history
- Keep state minimal
- Use private state channels for internal data

### Multi-Agent
- Start simple (single agent)
- Split when complexity grows
- Choose pattern based on coordination needs

### Production
- Always use checkpointers
- Enable LangSmith tracing
- Set recursion limits
- Handle errors gracefully

---

## 📈 Version Compatibility

| Package | Version | Notes |
|---------|---------|-------|
| LangChain | 1.0+ | Major release with simplified API |
| LangGraph | 1.0+ | Stable for production |
| LangSmith | Latest | Cloud & self-hosted options |

---

## 🤝 Contributing

This is a documentation collection. To update:
1. Edit relevant `.md` files
2. Test example code
3. Update this README

---

## 📝 License

Documentation compiled from official LangChain sources for educational purposes.

---

**Last Updated**: 2026-02-24  
**Total Documentation**: ~65KB across 4 comprehensive guides  
**Total Examples**: 10 production-ready implementations  

*Build better agents with LangChain! 🚀*
