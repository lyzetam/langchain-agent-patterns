# Design — Lead Lifecycle Agent

A deployable LangGraph workflow that chains business logic across two agents: a
**lead-qualification Deep Agent** (remembers each lead across conversations) and an
**engagement agent** that acts on the structured verdict.

## Workflow

```
WorkflowState: { lead_id, messages, qualification?, engagement? }

START → qualify ──route──► engage ──► consolidate → END
                     └────► nurture ─►┘
```

- **qualify** — `create_deep_agent`; reads the lead's long-term memory, assesses with
  a BANT skill + `lookup_company`/`think_tool`, emits a structured `Qualification`.
- **route** — conditional edge on `qualification.qualified`.
- **engage** — `create_agent`; drafts outreach for qualified leads.
- **nurture** — minimal node for unqualified leads.
- **consolidate** — learning loop: summarizes durable lead facts + what worked and
  writes them to per-lead long-term memory (closed when `qualify` reads it next run).

## Requirement mapping

| Requirement | How |
|-------------|-----|
| Deep agent | `qualify` = `create_deep_agent` |
| Tools | `lookup_company` (enrichment), `draft_outreach`, `think_tool` |
| Memory | `CompositeBackend(default=FilesystemBackend, routes={"/memories/": StoreBackend(ns=("leads",))})`; per-lead file `/memories/{lead_id}.md`; `InMemoryStore` default, Supabase Postgres via `DATABASE_URL` |
| Learning loop | `think_tool` (in-convo) + `consolidate` node (cross-convo store write) |
| Skills | `skills/lead-qualification/SKILL.md` (BANT rubric), on-demand from disk |
| Workflow chaining | the `StateGraph`: qualifier → router → engagement, typed `Qualification` handoff |
| Container deploy | `langgraph.json` exposes `workflow.py:graph`; `Dockerfile` builds a servable image |

## Files (flat, for robust import under langgraph)

```
lead-lifecycle-agent/
├── config.py              # MODEL, BASE_DIR
├── schemas.py            # Pydantic Qualification / BANT
├── tools.py              # lookup_company, think_tool, draft_outreach
├── memory.py             # store factory + composite backend + per-lead path
├── qualification_agent.py
├── engagement_agent.py
├── workflow.py           # StateGraph (compiled `graph`)
├── skills/lead-qualification/SKILL.md
├── langgraph.json · Dockerfile · pyproject.toml · .env.example · README.md
```

## Scope guards (YAGNI)
`nurture` is minimal; `lookup_company`/`draft_outreach` are mock tools (no external
services); Supabase is opt-in. Verified locally on `deepagents 0.4.2` /
`langgraph 1.x` with `InMemoryStore`.
