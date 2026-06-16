# LangChain Agents - Complete Documentation

> **Version**: LangChain 1.0+ with LangGraph  
> **Last Updated**: 2026-02-24

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Creating Agents](#creating-agents)
5. [Tools](#tools)
6. [Multi-Agent Systems](#multi-agent-systems)
7. [Memory & Persistence](#memory--persistence)
8. [Streaming](#streaming)
9. [Human-in-the-Loop](#human-in-the-loop)
10. [Advanced Patterns](#advanced-patterns)

---

## Introduction

LangChain is the easy way to start building completely custom agents and applications powered by LLMs. With under 10 lines of code, you can connect to OpenAI, Anthropic, Google, and more.

LangChain agents are built on top of **LangGraph** to provide:
- Durable execution
- Streaming support
- Human-in-the-loop capabilities
- Persistence
- Fault tolerance

You do not need to know LangGraph for basic LangChain agent usage.

### When to Use LangChain vs LangGraph

| Use Case | Recommendation |
|----------|----------------|
| Quickly build agents and autonomous applications | **LangChain** |
| Combination of deterministic and agentic workflows | **LangGraph** |
| Heavy customization needs | **LangGraph** |
| Carefully controlled latency | **LangGraph** |

---

## Quick Start

### Installation

```bash
pip install -qU langchain "langchain[anthropic]"
# or for OpenAI
pip install -qU langchain "langchain[openai]"
```

### Basic Agent

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",  # or "gpt-5", etc.
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
```

### Streaming Example

```python
for step in agent.stream(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
```

---

## Core Concepts

### Agent Architecture

An LLM Agent runs tools in a loop to achieve a goal. An agent runs until:
1. The model emits a final output, OR
2. An iteration limit is reached

Agents follow the **ReAct** ("Reasoning + Acting") pattern:
1. Reason about the task
2. Act by calling tools
3. Observe results
4. Repeat until complete

### Example ReAct Loop

```
User: "Find the most popular wireless headphones and check availability"

Step 1 - Reasoning: "I need to search for popular headphones"
Step 1 - Acting: Call search_products("wireless headphones")
Step 1 - Observation: "Found: WH-1000XM5, ..."

Step 2 - Reasoning: "I need to check inventory for the top item"
Step 2 - Acting: Call check_inventory("WH-1000XM5")
Step 2 - Observation: "10 units in stock"

Step 3 - Reasoning: "I have all the information needed"
Step 3 - Acting: Produce final answer
```

---

## Creating Agents

### Basic Agent Creation

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-5",  # Model identifier or instance
    tools=[tool1, tool2],
    system_prompt="You are a helpful assistant"
)
```

### With Custom Model Instance

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-5",
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

agent = create_agent(model, tools=tools)
```

### Dynamic Model Selection

Use middleware with `@wrap_model_call` for runtime model selection:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

basic_model = ChatOpenAI(model="gpt-4o-mini")
advanced_model = ChatOpenAI(model="gpt-4o")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])
    
    if message_count > 10:
        model = advanced_model  # Use advanced for longer conversations
    else:
        model = basic_model
    
    return handler(request.override(model=model))

agent = create_agent(
    model=basic_model,
    tools=tools,
    middleware=[dynamic_model_selection]
)
```

### Dynamic System Prompt

```python
from typing import TypedDict
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

class Context(TypedDict):
    user_role: str

@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on user role."""
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."
    
    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply."
    
    return base_prompt

agent = create_agent(
    model="gpt-4o",
    tools=[web_search],
    middleware=[user_role_prompt],
    context_schema=Context
)
```

---

## Tools

### Defining Tools

#### Using the @tool Decorator

```python
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"

agent = create_agent(model, tools=[search, get_weather])
```

#### Tools with Response Format

```python
from langchain.tools import tool

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs  # (content, artifact)
```

### Tool Error Handling

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

agent = create_agent(
    model="gpt-4o",
    tools=[search, get_weather],
    middleware=[handle_tool_errors]
)
```

### Built-in Tool Integration

LangChain offers 1000+ integrations across:
- Chat & embedding models
- Tools & toolkits
- Document loaders
- Vector stores

Popular integrations include:
- OpenAI (GPT models, embeddings)
- Anthropic (Claude models)
- Azure OpenAI
- Google (Gemini, Vertex AI)
- AWS (Bedrock)
- HuggingFace
- And many more...

---

## Multi-Agent Systems

When a single agent needs to specialize in multiple domains or manage many tools, it can struggle. Multi-agent systems decompose agents into smaller, independent agents that communicate through **handoffs**.

### Multi-Agent Patterns

| Pattern | How It Works | Best For |
|---------|--------------|----------|
| **Subagents** | Main agent coordinates subagents as tools | Centralized control, distributed development |
| **Handoffs** | Agents transfer control dynamically | Direct user interaction, stateful conversations |
| **Skills** | Specialized prompts loaded on-demand | Context management, modular capabilities |
| **Router** | Routing step classifies and directs input | Parallelization, simple delegation |
| **Custom Workflow** | Bespoke execution flows with LangGraph | Complex, hybrid workflows |

### Pattern Comparison

| Pattern | Distributed Dev | Parallelization | Multi-hop | Direct User Interaction |
|---------|----------------|-----------------|-----------|------------------------|
| Subagents | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Handoffs | — | — | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Skills | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Router | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | — | ⭐⭐⭐ |

### Performance Comparison

**One-shot request (e.g., "Buy coffee"):**
- Subagents: 4 calls
- Handoffs: 3 calls ✅
- Skills: 3 calls ✅
- Router: 3 calls ✅

**Repeat request:**
- Subagents: 8 calls (stateless)
- Handoffs: 5 calls (saves 1 by skipping handoff)
- Skills: 5 calls (reuses loaded skill)
- Router: 6 calls (stateless)

**Multi-domain (e.g., compare Python, JavaScript, Rust):**
- Subagents: 5 calls, ~9K tokens ✅
- Handoffs: 7+ calls, ~14K+ tokens
- Skills: 3 calls, ~15K tokens
- Router: 5 calls, ~9K tokens ✅

### Supervisor Pattern

A central supervisor agent coordinates specialized agents:

```python
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

# Create specialized agents
def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."

def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

flight_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[book_flight],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

hotel_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)

# Create supervisor
supervisor = create_supervisor(
    agents=[flight_assistant, hotel_assistant],
    model=ChatOpenAI(model="gpt-4o"),
    prompt="You manage a hotel booking assistant and a flight booking assistant. Assign work to them."
).compile()

# Run
for chunk in supervisor.stream({
    "messages": [{
        "role": "user",
        "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
    }]
}):
    print(chunk)
```

### Swarm Pattern

Agents dynamically hand off control to each other:

```python
from langgraph_swarm import create_swarm, create_handoff_tool
from langgraph.prebuilt import create_react_agent

# Create handoff tools
transfer_to_hotel = create_handoff_tool(
    agent_name="hotel_assistant",
    description="Transfer user to the hotel-booking assistant."
)
transfer_to_flight = create_handoff_tool(
    agent_name="flight_assistant",
    description="Transfer user to the flight-booking assistant."
)

# Create agents with handoff tools
flight_assistant = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    tools=[book_flight, transfer_to_hotel],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

hotel_assistant = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    tools=[book_hotel, transfer_to_flight],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)

# Create swarm
swarm = create_swarm(
    agents=[flight_assistant, hotel_assistant],
    default_active_agent="flight_assistant"
).compile()

# Run
for chunk in swarm.stream({
    "messages": [{
        "role": "user",
        "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
    }]
}):
    print(chunk)
```

### Manual Handoffs

For custom implementations:

```python
from typing import Annotated
from langchain.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

def create_handoff_tool(*, agent_name: str, description: str):
    name = f"transfer_to_{agent_name}"
    
    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={"messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )
    return handoff_tool
```

---

## Memory & Persistence

### Short-term Memory (Thread-scoped)

Short-term memory tracks the ongoing conversation within a session:

```python
from langgraph.checkpoint.memory import InMemorySaver

# Create checkpointer
checkpointer = InMemorySaver()

# Compile agent with checkpointer
agent = create_agent(
    model="gpt-4o",
    tools=[get_weather],
    checkpointer=checkpointer
)

# Invoke with thread_id
config = {"configurable": {"thread_id": "1"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi, I'm Bob"}]},
    config=config
)

# Continue conversation - agent remembers!
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config=config
)
```

### Long-term Memory (Cross-thread)

Long-term memory stores user-specific data across sessions:

```python
from langgraph.store.memory import InMemoryStore

# Create store with embeddings for semantic search
store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),
        "dims": 1536,
        "fields": ["food_preference", "$"]
    }
)

# Store memory
user_id = "my-user"
namespace = (user_id, "memories")
memory_id = str(uuid.uuid4())
memory = {"food_preference": "I like pizza"}
store.put(namespace, memory_id, memory)

# Search memories
memories = store.search(
    namespace,
    query="What does the user like to eat?",
    limit=3
)
```

### Memory Types

| Memory Type | What is Stored | Agent Example |
|-------------|----------------|---------------|
| **Semantic** | Facts | Facts about a user |
| **Episodic** | Experiences | Past agent actions |
| **Procedural** | Instructions | Agent system prompt |

### Checkpointer Libraries

| Library | Implementation | Use Case |
|---------|----------------|----------|
| `langgraph-checkpoint` | Base interface + InMemorySaver | Development, experimentation |
| `langgraph-checkpoint-sqlite` | SqliteSaver / AsyncSqliteSaver | Local workflows |
| `langgraph-checkpoint-postgres` | PostgresSaver / AsyncPostgresSaver | Production |
| `langgraph-checkpoint-cosmosdb` | CosmosDBSaver / AsyncCosmosDBSaver | Azure production |

---

## Streaming

### Stream Modes

| Mode | Description |
|------|-------------|
| `updates` | Stream state updates after each agent step |
| `values` | Stream full graph state after each step |
| `messages` | Stream LLM tokens with metadata |
| `custom` | Stream custom data from inside nodes |
| `debug` | Stream all information for debugging |

### Streaming Agent Progress

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="updates",
):
    for step, data in chunk.items():
        print(f"step: {step}")
        print(f"content: {data['messages'][-1].content_blocks}")
```

Output:
```
step: model
content: [{'type': 'tool_call', 'name': 'get_weather', ...}]

step: tools
content: [{'type': 'text', 'text': "It's always sunny in San Francisco!"}]

step: model
content: [{'type': 'text', 'text': "It's always sunny in San Francisco!"}]
```

### Streaming LLM Tokens

```python
for token, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="messages",
):
    print(f"node: {metadata['langgraph_node']}")
    print(f"content: {token.content_blocks}")
```

### Custom Stream Updates

```python
from langgraph.config import get_stream_writer

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    writer = get_stream_writer()
    writer(f"Looking up data for city: {city}")
    writer(f"Acquired data for city: {city}")
    return f"It's always sunny in {city}!"

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="custom"
):
    print(chunk)
# Output: "Looking up data for city: San Francisco"
#         "Acquired data for city: San Francisco"
```

### Multiple Stream Modes

```python
for stream_mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["updates", "custom"]
):
    print(f"stream_mode: {stream_mode}")
    print(f"content: {chunk}")
```

---

## Human-in-the-Loop

Human-in-the-loop allows humans to inspect, interrupt, and approve agent steps.

### Using Interrupt Before/After

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model="gpt-4o",
    tools=[search],
    interrupt_before=["tools"],  # Interrupt before tools execute
    # or
    interrupt_after=["agent"]    # Interrupt after agent responds
)
```

### Using Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

checkpointer = InMemorySaver()

agent = create_agent(
    model="gpt-4o",
    tools=[get_weather],
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on={"get_weather": True}),
    ],
    checkpointer=checkpointer,
)

# Stream and collect interrupts
interrupts = []
for stream_mode, data in agent.stream(
    {"messages": [input_message]},
    config=config,
    stream_mode=["messages", "updates"],
):
    if stream_mode == "updates" and "__interrupt__" in data:
        interrupts.extend(data["__interrupt__"])

# Respond to interrupts with decisions
decisions = {
    interrupt.id: {
        "decisions": [
            {"type": "approve"},
            {"type": "edit", "edited_action": {...}},
            {"type": "reject"},
        ]
    }
    for interrupt in interrupts
}

# Resume
for stream_mode, data in agent.stream(
    Command(resume=decisions),
    config=config,
    stream_mode=["messages", "updates"],
):
    # Process streaming output
    pass
```

---

## Advanced Patterns

### Middleware System

LangChain agents support middleware for customizing behavior:

| Middleware | Purpose |
|------------|---------|
| `@wrap_model_call` | Dynamic model selection |
| `@dynamic_prompt` | Dynamic system prompts |
| `@wrap_tool_call` | Custom tool error handling |
| `@after_agent` | Post-processing, guardrails |

### Example: Safety Guardrail

```python
from typing import Any, Literal
from langchain.agents.middleware import after_agent, AgentState
from pydantic import BaseModel

class ResponseSafety(BaseModel):
    """Evaluate a response as safe or unsafe."""
    evaluation: Literal["safe", "unsafe"]

safety_model = init_chat_model("openai:gpt-4o")

@after_agent(can_jump_to=["end"])
def safety_guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Model-based guardrail: Use an LLM to evaluate response safety."""
    if not state["messages"]:
        return None
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        return None
    
    # Evaluate safety
    model_with_tools = safety_model.bind_tools([ResponseSafety], tool_choice="any")
    result = model_with_tools.invoke([
        {"role": "system", "content": "Evaluate this AI response as safe or unsafe."},
        {"role": "user", "content": f"AI response: {last_message.text}"}
    ])
    
    tool_call = result.tool_calls[0]
    if tool_call["args"]["evaluation"] == "unsafe":
        last_message.content = "I cannot provide that response. Please rephrase."
    
    return None

agent = create_agent(
    model="gpt-4o",
    tools=[get_weather],
    middleware=[safety_guardrail],
)
```

### Reflection Pattern

Agents can modify their own instructions based on feedback:

```python
# Node that uses instructions
def call_model(state: State, store: BaseStore):
    namespace = ("agent_instructions",)
    instructions = store.get(namespace, key="agent_a")[0]
    prompt = prompt_template.format(instructions=instructions.value["instructions"])
    # ... use in model call

# Node that updates instructions
def update_instructions(state: State, store: BaseStore):
    namespace = ("instructions",)
    instructions = store.search(namespace)[0]
    
    prompt = prompt_template.format(
        instructions=instructions.value["instructions"],
        conversation=state["messages"]
    )
    output = llm.invoke(prompt)
    new_instructions = output['new_instructions']
    
    store.put(("agent_instructions",), "agent_a", {"instructions": new_instructions})
```

---

## Best Practices

### 1. Tool Design
- Keep tool descriptions clear and specific
- Use `response_format="content_and_artifact"` when returning complex data
- Implement proper error handling

### 2. Model Selection
- Use simpler models for straightforward tasks
- Reserve advanced models for complex reasoning
- Implement dynamic model selection for cost optimization

### 3. Memory Management
- Use short-term memory (checkpointers) for conversation history
- Use long-term memory (store) for user preferences and facts
- Implement semantic search for large memory collections

### 4. Multi-Agent Design
- Start with a single agent and split when complexity grows
- Choose patterns based on: distributed development needs, parallelization requirements, and user interaction style
- Use subagents for strong context isolation
- Use handoffs for stateful, direct user interactions

### 5. Streaming
- Always stream for interactive applications
- Use `stream_mode="updates"` for progress tracking
- Use `stream_mode="messages"` for token-by-token display
- Combine multiple stream modes for rich UIs

---

## Resources

- **LangChain Documentation**: https://python.langchain.com
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph
- **LangSmith**: https://smith.langchain.com
- **GitHub Repositories**:
  - https://github.com/langchain-ai/langgraph-supervisor-py
  - https://github.com/langchain-ai/langgraph-swarm-py

---

*This documentation is compiled from official LangChain and LangGraph sources for building production-ready AI agents.*
