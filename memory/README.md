# Memory

Dated, provisional observations about the workspace this harness is cloned into: what happened, when, and what it cost.

**Gitignored.** Only this README is tracked. Memory is per-workspace — an observation about one organisation's CI or stack is noise, or a leak, in another's. There is no index file for the same reason: read the entries by listing this directory (`ls llm/memory/*.md`) before planning or implementing.

Prescriptive instructions belong elsewhere:

| Destination | Use it for |
| --- | --- |
| [`../../AGENTS.md`](../../AGENTS.md) | Facts about this organisation: repos, commands, stack, tracker, voice |
| [`../agents/`](../agents/README.md) | One role's responsibilities and craft, true in any organisation |
| [`../skills/`](../skills/README.md) | Ordered procedures, references, and templates, true in any organisation |
| `memory/` | A newly observed fact that may expire and is not already documented |

Memory must not duplicate or contradict the prescriptive files. Check them before adding an entry.

## Add an entry

One file per observation, named `<slug>.md`:

```markdown
---
name: <slug matching the filename>
description: <one-line description>
observed: <YYYY-MM-DD>
status: active
---

<Exact observation, including commands and error messages when useful.>

**Cost:** <what failed or how much time it consumed>
**How to apply:** <what to do differently next time>
```

Use absolute dates. Add later observations in the body rather than overwriting the original date.

## Lifecycle

- `active` — still relevant, provisional, and not yet a rule.
- `promoted` — moved to its permanent home: the workspace `AGENTS.md` when it is an organisation fact, or `agents/` / `skills/` when it turned out to be true everywhere; link that home from the entry.
- `stale` — no longer true, retained only when the obsolete belief is likely to recur.

Delete promoted or stale entries when their history no longer provides useful context.
