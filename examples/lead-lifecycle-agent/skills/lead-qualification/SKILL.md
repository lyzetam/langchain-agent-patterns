---
name: lead-qualification
description: How to qualify an inbound lead using BANT and produce a fit score. Use whenever assessing, scoring, or qualifying a lead.
---

# lead-qualification

Qualify the lead using **BANT**, then produce a 0–100 fit score and a clear next action.

## Process
1. Read any existing memory about this lead first; don't re-ask what you already know.
2. If the lead gives a company/email domain, call `lookup_company` to enrich (size, industry, tier).
3. Assess each BANT dimension from the conversation + enrichment:
   - **Budget** — can they afford / do they have spend authority?
   - **Authority** — are they a decision-maker or influencer?
   - **Need** — is there a concrete, urgent problem we solve?
   - **Timeline** — are they acting soon (≤ 90 days) or just browsing?
4. Use `think_tool` to reflect before deciding: what do I know, what's missing, do I have enough to score?

## Scoring rubric (0–100)
- Each BANT dimension contributes up to 25 points.
- **qualified = true** when score ≥ 60 AND there is at least some Authority and Need.
- Enterprise/mid-market tier with a clear near-term need should score higher; SMB tire-kickers lower.

## Output
Return the structured verdict: `score`, `qualified`, a 2–3 sentence `summary`, the single
best `next_action`, and the `bant` breakdown. Keep the summary tight and decision-useful.
