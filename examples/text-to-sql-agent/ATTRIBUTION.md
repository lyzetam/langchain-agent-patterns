# Attribution

This folder is a faithful port of the official LangChain Deep Agents example
**`text-to-sql-agent`**.

- **Upstream:** [`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents)
- **Source path:** `examples/text-to-sql-agent/`
- **Commit (pinned):** `a98f0dfa8d534d8a1885b524632400e52db22ac6`
- **License:** MIT — Copyright (c) LangChain, Inc.

## Fidelity

The following files are reproduced **byte-for-byte** from upstream:

- `agent.py`
- `AGENTS.md`
- `.env.example`
- `pyproject.toml`
- `skills/query-writing/SKILL.md`
- `skills/schema-exploration/SKILL.md`

Model identifiers (e.g. `claude-sonnet-4-5-20250929` in `agent.py`) are **upstream's
own** and were intentionally left unchanged.

## Files omitted from this port

- `uv.lock` — large generated lockfile (regenerate locally with `uv sync`)
- `text-to-sql-langsmith-trace.png` — binary image asset
- `chinook.db` — binary SQLite sample database; **not committed**. See `README.md`
  for the download command.

## Files added in this port (not from upstream)

- `README.md` — deploy-focused readme for this standalone folder
- `ATTRIBUTION.md` — this file
- `.gitignore` — ignores `chinook.db`, `.env`, and Python artifacts

---

## License

The upstream project is MIT-licensed. The full license text from the root of
`langchain-ai/deepagents` (at the pinned commit) is reproduced below.

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
