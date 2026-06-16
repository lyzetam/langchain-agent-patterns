"""
Streaming Agent Example
=======================
An agent that streams progress and tokens in real-time.
"""

import asyncio
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.config import get_stream_writer


@tool
def search_web(query: str) -> str:
    """Search the web for information.
    
    Args:
        query: The search query
    """
    # Simulate search delay
    import time
    time.sleep(1)
    return f"Search results for '{query}': Found 10 relevant pages."


@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression.
    
    Args:
        expression: Math expression like "2 + 2" or "10 * 5"
    """
    try:
        # Safe evaluation
        allowed = {"__builtins__": {}}
        allowed.update({
            'abs': abs, 'round': round, 'max': max, 'min': min,
            'sum': sum, 'pow': pow
        })
        result = eval(expression, allowed, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def stream_with_progress(agent, user_input):
    """Stream agent execution with progress updates."""
    print(f"\nUser: {user_input}")
    print("Agent: ", end="", flush=True)
    
    for stream_mode, data in agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode=["updates", "messages"]
    ):
        if stream_mode == "messages":
            token, metadata = data
            # Print token content
            if hasattr(token, 'content') and token.content:
                print(token.content, end="", flush=True)
        
        elif stream_mode == "updates":
            for node, update in data.items():
                if node in ["model", "tools"]:
                    message = update["messages"][-1]
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        print(f"\n[Calling tool: {message.tool_calls[0]['name']}]")
    
    print()  # Final newline


def main():
    agent = create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[search_web, calculate],
        system_prompt="You are a helpful assistant. Use tools when needed."
    )
    
    print("Streaming Agent - Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        stream_with_progress(agent, user_input)


if __name__ == "__main__":
    main()
