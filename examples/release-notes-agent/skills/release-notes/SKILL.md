---
name: release-notes
description: House style for writing release notes and changelogs from raw commit logs. Use whenever asked to write release notes, a changelog, or to summarize commits for end users.
---

# release-notes

Produce release notes in the team's house style. Format the output EXACTLY like this:

## 🚀 Release <version>

**Added**
- <user-facing description>

**Fixed**
- <user-facing description>

**Changed**
- <user-facing description>

Rules:
- Group each commit by its conventional-commit prefix: `feat:` → **Added**, `fix:` → **Fixed**, `refactor:` / `chore:` / `perf:` → **Changed**.
- Rewrite every line in clear, user-facing language. Do NOT include commit hashes, scopes, or the raw `feat:` / `fix:` prefixes.
- Omit any section that has no items.
- Keep each bullet to a single line.
