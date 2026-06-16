# Agent Skills Reference

Six Claude Code slash commands for building LangChain / LangGraph / Deep Agents. All saved globally at `~/.claude/commands/`. Updated to the current LangChain API (`create_agent`, `create_deep_agent`, `provider:model` strings).

---

## `/agent-pattern` — Pattern Selection Advisor

**Advisory only — no code output.**

Interactive decision tool that recommends the right approach for a use case. Asks clarifying questions (task type, step count, quality vs speed, tool needs, single vs multi-domain, state/memory), then applies a decision tree. First picks the **layer**, then (if multi-agent) the **pattern**. Presents a recommendation with a qualitative profile (complexity, relative latency/cost, parallelism), trade-offs, and when to reconsider. Points to the matching scaffolder.

**Layers:** `create_agent` (single agent) · Deep Agents (`create_deep_agent`) · LangGraph (Graph/Functional API).
**Multi-agent patterns:** Subagents · Handoffs · Skills · Router · Custom workflow.

---

## `/langchain-agent` — Single Agent Scaffolder

Generates a complete, runnable agent from a natural-language description using `create_agent`. Analyzes requirements (tools, memory, streaming, model, middleware), then outputs a single Python file with tools, agent creation, and a main loop.

**Handles:** tool design with docstrings, short-term/long-term memory (InMemorySaver / InMemoryStore), streaming (updates + token-by-token), middleware (`@wrap_model_call`, `@dynamic_prompt`, `@wrap_tool_call`, HumanInTheLoopMiddleware), and install deps. Default model `anthropic:claude-sonnet-4-6`.

**Example input:** "A research agent that searches the web and summarizes findings, using Claude"

---

## `/langgraph-workflow` — Custom StateGraph / Functional Builder

Generates a LangGraph implementation from a workflow description. Analyzes data flow, node responsibilities, edge types, cycles, and subgraphs. Outputs a structured Python file with TypedDict state, node functions, routing, and graph compilation.

**Key patterns:** state reducers (`Annotated[list, operator.add]`), conditional edges, `Command` for route+update, `Send` for map-reduce, node caching, checkpointing. Covers both the **Graph API** (`StateGraph`) and the **Functional API** (`@entrypoint` / `@task`), and when to choose each.

**Example input:** "A document processing pipeline: extract text, classify, route to summarizer or translator"

---

## `/multi-agent` — Multi-Agent System Designer

Recommends a multi-agent pattern and generates the full implementation using `create_agent` + `Command` (no `langgraph-supervisor` / `langgraph-swarm` — those are superseded). Presents the recommendation with trade-offs, then scaffolds after confirmation.

| Pattern | Mechanism | Best For |
|---------|-----------|----------|
| **Subagents** | Specialists wrapped as tools / a `task` registry | Centralized control, parallel, isolation |
| **Handoffs** | `Command(goto=…, graph=Command.PARENT)` + `active_agent` state | Peer control transfer across a conversation |
| **Skills** | One agent loads expertise on demand | Swap knowledge per task without spawning agents |
| **Router** | Classify → `Send`/`Command` dispatch → synthesize | Distinct verticals, parallel multi-source |
| **Custom workflow** | Bespoke `StateGraph` of agent + deterministic nodes | Multi-stage pipelines (e.g. RAG) |

**Example input:** "A customer support system with triage, billing, and technical agents"

---

## `/deep-agent` — Deep Agents Scaffolder

Scaffolds an agent on LangChain's official **Deep Agents** framework (`deepagents` package / `create_deep_agent`) — batteries included: planning, virtual filesystem for context management, subagents, and long-term memory out of the box.

**Wires up only what's needed:** custom tools + MCP, subagents (dict or `CompiledSubAgent`), backends (State / Filesystem / LocalShell / Store / Composite + sandboxes), human-in-the-loop (`interrupt_on` + checkpointer), long-term memory (namespaced `StoreBackend`), skills (on-demand `SKILL.md`), structured output, streaming, custom middleware. Default model `anthropic:claude-sonnet-4-6`.

**Example input:** "A research deep agent that plans, delegates to a search subagent, and writes a report"
**Runnable example:** `examples/deepagent_release_notes.py` (planning + on-demand skill).

---

## `/agent-review` — Implementation Reviewer

Audits an existing LangChain / LangGraph / Deep Agents implementation against an 8-category checklist. Reads the code, identifies the pattern and framework, then scores each category PASS/WARN/FAIL with specific issues, line numbers, and concrete fixes.

**Review categories:**
1. **Pattern Fit** — right layer/pattern, over/under-engineering check
2. **State Design** — TypedDict/AgentState usage, reducers, minimal fields
3. **Tool Design** — docstrings, typed params, error handling
4. **Memory Strategy** — checkpointer/store choice, thread IDs, production readiness
5. **Edge Logic** — valid routing, termination, bounded cycles
6. **Multi-Agent** — agent names, handoff/subagent descriptions, `Command.PARENT` usage
7. **Streaming & Production** — streaming support, error handling, recursion limits, tracing
8. **Token Efficiency** — model selection per step, prompt conciseness, pattern cost

Offers to apply fixes directly or scaffold a replacement using the other skills.
