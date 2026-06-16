"""
Basic Agent Example
===================
A simple agent with weather tool.
"""

from langchain.agents import create_agent
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city.
    
    Args:
        city: The city name (e.g., "San Francisco", "New York")
    
    Returns:
        Weather information for the city
    """
    # In production, call a real weather API
    return f"It's always sunny in {city}!"


@tool
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    # Create agent
    agent = create_agent(
        model="anthropic:claude-sonnet-4-6",  # provider:model — or pass a model instance
        tools=[get_weather, get_time],
        system_prompt="You are a helpful assistant. Be concise and accurate."
    )
    
    # Interactive loop
    print("Basic Agent - Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        # Invoke agent
        result = agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })
        
        # Print response
        response = result["messages"][-1]
        print(f"Agent: {response.content}")


if __name__ == "__main__":
    main()
