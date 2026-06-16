# pip install -U deepagents langchain
"""
Deep Agent Sample App: Release Notes Writer
===========================================
A complete sample application built on LangChain's official Deep Agents framework
(`deepagents` / `create_deep_agent`). It turns raw git commit messages into
polished, house-style release notes.

This one app exercises the core deep-agent capabilities:
  - Planning        : the built-in `write_todos` tool breaks the task into steps
  - Custom tools    : `get_recent_commits` supplies the raw commit log
  - Skills          : an on-demand SKILL.md (skills/release-notes/) defines the
                      house format; the agent reads it only when relevant
  - Virtual FS      : the skill file is loaded into the agent's filesystem state

Run against the bundled sample commits:
    export ANTHROPIC_API_KEY=...            # or DEEP_AGENT_MODEL for another provider
    python deepagent_release_notes.py

Run against a real git repo:
    python deepagent_release_notes.py --repo /path/to/repo --version 1.2.0

Verified locally against deepagents 0.4.2 / langchain 1.2.x.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

MODEL = os.environ.get("DEEP_AGENT_MODEL", "anthropic:claude-sonnet-4-6")

# The skill lives next to this file as a real SKILL.md. The default (in-memory)
# backend can't read disk, so we load the file and inject it into the agent's
# virtual filesystem under /skills/ via the invoke `files` payload.
SKILLS_DIR = Path(__file__).parent / "skills"

# Set by main() when --repo is passed; None means use the bundled sample commits.
_REPO_PATH: str | None = None

SAMPLE_COMMITS = [
    "feat(auth): add passwordless email magic-link login",
    "feat(dashboard): show per-project token usage charts",
    "fix(api): correct timezone offset in scheduled-report timestamps",
    "fix(ui): stop the sidebar from collapsing on iPad landscape",
    "refactor(core): extract retry logic into a shared helper",
    "chore(deps): bump langgraph to the latest 1.x",
    "perf(search): cache embeddings to cut query latency ~40%",
]


def load_skill_files() -> dict[str, object]:
    """Read every SKILL.md under ./skills and map it to a virtual /skills/ path."""
    files: dict[str, object] = {}
    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        rel = skill_md.relative_to(SKILLS_DIR)
        virtual_path = f"/skills/{rel.as_posix()}"
        files[virtual_path] = create_file_data(skill_md.read_text())
    return files


# ============ Tools ============

@tool
def get_recent_commits() -> list[str]:
    """Return the conventional-commit messages since the last release."""
    if _REPO_PATH:
        # Real mode: read the actual commit log from the target repo.
        out = subprocess.check_output(
            ["git", "-C", _REPO_PATH, "log", "--pretty=format:%s", "--reverse"],
            text=True,
        )
        return [line for line in out.splitlines() if line.strip()]
    # Demo mode: bundled sample commits (no git required).
    return SAMPLE_COMMITS


# ============ Agent ============

def build_agent():
    return create_deep_agent(
        model=MODEL,
        tools=[get_recent_commits],
        system_prompt=(
            "You are a release manager. When asked for release notes, first call "
            "get_recent_commits to gather the changes, then write the notes. "
            "Follow the team's release-notes skill for formatting."
        ),
        skills=["/skills/"],
        checkpointer=InMemorySaver(),
    )


def main() -> None:
    global _REPO_PATH

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--repo",
        metavar="PATH",
        help="Path to a git repo; reads its real commit log. Omit to use bundled sample commits.",
    )
    parser.add_argument(
        "--version",
        default="2.4.0",
        help="Version label for the release notes (default: 2.4.0).",
    )
    args = parser.parse_args()
    _REPO_PATH = args.repo

    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("DEEP_AGENT_MODEL")):
        raise SystemExit(
            "Set ANTHROPIC_API_KEY (or DEEP_AGENT_MODEL for another provider) first."
        )

    agent = build_agent()
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": f"Write the release notes for version {args.version}."}
            ],
            "files": load_skill_files(),
        },
        config={"configurable": {"thread_id": "release-notes-demo"}},
    )

    final = result["messages"][-1].content
    print(final if isinstance(final, str) else str(final))


if __name__ == "__main__":
    main()
