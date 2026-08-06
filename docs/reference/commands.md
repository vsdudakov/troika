---
title: Commands
description: Every /troika command, what it takes as an argument, which role runs it and what it leaves behind.
---

# Commands

Nine commands, one per procedure you **start** a session with. In Claude Code and Cursor they
appear as `/troika:<name>`; in Codex the same procedures are model-invoked skills with no `/`
prefix.

Every command does the same three things before it starts: resolves the workspace (creating the
state directories), reads the procedure, and reads `$TROIKA_PROFILE`.

`/troika:setup` is the exception, and the one to run first: it is what *creates* the workspace
the others resolve, so it cannot open by resolving one. Every other command exits immediately
until it has been run once.

## The commands

| Command | Procedure | Argument | What it does |
| --- | --- | --- | --- |
| `/troika:setup` | `workspace-setup` | `[PATH]` | creates `.troika/` and writes the profile — reads your repos first, asks only what they cannot answer |
| `/troika:dev` | `develop-flow` | `<TICKET>` | the whole pipeline, ticket to merge-ready PR |
| `/troika:spike` | `spike` | `<TICKET>` | investigates the ticket and produces a reviewed plan — and stops there, nothing is built |
| `/troika:review` | `pr-review` | `<PR>` | reviews an open PR in an isolated worktree and posts one comment |
| `/troika:fix` | `fix-pr` | `<PR>` | fixes an open PR — what you describe, or its unresolved review comments |
| `/troika:qa` | `qa-verify` | `<PR>` | verifies a PR on the local stack and captures a proof per requirement |
| `/troika:triage` | `incident-triage` | `<ISSUE>` | investigates a production symptom read-only, lands on a cause with evidence |
| `/troika:release` | `release-cut` | `<VERSION>` | cuts a periodic release end to end |
| `/troika:demo` | `demo-prep` | `[LABEL]` | builds the demo integration branch, deploys, prepares the notification |

## The flow of each command

<a id="setup"></a>
### `/troika:setup` — create the workspace

```mermaid
flowchart LR
  A[folder of repos] --> B{already set up?}
  B -- yes --> Z([ask: leave · update · rewrite])
  B -- no --> C[--init: settings.json,<br/>.gitignore, state dirs]
  C --> D[probe every repo<br/>read-only]
  D --> E[draft the anchors<br/>evidence can prove]
  E --> F[ask what no repo records:<br/>tracker · ownership · voice · gotchas]
  F --> G[confirm the whole draft, once]
  G --> H([.troika/PROFILE.md])
```

<a id="dev"></a>
### `/troika:dev` — ticket to merge-ready PR

Every diamond is a gate, and every failed gate goes back to the dev lanes rather than forward.

```mermaid
flowchart TD
  T[ticket] --> P[1 · plan<br/>architect]
  P --> PR{2 · plan review<br/>reviewer, other model family}
  PR -- request changes --> P
  PR -- approved --> D[3 · dev lanes, one per repo<br/>backend-dev · frontend-dev]
  D --> IR{4 · internal review<br/>lint only, never runs tests}
  IR -- blocker/major --> D
  IR -- pass --> U{5 · unit tests<br/>tester, parallel lanes}
  U -- fail --> D
  U -- green --> Q{6 · QA on the local stack}
  Q -- fail --> D
  Q -- pass --> R[7 · release<br/>commit · PR · proofs · ticket]
  R --> C{8 · CI + review watch}
  C -- red --> D
  C -- quiet --> M([merge-ready PR])
```

<a id="spike"></a>
### `/troika:spike` — plan it, build nothing

```mermaid
flowchart LR
  T[ticket] --> F[fan out:<br/>index · ticket · memory]
  F --> I[read-only probe per repo]
  I --> P[plan + cost + alternatives]
  P --> R{plan review<br/>cap 3 cycles}
  R -- request changes --> P
  R -- approved --> O([plan file — no branch, no code])
```

<a id="fix"></a>
### `/troika:fix` — fix an open PR in place

```mermaid
flowchart TD
  A[PR, with or without a description] --> B[read the PR<br/>+ unresolved threads]
  B --> C[worktree on the head branch]
  C --> D[fix list, written before any edit]
  D --> E[owning dev role per repo]
  E --> F{internal review}
  F -- blocker/major --> E
  F -- pass --> G{unit tests}
  G -- fail --> E
  G -- green --> H{QA — only if user-visible}
  H -- fail --> E
  H -- pass --> I[commit + push, same branch]
  I --> J[answer every thread]
  J --> K{CI}
  K -- red --> E
  K -- green --> L([the same PR, updated])
```

<a id="review"></a>
### `/troika:review` — read-only PR review

```mermaid
flowchart LR
  A[PR] --> B[requirements:<br/>plan file, else the PR body]
  B --> C[isolated worktree<br/>on the head branch]
  C --> D[nine checks · lint only<br/>never runs tests, never edits]
  D --> E[one comment:<br/>Blocker · Major · Nit]
  E --> F([worktree removed])
```

<a id="qa"></a>
### `/troika:qa` — verify on the real local stack

```mermaid
flowchart TD
  A[PR, or the flow's lanes] --> B[point the stack at the branch]
  B --> C[bring the stack up]
  C --> D{split the change}
  D -- frontend --> E[browser E2E<br/>before/after GIF]
  D -- backend --> F[API calls + datastore checks]
  E --> G[regression + integration suite]
  F --> G
  G --> H[stack limits:<br/>what a green run does not prove]
  H --> I([proofs per requirement · Pass/Fail])
```

<a id="triage"></a>
### `/troika:triage` — production symptom to cause

```mermaid
flowchart LR
  A[symptom] --> B[pin the question]
  B --> C[aggregate to the hot service]
  C --> D[read raw events]
  D --> E[follow traces into the code]
  E --> F[blast radius + first occurrence]
  F --> G([cause with evidence — nothing changed])
```

<a id="release"></a>
### `/troika:release` — cut a periodic release

```mermaid
flowchart LR
  A[version] --> B[promote the previous pre-release]
  B --> C[cut the branch<br/>+ pre-release]
  C --> D[notes from the diff]
  D --> E[QA plan]
  E --> F[deploy to pre-production]
  F --> G([announcement prepared, not posted])
```

<a id="demo"></a>
### `/troika:demo` — build the demo branch

```mermaid
flowchart LR
  A[label] --> B[collect the labelled PRs]
  B --> C[reset the integration branch<br/>from the default branch]
  C --> D[merge in conflict-minimising order]
  D --> E{conflict}
  E -- semantic --> S([stop and report])
  E -- none --> F[deploy]
  F --> G([team notification prepared])
```

## Arguments

The hint is one upper-case word naming what the first step resolves; the forms it accepts
(a number, a link, a ticket key, a pasted stack trace) are the procedure's business, not the
menu's. `<>` is required, `[]` optional.

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

`/troika:fix` is the other half of `/troika:review`: the reviewer posts findings and stops,
and `fix-pr` picks an open PR up from there. With no description it works through the
unresolved review comments, fixing or rejecting each one with a reason; with a description it
does exactly that instead, and still reports the comments it left alone. Either way the work
goes through the owning dev roles, gets re-reviewed and re-tested, and is pushed to the same
branch — it never opens a second PR.

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
