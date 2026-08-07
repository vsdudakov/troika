---
name: help
description: List every Troika command — the argument each takes and what it does.
---

Show the caller Troika's command surface. Print the list below as it stands —
run nothing, resolve nothing, and add no commands that are not on it.

- `/tr:demo [LABEL]` — Builds the demo integration branch — reset it from the default branch, merge the demo-labeled PRs in a conflict-minimising order, deploy, and prepare the team notification.
- `/tr:dev <TICKET>` — The full pipeline from ticket to merge-ready PR — bug tickets reproduce first, feature tickets plan first, then parallel dev, internal review loop, unit tests on the change only, QA before/after on the local stack, release, CI.
- `/tr:fix <PR>` — Fixes an open PR — either what you asked for in words, or every unresolved review comment on it — through the owning dev roles, then re-reviews, re-tests, pushes to the same branch and answers every thread.
- `/tr:qa <PR>` — Verifies a change on the real local stack — browser E2E with before/after GIFs for frontend work, API calls plus datastore checks for backend work — and returns proofs and a Pass/Fail verdict.
- `/tr:release <VERSION>` — Cuts a periodic release end-to-end — promote the previous pre-release, branch, pre-release, notes, QA plan, deploy to the pre-production environment, prepare the announcement.
- `/tr:review <PR>` — Reviews an open PR in an isolated worktree and posts one review comment. Read-only and lint-only — never runs tests, edits code, or merges.
- `/tr:setup [PATH]` — Creates a workspace — the .troika directory, its settings, and the profile every other procedure reads — by investigating the repos first and asking only what they cannot answer.
- `/tr:spike <TICKET>` — Investigates a ticket read-only and produces a reviewed implementation plan — the pipeline's planning half, stopped before any code is written.
- `/tr:triage <ISSUE>` — Investigates a production symptom from the observability platform — aggregate to the hot service, read raw events, follow traces, and land on a cause with evidence, changing nothing.

Every command except `/tr:setup` starts by resolving the workspace `/tr:setup` created, and
stops — pointing at `/tr:setup` — when there is none. The steps the flow runs for you
(plan-review, implement-change, internal-review, run-unit-tests and the rest) have no
command on purpose: they are skills, invocable by name, wrong to start on their own.
