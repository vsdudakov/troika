---
title: Set up a workspace
description: A workspace is the folder holding your repos. It needs an AGENTS.md profile and a .troika.json — what goes in each, and why.
---

# Set up a workspace

A **workspace** is the folder that holds your repos. Troika needs two files in it.

```
<workspace>/
  AGENTS.md      the project profile — what your codebase is
  .troika.json   where this workspace keeps its files
  troika/        the clone, if you are not using the plugin
  backend/       your repos, each an independent clone
  frontend/
```

Both files are yours: they stay in your workspace, never in the Troika repository. That
separation is the whole design — [the repo is organisation-neutral](../guides/profile.md),
and everything specific to you lives in these two files.

## 1. `AGENTS.md` — the profile

Copy [`AGENTS.template.md`](https://github.com/vsdudakov/troika/blob/main/AGENTS.template.md)
to `<workspace>/AGENTS.md` and fill every section: which repos exist and what each is, who
owns what, the exact verification commands a dev role must run, the base branch, the tracker
and which writes are allowed, how to bring the local stack up, the PR template, the release
scheme.

The **anchors are a contract**. Roles link into the profile by anchor — `#commands`,
`#branches`, `#tests`, `#tracker` — so a missing section is a role reading a dead link. The
structural gate checks this for you:

```bash
python3 tests/check.py
```

Where the profile declares a *limit* — no ticket transitions, one repo and one PR, no build
step, a base branch that is not `origin/main` — **the roles follow the profile**, not the
generic wording in a skill.

[Writing the profile :material-arrow-right:](../guides/profile.md){ .md-button }
[Anchor reference :material-arrow-right:](../reference/agents-md.md){ .md-button }

## 2. `.troika.json` — the paths

```json
{
  "profile": "AGENTS.md",
  "home": "troika",
  "scratchpad": "troika/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees",
  "memory": "troika/memory"
}
```

Every key is optional. Relative values resolve against the file; absolute ones are taken
as-is, so state can live outside the workspace entirely — useful when the tree is an
installed plugin in a host's cache rather than a clone.

Write one in **each folder that holds a set of repos** — one per organisation, per client,
per checkout. A single installed plugin then serves all of them, because roles resolve the
paths at run time rather than carrying them.

[.troika.json reference :material-arrow-right:](../reference/troika-json.md){ .md-button }

## Check it

```bash
eval "$(python3 troika/plugin/resolve.py --ensure)"
env | grep TROIKA_
```

`--ensure` creates the three directories the roles write into. If the resolver exits
non-zero, it could not find a workspace above the current directory — that is a stop, not a
default. [Paths and the resolver](../concepts/paths.md) explains what it looks for.

## Next

[Your first ticket :material-arrow-right:](first-ticket.md){ .md-button .md-button--primary }
