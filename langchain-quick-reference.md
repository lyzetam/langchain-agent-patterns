# LangChain Agents - Quick Reference

## Installation

```bash
# Basic
pip install -U langchain

# With provider
pip install -U "langchain[openai]"
pip install -U "langchain[anthropic]"

# Multi-agent libraries
pip install langgraph-supervisor
pip install langgraph-swarm

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
    model="gpt-4o",  # or "claude-sonnet-4-5-20250929"
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

## Multi-Agent: Supervisor

```python
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

agent1 = create_react_agent(model, tools=[tool1], name="agent1")
agent2 = create_react_agent(model, tools=[tool2], name="agent2")

supervisor = create_supervisor(
    agents=[agent1, agent2],
    model=model,
    prompt="You manage agent1 and agent2. Assign work appropriately."
).compile()
```

## Multi-Agent: Swarm

```python
from langgraph_swarm import create_swarm, create_handoff_tool
from langgraph.prebuilt import create_react_agent

handoff_to_b = create_handoff_tool(agent_name="agent_b", description="Transfer to B")
handoff_to_a = create_handoff_tool(agent_name="agent_a", description="Transfer to A")

agent_a = create_react_agent(model, tools=[tool1, handoff_to_b], name="agent_a")
agent_b = create_react_agent(model, tools=[tool2, handoff_to_a], name="agent_b")

swarm = create_swarm(
    agents=[agent_a, agent_b],
    default_active_agent="agent_a"
).compile()
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
| OpenAI | `from langchain_openai import ChatOpenAI` | `"gpt-4o"`, `"gpt-5"` |
| Anthropic | `from langchain_anthropic import ChatAnthropic` | `"claude-sonnet-4-5-20250929"` |
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
