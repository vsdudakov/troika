---
title: .troika.json
description: The per-workspace path file — every key, how relative and absolute values resolve, and what happens when the file is absent.
---

# `.troika.json`

One file at the root of each folder-of-repos. It is the only place a path is declared.

```json
{
  "profile": "AGENTS.md",
  "home": "troika",
  "scratchpad": "troika/scratchpad",
  "worktrees": "troika/worktrees",
  "memory": "troika/memory"
}
```

## Keys

| Key | Exported as | Default | Holds |
| --- | --- | --- | --- |
| `profile` | `TROIKA_PROFILE` | `AGENTS.md` | the project profile |
| `home` | `TROIKA_HOME` | `troika` | the tree itself, when it is a clone |
| `scratchpad` | `TROIKA_SCRATCHPAD` | `troika/scratchpad` | plans, reviews, work logs, proofs |
| `worktrees` | `TROIKA_WORKTREES` | `troika/worktrees` | one checkout per branch |
| `memory` | `TROIKA_MEMORY` | `troika/memory` | dated observations |

The workspace root itself is exported as `WS`; it is the directory holding the file, never
declared inside it.

Every key is optional. An unknown key is an error rather than a silent no-op — a typo in a
path is exactly the mistake this file exists to prevent.

## Relative and absolute

Relative values resolve against the file's own directory. **Absolute values are taken
verbatim**, which is how state lives outside the workspace:

```json
{
  "scratchpad": "/Volumes/fast/acme/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees"
}
```

`~` is expanded. That matters when the tree is an installed plugin in a host's cache: the
cache cannot hold your worktrees, so point them somewhere real.

## When the file is absent

The resolver falls back to the nearest ancestor holding **both** `AGENTS.md` and a `troika/`
directory, with the defaults above — so a plain clone works with no file at all.

It requires both because repos carry their own `AGENTS.md`; stopping at the first one found
would resolve a worktree as the workspace.

## Using it

```bash
eval "$(python3 troika/plugin/resolve.py --ensure)"   # export, and create the state dirs
python3 troika/plugin/resolve.py --json              # machine-readable
python3 troika/plugin/resolve.py --from /some/path   # resolve as if standing there
```

A non-zero exit means no workspace was found above the starting directory. That is a stop, not
a default.

## One per organisation

Write one in every folder that holds a set of repos. A single installed plugin then serves all
of them — client work, employer, side project — each with its own profile, its own paths, and
no per-workspace install.
