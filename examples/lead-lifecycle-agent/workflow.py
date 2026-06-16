"""Lead-lifecycle LangGraph workflow.

Chains business logic across agents:
    START -> qualify (deep agent) -> route -> engage | nurture -> consolidate -> END

`graph` is the compiled, deployable workflow (see langgraph.json).

CLI:
    export ANTHROPIC_API_KEY=...
    python workflow.py --lead-id acme-jane --message "Hi, I'm Jane from acme.com, we need to cut report latency this quarter."
"""
from __future__ import annotations

import argparse
import os
from typing import Literal, Optional

from deepagents.backends.utils import create_file_data
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from config import MODEL
from engagement_agent import build_engagement_agent
from memory import LEADS_NS, lead_memory_path, make_store
from qualification_agent import build_qualification_agent

# One shared store for the process (InMemory, or Postgres/Supabase via DATABASE_URL).
store = make_store()


class WorkflowState(TypedDict):
    lead_id: str
    messages: Annotated[list, add_messages]
    qualification: Optional[dict]
    engagement: Optional[str]


def qualify_node(state: WorkflowState) -> dict:
    """Run the qualification deep agent and capture its structured verdict."""
    agent = build_qualification_agent(state["lead_id"], store)
    result = agent.invoke({"messages": state["messages"]})
    verdict = result.get("structured_response")
    return {
        "qualification": verdict.model_dump() if verdict is not None else None,
        "messages": result["messages"],
    }


def route(state: WorkflowState) -> Literal["engage", "nurture"]:
    q = state.get("qualification") or {}
    return "engage" if q.get("qualified") else "nurture"


def engage_node(state: WorkflowState) -> dict:
    """Engagement agent drafts outreach for a qualified lead."""
    q = state["qualification"]
    agent = build_engagement_agent()
    prompt = (
        f"Qualified lead.\nSummary: {q['summary']}\nNext action: {q['next_action']}\n"
        f"BANT: {q['bant']}\nDraft the outreach now."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return {"engagement": result["messages"][-1].content}


def nurture_node(state: WorkflowState) -> dict:
    """Minimal path for unqualified leads."""
    q = state.get("qualification") or {}
    return {
        "engagement": f"Not qualified (score {q.get('score', '?')}). "
        f"Tagged for nurture drip. Reason: {q.get('summary', 'n/a')}"
    }


def consolidate_node(state: WorkflowState) -> dict:
    """Learning loop: write durable lead facts + what worked to long-term memory."""
    model = init_chat_model(MODEL, temperature=0)
    convo = "\n".join(
        f"{getattr(m, 'type', 'msg')}: {getattr(m, 'content', '')}" for m in state["messages"]
    )
    notes = model.invoke(
        "Summarize durable facts about this lead and what worked, as concise markdown "
        "notes for the next conversation. Be specific and brief.\n\n"
        f"Conversation:\n{convo}\n\nQualification: {state.get('qualification')}"
    ).content
    text = notes if isinstance(notes, str) else str(notes)
    store.put(LEADS_NS, lead_memory_path(state["lead_id"]), create_file_data(text))
    return {}


def _build_graph():
    b = StateGraph(WorkflowState)
    b.add_node("qualify", qualify_node)
    b.add_node("engage", engage_node)
    b.add_node("nurture", nurture_node)
    b.add_node("consolidate", consolidate_node)
    b.add_edge(START, "qualify")
    b.add_conditional_edges("qualify", route, ["engage", "nurture"])
    b.add_edge("engage", "consolidate")
    b.add_edge("nurture", "consolidate")
    b.add_edge("consolidate", END)
    # Compile with the store so nested agent invokes (qualify) find it in runtime.
    return b.compile(store=store)


graph = _build_graph()


def main() -> None:
    parser = argparse.ArgumentParser(description="Lead-lifecycle workflow (CLI).")
    parser.add_argument("--lead-id", required=True, help="Stable id for this lead (memory key).")
    parser.add_argument("--message", required=True, help="The lead's inbound message.")
    args = parser.parse_args()

    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("DEEP_AGENT_MODEL")):
        raise SystemExit("Set ANTHROPIC_API_KEY (or DEEP_AGENT_MODEL) first.")

    result = graph.invoke(
        {"lead_id": args.lead_id, "messages": [{"role": "user", "content": args.message}]}
    )
    print("\n=== QUALIFICATION ===")
    print(result.get("qualification"))
    print("\n=== ENGAGEMENT ===")
    print(result.get("engagement"))


if __name__ == "__main__":
    main()
