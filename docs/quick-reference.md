# LangChain Agents - Quick Reference

## Installation

```bash
# Basic
pip install -U langchain

# With provider
pip install -U "langchain[openai]"
pip install -U "langchain[anthropic]"

# Multi-agent libraries
pip install -U deepagents  # official Deep Agents framework

# Checkpointing
pip install langgraph-checkpoint-sqlite
pip install langgraph-checkpoint-postgres
```

## Basic Agent

```python
from langchain.agents import create_agent

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",  # or "openai:gpt-5"
    tools=[get_weather],
    system_prompt="You are a helpful assistant"
)

# Invoke
result = agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather in sf"}]
})

# Stream
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    stream_mode="updates"
):
    print(chunk)
```

## Tools

```python
from langchain.tools import tool

# Basic tool
@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

# Tool with artifact
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve documents."""
    docs = vector_store.search(query)
    return format(docs), docs  # (content, artifact)
```

## Memory

```python
from langgraph.checkpoint.memory import InMemorySaver

# Short-term memory
checkpointer = InMemorySaver()
agent = create_agent(model, tools, checkpointer=checkpointer)

# Use with thread_id
config = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": [msg]}, config=config)
```

## Multi-Agent: Subagents (agent-as-tool)

```python
from langchain.agents import create_agent
from langchain.tools import tool

# Specialized subagents
agent1 = create_agent(model, tools=[tool1])
agent2 = create_agent(model, tools=[tool2])

# Wrap each subagent as a tool the supervisor can call
@tool("agent1", description="Delegate work to agent1")
def call_agent1(query: str) -> str:
    result = agent1.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

@tool("agent2", description="Delegate work to agent2")
def call_agent2(query: str) -> str:
    result = agent2.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

supervisor = create_agent(
    model=model,
    tools=[call_agent1, call_agent2],
    system_prompt="You manage agent1 and agent2. Assign work appropriately."
)
```

## Multi-Agent: Handoffs (Command graph transfer)

```python
from langchain.agents import create_agent
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

@tool
def transfer_to_b(runtime: ToolRuntime) -> Command:
    """Transfer to agent B."""
    last_ai = next(
        m for m in reversed(runtime.state["messages"]) if isinstance(m, AIMessage)
    )
    transfer = ToolMessage(
        content="Transferred to agent B", tool_call_id=runtime.tool_call_id
    )
    return Command(
        goto="agent_b",
        update={"active_agent": "agent_b", "messages": [last_ai, transfer]},
        graph=Command.PARENT,
    )

agent_a = create_agent(model, tools=[tool1, transfer_to_b])
agent_b = create_agent(model, tools=[tool2])
# Wire agent_a / agent_b as nodes in a StateGraph that routes on active_agent.
```

## Streaming Modes

| Mode | Usage |
|------|-------|
| `updates` | `agent.stream(input, stream_mode="updates")` |
| `messages` | `agent.stream(input, stream_mode="messages")` |
| `custom` | `agent.stream(input, stream_mode="custom")` |
| Multiple | `agent.stream(input, stream_mode=["updates", "custom"])` |

## Middleware

```python
from langchain.agents.middleware import wrap_model_call, dynamic_prompt

# Dynamic model
@wrap_model_call
def select_model(request: ModelRequest, handler):
    model = advanced_model if complex(request) else basic_model
    return handler(request.override(model=model))

# Dynamic prompt
@dynamic_prompt
def custom_prompt(request: ModelRequest) -> str:
    return f"You are {request.runtime.context['role']}"

agent = create_agent(
    model=model,
    tools=tools,
    middleware=[select_model, custom_prompt]
)
```

## Human-in-the-Loop

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model=model,
    tools=tools,
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"tool_name": True})],
    checkpointer=checkpointer
)

# Handle interrupts
for mode, data in agent.stream(input, stream_mode=["updates"]):
    if mode == "updates" and "__interrupt__" in data:
        # Handle interrupt
        decisions = {...}
        agent.stream(Command(resume=decisions), config)
```

## Common Patterns

### RAG Agent
```python
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in docs
    )
    return serialized, docs

agent = create_agent(
    model=model,
    tools=[retrieve_context],
    system_prompt="Use the retrieve tool to help answer user queries."
)
```

### Sub-agent Pattern
```python
sub_agent = create_agent(model, tools=[...], name="sub_agent")

def call_sub_agent(query: str) -> str:
    """Query the sub-agent."""
    result = sub_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].text

main_agent = create_agent(model, tools=[call_sub_agent])
```

## Configuration

```python
# Environment variables
export OPENAI_API_KEY="..."
export LANGSMITH_TRACING="true"
export LANGSMITH_API_KEY="..."

# Or in Python
import os
os.environ["OPENAI_API_KEY"] = "..."
```

## Model Providers

| Provider | Import | Model String |
|----------|--------|--------------|
| Anthropic (recommended) | `from langchain_anthropic import ChatAnthropic` | `"claude-sonnet-4-6"` |
| OpenAI | `from langchain_openai import ChatOpenAI` | `"gpt-5"` |
| Azure | `from langchain_openai import AzureChatOpenAI` | - |
| Google | `from langchain_google_genai import ChatGoogleGenerativeAI` | `"gemini-1.5-pro"` |
| AWS | `from langchain_aws import ChatBedrock` | - |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not using tools | Improve tool descriptions, add examples |
| Context too long | Use checkpointer with message trimming |
| Slow responses | Use streaming, dynamic model selection |
| State not persisting | Always pass checkpointer to compile() |
| Multi-agent not routing | Check handoff tool descriptions |
