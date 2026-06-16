"""
Reflection Agent Example
=======================
An agent that generates content, reflects on it, and iteratively improves.
Based on the Reflexion paper - self-reflective agents.

Pattern:
1. Generate initial response
2. Reflect/critique the response
3. Revise based on critique
4. Repeat until satisfactory or max iterations
"""

from typing import Annotated, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


# ============ State ============

class ReflectionState(TypedDict):
    """State for reflection agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    iterations: int
    max_iterations: int


# ============ LLMs ============

# Can use different models for generation and reflection
generator_llm = init_chat_model("anthropic:claude-sonnet-4-6", temperature=0.7)
reflector_llm = init_chat_model("anthropic:claude-sonnet-4-6", temperature=0)


# ============ Prompts ============

GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert writer tasked with creating excellent content. "
        "Generate the best possible response for the user's request. "
        "If the user provides critique, respond with a revised version "
        "that addresses all the feedback."
    ),
    MessagesPlaceholder(variable_name="messages")
])

REFLECTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a critical reviewer grading content submissions. "
        "Provide detailed critique and specific recommendations for improvement. "
        "Focus on: clarity, accuracy, completeness, structure, and style. "
        "Be constructive but thorough in your criticism."
    ),
    MessagesPlaceholder(variable_name="messages"),
    (
        "user",
        "Provide critique and recommendations for the above content."
    )
])


# ============ Nodes ============

def generate(state: ReflectionState):
    """Generate or revise content based on history."""
    print(f"\n✍️  Generation (iteration {state['iterations'] + 1}/{state['max_iterations']})")
    
    chain = GENERATION_PROMPT | generator_llm
    response = chain.invoke({"messages": state["messages"]})
    
    # Print preview
    preview = response.content[:200].replace("\n", " ")
    print(f"   Generated: {preview}...")
    
    return {
        "messages": [response],
        "iterations": state["iterations"] + 1
    }


def reflect(state: ReflectionState):
    """Reflect on and critique the generated content."""
    print(f"\n🔍 Reflection")
    
    chain = REFLECTION_PROMPT | reflector_llm
    critique = chain.invoke({"messages": state["messages"]})
    
    # Print critique preview
    preview = critique.content[:200].replace("\n", " ")
    print(f"   Critique: {preview}...")
    
    return {"messages": [critique]}


# ============ Conditional Edges ============

def should_continue(state: ReflectionState) -> Literal["generate", END]:
    """Decide whether to continue iterating or end."""
    if state["iterations"] >= state["max_iterations"]:
        print(f"\n⏹️  Reached max iterations ({state['max_iterations']})")
        return END
    return "generate"


# ============ Build Graph ============

def create_reflection_graph(max_iterations: int = 3):
    """Create the reflection graph."""
    builder = StateGraph(ReflectionState)
    
    builder.add_node("generate", generate)
    builder.add_node("reflect", reflect)
    
    builder.add_edge(START, "generate")
    builder.add_edge("generate", "reflect")
    builder.add_conditional_edges("reflect", should_continue)
    
    return builder.compile()


# ============ Main ============

def main():
    print("=" * 60)
    print("Reflection Agent - Essay Generator")
    print("=" * 60)
    
    graph = create_reflection_graph(max_iterations=3)
    
    # Example task
    task = (
        "Write a 3-paragraph essay on the importance of "
        "artificial intelligence in modern healthcare."
    )
    
    print(f"\n🎯 Task: {task}\n")
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=task)],
        "iterations": 0,
        "max_iterations": 3
    }
    
    # Run the agent with streaming
    print("\n" + "─" * 60)
    print("Running Reflection Loop...")
    print("─" * 60)
    
    final_state = None
    for event in graph.stream(initial_state, stream_mode="values"):
        final_state = event
    
    # Display final result
    print("\n" + "=" * 60)
    print("📄 Final Essay:")
    print("=" * 60)
    
    # Get the last AI message (final generation)
    ai_messages = [
        m for m in final_state["messages"]
        if isinstance(m, AIMessage)
    ]
    if ai_messages:
        print(ai_messages[-1].content)
    
    # Show iteration history
    print("\n📊 Iteration Summary:")
    print(f"   Total iterations: {final_state['iterations']}")
    print(f"   Max iterations: {final_state['max_iterations']}")
    
    # Show message flow
    print("\n📝 Message Flow:")
    for i, msg in enumerate(final_state["messages"], 1):
        msg_type = type(msg).__name__
        content_preview = msg.content[:50].replace("\n", " ")
        print(f"   {i}. [{msg_type}] {content_preview}...")


if __name__ == "__main__":
    main()
