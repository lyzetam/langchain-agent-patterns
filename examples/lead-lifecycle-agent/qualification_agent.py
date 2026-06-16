"""Lead-qualification Deep Agent.

Built per-lead so its memory points at that lead's file. Uses an on-disk skill
(BANT rubric), enrichment + reflection tools, persistent memory, and returns a
structured `Qualification`.
"""
from deepagents import create_deep_agent

from config import MODEL
from memory import lead_memory_path, memory_backend
from schemas import Qualification
from tools import lookup_company, think_tool

QUALIFY_PROMPT = """You are a senior SDR qualifying inbound leads.

Engage the lead, gather what you need, and qualify them. Follow the
`lead-qualification` skill for the BANT process and scoring. Always check the
lead's existing memory first so you don't repeat questions, and use `think_tool`
to reflect before producing your verdict.

When you have enough, return the structured Qualification verdict."""


def build_qualification_agent(lead_id: str, store):
    """Create a qualification deep agent bound to one lead's memory file."""
    return create_deep_agent(
        model=MODEL,
        tools=[lookup_company, think_tool],
        system_prompt=QUALIFY_PROMPT,
        skills=["./skills/"],
        backend=memory_backend,
        store=store,
        memory=[lead_memory_path(lead_id)],
        response_format=Qualification,
    )
