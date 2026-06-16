"""
Release Notes Deep Agent
========================
A self-contained, deployable Deep Agent (LangChain `deepagents`) that turns raw
git commit messages into house-style release notes.

Capabilities exercised:
  - Planning        : built-in `write_todos`
  - Custom tool     : `get_recent_commits` (bundled samples, or a real repo via --repo)
  - Skills          : on-demand `skills/release-notes/SKILL.md`, loaded from disk
                      via FilesystemBackend (no manual injection)

Deploy (LangGraph Platform / local):
    langgraph dev            # uses langgraph.json -> agent.py:agent

CLI:
    export ANTHROPIC_API_KEY=...                 # or DEEP_AGENT_MODEL=<provider:model>
    python agent.py                              # bundled sample commits
    python agent.py --repo /path/to/repo --version 1.2.0

Verified against deepagents 0.4.2 / langchain 1.2.x.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.tools import tool

BASE_DIR = Path(__file__).parent
MODEL = os.environ.get("DEEP_AGENT_MODEL", "anthropic:claude-sonnet-4-6")

# Set by main() when --repo is passed; None means use the bundled sample commits.
# (At deploy time main() doesn't run, so a deployed instance uses SAMPLE_COMMITS.)
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


@tool
def get_recent_commits() -> list[str]:
    """Return the conventional-commit messages since the last release."""
    if _REPO_PATH:
        out = subprocess.check_output(
            ["git", "-C", _REPO_PATH, "log", "--pretty=format:%s", "--reverse"],
            text=True,
        )
        return [line for line in out.splitlines() if line.strip()]
    return SAMPLE_COMMITS


def build_agent():
    """Build the deep agent. Skills load from ./skills/ via FilesystemBackend."""
    return create_deep_agent(
        model=MODEL,
        tools=[get_recent_commits],
        system_prompt=(
            "You are a release manager. When asked for release notes, first call "
            "get_recent_commits to gather the changes, then write the notes. "
            "Follow the team's release-notes skill for formatting."
        ),
        skills=["./skills/"],
        backend=FilesystemBackend(root_dir=str(BASE_DIR)),
    )


# Module-level graph for `langgraph dev` / LangGraph Platform (see langgraph.json).
agent = build_agent()


def main() -> None:
    global _REPO_PATH

    parser = argparse.ArgumentParser(
        description="Release-notes deep agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        metavar="PATH",
        help="Path to a git repo; reads its real commit log. Omit for bundled sample commits.",
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

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": f"Write the release notes for version {args.version}."}
            ]
        },
        config={"configurable": {"thread_id": "release-notes-demo"}},
    )

    final = result["messages"][-1].content
    print(final if isinstance(final, str) else str(final))


if __name__ == "__main__":
    main()
