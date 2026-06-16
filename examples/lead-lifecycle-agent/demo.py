"""Demo: run the workflow twice for the same lead (one process) to show the learning loop.

With the default InMemoryStore, memory persists only within a single process — so this
script demonstrates recall by running both turns here. With DATABASE_URL (Supabase/Postgres)
set, memory persists across processes and the CLI alone shows recall.

    export ANTHROPIC_API_KEY=...
    python demo.py
"""
from memory import LEADS_NS, lead_memory_path
from workflow import graph, store

LEAD = "acme-jane"


def run(message: str, label: str) -> dict:
    print(f"\n========== {label} ==========")
    result = graph.invoke(
        {"lead_id": LEAD, "messages": [{"role": "user", "content": message}]}
    )
    print("QUALIFICATION:", result.get("qualification"))
    eng = result.get("engagement") or ""
    print("ENGAGEMENT:", eng[:300].replace("\n", " "), "...")
    return result


if __name__ == "__main__":
    run(
        "Hi, I'm Jane, VP Eng at acme.com. We need to cut reporting latency this "
        "quarter and have budget approved.",
        "RUN 1 — first contact",
    )

    item = store.get(LEADS_NS, lead_memory_path(LEAD))
    print("\n--- LONG-TERM MEMORY written by consolidate ---")
    print(item.value.get("content") if item else "(none)")

    run(
        "Jane here, following up. Anything I should know based on our last conversation?",
        "RUN 2 — same lead, later (should recall prior context)",
    )
