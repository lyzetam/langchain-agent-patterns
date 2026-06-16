# Sample output — `release-notes-agent`

Captured from live runs against `deepagents 0.4.2` / `langchain 1.2.x` with
`model="anthropic:claude-sonnet-4-6"`. Model output varies run to run; these are
representative.

---

## Mode 1 — bundled sample commits

```bash
export ANTHROPIC_API_KEY=...
python agent.py
```

The agent calls `get_recent_commits` (returns the bundled `SAMPLE_COMMITS`), reads the
on-demand `skills/release-notes/SKILL.md`, and writes:

```text
## 🚀 Release 2.4.0

**Added**
- Sign in instantly with a passwordless magic link sent to your email — no password required.
- View per-project token usage charts directly from the dashboard.

**Fixed**
- Scheduled report timestamps now reflect the correct timezone offset.
- The sidebar no longer collapses unexpectedly on iPad in landscape orientation.

**Changed**
- Search queries are now significantly faster thanks to embedding caching, reducing latency by ~40%.
- Retry logic has been consolidated into a shared helper for improved reliability across the app.
- Upgraded LangGraph to the latest 1.x release.
```

Note how the skill drives the format: the `🚀 Release` header, the
Added/Fixed/Changed grouping by conventional-commit prefix (`feat:`→Added,
`fix:`→Fixed, `refactor:`/`chore:`/`perf:`→Changed), and the user-facing rewrites
that drop the raw `feat:`/scope prefixes.

---

## Mode 2 — against a real repo (`--repo`)

```bash
python agent.py --repo /path/to/repo --version 0.1.0
```

Run against this repository's actual two-commit history
(`chore: initial commit …`, `feat: add Deep Agents sample app …`):

```text
## 🚀 Release 0.1.0

**Added**
- Introduced LangChain/LangGraph agent examples and supporting documentation.
- Added the Deep Agents sample app, including a release-notes writer, along with refreshed documentation.
```

With only two commits there's nothing to put under **Fixed** or **Changed**, and
the skill says to omit empty sections — so only **Added** appears. (The model
filed the `chore:` initial commit under Added rather than Changed; an initial
commit reasonably reads as "introducing" everything. A richer history with
`fix:`/`refactor:` commits populates all three sections, as in Mode 1.)
