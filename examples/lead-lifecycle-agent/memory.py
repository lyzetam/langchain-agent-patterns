"""Long-term, per-lead memory.

Memory files live under /memories/{lead_id}.md in a LangGraph Store:
  - InMemoryStore by default (runs with no external setup)
  - Supabase / Postgres when DATABASE_URL is set (requires langgraph-checkpoint-postgres)

Skills and scratch files are served from disk via FilesystemBackend so the agent can
read ./skills/ ; only the /memories/ route is persisted in the Store.
"""
import os

from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

from config import BASE_DIR

# All leads share one store namespace; the lead is distinguished by the file path.
LEADS_NS = ("leads",)


def make_store():
    """Return a LangGraph Store: Postgres (Supabase) if DATABASE_URL is set, else in-memory."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        try:
            from langgraph.store.postgres import PostgresStore

            # NOTE: API varies by langgraph-checkpoint-postgres version; adapt as needed.
            store = PostgresStore.from_conn_string(db_url)
            store.setup()
            return store
        except Exception as exc:  # pragma: no cover - depends on external service
            print(f"[memory] Postgres unavailable ({exc}); falling back to InMemoryStore")
    return InMemoryStore()


def memory_backend(rt):
    """Composite backend: disk for skills/scratch, Store for persistent /memories/."""
    return CompositeBackend(
        default=FilesystemBackend(root_dir=str(BASE_DIR)),
        routes={"/memories/": StoreBackend(rt, namespace=lambda _ctx: LEADS_NS)},
    )


def lead_memory_path(lead_id: str) -> str:
    """Per-lead memory file path (the Store key under LEADS_NS)."""
    return f"/memories/{lead_id}.md"
