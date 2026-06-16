# Attribution

This folder is a faithful port of the official LangChain Deep Agents
**`deep_research`** example.

- **Upstream source:** [`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents) — `examples/deep_research/`
- **Pinned commit:** `a98f0dfa8d534d8a1885b524632400e52db22ac6`
- **License:** MIT License — Copyright (c) LangChain, Inc.

The code files (`agent.py`, `research_agent/__init__.py`, `research_agent/prompts.py`,
`research_agent/tools.py`) and the config/example files (`.env.example`,
`langgraph.json`, `pyproject.toml`) are reproduced verbatim from upstream. No
logic, prompts, or model identifiers were altered. **The model id
(`anthropic:claude-sonnet-4-5-20250929`) and the commented-out Gemini option are
upstream's** and were left exactly as published.

## Files omitted from this port

The following upstream files were intentionally not copied:

- `research_agent.ipynb` — Jupyter notebook walkthrough (large, not needed for deployment)
- `uv.lock` — lockfile (large; regenerate locally with `uv sync`)
- `utils.py` — Jupyter-display-only helpers (not used by the deployable agent)

## Locally added files

These two files are not part of the upstream example; they were written for this port:

- `ATTRIBUTION.md` (this file)
- `README.md` — a deploy-focused rewrite (the upstream README was replaced)

## Full MIT License (from upstream repo root `LICENSE`)

```
MIT License

Copyright (c) LangChain, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
