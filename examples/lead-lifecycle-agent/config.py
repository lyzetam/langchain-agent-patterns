"""Shared config."""
import os
from pathlib import Path

# Default model; override with DEEP_AGENT_MODEL (provider:model) env var.
MODEL = os.environ.get("DEEP_AGENT_MODEL", "anthropic:claude-sonnet-4-6")

# Folder root — used by FilesystemBackend so the agent can read ./skills/ from disk.
BASE_DIR = Path(__file__).parent
