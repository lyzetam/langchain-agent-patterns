 n# LangGraph & Deep Agents - Complete Documentation

> **Version**: LangGraph 1.0+ | LangChain 1.0+  
> **Last Updated**: 2026-02-24

---

## Table of Contents

1. [LangGraph Overview](#langgraph-overview)
2. [Core Concepts](#core-concepts)
3. [StateGraph API](#stategraph-api)
4. [Nodes](#nodes)
5. [Edges](#edges)
6. [Advanced Patterns](#advanced-patterns)
7. [Deep Agents](#deep-agents)
8. [LangSmith Integration](#langsmith-integration)
9. [Common Patterns & Use Cases](#common-patterns--use-cases)
10. [Deployment](#deployment)

---

## LangGraph Overview

LangGraph is a **low-level orchestration framework** for building, managing, and deploying long-running, stateful agents. It is trusted by companies like Klarna, Replit, and Elastic.

### LangGraph vs LangChain

| Aspect | LangChain | LangGraph |
|--------|-----------|-----------|
| Level | High-level | Low-level |
| Focus | Pre-built agent architectures | Agent orchestration primitives |
| Control | Less control, faster setup | Full control, more customization |
| Use Case | Quick agent building | Complex, production-grade agents |

### Core Benefits

1. **Durable Execution**: Agents persist through failures, resuming from checkpoints
2. **Human-in-the-Loop**: Inspect and modify agent state at any point
3. **Comprehensive Memory**: Short-term working memory + long-term cross-session memory
4. **Debugging**: Deep visibility with LangSmith tracing
5. **Production-Ready**: Scalable infrastructure for stateful, long-running workflows

### When to Use LangGraph

Use LangGraph when you need:
- Cyclical workflows (not just DAGs)
- Fine-grained control over agent behavior
- Complex state management
- Multi-agent orchestration
- Long-running, durable execution

---

## Core Concepts

### Graph Structure

LangGraph models workflows as graphs with three key components:

```
┌─────────────────────────────────────────────────────────────┐
│                        State                                 │
│  (Shared data structure - current snapshot of application)   │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │ updates
        ┌───────────┐    ┌────┴────┐    ┌───────────┐
        │  Node A   │───→│  Node B │───→│  Node C   │
        │ (does work)    │(does work)    │(does work)│
        └───────────┘    └────┬────┘    └───────────┘
                              │
                              ↓
                        ┌───────────┐
                        │   Edges   │
                        │(determine  │
                        │ what next) │
                        └───────────┘
```

### Execution Model: Pregel Super-Steps

LangGraph uses a message-passing algorithm inspired by Google's Pregel:

1. **Super-steps**: Discrete iterations over graph nodes
2. **Parallel execution**: Nodes in same super-step run concurrently
3. **Sequential execution**: Nodes in different super-steps run sequentially
4. **Activation**: Nodes become `active` when receiving messages
5. **Halting**: Nodes vote to `halt` when no more messages

```
Super-step 1:        Super-step 2:        Super-step 3:
┌─────────┐          ┌─────────┐          ┌─────────┐
│ Node A  │─────────→│ Node B  │─────────→│  Node D │
│ (active)│          │(active) │          │(active) │
└─────────┘          └────┬────┘          └─────────┘
                          │
                          ↓
                     ┌─────────┐
                     │ Node C  │
                     │(active) │
                     └─────────┘
```

---

## StateGraph API

### Basic Graph Definition

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from typing_extensions import TypedDict

# Define state
class State(TypedDict):
    input: str
    output: str
    steps: list[str]

# Create graph
builder = StateGraph(State)

# Add nodes
def process_node(state: State):
    return {
        "output": f"Processed: {state['input']}",
        "steps": ["process"]
    }

def finalize_node(state: State):
    return {
        "output": f"Final: {state['output']}",
        "steps": state["steps"] + ["finalize"]
    }

builder.add_node("process", process_node)
builder.add_node("finalize", finalize_node)

# Add edges
builder.add_edge(START, "process")
builder.add_edge("process", "finalize")
builder.add_edge("finalize", END)

# Compile
graph = builder.compile()

# Run
result = graph.invoke({"input": "hello", "output": "", "steps": []})
```

### Multiple Schemas

For complex workflows with different input/output schemas:

```python
from langgraph.graph import StateGraph

class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    graph_output: str

class OverallState(TypedDict):
    foo: str
    user_input: str
    graph_output: str

class PrivateState(TypedDict):
    bar: str

def node_1(state: InputState) -> OverallState:
    return {"foo": state["user_input"] + " name"}

def node_2(state: OverallState) -> PrivateState:
    return {"bar": state["foo"] + " is"}

def node_3(state: PrivateState) -> OutputState:
    return {"graph_output": state["bar"] + " Lance"}

builder = StateGraph(
    OverallState,
    input_schema=InputState,
    output_schema=OutputState
)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

result = graph.invoke({"user_input": "My"})
# {'graph_output': 'My name is Lance'}
```

### Reducers

Reducers specify how state updates are applied:

```python
from typing import Annotated
from operator import add

# Default: overwrite
class State(TypedDict):
    foo: int           # Overwrites completely
    bar: list[str]     # Overwrites completely

# With reducer: append
class State(TypedDict):
    foo: int
    bar: Annotated[list[str], add]  # Appends to list

# Messages reducer (tracks IDs, handles updates)
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

**Reducer Behavior:**

| Input State | Node Returns | Result (default) | Result (with add) |
|-------------|--------------|------------------|-------------------|
| `{"foo": 1, "bar": ["hi"]}` | `{"foo": 2}` | `{"foo": 2, "bar": ["hi"]}` | Same |
| `{"foo": 2, "bar": ["hi"]}` | `{"bar": ["bye"]}` | `{"foo": 2, "bar": ["bye"]}` | `{"foo": 2, "bar": ["hi", "bye"]}` |

---

## Nodes

### Node Types

```python
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

# Simple node
 def simple_node(state: State):
    return {"output": "result"}

# Node with config
 def node_with_config(state: State, config: RunnableConfig):
    thread_id = config["configurable"]["thread_id"]
    return {"output": f"Thread: {thread_id}"}

# Node with runtime
@dataclass
class Context:
    user_id: str

def node_with_runtime(state: State, runtime: Runtime[Context]):
    user_id = runtime.context.user_id
    return {"output": f"User: {user_id}"}

builder.add_node("simple", simple_node)
builder.add_node("with_config", node_with_config)
builder.add_node("with_runtime", node_with_runtime)
```

### Node Caching

```python
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

builder.add_node(
    "expensive_node",
    expensive_node,
    cache_policy=CachePolicy(ttl=300)  # 5 minute cache
)

graph = builder.compile(cache=InMemoryCache())

# First call: executes
result1 = graph.invoke({"x": 5})
# Second call (within 5 min): cached
result2 = graph.invoke({"x": 5})
```

---

## Edges

### Normal Edges

```python
from langgraph.graph import START, END

# Fixed transitions
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
```

### Conditional Edges

```python
from typing import Literal

def routing_function(state: State) -> Literal["node_b", "node_c"]:
    if state["condition"]:
        return "node_b"
    return "node_c"

builder.add_conditional_edges(
    "node_a",
    routing_function,
    {"node_b": "node_b", "node_c": "node_c"}
)
```

### Map-Reduce with Send

```python
from langgraph.types import Send

def continue_to_jokes(state: OverallState):
    # Dynamically send to multiple nodes
    return [
        Send("generate_joke", {"subject": s})
        for s in state['subjects']
    ]

builder.add_conditional_edges("node_a", continue_to_jokes)
```

### Command for Dynamic Control Flow

```python
from langgraph.types import Command
from typing import Literal

def my_node(state: State) -> Command[Literal["my_other_node"]]:
    # Update state AND route in one node
    return Command(
        update={"foo": "bar"},
        goto="my_other_node"
    )

# Navigate to parent graph node
def handoff_node(state: State) -> Command[Literal["other_subgraph"]]:
    return Command(
        update={"foo": "bar"},
        goto="other_subgraph",
        graph=Command.PARENT
    )
```

**Command vs Conditional Edges:**

| Use Case | Use |
|----------|-----|
| Route only (no state update) | Conditional edges |
| State update + routing | Command |
| Multi-agent handoffs | Command with `graph=Command.PARENT` |

---

## Advanced Patterns

### 1. ReAct Agent (from scratch)

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.tools import tool
from langchain_openai import ChatOpenAI

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

tools = [search]
model = ChatOpenAI(model="gpt-4o").bind_tools(tools)

def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()
```

### 2. Plan-and-Execute

```python
from langgraph.graph import StateGraph

class PlanExecute(TypedDict):
    input: str
    plan: list[str]
    past_steps: Annotated[list[tuple], operator.add]
    response: str

def planner(state: PlanExecute):
    """Generate multi-step plan."""
    plan = llm.invoke(
        f"Create plan for: {state['input']}"
    )
    return {"plan": plan.content.split("\n")}

def executor(state: PlanExecute):
    """Execute one step of the plan."""
    task = state["plan"][0]
    result = execute_task(task)
    return {
        "past_steps": [(task, result)],
        "plan": state["plan"][1:]  # Remove completed step
    }

def replanner(state: PlanExecute):
    """Replan based on results."""
    if not state["plan"]:
        # Generate final response
        response = llm.invoke(
            f"Summarize: {state['past_steps']}"
        )
        return {"response": response.content}
    # Otherwise, continue with plan
    return {"plan": state["plan"]}

def should_end(state: PlanExecute) -> Literal["executor", END]:
    if state["response"]:
        return END
    return "executor"

builder = StateGraph(PlanExecute)
builder.add_node("planner", planner)
builder.add_node("executor", executor)
builder.add_node("replan", replanner)

builder.add_edge(START, "planner")
builder.add_edge("planner", "executor")
builder.add_edge("executor", "replan")
builder.add_conditional_edges("replan", should_end)

graph = builder.compile()
```

### 3. Reflection Pattern

```python
class ReflectionState(TypedDict):
    messages: Annotated[list, add_messages]
    iterations: int
    max_iterations: int

def generate(state: ReflectionState):
    """Generate initial response."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an essay assistant."),
        MessagesPlaceholder("messages")
    ])
    response = (prompt | llm).invoke({"messages": state["messages"]})
    return {"messages": [response]}

def reflect(state: ReflectionState):
    """Reflect on and critique the response."""
    reflection_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a teacher grading an essay."),
        MessagesPlaceholder("messages"),
        ("user", "Provide critique and recommendations.")
    ])
    critique = (reflection_prompt | llm).invoke({"messages": state["messages"]})
    return {
        "messages": [critique],
        "iterations": state["iterations"] + 1
    }

def should_continue(state: ReflectionState) -> Literal["generate", END]:
    if state["iterations"] >= state["max_iterations"]:
        return END
    return "generate"

builder = StateGraph(ReflectionState)
builder.add_node("generate", generate)
builder.add_node("reflect", reflect)

builder.add_edge(START, "generate")
builder.add_edge("generate", "reflect")
builder.add_conditional_edges("reflect", should_continue)

graph = builder.compile()
```

### 4. Multi-Agent with Handoffs

```python
from langgraph.types import Command
from typing import Literal

class State(MessagesState):
    active_agent: str

def agent_a(state: State) -> Command[Literal["agent_b", END]]:
    # Do work...
    if should_handoff:
        return Command(
            update={
                "messages": [AIMessage(content="Handing off...")],
                "active_agent": "agent_b"
            },
            goto="agent_b",
            graph=Command.PARENT
        )
    return Command(update={"messages": [response]}, goto=END)

def agent_b(state: State) -> Command[Literal["agent_a", END]]:
    # Do work...
    if should_handoff_back:
        return Command(
            update={"active_agent": "agent_a"},
            goto="agent_a",
            graph=Command.PARENT
        )
    return Command(goto=END)

# Parent graph
builder = StateGraph(State)
builder.add_node("agent_a", agent_a)
builder.add_node("agent_b", agent_b)
builder.add_edge(START, "agent_a")

graph = builder.compile()
```

### 5. LATS (Language Agent Tree Search)

```python
class Reflection(BaseModel):
    reflections: str
    score: int = Field(ge=0, le=10)
    found_solution: bool

class Node:
    def __init__(self, messages, reflection, parent=None):
        self.messages = messages
        self.parent = parent
        self.children = []
        self.value = 0
        self.visits = 0
        self.reflection = reflection
        self.depth = parent.depth + 1 if parent else 1
        
    def upper_confidence_bound(self, exploration_weight=1.0):
        """UCT score for balancing exploration/exploitation."""
        if self.visits == 0:
            return self.value
        average_reward = self.value / self.visits
        exploration_term = math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return average_reward + exploration_weight * exploration_term
    
    def backpropagate(self, reward: float):
        """Update scores up the tree."""
        node = self
        while node:
            node.visits += 1
            node.value = (node.value * (node.visits - 1) + reward) / node.visits
            node = node.parent

class TreeState(TypedDict):
    root: Node
    input: str

def select(state: TreeState) -> Node:
    """Select node with highest UCB."""
    root = state["root"]
    if not root.children:
        return root
    return max(root.children, key=lambda n: n.upper_confidence_bound())

def expand(state: TreeState):
    """Generate candidate actions."""
    node = select(state)
    # Generate 5 candidate next steps
    candidates = generate_candidates(node)
    for candidate in candidates:
        child = Node(
            messages=node.messages + [candidate],
            reflection=evaluate(candidate),
            parent=node
        )
        node.children.append(child)
    return {"root": state["root"]}

def evaluate(response) -> Reflection:
    """Score the action."""
    evaluation_prompt = "Score this response 0-10..."
    return llm.with_structured_output(Reflection).invoke(evaluation_prompt)

# Build tree search graph
builder = StateGraph(TreeState)
builder.add_node("expand", expand)
builder.add_node("evaluate", evaluate_and_backprop)
builder.add_conditional_edges("expand", should_continue)
```

---

## Deep Agents

### Overview

Deep Agents refers to advanced agent architectures that go beyond simple ReAct loops:

1. **Plan-and-Solve**: Multi-step planning before execution
2. **Reflection**: Self-evaluation and improvement loops
3. **Tree Search**: LATS, Monte Carlo Tree Search
4. **Multi-Agent**: Specialized agents with handoffs

### Architecture Comparison

| Architecture | Strengths | Best For |
|--------------|-----------|----------|
| ReAct | Simple, flexible | General tasks, tool use |
| Plan-and-Solve | Better long-term planning | Complex multi-step tasks |
| Reflection | Self-improvement | Writing, coding, creative tasks |
| LATS | Optimal decision making | Search, reasoning problems |
| Multi-Agent | Distributed expertise | Complex workflows |

---

## LangSmith Integration

### Automatic Tracing

```python
# Set environment variables
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-key>
export LANGSMITH_PROJECT=my-project

# Tracing happens automatically
result = graph.invoke({"input": "hello"})
```

### Programmatic Tracing

```python
import langsmith as ls

# Trace specific invocations
with ls.tracing_context(enabled=True, project_name="test"):
    result = graph.invoke({"input": "hello"})

# Add metadata
result = graph.invoke(
    {"input": "hello"},
    config={
        "tags": ["production", "v1.0"],
        "metadata": {
            "user_id": "user_123",
            "session_id": "sess_456"
        }
    }
)
```

### Evaluation

```python
from langsmith import Client
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

client = Client()

# Create dataset
dataset = client.create_dataset("MathQA")
client.create_examples(
    dataset_id=dataset.id,
    examples=[
        {
            "inputs": {"question": "What is 2+2?"},
            "outputs": {"answer": "4"}
        }
    ]
)

# Define evaluator
judge = create_llm_as_judge(prompt=CORRECTNESS_PROMPT)

# Run experiment
experiment = client.run_on_dataset(
    dataset_name="MathQA",
    func=target_function,
    evaluators=[judge]
)
```

---

## Common Patterns & Use Cases

### 1. RAG with Agentic Routing

```python
def generate_or_retrieve(state: MessagesState):
    """Decide whether to retrieve or respond directly."""
    response = router_model.bind_tools([retriever_tool]).invoke(
        state["messages"]
    )
    return {"messages": [response]}

def grade_documents(state: MessagesState) -> Literal["generate", "rewrite"]:
    """Grade retrieved documents for relevance."""
    class Grade(BaseModel):
        relevance: Literal["relevant", "not_relevant"]
    
    grader = llm.with_structured_output(Grade)
    result = grader.invoke(f"Grade: {state['messages'][-1].content}")
    
    if result.relevance == "relevant":
        return "generate"
    return "rewrite"

def rewrite_query(state: MessagesState):
    """Rewrite query for better retrieval."""
    rewritten = llm.invoke(f"Improve this query: {state['messages'][0].content}")
    return {"messages": [HumanMessage(content=rewritten.content)]}

builder = StateGraph(MessagesState)
builder.add_node("router", generate_or_retrieve)
builder.add_node("retriever", ToolNode([retriever_tool]))
builder.add_node("generator", generate_answer)
builder.add_node("rewriter", rewrite_query)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", route_after_router)
builder.add_conditional_edges("retriever", grade_documents)
builder.add_edge("rewriter", "retriever")
```

### 2. Customer Support Agent

```python
class SupportState(MessagesState):
    customer_id: str
    issue_category: str
    requires_human: bool
    resolved: bool

def classify_issue(state: SupportState):
    """Classify the customer issue."""
    classification = classifier.invoke(state["messages"][-1].content)
    return {
        "issue_category": classification.category,
        "requires_human": classification.complexity > 7
    }

def route_issue(state: SupportState) -> Literal["automated", "human"]:
    if state["requires_human"]:
        return "human"
    return "automated"

def automated_response(state: SupportState):
    """Generate automated response."""
    response = support_llm.invoke(state["messages"])
    return {
        "messages": [response],
        "resolved": True
    }

def human_handoff(state: SupportState):
    """Prepare for human agent."""
    return Command(
        update={"messages": [SystemMessage(content="Transferred to human")]},
        goto="human_queue",
        graph=Command.PARENT
    )

builder = StateGraph(SupportState)
builder.add_node("classify", classify_issue)
builder.add_node("automated", automated_response)
builder.add_node("human", human_handoff)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_issue)
```

### 3. Code Generation with Reflection

```python
class CodeState(TypedDict):
    requirements: str
    code: str
    test_results: str
    iterations: int
    max_iterations: int

def generate_code(state: CodeState):
    """Generate code based on requirements."""
    code = coder_llm.invoke(
        f"Write code for: {state['requirements']}"
    )
    return {"code": code.content}

def run_tests(state: CodeState):
    """Run tests on generated code."""
    result = execute_code(state["code"])
    return {"test_results": result.output}

def reflect_on_errors(state: CodeState):
    """Reflect on test failures."""
    if "error" in state["test_results"]:
        reflection = llm.invoke(
            f"Fix this code:\n{state['code']}\n\nError: {state['test_results']}"
        )
        return {
            "code": reflection.content,
            "iterations": state["iterations"] + 1
        }
    return {"iterations": state["iterations"]}

def should_continue(state: CodeState) -> Literal["generate", "done"]:
    if state["iterations"] >= state["max_iterations"]:
        return "done"
    if "error" in state["test_results"]:
        return "generate"
    return "done"

builder = StateGraph(CodeState)
builder.add_node("generate", generate_code)
builder.add_node("test", run_tests)
builder.add_node("reflect", reflect_on_errors)

builder.add_edge(START, "generate")
builder.add_edge("generate", "test")
builder.add_edge("test", "reflect")
builder.add_conditional_edges("reflect", should_continue)
```

---

## Deployment

### LangSmith Agent Server

Deploy agents with LangSmith Deployment:

```python
# graph.py
from langgraph.graph import StateGraph

# Define your graph
builder = StateGraph(State)
# ... add nodes and edges
graph = builder.compile()
```

```bash
# langgraph.json
{
  "dependencies": ["./requirements.txt"],
  "graphs": {
    "agent": "./graph.py:graph"
  }
}
```

```bash
# Deploy
langgraph deploy
```

### Docker Deployment

```dockerfile
FROM langchain/langgraph-api:latest

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["langgraph", "serve"]
```

---

## Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph
- **LangSmith Docs**: https://docs.langchain.com/langsmith
- **GitHub**: https://github.com/langchain-ai/langgraph
- **Examples**: https://github.com/langchain-ai/langgraph/tree/main/examples

---

*This documentation provides comprehensive coverage of LangGraph for building production-grade AI agents.*
