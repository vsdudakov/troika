---
title: .troika/settings.json
description: The per-workspace path file — every key, how relative and absolute values resolve, and why it is the only thing that marks a workspace.
---

# `.troika/settings.json`

One file per folder-of-repos, written by [`/tr:setup`](commands.md). It is the only place
a path is declared, and the only thing that marks a directory as a workspace.

```json
{
  "profile": ".troika/PROFILE.md",
  "scratchpad": ".troika/scratchpad",
  "worktrees": ".troika/worktrees",
  "memory": ".troika/memory"
}
```

## The directory

```
<workspace>/
├── .troika/
│   ├── settings.json   the paths — committed
│   ├── PROFILE.md      the project profile — committed
│   ├── .gitignore      keeps the three below out of the workspace's history
│   ├── scratchpad/     plans, reviews, work logs, proofs
│   ├── worktrees/      one checkout per branch
│   └── memory/         dated observations
├── backend/
└── frontend/
```

Settings and profile are the workspace's shared contract and belong in its history. The three
state directories are per-person — uncommitted dev branches, half-finished plans, QA proofs —
and the `.gitignore` setup writes keeps them out of it.

## Keys

| Key | Exported as | Default | Holds |
| --- | --- | --- | --- |
| `profile` | `TROIKA_PROFILE` | `.troika/PROFILE.md` | the project profile |
| `scratchpad` | `TROIKA_SCRATCHPAD` | `.troika/scratchpad` | plans, reviews, work logs, proofs |
| `worktrees` | `TROIKA_WORKTREES` | `.troika/worktrees` | one checkout per branch |
| `memory` | `TROIKA_MEMORY` | `.troika/memory` | dated observations |

The workspace root itself is exported as `TROIKA_WORKSPACE`; it is the directory holding
`.troika/`, never declared inside it.

Every key is optional. An unknown key is an error rather than a silent no-op — a typo in a
path is exactly the mistake this file exists to prevent.

**Troika's own tree is not a key.** It is installed as a plugin, so the host says where it put
it — `${CLAUDE_PLUGIN_ROOT}` — and a workspace-declared second copy of that path could only
ever disagree with the host.

## Relative and absolute

Relative values resolve against the workspace root. **Absolute values are taken verbatim**,
which is how state lives outside the workspace:

```json
{
  "scratchpad": "/Volumes/fast/acme/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees"
}
```

`~` is expanded. Worth doing when the worktrees belong on a faster disk, or when the workspace
itself sits on a network mount a `git worktree` would crawl on.

Move them before a flow runs. Moving them after one has written strands its files where no
later role looks.

## When the file is absent

Nothing falls back. A directory with no `.troika/settings.json` above it is one nobody has run
setup in, and the resolver exits non-zero saying exactly that:

```
no workspace above /Users/me/acme/backend/src: expected a .troika/settings.json in it or in
an ancestor. Run /tr:setup in the folder that holds your repos.
```

That is a stop, not a default. The alternative — walking up to the first `AGENTS.md` — resolves
a *repo* as the workspace, because repos carry their own, and then scatters handoff files
through the code under review.

## Using it

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --init <dir>          # create .troika/ and stop
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"    # export, create state dirs
python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --json                # machine-readable
python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --from /some/path     # resolve as if standing there
```

`--init` is idempotent: it writes nothing that already exists, and says so.

## One per organisation

Run setup in every folder that holds a set of repos. A single installed plugin then serves all
of them — client work, employer, side project — each with its own profile, its own paths, and
no per-workspace install.
