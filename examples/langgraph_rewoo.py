"""
ReWOO (Reasoning Without Observation) Example
=============================================
An agent that separates planning from execution to reduce token consumption.

Key insight: Generate the full plan first with variable substitution,
then execute tools without redundant LLM calls.

Advantages:
1. Reduced token consumption (no redundant prefixes)
2. Faster execution
3. Easier fine-tuning (planning doesn't depend on tool outputs)

Structure:
1. Planner: Generate plan with placeholders (#E1, #E2, ...)
2. Worker: Execute tools and substitute variables
3. Solver: Generate final answer from evidence
"""

import re
from typing import List

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


# ============ Tools ============

@tool
def google_search(query: str) -> str:
    """Search Google for information."""
    # In production: use Tavily, SerpAPI, etc.
    return f"Search results for '{query}': [relevant information found]"


@tool
def llm_reason(input_text: str) -> str:
    """Use LLM for reasoning."""
    llm = init_chat_model("anthropic:claude-haiku-4-5")
    return llm.invoke(input_text).content


TOOLS = {
    "Google": google_search,
    "LLM": llm_reason
}


# ============ State ============

class ReWOOState(TypedDict):
    """State for ReWOO agent."""
    task: str
    plan_string: str
    steps: List[tuple]  # (plan_text, var_name, tool_name, tool_input)
    results: dict  # Variable substitutions
    result: str


# ============ Planner ============

PLANNER_PROMPT = """For the following task, create a step-by-step plan.
For each step, indicate which external tool to use.

You can store evidence from each step in a variable #E1, #E2, etc.
that can be referenced in later steps.

Available tools:
(1) Google[input]: Search Google. Use for finding current information.
(2) LLM[input]: Use the LLM for reasoning. Use when you know the answer.

Format each step as:
Plan: <reasoning for this step>
#E1 = ToolName[tool input]
Plan: <reasoning>
#E2 = ToolName[tool input with #E1 substitution]

Example:
Task: Who won the 2024 Australian Open and where are they from?
Plan: Search for 2024 Australian Open winner
#E1 = Google[2024 Australian Open winner]
Plan: Get the winner's name from search results
#E2 = LLM[What is the winner's name given #E1]
Plan: Search for the winner's birthplace
#E3 = Google[hometown of Australian Open winner #E2]

Now solve this task:
Task: {task}
"""


def get_plan(state: ReWOOState):
    """Generate the initial plan."""
    print(f"\n📋 Planning...")
    
    llm = init_chat_model("anthropic:claude-sonnet-4-6", temperature=0)
    prompt = ChatPromptTemplate.from_messages([("user", PLANNER_PROMPT)])
    planner = prompt | llm
    
    result = planner.invoke({"task": state["task"]})
    plan_text = result.content
    
    # Parse plan steps
    # Pattern: Plan: <reasoning> #E<number> = ToolName[arguments]
    regex_pattern = r"Plan:\s*(.+?)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"
    matches = re.findall(regex_pattern, plan_text, re.DOTALL)
    
    steps = []
    for plan_desc, var_name, tool_name, tool_input in matches:
        steps.append((
            plan_desc.strip(),
            var_name.strip(),
            tool_name.strip(),
            tool_input.strip()
        ))
    
    print(f"   Generated {len(steps)} steps")
    for i, (desc, var, tool, inp) in enumerate(steps, 1):
        print(f"   {i}. {var} = {tool}[{inp[:40]}...]")
    
    return {
        "steps": steps,
        "plan_string": plan_text,
        "results": {}
    }


# ============ Worker ============

def _get_current_step(state: ReWOOState) -> int:
    """Determine which step to execute next."""
    results = state.get("results", {})
    return len(results) + 1


def tool_execution(state: ReWOOState):
    """Execute the current tool in the plan."""
    step_num = _get_current_step(state)
    
    if step_num > len(state["steps"]):
        return {"results": state.get("results", {})}
    
    plan_desc, var_name, tool_name, tool_input = state["steps"][step_num - 1]
    
    print(f"\n🔧 Step {step_num}: {var_name} = {tool_name}[...]")
    print(f"   Plan: {plan_desc[:60]}...")
    
    # Substitute previous results
    results = state.get("results", {})
    for var, value in results.items():
        tool_input = tool_input.replace(var, value)
    
    print(f"   Executing: {tool_input[:50]}...")
    
    # Execute tool
    if tool_name in TOOLS:
        result = TOOLS[tool_name].invoke(tool_input)
    else:
        result = f"Error: Unknown tool {tool_name}"
    
    # Store result
    results[var_name] = str(result)
    
    print(f"   Result: {str(result)[:80]}...")
    
    return {"results": results}


def should_continue(state: ReWOOState) -> str:
    """Check if there are more steps to execute."""
    current_step = _get_current_step(state)
    if current_step > len(state["steps"]):
        return "solve"
    return "worker"


# ============ Solver ============

SOLVE_PROMPT = """Solve the following task using the provided evidence.

Task: {task}

Plan and Evidence:
{evidence}

Provide a clear, direct answer based on the evidence above.
Answer:"""


def solve(state: ReWOOState):
    """Generate final answer from all evidence."""
    print(f"\n📝 Solving...")
    
    # Build evidence string
    evidence_parts = []
    for i, (plan_desc, var_name, tool_name, tool_input) in enumerate(state["steps"], 1):
        result = state["results"].get(var_name, "No result")
        evidence_parts.append(
            f"Step {i}: {plan_desc}\n"
            f"  {var_name} = {tool_name}[...]\n"
            f"  Result: {result}\n"
        )
    
    evidence = "\n".join(evidence_parts)
    
    llm = init_chat_model("anthropic:claude-sonnet-4-6", temperature=0)
    prompt = SOLVE_PROMPT.format(
        task=state["task"],
        evidence=evidence
    )
    
    result = llm.invoke(prompt)
    
    print(f"   Generated answer: {result.content[:100]}...")
    
    return {"result": result.content}


# ============ Build Graph ============

def create_rewoo_graph():
    """Create ReWOO graph."""
    builder = StateGraph(ReWOOState)
    
    builder.add_node("planner", get_plan)
    builder.add_node("worker", tool_execution)
    builder.add_node("solver", solve)
    
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "worker")
    builder.add_conditional_edges("worker", should_continue, {
        "worker": "worker",
        "solve": "solver"
    })
    builder.add_edge("solver", END)
    
    return builder.compile()


# ============ Main ============

def main():
    print("=" * 60)
    print("ReWOO: Reasoning Without Observation")
    print("=" * 60)
    
    # Example task
    task = (
        "What is the hometown of the 2024 Australian Open winner, "
        "and what is the population of that city?"
    )
    
    print(f"\n🎯 Task: {task}\n")
    
    graph = create_rewoo_graph()
    
    initial_state = {
        "task": task,
        "plan_string": "",
        "steps": [],
        "results": {},
        "result": ""
    }
    
    result = graph.invoke(initial_state)
    
    # Display results
    print("\n" + "=" * 60)
    print("📄 Final Answer:")
    print("=" * 60)
    print(result["result"])
    
    # Show execution trace
    print("\n📊 Execution Trace:")
    for i, (desc, var, tool, inp) in enumerate(result["steps"], 1):
        res = result["results"].get(var, "N/A")
        print(f"\n  Step {i}: {desc}")
        print(f"    {var} = {tool}[{inp}]")
        print(f"    → {res[:100]}...")


if __name__ == "__main__":
    main()
