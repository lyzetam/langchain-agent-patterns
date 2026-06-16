# Release Notes Agent

A self-contained, deployable **Deep Agent** (LangChain `deepagents`) that turns a raw git commit log into house-style release notes.

It exercises the core deep-agent capabilities: built-in **planning** (`write_todos`), a **custom tool** (`get_recent_commits`), and an on-demand **skill** (`skills/release-notes/SKILL.md`) loaded from disk via `FilesystemBackend`.

## Layout

```
release-notes-agent/
├── agent.py                       # the agent (module-level `agent` + CLI)
├── langgraph.json                 # deploy manifest -> agent.py:agent
├── pyproject.toml                 # dependencies
├── .env.example                   # copy to .env
├── skills/release-notes/SKILL.md  # on-demand house-style skill
└── outputs/sample-output.md       # captured sample output
```

## Prerequisites

- Python 3.11+
- `ANTHROPIC_API_KEY` (or set `DEEP_AGENT_MODEL` to another `provider:model`)

## Install

```bash
uv sync           # or: pip install -e .
cp .env.example .env   # then add your key
```

## Run (CLI)

```bash
export ANTHROPIC_API_KEY=...
python agent.py                                   # bundled sample commits
python agent.py --repo /path/to/repo --version 1.2.0   # real git log
```

## Deploy (LangGraph Platform / local)

```bash
langgraph dev     # serves the `release_notes` graph from langgraph.json
```

`langgraph.json` exposes `agent.py:agent`. A deployed instance uses the bundled
sample commits (the `--repo` flag is a CLI convenience; `main()` doesn't run when
served).

## Notes

- Default model is `anthropic:claude-sonnet-4-6`; override with `DEEP_AGENT_MODEL`.
- The house format lives entirely in `skills/release-notes/SKILL.md` — edit it to
  change the output style; no code change needed.
- See [`outputs/sample-output.md`](outputs/sample-output.md) for example output.
