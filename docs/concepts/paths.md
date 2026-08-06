---
title: Paths and the resolver
description: How a role standing deep inside a worktree finds the workspace that owns it, and why no procedure spells a path out.
---

# Paths and the resolver

Two things are true at once, and they are why paths are resolved rather than written down:

1. A role's cwd is **inside a worktree**, several levels below the workspace.
2. The tree itself may be an **installed plugin in a host's cache**, nowhere near the repos.

So neither end of a path can be assumed.

```bash
eval "$(python3 plugin/resolve.py --ensure)"
```

| Variable | Default | Holds |
| --- | --- | --- |
| `WS` | the directory found | the workspace root; repos are `$WS/<repo>` |
| `TROIKA_PROFILE` | `$WS/AGENTS.md` | the project profile |
| `TROIKA_HOME` | `$WS/troika` | the tree, when it is a clone rather than an install |
| `TROIKA_WORKTREES` | `$WS/troika/worktrees` | one checkout per branch |
| `TROIKA_SCRATCHPAD` | `$WS/troika/scratchpad` | plans, reviews, work logs, proofs |
| `TROIKA_MEMORY` | `$WS/troika/memory` | dated observations about this workspace |

`--ensure` creates the three the roles write into. They are ignored whole and never tracked,
so a fresh clone does not contain them.

## How the workspace is found

The resolver walks up from the current directory and takes the **first ancestor holding
`.troika.json`**. Failing that, it takes the first holding **both** `AGENTS.md` *and* a
`troika/` directory.

That second condition matters more than it looks. Repos carry their own `AGENTS.md` — a walk
that stopped at the first one found would resolve a *worktree* as the workspace and scatter
handoff files through the code under review.

If neither is found, the resolver exits non-zero with a diagnosis. **That is a stop, not a
default.** A guessed path writes proofs nobody reads.

## Why no procedure spells a path out

A workspace is allowed to move its state — onto a faster disk, outside the clone, into a
shared location. If a procedure said `$WS/troika/scratchpad`, `.troika.json` would be a lie
the moment anyone used it. So the structural gate fails any file that hardcodes one:

```
agents/qa.md: line 31: hardcoded path — use $TROIKA_HOME, $TROIKA_SCRATCHPAD,
$TROIKA_WORKTREES, $TROIKA_MEMORY, or $TROIKA_PROFILE
```

## One plugin, many workspaces

Because resolution happens at run time, one installed plugin serves every folder-of-repos on
the machine — a client, an employer, a side project — each with its own profile and its own
paths. There is nothing per-workspace in the install.

[.troika.json reference :material-arrow-right:](../reference/troika-json.md){ .md-button }
