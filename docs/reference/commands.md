---
title: Commands
description: Every /tr command, what it takes as an argument, which role runs it and what it leaves behind.
---

# Commands

Nine commands, one per procedure you **start** a session with. In Claude Code and Cursor they
appear as `/tr:<name>`; in Codex the same procedures are model-invoked skills with no `/`
prefix.

Every command does the same three things before it starts: resolves the workspace (creating the
state directories), reads the procedure, and reads `$TROIKA_PROFILE`.

`/tr:setup` is the exception, and the one to run first: it is what *creates* the workspace
the others resolve, so it cannot open by resolving one. Every other command exits immediately
until it has been run once.

## The commands

| Command | Procedure | Argument | What it does |
| --- | --- | --- | --- |
| `/tr:setup` | `workspace-setup` | `[PATH]` | creates `.troika/` and writes the profile — reads your repos first, asks only what they cannot answer |
| `/tr:dev` | `develop-flow` | `<TICKET>` | the whole pipeline, ticket to merge-ready PR — bugs reproduce first, features plan first; unattended unless you pass `--ask` |
| `/tr:spike` | `spike` | `<TICKET>` | investigates the ticket and produces a reviewed plan — and stops there, nothing is built |
| `/tr:review` | `pr-review` | `<PR>` | reviews an open PR in an isolated worktree and posts one comment |
| `/tr:fix` | `fix-pr` | `<PR>` | fixes an open PR — what you describe, or its unresolved review comments |
| `/tr:qa` | `qa-verify` | `<PR>` | verifies a PR on the local stack and captures a proof per requirement |
| `/tr:triage` | `incident-triage` | `<ISSUE>` | investigates a production symptom read-only, lands on a cause with evidence |
| `/tr:release` | `release-cut` | `<VERSION>` | cuts a periodic release end to end |
| `/tr:demo` | `demo-prep` | `[LABEL]` | builds the demo integration branch, deploys, prepares the notification |

## Who runs which

The split a team ends up with, in the order a week happens:

| Who | When | What they type |
| --- | --- | --- |
| developer | a ticket is assigned | `/tr:dev SCRUM-123` — or `/tr:spike SCRUM-123` first, when it needs sizing or a design call |
| developer | their PR is open and reviewed | `/tr:fix <PR URL>` for every unresolved comment, or `/tr:fix <PR URL> stream the export instead of buffering it` for a change you name |
| developer | reviewing a teammate's PR | `/tr:review <PR URL>`, and `/tr:qa <PR URL>` when it needs proving on a running stack |
| anyone | a production symptom or a pasted stack trace | `/tr:triage <stack trace>` |
| release manager | demo day | `/tr:demo release/X.Y.Z` |
| release manager | the release cadence says cut | `/tr:release release/X.Y.Z` |
| the ticket's reporter | asked once at 2r, before any code — only on a `--ask` run | answers **go ahead**, **change this** (with what), or **not this at all** |

**Flag.** `/tr:dev` takes one: `--ask`, after the ticket — `/tr:dev SCRUM-123 --ask` — which
stops at the reporter-review gate and waits for their answer. Without it the run is unattended
end to end. There is no flag for the other direction, because a plain run already is it.
Unattended never silences a stop condition and never overrides what the profile marks
never-automatic.

`/tr:fix` always pushes to the PR's own branch — no command here opens a second PR for work
that already has one. `/tr:demo` and `/tr:release` stop at a drafted announcement and wait for
a human to send it. Every one of them needs `/tr:setup` to have been run once.

## The flow of each command

<a id="setup"></a>
### `/tr:setup` — create the workspace

```mermaid
flowchart TD
  A[folder of repos] --> B{already set up?}
  B -- yes --> Z([ask: leave · update · rewrite])
  B -- no --> C[list every repo<br/>tick what Troika covers]
  C --> D[--init: settings.json,<br/>.gitignore, state dirs]
  D --> E[probe each repo, read-only<br/>style · tests · commands · stack · branches]
  E --> F[find credentials already here<br/>gh · tracker token · tool keys]
  F --> G[one batched interview<br/>reviewer · branches · tracker · tools · voice]
  G --> H[confirm the whole draft, once]
  H --> I([.troika/PROFILE.md])
```

<a id="dev"></a>
### `/tr:dev` — ticket to merge-ready PR

Steps 0 – 2r decide what gets built; from step 3 the two paths are one flow:

