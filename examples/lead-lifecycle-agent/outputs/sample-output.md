# Sample output — `lead-lifecycle-agent`

Captured from a live run (`deepagents 0.4.2` / `langgraph 1.x`, `anthropic:claude-sonnet-4-6`,
default `InMemoryStore`). Model output varies run to run.

## RUN 1 — first contact (qualified lead)

Input:
```
lead_id: acme-jane
message: "Hi, I'm Jane, VP Eng at acme.com. We need to cut reporting latency this
          quarter and have budget approved."
```

`qualify` → structured `Qualification` (the typed hand-off to engagement):
```json
{
  "score": 88,
  "qualified": true,
  "summary": "Jane is VP of Engineering at Acme Corp, a 1,200-employee enterprise manufacturer — a strong authority with direct ownership over engineering tooling decisions. She has a concrete, urgent need (cut reporting latency this quarter) and states budget is already approved... a highly qualified lead.",
  "next_action": "Schedule a 30-minute technical discovery call this week to quantify current vs. target latency, data scale, and budget range — then fast-track to a tailored demo.",
  "bant": {
    "budget": "Self-reported as approved; specific range unknown — needs confirmation during discovery.",
    "authority": "VP of Engineering at a 1,200-person enterprise — strong decision-maker and likely budget owner.",
    "need": "Concrete pain: reduce reporting latency within the quarter. Depth still to be scoped.",
    "timeline": "This quarter — within ~90 days. High urgency, actively looking to act now."
  }
}
```

`route` → qualified → `engage` drafted a tailored email (mock send):
```
📧 Drafted Email — Jane, VP of Engineering, Acme Corp
Subject: Cutting Reporting Latency at Acme — 30 Min This Week?
...acknowledges her seniority + enterprise scale, names the specific pain, offers a
30-min technical discovery call with two time slots...
```

`consolidate` → wrote durable long-term memory to `/memories/acme-jane.md` (the learning loop):
```markdown
## Lead Notes — Jane / Acme Corp

**Contact:** Jane, VP Engineering — acme.com
**Company:** Acme Corp, 1,200 employees, enterprise manufacturing

### BANT
- **Budget:** Approved this quarter; exact range unknown
- **Authority:** VP Eng — strong decision-maker/budget owner
- **Need:** Reduce reporting latency; baseline/target/scale not yet scoped
- **Timeline:** This quarter (~90 days), high urgency

### Qualification
- **Score:** 88/100 — **Qualified** · Hot lead; fast-track priority

### Open Questions
- Current vs. target latency? Data volume/user scale?
- Budget range? Competing solutions being evaluated?

### Next Action
30-min technical discovery call this week → tailored demo

### What Worked
- `lookup_company(acme.com)` immediately enriched firmographic context (size, tier, industry)
- `think_tool` reflection before scoring prevented premature output and identified gaps cleanly
- Single-pass qualification with structured BANT output was sufficient; no back-and-forth needed
```

## RUN 2 — same lead, later (recall)

On a second call with the same `lead_id`, `qualify` loads `/memories/acme-jane.md`
before responding, so it skips re-asking known facts and builds on the prior verdict.

> Run it yourself: `python demo.py` (runs both turns in one process). With the default
> `InMemoryStore`, recall is visible within a single process; set `DATABASE_URL`
> (Supabase/Postgres) for recall across separate processes/deployments.
