---
title: Installing Troika
description: Install Troika as a plugin in Claude Code, Codex or Cursor, pin it to a release, or use it with no plugin system at all.
---

# Installation

Install it as a plugin — for `/tr:*` commands, subagents, and model-invoked skills — then
run `/tr:setup` once in the folder that holds your repos. That is the whole install.

Every command exists in all three hosts; only the spelling differs, because each host has
its own command surface:

| Host | Spelling | Example |
|------|----------|---------|
| Claude Code | `/tr:<command>` | `/tr:dev SCRUM-123` |
| Cursor | `/tr-<command>` | `/tr-dev SCRUM-123` |
| Codex | `$tr-<command>` (a skill mention — type `$`) | `$tr-dev SCRUM-123` |

These docs write the Claude Code spelling everywhere; substitute your host's.

There is nothing to compile. The only executable surface is two Python scripts on the standard
library, so any Python 3.9+ works and no virtualenv is needed.

Troika is markdown underneath, so a clone plus "read this file" also works in a host with no
plugin system at all — see [Running without a plugin](../guides/no-plugin.md).

## Claude Code

```bash
claude plugin marketplace add vsdudakov/troika
claude plugin install tr@troika
```

Add `--scope project` to the install to enable it for one workspace only; that writes
`enabledPlugins` into that workspace's `.claude/settings.json`, which you can commit.

Verify what registered:

```bash
claude plugin details tr
#   Skills (23)  cross-repo, demo-prep, develop-flow, …
#   Commands (9)  demo, dev, fix, qa, release, review, setup, spike, triage
#   Agents (8)   architect, backend-dev, …
```

!!! tip "Pin a version"
    A marketplace source takes a git ref, so a workspace can pin a release and never move
    unexpectedly. See [Releases and versioning](../reference/releases.md).

## Codex

```bash
codex plugin marketplace add vsdudakov/troika        # or a local path, or owner/repo@v0.1.0
codex plugin add tr@troika
```

Codex has no `commands` concept — no plugin commands, and no custom slash commands either
(the old `~/.codex/prompts` directory is no longer read). Its explicit surface is skills,
mentioned with a `$` prefix. So the plugin's 23 skills install as usual, and the nine
commands are exported as command-shaped skills from a clone:

```bash
python3 plugin/export.py codex        # writes tr-dev, tr-review, … into ~/.codex/skills
```

Then type `$tr-dev TICKET-123` in the composer — `$` opens the skill picker the way `/`
opens the command menu elsewhere. Installs are global; there is no per-project enable.

## Cursor

Cursor does not surface plugin commands, and its slash menu already lists every registered
skill — so the plugin registers none, and the commands are exported into Cursor's own
slash-command directory from a clone instead:

```bash
python3 plugin/export.py cursor       # writes /tr-dev, /tr-review, … into ~/.cursor/commands
```

Cursor command names allow only lowercase letters, digits and hyphens, so the spelling is
`/tr-dev` — the `/tr:dev` form exists only in Claude Code, whose plugin system owns the
`:` namespace.

`make export-commands` regenerates and exports for both hosts at once. The exported files
pin the clone's path where Claude Code would use `${CLAUDE_PLUGIN_ROOT}`, so re-run the
export after moving the clone; installing from a marketplace snapshot instead takes
`--root <snapshot-path>`.

## Upgrading

Every host installs from a cached marketplace snapshot, so an upgrade is always *refresh
the marketplace, then update the plugin*:

```bash
claude plugin marketplace update troika && claude plugin update tr@troika
codex plugin marketplace upgrade && codex plugin add tr@troika
```

Exported commands come from a clone, not a snapshot, so their upgrade is `git pull` in the
clone followed by `python3 plugin/export.py codex cursor` (or `make export-commands`).

Restart the host afterwards. A pinned version does not move until you bump the pin — see
[Upgrading an installed plugin](../reference/releases.md#upgrading-an-installed-plugin).

## No plugin at all

Every host that can read a file can run Troika:

```bash
git clone https://github.com/vsdudakov/troika
```

```
read troika/skills/develop-flow/SKILL.md and run it for SCRUM-123
```

This is the lowest-common-denominator mode and nothing about the pipeline depends on the
plugin layer. See [Running without a plugin](../guides/no-plugin.md).

## Next

The install is half of it. Every command exits immediately until a workspace exists, because
none of them will guess where your repos, plans and worktrees go:

```
/tr:setup
```

It reads your repos, drafts the profile from what they prove, and asks about the rest.

[Set up a workspace :material-arrow-right:](workspace.md){ .md-button .md-button--primary }
