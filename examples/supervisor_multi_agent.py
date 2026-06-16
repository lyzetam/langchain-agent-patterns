# pip install -U langchain "langchain[anthropic]" langgraph
"""
Supervisor Multi-Agent Example
==============================
A coordinator agent that delegates to specialized subagents for travel planning.

Pattern: Subagents (agent-as-tool). Replaces the deprecated langgraph_supervisor API.

The main coordinator agent decides which specialist to invoke and combines their
results. Each specialist is a `create_agent` instance, exposed to the coordinator
through a single parameterized `task` tool backed by a subagent registry.
"""

from langchain.agents import create_agent
from langchain.tools import tool


# ============ Tools ============

@tool
def search_flights(from_airport: str, to_airport: str, date: str) -> str:
    """Search for flights between airports on a specific date."""
    return f"Found 3 flights from {from_airport} to {to_airport} on {date}"


@tool
def book_flight(from_airport: str, to_airport: str, flight_id: str) -> str:
    """Book a flight."""
    return f"Successfully booked flight {flight_id} from {from_airport} to {to_airport}"


@tool
def search_hotels(location: str, check_in: str, check_out: str) -> str:
    """Search for hotels in a location."""
    return f"Found 5 hotels in {location} for {check_in} to {check_out}"


@tool
def book_hotel(hotel_name: str, check_in: str, check_out: str) -> str:
    """Book a hotel."""
    return f"Successfully booked {hotel_name} from {check_in} to {check_out}"


@tool
def calculate_expense(amounts: str) -> str:
    """Calculate total expenses from a comma-separated list."""
    total = sum(float(x.strip()) for x in amounts.split(","))
    return f"Total expense: ${total:.2f}"


# ============ Specialized Subagents ============

flight_agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search_flights, book_flight],
    system_prompt="""You are a flight booking specialist.

Your tasks:
- Search for flights when users want to travel
- Book flights when users confirm
- Provide flight details clearly
- Always confirm booking details before proceeding""",
)

hotel_agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search_hotels, book_hotel],
    system_prompt="""You are a hotel booking specialist.

Your tasks:
- Search for hotels when users need accommodation
- Book hotels when users confirm
- Provide hotel details clearly
- Always confirm booking details before proceeding""",
)

expense_agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[calculate_expense],
    system_prompt="""You are an expense calculation specialist.

Your tasks:
- Calculate total expenses from provided amounts
- Help with budgeting for trips
- Provide clear breakdowns of costs""",
)


# ============ Subagent Registry + Dispatch Tool ============

SUBAGENTS = {
    "flight_specialist": flight_agent,
    "hotel_specialist": hotel_agent,
    "expense_specialist": expense_agent,
}


@tool
def task(agent_name: str, description: str) -> str:
    """Launch an ephemeral subagent for a task.

    Available agents:
    - flight_specialist: Flight searches and bookings
    - hotel_specialist: Hotel searches and bookings
    - expense_specialist: Expense calculations and budgeting

    Args:
        agent_name: Which subagent to invoke (one of the names above).
        description: The full task description / request for that subagent.
    """
    agent = SUBAGENTS.get(agent_name)
    if agent is None:
        return f"Unknown agent '{agent_name}'. Available: {', '.join(SUBAGENTS)}"
    result = agent.invoke({"messages": [{"role": "user", "content": description}]})
    return result["messages"][-1].content


# ============ Coordinator ============

coordinator = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[task],
    system_prompt="""You are a travel planning coordinator managing three specialists:

1. flight_specialist - Handles flight searches and bookings
2. hotel_specialist - Handles hotel searches and bookings
3. expense_specialist - Handles expense calculations and budgeting

Your job:
- Analyze user requests and delegate to the appropriate specialist via the task tool
- If multiple specialists are needed, coordinate them sequentially
- Summarize results from specialists for the user
- Ensure all booking details are confirmed before proceeding

Route requests based on:
- Flights/airports -> flight_specialist
- Hotels/accommodation -> hotel_specialist
- Costs/budgets/expenses -> expense_specialist""",
)


def main():
    print("Travel Planning Multi-Agent System")
    print("Agents: Flight Specialist, Hotel Specialist, Expense Specialist")
    print("Type 'quit' to exit")
    print("-" * 60)

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        print("\n[Coordinator delegating...]\n")

        # Stream coordinator updates (one entry per node step).
        for chunk in coordinator.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode="updates",
        ):
            for node, update in chunk.items():
                messages = update.get("messages", []) if isinstance(update, dict) else []
                for msg in messages:
                    content = getattr(msg, "content", None)
                    if content:
                        print(f"[{node}] {getattr(msg, 'type', 'message')}: {content}")

        print("\n[Task completed]")


if __name__ == "__main__":
    main()
