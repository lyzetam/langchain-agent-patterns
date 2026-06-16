# LangChain & LangGraph - Patterns & Use Cases

> Comprehensive guide to agent patterns, use cases, and when to use each approach.

---

## Table of Contents

1. [Pattern Comparison Matrix](#pattern-comparison-matrix)
2. [Single Agent Patterns](#single-agent-patterns)
3. [Multi-Agent Patterns](#multi-agent-patterns)
4. [Use Cases](#use-cases)
5. [Architecture Decision Guide](#architecture-decision-guide)
6. [Performance Comparison](#performance-comparison)

---

## Pattern Comparison Matrix

### Single Agent Patterns

| Pattern | Complexity | Latency | Token Usage | Best For |
|---------|------------|---------|-------------|----------|
| **ReAct** | Low | Medium | Medium | General tool use, Q&A |
| **Plan-and-Execute** | Medium | Higher | Lower (batching) | Multi-step tasks, complex workflows |
| **Reflection** | Medium | Higher | Higher | Writing, coding, creative tasks |
| **ReWOO** | Medium | Lower | Lower | Search-based tasks, information gathering |
| **LATS** | High | Higher | Higher | Reasoning problems, optimization |

### Multi-Agent Patterns

| Pattern | Coordination | Parallelism | Context Isolation | Best For |
|---------|--------------|-------------|-------------------|----------|
| **Supervisor** | Centralized | Yes (controlled) | Yes | Distributed teams, complex workflows |
| **Swarm** | Decentralized | No (sequential) | No | Conversational, stateful interactions |
| **Subagents** | Tool-based | Yes | Yes | Modular capabilities, distributed dev |
| **Router** | Classifier | Yes | Partial | Simple delegation, cost optimization |
| **Custom Workflow** | Programmatic | Configurable | Configurable | Specific business logic |

---

## Single Agent Patterns

### 1. ReAct (Reasoning + Acting)

**Concept**: Agent reasons about what to do, acts by calling tools, observes results, and repeats.

```
Thought → Action → Observation → Thought → Action → ... → Answer
```

**Use When**:
- General purpose tool use
- Unknown number of steps
- Flexible reasoning needed

**Example**: Chatbot that searches web, calculates, and responds

**Code**:
```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4o",
    tools=[search, calculate],
    system_prompt="You are a helpful assistant."
)
```

---

### 2. Plan-and-Execute

**Concept**: Generate complete plan first, then execute each step systematically.

```
Plan Step 1 → Plan Step 2 → Plan Step 3
     ↓              ↓              ↓
  Execute 1     Execute 2      Execute 3
     ↓              ↓              ↓
  Replan?       Replan?         Answer
```

**Use When**:
- Known multi-step tasks
- Can separate planning from execution
- Want to use cheaper models for execution

**Example**: Research task requiring multiple searches and synthesis

**Pros**:
- Better long-term planning
- Reduced redundant tool calls
- Can use different models for plan vs execute

**Cons**:
- Higher initial latency (planning)
- Plans may need revision during execution

---

### 3. Reflection

**Concept**: Generate → Critique → Revise → Repeat

```
Generate → Reflect → Revise → Reflect → Final Output
   ↑___________________|
```

**Use When**:
- Quality > speed
- Creative tasks (writing, coding)
- Self-improvement needed

**Example**: Essay writing, code generation with testing

**Pros**:
- Self-correcting
- Iterative improvement
- Can catch own errors

**Cons**:
- Multiple LLM calls
- May over-iterate

---

### 4. ReWOO (Reasoning Without Observation)

**Concept**: Plan with variable substitution, then execute all tools without intermediate LLM calls.

```
Plan: #E1 = Search[winner]
      #E2 = LLM[name from #E1]
      #E3 = Search[hometown of #E2]
Execute #E1 → Execute #E2 → Execute #E3 → Solve
```

**Use When**:
- Search-heavy tasks
- Want to minimize LLM calls
- Can predict needed tools upfront

**Pros**:
- Fewer LLM calls (no ReAct loop)
- Faster execution
- Easier to cache/fine-tune

**Cons**:
- Less flexible
- Can't adapt plan based on tool results

---

### 5. LATS (Language Agent Tree Search)

**Concept**: Monte Carlo Tree Search with reflection for decision making.

```
        Root
       / | \
    N1   N2   N3   ← Expand & Evaluate
   /|\  /|\  /|\
  N4-N9...         ← Select by UCB
     |
   Solution
```

**Use When**:
- Complex reasoning problems
- Multiple solution paths
- Need optimal decisions

**Example**: Math problems, strategy games, code optimization

**Pros**:
- Explores multiple paths
- Balances exploration/exploitation
- Can find better solutions

**Cons**:
- Computationally expensive
- Complex implementation
- Many LLM calls

---

## Multi-Agent Patterns

### 1. Supervisor Pattern

**Architecture**:
```
         User
          ↓
      Supervisor
       /   |   \
   Agent1 Agent2 Agent3
       \   |   /
      Supervisor
          ↓
        Response
```

**How It Works**:
- Central supervisor coordinates all agents
- Supervisor decides which agent to call
- Agents report back to supervisor
- Supervisor synthesizes final response

**Use When**:
- Different teams maintain different agents
- Need centralized control
- Want to parallelize where possible

**Example**: Travel booking with flight, hotel, and expense agents

**Pros**:
- Clear control flow
- Easy to add/remove agents
- Can parallelize

**Cons**:
- Single point of failure
- Context grows with each handoff
- Extra latency from routing

---

### 2. Swarm Pattern

**Architecture**:
```
Agent A ←→ Agent B ←→ Agent C
  ↑_____________________|
        (handoffs)
```

**How It Works**:
- Agents dynamically hand off to each other
- Each agent can transfer to any other
- System remembers last active agent
- No central coordinator

**Use When**:
- Conversational interfaces
- Need to maintain user context
- Agents should feel like one system

**Example**: Customer support with triage, billing, and technical agents

**Pros**:
- Direct user interaction with specialists
- Natural conversation flow
- Stateful within specialist

**Cons**:
- Sequential only (no parallelism)
- Growing context
- Can loop if not careful

---

### 3. Subagents as Tools

**Architecture**:
```
Main Agent (with tools)
    ├── Tool 1
    ├── Tool 2
    └── Subagent A (as tool)
         ├── Tool A1
         └── Tool A2
```

**How It Works**:
- Subagents are exposed as tools to main agent
- Main agent decides when to call subagent
- Subagents run in isolation
- Results return to main agent

**Use When**:
- Strong context isolation needed
- Distributed development
- Subagents are independent capabilities

**Pros**:
- Strong isolation
- Can parallelize
- Clean boundaries

**Cons**:
- Context not shared
- More LLM calls
- Extra overhead

---

### 4. Router Pattern

**Architecture**:
```
User → Router → Agent A
          ↓
       Agent B
          ↓
       Agent C
          ↓
       Synthesizer → Response
```

**How It Works**:
- Router classifies input
- Directs to appropriate agent(s)
- Can call multiple agents in parallel
- Synthesizer combines results

**Use When**:
- Simple classification works
- Want maximum parallelism
- Clear domain separation

**Pros**:
- Fast (parallel)
- Simple routing logic
- Efficient token usage

**Cons**:
- Router can be wrong
- No multi-hop reasoning
- Limited flexibility

---

## Use Cases

### Customer Support

**Pattern**: Swarm or Supervisor
**Agents**:
- Triage Agent
- Billing Agent
- Technical Support Agent
- Escalation Agent

**Flow**:
1. Triage classifies issue
2. Handoff to appropriate specialist
3. Specialist resolves or escalates
4. Follow-up if needed

---

### Code Generation

**Pattern**: Reflection or Plan-and-Execute
**Components**:
- Requirements Parser
- Code Generator
- Test Runner
- Fixer/Reflector

**Flow**:
1. Parse requirements
2. Generate code
3. Run tests
4. If fail: reflect and fix
5. Repeat until pass

---

### Research Assistant

**Pattern**: ReWOO or LATS
**Components**:
- Query Planner
- Search Executor
- Synthesizer
- Fact Checker

**Flow**:
1. Plan search queries
2. Execute searches (ReWOO style)
3. Evaluate quality (LATS style)
4. Synthesize findings
5. Verify accuracy

---

### Travel Booking

**Pattern**: Supervisor
**Agents**:
- Flight Agent
- Hotel Agent
- Car Rental Agent
- Expense Calculator

**Flow**:
1. Supervisor parses user request
2. Dispatches to relevant agents (can be parallel)
3. Collects results
4. Presents options
5. Handles booking confirmation

---

### Content Creation

**Pattern**: Reflection
**Components**:
- Outline Generator
- Content Writer
- Editor/Reviewer
- SEO Optimizer

**Flow**:
1. Generate outline
2. Write content
3. Review and critique
4. Revise
5. Optimize for SEO
6. Final review

---

### Data Analysis

**Pattern**: Plan-and-Execute
**Components**:
- Data Loader
- Analysis Planner
- Query Executor
- Visualization Generator
- Insight Extractor

**Flow**:
1. Load and validate data
2. Plan analysis steps
3. Execute queries
4. Generate visualizations
5. Extract insights
6. Compile report

---

## Architecture Decision Guide

### Decision Tree

```
Start
  │
  ├── Single task, simple tools? ──→ ReAct
  │
  ├── Multi-step, can plan ahead? ──→ Plan-and-Execute
  │
  ├── Quality critical, iterative? ──→ Reflection
  │
  ├── Search-heavy, minimize LLM calls? ──→ ReWOO
  │
  ├── Complex reasoning, explore options? ──→ LATS
  │
  ├── Multiple domains, need specialization? ──→ Multi-Agent
  │       │
  │       ├── Conversational, stateful? ──→ Swarm
  │       │
  │       ├── Need parallelism? ──→ Supervisor or Router
  │       │
  │       ├── Strong isolation needed? ──→ Subagents
  │       │
  │       └── Simple classification? ──→ Router
  │
  └── Custom flow, specific requirements? ──→ Custom LangGraph
```

### Questions to Ask

1. **How many steps?**
   - Variable → ReAct
   - Fixed → Plan-and-Execute

2. **Can steps be predicted?**
   - Yes → ReWOO
   - No → ReAct

3. **Quality vs Speed?**
   - Quality → Reflection, LATS
   - Speed → ReAct, Router

4. **How many domains?**
   - One → Single agent
   - Multiple → Multi-agent

5. **Need to parallelize?**
   - Yes → Supervisor, Subagents, Router
   - No → Swarm

6. **State important?**
   - Yes → Swarm, Supervisor
   - No → Router, Subagents

---

## Performance Comparison

### Single Agent: One-shot Task

| Pattern | Model Calls | Token Usage | Latency | Best |
|---------|-------------|-------------|---------|------|
| ReAct | 2-3 | ~2K | Medium | ✅ General |
| Plan-and-Execute | 2+ | ~1.5K | Higher | Multi-step |
| Reflection | 4+ | ~3K | Higher | Quality |
| ReWOO | 2 | ~1K | Lower | ✅ Search |
| LATS | 10+ | ~8K | Highest | Optimization |

### Multi-Agent: One-shot Task

| Pattern | Model Calls | Token Usage | Latency | Best |
|---------|-------------|-------------|---------|------|
| Supervisor | 4 | ~2K | Medium | ✅ Control |
| Swarm | 3 | ~1.8K | Medium | ✅ Conversational |
| Subagents | 5 | ~2.5K | Higher | Isolation |
| Router | 3 | ~1.5K | Lower | ✅ Speed |

### Multi-Agent: Repeat Request

| Pattern | Calls (Turn 1) | Calls (Turn 2) | Total | Best |
|---------|----------------|----------------|-------|------|
| Supervisor | 4 | 4 | 8 | - |
| Swarm | 3 | 2 | 5 | ✅ Stateful |
| Subagents | 5 | 5 | 10 | - |
| Router | 3 | 3 | 6 | - |

### Multi-Agent: Multi-Domain (Parallel)

| Pattern | Model Calls | Token Usage | Best |
|---------|-------------|-------------|------|
| Supervisor | 5 | ~9K | ✅ Parallel |
| Swarm | 7+ | ~14K | - |
| Subagents | 5 | ~9K | ✅ Isolation |
| Router | 5 | ~9K | ✅ Simple |

---

## Summary

### Quick Reference

| If you need... | Use... |
|----------------|--------|
| Simple Q&A with tools | ReAct |
| Complex multi-step tasks | Plan-and-Execute |
| High-quality outputs | Reflection |
| Fast search tasks | ReWOO |
| Optimal decision making | LATS |
| Conversational multi-agent | Swarm |
| Controlled parallel agents | Supervisor |
| Maximum parallelism | Router |
| Strong isolation | Subagents |

### Recommendations by Experience

**Beginners**:
- Start with `create_agent` (ReAct)
- Use prebuilt multi-agent (Supervisor, Swarm)

**Intermediate**:
- Build custom LangGraph for specific flows
- Implement Plan-and-Execute or Reflection

**Advanced**:
- Implement LATS for optimization problems
- Design custom multi-agent architectures
- Combine patterns (e.g., Reflection + Multi-Agent)

---

*This guide helps you choose the right agent pattern for your use case.*
