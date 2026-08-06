---
title: Plugin manifests
description: What each host reads, the three schema quirks that fail silently, and how the generated surface is kept honest.
---

# Plugin manifests

One tree, three hosts, three manifests. All of them describe the same skills, roles and
commands.

| | Claude Code | Codex | Cursor |
| --- | --- | --- | --- |
| manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.cursor-plugin/plugin.json` |
| marketplace | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` | `.cursor-plugin/marketplace.json` |
| commands | `plugin/commands/*.md`, listed file by file | — (no such concept) | `./plugin/commands/*.md` glob |
| skills | `./skills` | `./skills` (fixed) | `./skills/` |
| roles | auto-scanned from `agents/` | — | — |

## Three quirks worth knowing

Each of these fails **silently** — the plugin installs, and something is quietly missing or
duplicated.

**Codex pins skills to `<plugin root>/skills`.** The path is not configurable, which is why
the skills live at the repository root rather than under `plugin/`. Codex ships a validator,
and it is worth running after any manifest change:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

**Claude Code's `commands` key takes command *files*.** Point it at a directory and the
directory is read as a *skill directory* instead — every procedure registers a second time as
a skill and no commands appear. The list is therefore spelled out, and generated:

```bash
python3 plugin/generate.py     # writes plugin/commands/*.md and the manifest's commands list
```

**Claude Code's `agents` key accepts a path list that registers nothing.** Only the automatic
scan of `agents/` works — and it loads *every* file in that directory. So the manifest declares
no `agents` key at all, and `agents/` contains nothing but roles. The roles index lives at
`ROLES.md` in the repository root for exactly this reason.

Verify what actually registered:

```bash
claude plugin details troika
#   Skills (20)  …
#   Agents (8)   …
```

## What the gate enforces

`tests/check.py` fails the build on each of the above:

- a stale, missing, or orphaned generated command
- a `commands` list in the manifest that has drifted from the procedures
- an `agents` key in the Claude manifest
- a directory listed where a command file belongs
- a version that disagrees between any two manifests
  ([Releases and versioning](releases.md))

## The two roots

A plugin installs into the host's **cache**. The cached copy holds the roles and procedures; it
cannot hold `AGENTS.md`, worktrees, plans or memory, which are per-workspace. So a command
reads its procedure from the plugin root and resolves everything it *writes* through the
workspace — see [Paths and the resolver](../concepts/paths.md).
