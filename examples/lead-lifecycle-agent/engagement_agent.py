"""Engagement agent — acts on a qualified lead's verdict by drafting outreach."""
from langchain.agents import create_agent

from config import MODEL
from tools import draft_outreach

ENGAGE_PROMPT = """You are an engagement specialist. You receive a qualified lead's
summary and recommended next action. Draft a concise, personalized outreach using
the draft_outreach tool, hitting the lead's specific need and timeline. Then briefly
state what you sent and why."""


def build_engagement_agent():
    return create_agent(
        model=MODEL,
        tools=[draft_outreach],
        system_prompt=ENGAGE_PROMPT,
    )
