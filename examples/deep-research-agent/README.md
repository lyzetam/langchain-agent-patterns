# Deep Research Agent

A deployable port of LangChain's official **Deep Agents `deep_research`** example.
It performs multi-step web research and produces a comprehensive, citation-backed
report.

## What it does

An **orchestrator** agent plans the work (a TODO list), saves the research request,
then delegates focused topics to one or more parallel **`research-agent`**
subagents. Each subagent runs a tool-calling loop over:

- **`tavily_search`** — discovers URLs via Tavily and fetches full webpage content as markdown.
- **`think_tool`** — a reflection step used after each search to assess findings, gaps, and next steps.

The orchestrator consolidates citations across all subagent findings and writes a
final report to `/final_report.md` (in the agent's virtual filesystem). Parallelism
is bounded (default: up to 3 concurrent subagents, 3 delegation rounds) — see the
limits at the top of `agent.py`.

## Prerequisites

- Python **3.11+**
- `ANTHROPIC_API_KEY` — for the Claude model
- `TAVILY_API_KEY` — for web search
- (For `langgraph dev` local server) `LANGSMITH_API_KEY`

Copy `.env.example` to `.env` and fill in your keys.

## Install

```bash
# with uv (recommended)
uv sync

# or with pip
pip install -e .
```

## Run locally

A `langgraph.json` is included, so run the LangGraph dev server:

```bash
langgraph dev
```

This serves the `research` graph (defined as `./agent.py:agent`) with a local
inspector UI. The same project deploys unchanged to **LangGraph Platform**.

## Model

The model id is upstream's — **`claude-sonnet-4-5`** (`anthropic:claude-sonnet-4-5-20250929`).
You can swap it to `anthropic:claude-sonnet-4-6` in `agent.py` if desired. A
commented-out Gemini option is also present upstream.

## Source & license

Faithful MIT-licensed port of
[`langchain-ai/deepagents` · `examples/deep_research/`](https://github.com/langchain-ai/deepagents/tree/a98f0dfa8d534d8a1885b524632400e52db22ac6/examples/deep_research)
(commit `a98f0dfa8d534d8a1885b524632400e52db22ac6`). See [`ATTRIBUTION.md`](./ATTRIBUTION.md)
for the full license, omitted files, and details.
