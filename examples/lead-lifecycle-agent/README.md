# Lead Lifecycle Agent

A deployable **LangGraph workflow** that chains business logic across two agents:

1. a **lead-qualification Deep Agent** that assesses an inbound lead (BANT skill +
   enrichment + reflection) and **remembers each lead across conversations**, then
2. an **engagement agent** that acts on the structured verdict.

It demonstrates: a Deep Agent, tools, long-term memory, a learning loop, skills, and
multi-agent workflow chaining — in one deployable container.

## Workflow

```
WorkflowState: { lead_id, messages, qualification?, engagement? }

START → qualify (deep agent) ──route──► engage ──► consolidate → END
                                  └────► nurture ─►┘
```

- **qualify** — `create_deep_agent`; reads the lead's memory, runs the BANT skill, uses
  `lookup_company` + `think_tool`, returns a structured `Qualification`.
- **route** — branches on `qualification.qualified`.
- **engage** — `create_agent`; drafts outreach for qualified leads.
- **nurture** — minimal path for unqualified leads.
- **consolidate** — learning loop: writes durable lead facts + what worked to long-term
  memory, so the next conversation with that lead starts smarter.

## Layout

```
lead-lifecycle-agent/
├── workflow.py            # the StateGraph (compiled `graph`, deployed)
├── qualification_agent.py # the deep agent (tools + skill + memory + response_format)
├── engagement_agent.py    # the engagement create_agent
├── tools.py               # lookup_company, think_tool, draft_outreach (mocks)
├── schemas.py             # Pydantic Qualification / BANT (structured handoff)
├── memory.py              # store factory + composite backend + per-lead path
├── config.py              # MODEL, BASE_DIR
├── demo.py                # two-turn learning-loop demo
├── skills/lead-qualification/SKILL.md
└── langgraph.json · Dockerfile · pyproject.toml · .env.example
```

## Prerequisites
- Python 3.11+
- `ANTHROPIC_API_KEY` (or `DEEP_AGENT_MODEL` for another provider)

## Install & run (CLI)
```bash
pip install -e .            # or: uv sync
cp .env.example .env        # add your key
python workflow.py --lead-id acme-jane \
  --message "Hi, I'm Jane, VP Eng at acme.com. We need to cut reporting latency this quarter, budget approved."
```

## Learning-loop demo
```bash
python demo.py             # runs the same lead twice in one process; run 2 recalls run 1
```
See [`outputs/sample-output.md`](outputs/sample-output.md) for a captured run.

## Memory (InMemory → Supabase/Postgres)
- **Default:** `InMemoryStore` — process-local. The learning loop is visible within one
  process (e.g. `demo.py`), but separate CLI invocations don't share memory.
- **Persistent:** set `DATABASE_URL` and `pip install -e ".[postgres]"` to use Supabase /
  Postgres. Memory then persists across processes, so the CLI alone shows recall.

Memory is namespaced per lead: `/memories/{lead_id}.md` in the Store; skills/scratch are
served from disk via `FilesystemBackend`.

## Deploy (container)
```bash
docker build -t lead-lifecycle-agent .
docker run --rm -p 8000:8000 --env-file .env lead-lifecycle-agent
```
`langgraph.json` exposes `workflow.py:graph` as the `lead_lifecycle` graph; the container
serves it over the LangGraph API. Use a managed Postgres (Supabase) `DATABASE_URL` for
durable memory in production.

## Chaining into your own systems
`workflow.py:graph` is a standard compiled LangGraph graph — invoke it as a node inside a
larger graph, or call `graph.invoke({...})` from any service. The `Qualification` schema is
the contract for the hand-off to engagement (or your CRM).

## Notes
- `lookup_company` / `draft_outreach` are mocks (marked `# TODO`) — swap for real
  enrichment / send.
- Default model `anthropic:claude-sonnet-4-6`; override with `DEEP_AGENT_MODEL`.
