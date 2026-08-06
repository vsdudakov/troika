---
title: Installing Troika
description: Install Troika as a plugin in Claude Code, Codex or Cursor, pin it to a release, or use it with no plugin system at all.
---

# Installation

Troika works two ways, and they compose:

1. **Clone it** into a workspace — the roles are markdown, so any agent reads them by path.
2. **Install it as a plugin** — for `/troika:*` commands, subagents, and model-invoked skills.

There is nothing to compile. The only executable surface is two Python scripts on the
standard library, so any Python 3.9+ works and no virtualenv is needed.

## Claude Code

```bash
claude plugin marketplace add vsdudakov/troika
claude plugin install troika@troika
```

Add `--scope project` to the install to enable it for one workspace only; that writes
`enabledPlugins` into that workspace's `.claude/settings.json`, which you can commit.

Verify what registered:

```bash
claude plugin details troika
#   Skills (20)  cross-repo, demo-prep, develop-flow, …
#   Agents (8)   architect, backend-dev, …
```

!!! tip "Pin a version"
    A marketplace source takes a git ref, so a workspace can pin a release and never move
    unexpectedly. See [Releases and versioning](../reference/releases.md).

## Codex

```bash
codex plugin marketplace add vsdudakov/troika        # or a local path, or owner/repo@v0.1.0
codex plugin add troika@troika
```

Codex has no `commands` concept, so its surface is the skills — the model invokes them by
description rather than you typing a `/` command. Installs are global; there is no
per-project enable.

## Cursor

```bash
cursor-agent plugin marketplace add https://github.com/vsdudakov/troika
```

Cursor requires a **git URL** — a local path is not accepted.

## Upgrading

Every host installs from a cached marketplace snapshot, so an upgrade is always *refresh
the marketplace, then update the plugin*:

```bash
claude plugin marketplace update troika && claude plugin update troika@troika
codex plugin marketplace upgrade && codex plugin add troika@troika
cursor-agent plugin marketplace update https://github.com/vsdudakov/troika
```

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

The install is half of it. Troika does nothing useful until the workspace tells it what your
codebase is:

[Set up a workspace :material-arrow-right:](workspace.md){ .md-button .md-button--primary }
