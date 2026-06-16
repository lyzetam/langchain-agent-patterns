# pip install -U langchain "langchain[anthropic]" langgraph
"""
Swarm Multi-Agent Example
=========================
Agents dynamically handing off control to each other based on specialization,
for a code-review workflow (triage -> specialist -> back to triage).

Pattern: Handoffs. Replaces the deprecated langgraph_swarm API.

Each agent is a node in a LangGraph StateGraph. Handoff tools return a
`Command(goto=..., graph=Command.PARENT, update={"active_agent": ...})` to
transfer control. State extends AgentState with an `active_agent` field that
persists across turns.
"""

from typing import Literal

from langchain.agents import AgentState, create_agent
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing_extensions import NotRequired


# ============ State ============

class MultiAgentState(AgentState):
    active_agent: NotRequired[str]


# ============ Domain Tools ============

@tool
def code_review(code: str) -> str:
    """Review code for issues and improvements."""
    issues = []
    if "print(" in code:
        issues.append("- Consider using logging instead of print statements")
    if "except:" in code:
        issues.append("- Avoid bare except clauses, catch specific exceptions")
    if len(code) > 500:
        issues.append("- Consider breaking this into smaller functions")

    if not issues:
        return "Code review: No major issues found!"
    return "Code review findings:\n" + "\n".join(issues)


@tool
def write_tests(code: str) -> str:
    """Generate test cases for code."""
    return "Generated 3 test cases for the provided code.\nTest coverage: 85%"


@tool
def check_style(code: str) -> str:
    """Check code style compliance."""
    return "Style check: PEP 8 compliant with 2 minor formatting suggestions"


@tool
def security_scan(code: str) -> str:
    """Scan code for security vulnerabilities."""
    return "Security scan: No vulnerabilities detected"


# ============ Handoff Tools ============

def _make_handoff(target: str, label: str):
    """Build a handoff tool that transfers control to `target` node."""

    @tool(f"transfer_to_{target}", description=f"Transfer to the {label}.")
    def _handoff(runtime: ToolRuntime) -> Command:
        last_ai_message = next(
            msg
            for msg in reversed(runtime.state["messages"])
            if isinstance(msg, AIMessage)
        )
        transfer_message = ToolMessage(
            content=f"Transferred to {label}",
            tool_call_id=runtime.tool_call_id,
        )
        return Command(
            goto=target,
            update={
                "active_agent": target,
                "messages": [last_ai_message, transfer_message],
            },
            graph=Command.PARENT,
        )

    return _handoff


transfer_to_code_reviewer = _make_handoff("code_reviewer", "code review specialist")
transfer_to_test_writer = _make_handoff("test_writer", "test writing specialist")
transfer_to_style_checker = _make_handoff("style_checker", "code style specialist")
transfer_to_security_scanner = _make_handoff("security_scanner", "security specialist")
transfer_to_triage = _make_handoff("triage_agent", "triage agent")


# ============ Specialized Agents ============

triage_agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[
        transfer_to_code_reviewer,
        transfer_to_test_writer,
        transfer_to_style_checker,
        transfer_to_security_scanner,
    ],
    system_prompt="""You are a triage agent for code review tasks.

Analyze user requests and route to the appropriate specialist:
- Code quality/review issues -> code_reviewer
- Test generation -> test_writer
- Style/formatting -> style_checker
- Security concerns -> security_scanner

After the specialist completes their work, summarize the results for the user
and ask if they need anything else.""",
)

code_reviewer = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[code_review, transfer_to_triage],
    system_prompt="""You are a code review specialist.

Review code for:
- Logic errors
- Performance issues
- Maintainability concerns
- Best practice violations

Provide constructive feedback and suggestions for improvement.
After completing your review, transfer back to triage_agent.""",
)

test_writer = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[write_tests, transfer_to_triage],
    system_prompt="""You are a test writing specialist.

Generate comprehensive test cases including:
- Unit tests
- Edge cases
- Error scenarios

Provide the generated tests with explanations.
After completing test generation, transfer back to triage_agent.""",
)

style_checker = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[check_style, transfer_to_triage],
    system_prompt="""You are a code style specialist.

Check code for:
- PEP 8 compliance
- Consistent formatting
- Naming conventions
- Documentation quality

Provide specific recommendations for style improvements.
After completing style check, transfer back to triage_agent.""",
)

security_scanner = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[security_scan, transfer_to_triage],
    system_prompt="""You are a security specialist.

Scan code for:
- Injection vulnerabilities
- Insecure dependencies
- Authentication issues
- Data exposure risks

Report any security concerns with severity levels.
After completing security scan, transfer back to triage_agent.""",
)


# ============ Graph Nodes ============

AGENTS = {
    "triage_agent": triage_agent,
    "code_reviewer": code_reviewer,
    "test_writer": test_writer,
    "style_checker": style_checker,
    "security_scanner": security_scanner,
}

_NODES = list(AGENTS)


def _make_node(name: str):
    def _node(state: MultiAgentState):
        return AGENTS[name].invoke(state)

    return _node


def route_after_agent(state: MultiAgentState):
    """Route to active_agent, or END if the agent finished without handoff."""
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
            return END
    return state.get("active_agent") or "triage_agent"


def route_initial(state: MultiAgentState):
    """Route to the active agent, defaulting to triage."""
    return state.get("active_agent") or "triage_agent"


builder = StateGraph(MultiAgentState)
for _name in _NODES:
    builder.add_node(_name, _make_node(_name))

builder.add_conditional_edges(START, route_initial, _NODES)
for _name in _NODES:
    builder.add_conditional_edges(_name, route_after_agent, _NODES + [END])

# Checkpointer persists conversation + active_agent across turns on a thread.
graph = builder.compile(checkpointer=InMemorySaver())


def main():
    print("Code Review Swarm (Handoffs)")
    print("Agents: Triage, Code Reviewer, Test Writer, Style Checker, Security Scanner")
    print("Type 'quit' to exit")
    print("-" * 60)

    # Same thread_id across the loop so state (history + active_agent) carries over.
    config = {"configurable": {"thread_id": "swarm-session-1"}}

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        print("\n[Swarm processing...]\n")

        result = graph.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        if result["messages"]:
            last_message = result["messages"][-1]
            content = getattr(last_message, "content", "")
            if content:
                print(f"\nFinal Response: {content}")


if __name__ == "__main__":
    main()