- **bug** — steps to reproduce → **local QA reproduces it on the base ref** → *(reporter review, under `--ask`)* → fix → internal review loop → unit tests → local QA before/after → PR with proofs → CI + post-PR actions
- **feature** — requirements → plan → **plan review loop** → *(reporter review, under `--ask`)* → implement → internal review loop → unit tests → local QA before/after → PR with proofs → CI + post-PR actions

The reporter review is the only step that waits for a person, and a plain run does not run it —
`--ask` is what puts the gate in. Your profile's `#autonomy` anchor says who that reporter is
and how they are reached ([Running it without a human](../concepts/pipeline.md#running-it-without-a-human)).

```mermaid
flowchart TD
  A[ticket] --> B{bug or feature?}
  B -- bug --> C[1b · collect steps to reproduce]
  C --> D{2b · local QA reproduces it<br/>on the base checkout}
  D -- not reproduced --> E([stop · ask the reporter])
  D -- reproduced · approved<br/>human approves in ask mode --> H
  B -- feature --> F[1f · collect requirements and plan]
  F --> G{2f · plan review loop<br/>other model family, max 3}
  G -- request changes --> F
  G -- approved<br/>human approves in ask mode --> H[3 · implement · one lane per repo]
  H --> I[lane A · backend-dev<br/>code and tests written, not run]
  H --> J[lane B · frontend-dev<br/>code and tests written, not run]
  I --> K
  J --> K{4 · internal review loop<br/>lint only, max 3}
  K -- blocker or major --> H
  K -- approved --> L{5 · unit tests<br/>only the changed tests}
  L -- fail --> H
  L -- green --> M{6 · local QA before and after<br/>one proof per requirement, max 3}
  M -- fail --> H
  M -- approved --> N[7 · create the PR<br/>template · QA proofs · ticket link]
  N --> O{8 · wait for CI and review waves}
  O -- red --> H
  O -- green and quiet --> P[post-PR actions<br/>tracker writes · worktree cleanup]
  P --> Q([merge-ready PR])
```

`2r` is the only step that waits for a person: a plain run passes straight through it, and
`--ask` is what makes it stop for the reporter's answer ([Running it without a human](../concepts/pipeline.md#running-it-without-a-human)).

<a id="spike"></a>
### `/tr:spike` — plan it, build nothing

```mermaid
flowchart TD
  T[ticket] --> F[fan out:<br/>index · ticket · memory]
  F --> I[read-only probe per repo]
  I --> P[plan + cost + alternatives]
  P --> R{plan review<br/>cap 3 cycles}
  R -- request changes --> P
  R -- approved --> O([plan file — no branch, no code])
```

<a id="fix"></a>
### `/tr:fix` — fix an open PR in place

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
### `/tr:review` — read-only PR review

```mermaid
flowchart TD
  A[PR] --> B[requirements:<br/>plan file, else the PR body]
  B --> C[isolated worktree<br/>on the head branch]
  C --> D[nine checks · lint only<br/>never runs tests, never edits]
  D --> E[one comment:<br/>Blocker · Major · Nit]
  E --> F([worktree removed])
```

<a id="qa"></a>
### `/tr:qa` — verify on the real local stack

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
### `/tr:triage` — production symptom to cause

```mermaid
flowchart TD
  A[symptom] --> B[pin the question]
  B --> C[aggregate to the hot service]
  C --> D[read raw events]
  D --> E[follow traces into the code]
  E --> F[blast radius + first occurrence]
  F --> G([cause with evidence — nothing changed])
```

<a id="release"></a>
### `/tr:release` — cut a periodic release

```mermaid
flowchart TD
  A[version] --> B[promote the previous pre-release]
  B --> C[cut the branch<br/>+ pre-release]
  C --> D[notes from the diff]
  D --> E[QA plan]
  E --> F[deploy to pre-production]
  F --> G([announcement prepared, not posted])
```

<a id="demo"></a>
### `/tr:demo` — build the demo branch

```mermaid
flowchart TD
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

The steps `/tr:dev` runs for you are procedures too, but they are not in the `/` menu:

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

`/tr:fix` is the other half of `/tr:review`: the reviewer posts findings and stops,
and `fix-pr` picks an open PR up from there. With no description it works through the
unresolved review comments, fixing or rejecting each one with a reason; with a description it
does exactly that instead, and still reports the comments it left alone. Either way the work
goes through the owning dev roles, gets re-reviewed and re-tested, and is pushed to the same
branch — it never opens a second PR.

`qa-verify` is the one procedure with both roles: the flow runs it at step 6 against the
lanes it just built, and `/tr:qa` runs it against a PR that already exists — checking
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
