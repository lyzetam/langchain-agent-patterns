"""Structured handoff between the qualification and engagement agents."""
from pydantic import BaseModel, Field


class BANT(BaseModel):
    """Classic BANT qualification dimensions, each a short free-text assessment."""
    budget: str = Field(description="What we know about the lead's budget/spend ability")
    authority: str = Field(description="Is this person a decision-maker / influencer?")
    need: str = Field(description="The concrete problem the lead is trying to solve")
    timeline: str = Field(description="How soon they intend to act")


class Qualification(BaseModel):
    """The qualifier's verdict — consumed by the engagement node."""
    score: int = Field(ge=0, le=100, description="Overall fit score, 0-100")
    qualified: bool = Field(description="True if the lead should be engaged now")
    summary: str = Field(description="2-3 sentence summary of the lead and rationale")
    next_action: str = Field(description="The single recommended next step")
    bant: BANT
