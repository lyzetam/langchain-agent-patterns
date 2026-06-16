# Agent Skills Reference

Six Claude Code slash commands for building LangChain/LangGraph agents. All saved globally at `~/.claude/commands/`.

---

## `/agent-pattern` — Pattern Selection Advisor

**Advisory only — no code output.**

Interactive decision tool that recommends the best agent pattern for a use case. Asks clarifying questions (task type, step count, quality vs speed, tool needs, single vs multi-domain), then applies a decision tree across all 9 patterns. Presents a recommendation with performance profile (complexity, latency, token usage, parallelism), trade-offs vs alternatives, and when to reconsider. Points to other skills for implementation.

**Patterns covered:** ReAct, Plan-and-Execute, Reflection, ReWOO, LATS, Supervisor, Swarm, Subagents, Router.

---

## `/langchain-agent` — Single Agent Scaffolder

Generates a complete, runnable LangChain agent from a natural language description using `create_agent`. Analyzes requirements (tools, memory, streaming, model, middleware), then outputs a single Python file with tools, agent creation, and main loop.

**Handles:** tool design with docstrings, short-term/long-term memory (InMemorySaver/InMemoryStore), streaming (updates and token-by-token), middleware (dynamic prompts, model selection, error handling, HITL), and install dependencies.

**Example input:** "A research agent that searches the web and summarizes findings, using Claude"

---

## `/langgraph-workflow` — Custom StateGraph Builder

Generates a LangGraph `StateGraph` implementation from a workflow description. Analyzes data flow, node responsibilities, edge types (fixed, conditional, Send for parallelism), cycles, and subgraphs. Outputs a structured Python file with TypedDict state, node functions, routing logic, and graph compilation.

**Key patterns:** state reducers (`Annotated[list, operator.add]`), conditional edges, `Command` for route+update, `Send` for map-reduce parallelism, node caching, and checkpointing.

**Example input:** "A document processing pipeline: extract text, classify, route to summarizer or translator"

---

## `/multi-agent` — Multi-Agent System Designer

Recommends a multi-agent pattern and generates the full implementation. Evaluates the problem against four patterns using a decision matrix (user-facing? parallel? isolated? simple routing?), presents the recommendation with trade-offs, then scaffolds the system after user confirmation.

| Pattern | Package | Best For |
|---------|---------|----------|
| Supervisor | `langgraph-supervisor` | Centralized control, parallel execution |
| Swarm | `langgraph-swarm` | Conversational, stateful handoffs |
| Subagents | Manual (agent-as-tool) | Strong isolation, modular capabilities |
| Router | Custom LangGraph | Simple classification, max parallelism |

**Example input:** "A customer support system with triage, billing, and technical agents"

---

## `/deep-agent` — Advanced Pattern Scaffolder

Scaffolds complex LangGraph agent patterns that are hard to build from scratch. Each generates 200-350 lines of production-ready code with full state management, graph topology, and termination logic.

| Pattern | Structure | Key Advantage |
|---------|-----------|---------------|
| **Plan-and-Execute** | planner → executor → replanner (loop) | Separates planning from execution |
| **Reflection** | generate → reflect (loop, max N iterations) | Iterative quality improvement |
| **ReWOO** | planner → worker (batch) → solver | Only 2 LLM calls, rest are tool executions |
| **LATS** | Monte Carlo Tree Search with UCB selection | Explores multiple solution paths, backpropagation |

**Example input:** "LATS agent for solving coding challenges"

---

## `/agent-review` — Implementation Reviewer

Audits an existing LangChain/LangGraph agent against an 8-category checklist. Reads the code, identifies the pattern and framework, then scores each category as PASS/WARN/FAIL with specific issues, line numbers, and concrete fixes.

**Review categories:**
1. **Pattern Fit** — right pattern for the use case, over/under-engineering check
2. **State Design** — TypedDict usage, reducers, minimal fields
3. **Tool Design** — docstrings, typed params, error handling
4. **Memory Strategy** — checkpointer choice, thread IDs, production readiness
5. **Edge Logic** — valid routing, termination conditions, bounded cycles
6. **Multi-Agent** — agent names, supervisor prompts, handoff descriptions
7. **Streaming & Production** — streaming support, error handling, recursion limits, tracing
8. **Token Efficiency** — model selection per step, prompt conciseness, pattern cost

Offers to apply fixes directly or scaffold a replacement using the other skills.
