---
title: Installing Troika
description: Install Troika as a plugin in Claude Code, Codex or Cursor, pin it to a release, or use it with no plugin system at all.
---

# Installation

Install it as a plugin — for `/troika:*` commands, subagents, and model-invoked skills — then
run `/troika:setup` once in the folder that holds your repos. That is the whole install.

There is nothing to compile. The only executable surface is two Python scripts on the standard
library, so any Python 3.9+ works and no virtualenv is needed.

Troika is markdown underneath, so a clone plus "read this file" also works in a host with no
plugin system at all — see [Running without a plugin](../guides/no-plugin.md).

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

The install is half of it. Every command exits immediately until a workspace exists, because
none of them will guess where your repos, plans and worktrees go:

```
/troika:setup
```

It reads your repos, drafts the profile from what they prove, and asks about the rest.

[Set up a workspace :material-arrow-right:](workspace.md){ .md-button .md-button--primary }
