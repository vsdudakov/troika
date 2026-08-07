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
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
```

| Variable | Default | Holds |
| --- | --- | --- |
| `TROIKA_WORKSPACE` | the directory found | the workspace root; repos are `$TROIKA_WORKSPACE/<repo>` |
| `TROIKA_PROFILE` | `.troika/PROFILE.md` | the project profile |
| `TROIKA_WORKTREES` | `.troika/worktrees` | one checkout per branch |
| `TROIKA_SCRATCHPAD` | `.troika/scratchpad` | plans, reviews, work logs, proofs |
| `TROIKA_MEMORY` | `.troika/memory` | dated observations about this workspace |

`--ensure` creates the three the roles write into. They are ignored by the `.gitignore` setup
writes, so they never reach the workspace's history.

Troika's own tree is deliberately absent from that list. It is installed as a plugin, so the
host says where it put it — `${CLAUDE_PLUGIN_ROOT}` — and a workspace-declared second copy of
that path could only ever disagree with the host.

## How the workspace is found

The resolver walks up from the current directory and takes the **first ancestor holding
`.troika/settings.json`**. That file is the only marker, and nothing falls back.

The rejected alternative is worth stating, because it looks reasonable: walking up to the first
`AGENTS.md`. Repos carry their own, so that walk resolves a *worktree* as the workspace and
scatters handoff files through the code under review.

If no marker is found, the resolver exits non-zero with the fix:

```
no workspace above /Users/me/acme/backend/src: expected a .troika/settings.json in it or in
an ancestor. Run /tr:setup in the folder that holds your repos.
```

**That is a stop, not a default.** A guessed path writes proofs nobody reads.

## Why no procedure spells a path out

A workspace is allowed to move its state — onto a faster disk, outside the workspace, into a
shared location. If a procedure said `$TROIKA_WORKSPACE/.troika/scratchpad`, `settings.json`
would be a lie the moment anyone used it. So the structural gate fails any file that hardcodes
one:

```
agents/qa.md: line 31: hardcoded path — use $TROIKA_SCRATCHPAD,
$TROIKA_WORKTREES, $TROIKA_MEMORY, or $TROIKA_PROFILE
```

## One plugin, many workspaces

Because resolution happens at run time, one installed plugin serves every folder-of-repos on
the machine — a client, an employer, a side project — each with its own profile and its own
paths. There is nothing per-workspace in the install; `/tr:setup` is what makes a folder
one.

[settings.json reference :material-arrow-right:](../reference/settings-json.md){ .md-button }
