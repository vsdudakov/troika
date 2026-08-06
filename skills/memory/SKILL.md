---
name: memory
description: Dated, provisional observations about the workspace — what happened, when, what it cost, and when an entry graduates into a rule or is deleted.
---

# Memory

**Kind** reference · **Used by** every role · **When** before planning or implementing, and after anything surprising · **Ends with** an entry read, written, promoted, or deleted

Dated, provisional observations about the workspace this tree is cloned into: what happened,
when, and what it cost. The directory is `$TROIKA_MEMORY` ([workspace paths](../../../AGENTS.md#workspace-paths)).

**Untracked, and per-workspace.** An observation about one organisation's CI or stack is
noise, or a leak, in another's. There is no index file for the same reason: list the
directory before planning or implementing.

```bash
ls "$TROIKA_MEMORY"/*.md
```

The directory may not exist yet in a fresh workspace — `python3 plugin/resolve.py --ensure`
creates it.

## What belongs here, and what does not

Prescriptive instructions belong elsewhere. Memory is for what has been *observed* and may
still expire.

| Destination | Use it for |
| --- | --- |
| [`AGENTS.md`](../../../AGENTS.md) | facts about this organisation: repos, commands, stack, tracker, voice |
| [`agents/`](../../ROLES.md) | one role's responsibilities and craft, true in any organisation |
| [`skills/`](../README.md) | ordered procedures, references, and templates, true in any organisation |
| `$TROIKA_MEMORY` | a newly observed fact that may expire and is not already documented |

Memory must not duplicate or contradict the prescriptive files. Check them before adding an
entry.

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

Use absolute dates. Add later observations in the body rather than overwriting the original
date.

## Lifecycle

- `active` — still relevant, provisional, and not yet a rule.
- `promoted` — moved to its permanent home: the workspace `AGENTS.md` when it is an
  organisation fact, or `agents/` / `skills/` when it turned out to be true everywhere; link
  that home from the entry.
- `stale` — no longer true, retained only when the obsolete belief is likely to recur.

Delete promoted or stale entries when their history no longer provides useful context.

## Gotchas

- **No index.** A role that reads one entry and stops has read one workspace's opinion of the
  whole. List the directory.
- **`git clean -xfd` deletes all of it.** The directory is ignored, and `-x` is precisely the
  flag that removes ignored files ([worktree › Gotchas](../worktree/SKILL.md)).
- **An entry is not a gate.** It can invalidate a plan ([plan-review](../plan-review/SKILL.md))
  or explain a failure, but no role treats one as a rule until it is promoted.
