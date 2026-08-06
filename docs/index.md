---
title: Troika — from tracker ticket to reviewed pull request
description: Troika is an AI coding-agent pipeline for full-stack developers. It turns a tracker ticket into a reviewed, QA-verified pull request — planning, parallel implementation, automated code review, tests, QA proofs, release PRs, release notes and demo builds. A plugin for Claude Code, Codex and Cursor.
---

# Troika

![A troika — three horses harnessed abreast, pulling one sleigh](assets/troika.jpg)

*Nikolai Sverchkov (1817–1898), A Troika Ride Through The Snow. Public domain, via
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Nikolai_Sverchkov_-_A_Troika_Ride_Through_The_Snow.jpg).*

**Troika turns a tracker ticket into a reviewed, QA-verified pull request.** An AI
coding-agent pipeline for full-stack developers — plan, implement, review, test, verify,
ship — with a gate at every step. Install it as a plugin for
[Claude Code](https://claude.com/claude-code),
[Codex](https://developers.openai.com/codex/cli/) or [Cursor](https://cursor.com), or run it
from plain markdown in any agent.

[![CI](https://github.com/vsdudakov/troika/actions/workflows/check.yml/badge.svg)](https://github.com/vsdudakov/troika/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/vsdudakov/troika/blob/main/LICENSE.md)

Troika is an **agentic development pipeline**: eight specialised roles — architect,
backend and frontend developers, reviewer, tester, QA, releaser, commenter — that take a
ticket from your tracker and hand back a pull request with proofs attached. It automates the
whole loop a full-stack developer runs by hand: requirements and planning, parallel
implementation in git worktrees, **automated code review**, unit tests, **QA verification on
your real local stack**, the release PR, and the CI and review-bot watch after it. Release
cuts, **release notes** and demo builds are in the box too.

It is not a framework and not a runtime: it is **plain markdown** — roles, procedures and
templates — that any coding agent loads by path, wired into slash commands for the three
hosts that ship a plugin system.

```
/troika:develop-flow SCRUM-123
```

Behind that one command: the architect plans, a **different model family** reviews the plan
and loops it back, dev roles implement in parallel worktrees, the reviewer runs nine checks
on the diff, the tester runs only the tests the change developed, QA verifies on your real
local stack with before/after proofs, and the releaser opens the PR and watches CI.

[Install Troika :material-arrow-right:](getting-started/installation.md){ .md-button .md-button--primary }
[Set up a workspace :material-arrow-right:](getting-started/workspace.md){ .md-button }

## Why Troika

- :vertical_traffic_light: **Gates, not vibes.** Every step is a gate. A plan is not approved
  until a reviewer on a different model family approves it; a diff is not pushed until
  [nine checks](guides/review.md) pass; a PR is not done until CI is green and the review
  bots are quiet.
- :busts_in_silhouette: **Eight roles, eight contexts.** Each has its own scope, model,
  effort and hard refusals. Dev roles write tests but never run them; the reviewer never runs
  anything. [Roles :material-arrow-right:](concepts/roles.md)
- :electric_plug: **One tree, three hosts.** The same skills are `/troika:*` commands in
  Claude Code and Cursor, and model-invoked skills in Codex — or no plugin at all, just files
  read by path. [Running without a plugin :material-arrow-right:](guides/no-plugin.md)
- :office: **Organisation-neutral by construction.** Nothing in the repository names a repo,
  command, branch, tracker, URL or person. Those live in your `AGENTS.md` profile and are
  linked **by anchor**. [Writing the profile :material-arrow-right:](guides/profile.md)
- :file_folder: **Per-workspace paths.** `.troika.json` says where plans, worktrees and
  memory live — one file per folder-of-repos, so a single installed plugin serves every
  client and org you work in. [Paths :material-arrow-right:](concepts/paths.md)
- :test_tube: **It is tested on itself.** A structural gate checks every link, anchor and
  file shape; a behavioural gate plants seventeen known defects and asserts the role that
  claims to catch each one does. [Testing :material-arrow-right:](testing.md)

## How a ticket moves

```mermaid
flowchart LR
    A[ticket] --> B[architect<br/>plan]
    B --> C{plan review<br/>other model}
    C -- rewrite --> B
    C -- approve --> D[dev roles<br/>parallel worktrees]
    D --> E{internal review<br/>9 checks}
    E -- fix --> D
    E --> F[tester<br/>changed tests only]
    F --> G{QA<br/>real local stack}
    G -- fix --> D
    G --> H[releaser<br/>PR + proofs]
    H --> I[CI + review watch]
```

Every loop has a cap, and every arrow back is a role handing a file to another role — never a
shared context. [The pipeline :material-arrow-right:](concepts/pipeline.md)

## What it is not

Troika does not run your agent, host a model, or wrap an API. There is no daemon, no
scheduler and no lock-in: the executable surface is two Python scripts on the standard
library, and everything else is markdown you can fork, trim, or run by hand.

It also makes no claim to work well on a codebase whose profile is not written. A vague
`AGENTS.md` produces vague gates — the roles are only as sharp as the facts you give them.

## Licence

[MIT](https://github.com/vsdudakov/troika/blob/main/LICENSE.md) © Troika contributors.
If it saves your team time, consider
[sponsoring on GitHub](https://github.com/sponsors/vsdudakov). :heart:
