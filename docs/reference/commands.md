---
title: Commands
description: Every /troika command, what it takes as an argument, which role runs it and what it leaves behind.
---

# Commands

Seven commands, one per procedure you **start** a session with. In Claude Code and Cursor
they appear as `/troika:<name>`; in Codex the same procedures are model-invoked skills with
no `/` prefix.

Every command does the same three things before it starts: resolves the workspace (creating
the state directories), reads the procedure, and reads your `AGENTS.md` profile.

## The commands

| Command | Procedure | Argument | What it does |
| --- | --- | --- | --- |
| `/troika:dev` | `develop-flow` | `<TICKET>` | the whole pipeline, ticket to merge-ready PR |
| `/troika:spike` | `spike` | `<TICKET>` | investigates the ticket and produces a reviewed plan — and stops there, nothing is built |
| `/troika:review` | `pr-review` | `<PR number \| PR link>` | reviews an open PR in an isolated worktree and posts one comment |
| `/troika:qa` | `qa-verify` | `<PR number \| PR link \| TICKET>` | verifies a PR on the local stack and captures a proof per requirement |
| `/troika:triage` | `incident-triage` | `<issue link \| stack trace \| event>` | investigates a production symptom read-only, lands on a cause with evidence |
| `/troika:release` | `release-cut` | `<version>` | cuts a periodic release end to end |
| `/troika:demo` | `demo-prep` | `[demo label]` | builds the demo integration branch, deploys, prepares the notification |

## Procedures without a command

The steps `/troika:dev` runs for you are procedures too, but they are not in the `/` menu:

| Procedure | Runs | Leaves behind |
| --- | --- | --- |
| `plan-review` | reviewer | `…-plan-review-<n>.md` |
| `implement-change` | a dev role | a worktree and `…-<role>.md` |
| `internal-review` | reviewer | `…-review-<n>.md` |
| `run-unit-tests` | tester | `…-tests-<n>.md` and lane logs |
| `release-pr` | releaser | commit, PR, ticket update |
| `release-notes` | releaser | a release's notes from the diff |
| `ticket-intake` | architect · commenter | a well-shaped ticket, created or reshaped |

Most are read as `SKILL.md` by the role running them, so a `/` entry would only offer an
entry point that is wrong to start on its own — `internal-review` with no branch to review,
or `release-pr` with nothing reviewed to ship. All three hosts still discover every one of
them as a skill, so you can ask for one by name ("run internal-review on this branch", "run
ticket-intake for the Q3 export work") and the model pulls it in. The `/` menu is the short
list of ways to *start*, not the list of what Troika can do.

`qa-verify` is the one procedure with both roles: the flow runs it at step 6 against the
lanes it just built, and `/troika:qa` runs it against a PR that already exists — checking
the head branch out into its own worktree first, and saying in the report where it had to
take the requirements from when there is no plan file to read.

## Not procedures at all

References (`worktree`, `scratchpad`, `memory`, `cross-repo`, `tracker`) and templates
(`plan-template`, `pr-template`) are skills without commands for a different reason — they
are read *by* a procedure or filled by one, never run.

## Regenerating them

Commands are generated from `COMMANDS` in `plugin/generate.py` — the alias and the argument
hint — plus the procedure's own frontmatter for the description:

```bash
python3 plugin/generate.py
python3 tests/check.py     # fails on a stale, missing or orphaned command
```

Edit the procedure, or the map, never the command file. Adding a procedure to `COMMANDS`
gives it a `/` entry; removing it there leaves the skill in place and takes only the menu
entry away.
