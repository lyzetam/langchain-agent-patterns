"""
Plan-and-Execute Agent Example
===============================
A multi-step planning agent that creates a plan first, then executes it step by step.
Inspired by the Plan-and-Solve paper and Baby-AGI.

Key differences from ReAct:
1. Explicit long-term planning upfront
2. Can use weaker models for execution
3. Can revisit and modify plan during execution
"""

import operator
from typing import Annotated, Literal, TypedDict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.graph import END, START, StateGraph


# ============ Tools ============

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # In production, use Tavily, SerpAPI, etc.
    return f"Search results for '{query}': Found relevant information."


@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============ State ============

class PlanExecute(TypedDict):
    """State for plan-and-execute agent."""
    input: str
    plan: list[str]
    past_steps: Annotated[list[tuple[str, str]], operator.add]
    response: str


# ============ Nodes ============

# Planner LLM (can use stronger model for planning)
planner_llm = init_chat_model("anthropic:claude-sonnet-4-6", temperature=0)

# Executor LLM (can use cheaper/faster model for execution)
executor_llm = init_chat_model("anthropic:claude-haiku-4-5", temperature=0)
executor_agent = create_agent(executor_llm, tools=[search_web, calculate])


PLANNER_PROMPT = """For the following task, create a step-by-step plan.
Break down the task into clear, actionable steps.

Task: {task}

Return your plan as a numbered list, one step per line:
1. Step one
2. Step two
3. Step three

Plan:"""

REPLANNER_PROMPT = """Given the original task, the previous plan, and the completed steps,
update the plan if needed.

Original Task: {task}

Previous Plan: {plan}

Completed Steps: {past_steps}

If the task is complete, respond with "COMPLETE: <final answer>"
Otherwise, provide an updated plan as a numbered list.

Response:"""


def planner(state: PlanExecute):
    """Generate initial multi-step plan."""
    task = state["input"]
    
    response = planner_llm.invoke(PLANNER_PROMPT.format(task=task))
    
    # Parse plan into list of steps
    plan_text = response.content
    steps = [
        line.strip()[2:].strip()  # Remove "1. ", "2. ", etc.
        for line in plan_text.split("\n")
        if line.strip() and line[0].isdigit()
    ]
    
    print(f"\n📋 Generated Plan:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    
    return {"plan": steps}


def executor(state: PlanExecute):
    """Execute the next step in the plan."""
    if not state["plan"]:
        return {"response": "Task complete!"}
    
    # Get next step
    current_step = state["plan"][0]
    remaining_plan = state["plan"][1:]
    
    print(f"\n🔧 Executing: {current_step}")
    
    # Execute using the executor agent
    result = executor_agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Execute this step: {current_step}\n\n"
                      f"Original task context: {state['input']}"
        }]
    })
    
    # Extract result
    output = result["messages"][-1].content
    print(f"   Result: {output[:100]}...")
    
    return {
        "past_steps": [(current_step, output)],
        "plan": remaining_plan
    }


def replanner(state: PlanExecute):
    """Replan based on execution results."""
    task = state["input"]
    
    # Format completed steps
    completed = "\n".join([
        f"- {step}: {result}"
        for step, result in state["past_steps"]
    ])
    
    remaining = "\n".join([
        f"- {step}"
        for step in state["plan"]
    ]) if state["plan"] else "None - all steps completed"
    
    response = planner_llm.invoke(REPLANNER_PROMPT.format(
        task=task,
        plan=remaining,
        past_steps=completed
    ))
    
    content = response.content.strip()
    
    # Check if complete
    if content.startswith("COMPLETE:"):
        final_answer = content.replace("COMPLETE:", "").strip()
        return {"response": final_answer, "plan": []}
    
    # Parse updated plan
    steps = [
        line.strip()[2:].strip()
        for line in content.split("\n")
        if line.strip() and line[0].isdigit()
    ]
    
    if steps:
        print(f"\n🔄 Updated Plan:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
    
    return {"plan": steps}


# ============ Conditional Edges ============

def should_continue(state: PlanExecute) -> Literal["executor", END]:
    """Decide whether to continue executing or end."""
    if state.get("response"):
        return END
    if state["plan"]:
        return "executor"
    return END


def should_replan(state: PlanExecute) -> Literal["replan", END]:
    """Decide whether to replan or end."""
    if state.get("response"):
        return END
    return "replan"


# ============ Build Graph ============

def create_plan_execute_graph():
    """Create the plan-and-execute graph."""
    builder = StateGraph(PlanExecute)
    
    # Add nodes
    builder.add_node("planner", planner)
    builder.add_node("executor", executor)
    builder.add_node("replan", replanner)
    
    # Add edges
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "replan")
    builder.add_conditional_edges("replan", should_continue)
    
    return builder.compile()


# ============ Main ============

def main():
    print("=" * 60)
    print("Plan-and-Execute Agent")
    print("=" * 60)
    
    graph = create_plan_execute_graph()
    
    # Example task
    task = (
        "Research the top 3 programming languages in 2024, "
        "calculate their combined market share percentage, "
        "and provide a brief summary of each."
    )
    
    print(f"\n🎯 Task: {task}\n")
    
    # Run the agent
    result = graph.invoke({
        "input": task,
        "plan": [],
        "past_steps": [],
        "response": ""
    })
    
    print("\n" + "=" * 60)
    print("✅ Final Response:")
    print("=" * 60)
    print(result["response"])
    
    # Show execution history
    print("\n📊 Execution History:")
    for i, (step, output) in enumerate(result["past_steps"], 1):
        print(f"  {i}. {step}")
        print(f"     → {output[:80]}...")


if __name__ == "__main__":
    main()
