"""
Agent with Memory Example
=========================
An agent that remembers conversation history using checkpoints.
"""

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver


@tool
def get_user_info() -> str:
    """Get information about the current user."""
    return "User ID: 12345, Plan: Premium"


def main():
    # Create checkpointer for short-term memory
    checkpointer = InMemorySaver()
    
    # Create agent with memory
    agent = create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[get_user_info],
        system_prompt="You are a helpful assistant. Remember what the user tells you.",
        checkpointer=checkpointer
    )
    
    # Thread ID for this conversation
    config = {"configurable": {"thread_id": "user_123"}}
    
    print("Agent with Memory - Type 'quit' to exit")
    print("Thread ID: user_123")
    print("-" * 50)
    
    conversation_history = []
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Invoke with config (includes thread_id)
        result = agent.invoke(
            {"messages": conversation_history},
            config=config
        )
        
        # Get response and add to history
        response = result["messages"][-1]
        conversation_history.append({"role": "assistant", "content": response.content})
        
        print(f"Agent: {response.content}")
        
        # Demonstrate memory - ask "What's my name?" after introducing yourself


if __name__ == "__main__":
    main()
