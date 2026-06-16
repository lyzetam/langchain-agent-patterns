# Text-to-SQL Deep Agent

A natural-language → SQL agent built on LangChain's **Deep Agents** framework. Ask
questions in plain English and the agent explores the schema, writes SQL, runs it
against the **Chinook** SQLite database, and returns a formatted answer.

> Faithful MIT-licensed port of the official upstream example. See
> [`ATTRIBUTION.md`](./ATTRIBUTION.md). Upstream:
> [`langchain-ai/deepagents` → `examples/text-to-sql-agent`](https://github.com/langchain-ai/deepagents/tree/main/examples/text-to-sql-agent).

## What it does

- **Planning** — uses `write_todos` to break down complex analytical questions.
- **Skills (progressive disclosure)** — `skills/query-writing` and
  `skills/schema-exploration` load on demand; only their descriptions stay in
  context until the agent needs the full workflow.
- **Memory** — `AGENTS.md` is always loaded (identity, safety rules, read-only
  guardrails).
- **FilesystemBackend** — persistent file storage rooted at the agent folder for
  saving intermediate results.
- **SQL toolkit** — `sql_db_list_tables`, `sql_db_schema`, `sql_db_query`, and a
  query checker, scoped read-only (SELECT) by the agent instructions.

## Prerequisites

- Python 3.11+
- `ANTHROPIC_API_KEY` (get one at <https://console.anthropic.com/>)
- (Optional) LangSmith API key for tracing

## 1. Get the Chinook database

The DB is **not** committed (binary). Download it into this folder:

```bash
curl -L -o chinook.db https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
```

`agent.py` expects `chinook.db` to sit next to it.

## 2. Install

```bash
# Using uv (recommended)
uv venv --python 3.11
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv sync

# Or with pip
pip install -e .
```

## 3. Configure

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY (LangSmith/Tavily keys optional)
```

## 4. Run

```bash
python agent.py "What are the top 5 best-selling artists?"
python agent.py "Which employee generated the most revenue by country?"
python agent.py "How many customers are from Canada?"
```

Programmatic use:

```python
from agent import create_sql_deep_agent

agent = create_sql_deep_agent()
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What are the top 5 best-selling artists?"}]}
)
print(result["messages"][-1].content)
```

## Model note

The model id (`claude-sonnet-4-5-20250929` in `agent.py`) is **upstream's** and is
preserved verbatim. To use the LangChain provider-string form you can swap the
`ChatAnthropic(...)` model to `anthropic:claude-sonnet-4-6`.

## Resources

- [Deep Agents docs](https://docs.langchain.com/oss/python/deepagents/overview)
- [Chinook database](https://github.com/lerocha/chinook-database)
- [LangChain](https://www.langchain.com/)
