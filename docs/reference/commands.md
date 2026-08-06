---
title: Commands
description: Every /troika command, what it takes as an argument, which role runs it and what it leaves behind.
---

# Commands

One command per **procedure**, thirteen in all. In Claude Code and Cursor they appear as
`/troika:<name>`; in Codex the same procedures are model-invoked skills with no `/` prefix.

Every command does the same three things before it starts: resolves the workspace (creating
the state directories), reads the procedure, and reads your `AGENTS.md` profile.

## The pipeline

| Command | Argument | Runs | Leaves behind |
| --- | --- | --- | --- |
| `/troika:develop-flow` | `<TICKET>` | the whole pipeline | a merge-ready PR |
| `/troika:plan-review` | `<TICKET>` | reviewer | `…-plan-review-<n>.md` |
| `/troika:implement-change` | `<TICKET>` | a dev role | a worktree and `…-<role>.md` |
| `/troika:internal-review` | `<TICKET>` | reviewer | `…-review-<n>.md` |
| `/troika:run-unit-tests` | `<TICKET>` | tester | `…-tests-<n>.md` and lane logs |
| `/troika:qa-verify` | `<TICKET>` | qa | `…-qa-<n>.md` and proofs |
| `/troika:release-pr` | `<TICKET>` | releaser | commit, PR, ticket update |

## Around the pipeline

| Command | Argument | What it does |
| --- | --- | --- |
| `/troika:ticket-intake` | `<request>` | turns a short request into a well-shaped ticket, or reshapes an existing one |
| `/troika:pr-review` | `<TICKET>` | reviews an open PR in an isolated worktree and posts one comment |
| `/troika:incident-triage` | `<issue link \| stack trace \| event>` | investigates a production symptom read-only, lands on a cause with evidence |
| `/troika:demo-prep` | `[demo label]` | builds the demo integration branch, deploys, prepares the notification |
| `/troika:release-cut` | `<version>` | cuts a periodic release end to end |
| `/troika:release-notes` | `<version>` | generates customer-readable notes from the diff |

## Not commands

References (`worktree`, `scratchpad`, `memory`, `cross-repo`, `tracker`) and templates
(`plan-template`, `pr-template`) are skills without commands — they are read *by* a procedure
or filled by one. Hosts still surface them as skills, so a model can pull one in when it needs
the detail.

## Regenerating them

Commands are generated from each procedure's frontmatter:

```bash
python3 plugin/generate.py
python3 tests/check.py     # fails on a stale, missing or orphaned command
```

Edit the procedure, never the command file.
