"""Tools for the lead-lifecycle agents. Enrichment/outreach are mocks — swap for real APIs."""
from langchain.tools import tool

# Mock firmographic data. Replace with a real enrichment provider (Apollo, Clearbit, ...).
_COMPANY_DB = {
    "acme.com": {"name": "Acme Corp", "employees": 1200, "industry": "Manufacturing", "tier": "enterprise"},
    "tinystartup.io": {"name": "Tiny Startup", "employees": 4, "industry": "SaaS", "tier": "smb"},
    "midco.com": {"name": "MidCo", "employees": 180, "industry": "Logistics", "tier": "mid-market"},
}


@tool
def lookup_company(domain: str) -> dict:
    """Look up firmographic info (size, industry, tier) for a company by its email domain.

    Args:
        domain: The company email domain, e.g. "acme.com".
    """
    # TODO: replace with a real enrichment API call.
    return _COMPANY_DB.get(
        domain, {"name": domain, "employees": "unknown", "industry": "unknown", "tier": "unknown"}
    )


@tool
def think_tool(reflection: str) -> str:
    """Record a strategic reflection on qualification progress before deciding next steps.

    Use after gathering information to analyze what you know, what's missing, and whether
    you have enough to qualify the lead. This is a deliberate reasoning pause.

    Args:
        reflection: Your analysis of findings, gaps, and the next step.
    """
    return f"Reflection recorded: {reflection}"


@tool
def draft_outreach(lead_name: str, channel: str, key_points: list[str]) -> str:
    """Draft (mock-send) a personalized outreach message to a qualified lead.

    Args:
        lead_name: The lead's name.
        channel: Outreach channel, e.g. "email" or "linkedin".
        key_points: Bullet points the message should hit.
    """
    # TODO: replace with a real send (email/SMS/CRM task).
    bullets = "\n".join(f"- {p}" for p in key_points)
    return f"[{channel}] drafted for {lead_name}:\n{bullets}"
