---
name: develop-flow
description: The full pipeline from ticket to merge-ready PR — plan, plan review loop, parallel dev, internal review loop, parallel unit tests on the change only, QA on the local stack, release.
---

# Develop flow

Ticket to PR. The orchestrator spawns one [role](../agents/README.md) per phase; roles never call each other.

Model and effort are passed at spawn, never read from the file ([agents › Model and effort](../agents/README.md#model-and-effort)):

```bash
# architect — Claude, high effort
claude --model claude-fable-5 --effort high -p "read $WS/harness/agents/architect.md and act as that role for <TICKET>"
# reviewer — Codex, high effort, different family from whoever wrote the code
codex -m gpt-5.6-sol -c model_reasoning_effort="high" ...
```

Subagents inherit session effort; use the highest effort any role needs.

**Kind** procedure · **Used by** orchestrator · **When** a ticket or described change needs shipping · **Ends with** one PR per touched repo — CI green, review quiet, proofs attached, ticket updated per the profile

```
ticket
  └─ 0 ∥ index refresh per repo · ticket surfaces (comments, attachments, links) · memory
  └─ 1 architect ── plan ◀── ∥ read-only probes, one per repo/area
        │
        ▼ 2 plan review ∥ 2 lenses (other model family) ── rewrite loop (max 3) ── approved
        │
   ┌────┴─────────────────────┬──────────────────────────┬─────────────────────┐
   ▼ repo lane A              ▼ repo lane B              ▼ QA pre-warm         │
   3 dev role(s) for repo A   3 dev role(s) for repo B   boot the stack        │
     code + tests written       code + tests written     seed data             │
     tests NOT run, lint green  tests NOT run, lint green (no barrier)         │
   4 internal review ∥ 3 dims 4 internal review ∥ 3 dims                       │
     (lint · tests · design)    (lint · tests · design)                        │
   5 tester ∥ lanes per area  5 tester ∥ lanes per area                        │
     changed tests only         changed tests only                             │
   └────┬─────────────────────┴──────────────────────────┴─────────────────────┘
        ▼ join — every lane green
        ▼ 6 QA on local stack (∥ proof capture per requirement) + fix loop (max 3)
        ▼ 7 release ── ∥ commit+push per repo · PR bodies drafted during 6
        │              PRs opened in dependency order
        ▼ 8 ∥ per PR: CI watch + review waves + PR review (max 3) ──▶ green + quiet
```

`∥` means concurrent. **A lane is a repo, not a role** ([Lanes](#lanes)). Sibling lanes do not wait. Barriers: plan approval, the pre-QA join, CI.

Tests run locally once: dev writes (3), reviewer reads (4), [tester](../agents/tester.md) runs change tests (5), CI runs all (8). The human is not a gate; ask only under [Stop conditions](#stop-conditions).

<a id="lanes"></a>
## Lanes — one per repository

- **Two repos:** two worktrees, branches, PRs; parallel only with a pinned contract.
- **One repo, many roles:** one worktree, branch, PR. Roles take turns in [dependency order](../../AGENTS.md#dependency-order), inside their [ownership](../../AGENTS.md#ownership).

Never let two agents write one worktree. Split by repo, not role or feature.

<a id="parallelism"></a>
## Parallelism — what runs at the same time, and what must not

| Runs concurrently | Why it is safe |
| --- | --- |
| Index refresh, one job per repo (0) | independent roots, read-only |
| Ticket surfaces collected while code probes run (0–1) | different sources, both read-only |
| Read-only code probes, one per repo or area (1) | no writes; the architect synthesizes them |
| The two plan-review lenses (2) | read-only; findings merged before the rewrite |
| Dev roles in **different repos** (3) | separate worktrees and branches — **only with a pinned contract** |
| The three review dimensions in one repo (4) | read-only over one diff |
| Test lanes, one per area, across ready worktrees (5) | separate processes and test roots |
| Whole per-repo lanes 3→4→5 against each other | a lane touches only its own worktree |
| QA's stack boot, from the first dev role's done | boot depends on the checkout, not on review |
| Proof capture per requirement (6), paths not sharing state | independent flows on one stack |
| PR body drafting during QA (6→7) | text work, no repo state |
| Commit and push per repo (7) | separate repos |
| CI watch + review waves + PR review, per PR (8) | independent PRs and checks |

| Must stay sequential | Why |
| --- | --- |
| Plan → any product code | the plan is the contract every lane codes against |
| Dev roles sharing one repo's worktree (3) | one checkout, one branch — they take turns in dependency order |
| Review → tests, inside a lane | review removes what a test run finds the slow way |
| A fix → re-review → re-test | a fix is a diff, and no diff advances unreviewed |
| All lanes → QA | one stack, one branch under test |
| Provider PR → consumer PR | dependency order ([cross-repo](cross-repo.md)) |
| A suite the profile marks sequential | correctness, not speed ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)) |
| Migration work inside one repo | migration numbers collide silently |

Report wall clock per lane. Set `WS` once; all handoff paths are absolute ([workspace paths](../../AGENTS.md#workspace-paths)).

## 0. Fan out — index, ticket, memory, all at once

Start together; join before planning:

1. Refresh each repo index from its root ([code search](../../AGENTS.md#code-search)); dev repeats this in its worktree.
2. Read every ticket surface ([plan-review](plan-review.md#ticket-surfaces)).
3. Run `ls $WS/harness/memory/*.md`; read every entry ([memory](../memory/README.md)).

## 1. Collect requirements and plan

Run [agents/architect.md](../agents/architect.md) on the step 0 material — tracker access and auth check in [AGENTS.md › Tracker](../../AGENTS.md#tracker).

Fan out reading, not decisions: one read-only probe per area finds behavior, shape, and tests with `file:line` evidence. Architect decides. Ticket keys use profile casing; a false "missing" issue suggests stale auth.

The architect writes `$WS/harness/scratchpad/plans/<TICKET>.md` per [plan-template.md](plan-template.md).

## 2. Plan review + rewrite loop — gate, no human

Run [plan-review.md](plan-review.md) with [reviewer](../agents/reviewer.md), using a **different model family** from the architect ([runner](plan-review.md#runner)). No code before approval.

1. Check ticket coverage, testability, symbols, ownership, contracts, tests, assumptions.
2. Blocker/Major → architect rewrites `<TICKET>.md`; re-review.
3. Cap at 3 cycles; then stop.

Each pass writes `$WS/harness/scratchpad/plans/<TICKET>-plan-review-<n>.md`.

Ask the human only for scope/behavior with no safe assumption, unowned scope, undefined completion, or a hit cap ([human](plan-review.md#human)). `Approve` authorizes downstream commits and PRs.

On `Approve`, **if the profile declares an in-progress transition** ([AGENTS.md › Tracker](../../AGENTS.md#tracker) · [tracker › Transitions](tracker.md#transitions)), run it here — the flow's only chance, and step 7's transition is invalid from the initial state. Where the profile declares none, make **no** tracker write here.

## 3. Development — one lane per repo, no barrier downstream

Dev roles run [implement-change.md](implement-change.md). One worktree, branch, and PR per repo. Finished lanes advance immediately.

- [agents/backend-dev.md](../agents/backend-dev.md) — the plan's backend paths, in [dependency order](../../AGENTS.md#dependency-order).
- [agents/frontend-dev.md](../agents/frontend-dev.md) — only the client app(s) it owns. Work in an app no role owns → stop and report.
- Both in the **same repo** → they share its worktree and branch, sequentially in dependency order; the second starts from the first's work log and does not re-cut a branch.

Parallel repos require a pinned contract; otherwise provider precedes consumer. Dev writes complete mirrored tests and **collects but never executes** them ([collect](implement-change.md#collect)) — collection costs a second and catches the mechanical defects blind writing produces, each of which otherwise costs a full step 4 + 5 cycle. Run exactly the profile's verification commands ([verify](implement-change.md#verify)).

**Start QA's stack boot here**, as soon as the first lane reports done ([qa-verify › Pre-warm](qa-verify.md#prewarm)) — boot and seed cost minutes and depend on the checkout, not on review.

## 4. Internal review + fix loop — lint only, no tests run

Run [internal-review.md](internal-review.md) on each local diff before push. Nothing leaves the workspace.

1. Concurrently check profile commands, tests, and design; merge verdict. Never run tests.
2. Require a real mirror test for every source and branch.
3. Blocker/Major → owner fixes and verifies; re-review. Fix cheap nits.
4. Cap at 3 cycles.

Each pass writes `$WS/harness/scratchpad/plans/<TICKET>-review-<n>.md`; release reads the highest `<n>`.

## 5. Unit tests — the change's tests only, in parallel

Run [run-unit-tests.md](run-unit-tests.md) per repo as soon as review passes. This is the first test execution.

1. Select changed tests, source mirrors, and tests naming changed symbols ([selection](run-unit-tests.md#selection)).
2. Run one concurrent lane per profile area ([lanes](run-unit-tests.md#lanes)).
3. Verify collection, counts, and coverage — not only exit zero.
4. Fail → owner fixes; repeat review, then tests. Cap at 3 cycles.

Each pass writes `$WS/harness/scratchpad/plans/<TICKET>-tests-<n>.md` plus one log per lane; release reads the highest `<n>`.

## 6. QA on the local stack + fix loop

Run [qa-verify.md](qa-verify.md) on the dev worktrees and [local stack](../../AGENTS.md#stack).

1. Verify every requirement and adjacent regression; parallelize independent flows. Save one proof per requirement under `$WS/harness/scratchpad/proofs/<TICKET>/`.
2. Blocker/Major → owner fixes; repeat review, tests, QA.
3. Cap at 3 cycles.

Each pass writes `$WS/harness/scratchpad/plans/<TICKET>-qa-<n>.md`. Read its **Not verified** section — the stack cannot exercise everything ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)), and what is listed ships on unit tests alone.

## 7. Release

Run [release-pr.md](release-pr.md): commit, push, one PR per repo, proofs, PR-link comment, and only profile-declared tracker transitions.

Commit/push repos concurrently; open PRs in dependency order so consumers link providers. Draft bodies during QA.

All outward text comes from [commenter](../agents/commenter.md) and uses a quoted heredoc ([shell quoting](../README.md#shell-quoting)).

## 8. CI + review watch loop — the PR is not done until this is quiet

CI runs the full suite. A configured bot must also go quiet; without one, wait only for CI and handle existing human comments once ([release](release-pr.md#ci)).

0. Watch PRs concurrently; run [PR review](pr-review.md) during CI.
1. Red check → read failing log; route code failures, rerun one flake, escalate infra/secrets.
2. Bot comment → fix or reject with reason; never leave a thread silent. No bot → handle current human comments, no silence gate.
3. Push fixes on the same branch, back to 1 — a push restarts CI and, only where configured, the bot.
4. Cap bot waves at 3.

Never weaken CI — no lowered coverage threshold, no `skip`/`xfail` on a genuinely failing test, no disabled lint rule. Remove worktrees only after green: removing one destroys the place a fix would happen.

## Output

PR URLs in dependency order · ticket state · plan/code review verdicts · unit tests per lane and CI remainder · QA and proofs · CI state/fixes · review responses · gaps and assumptions.

<a id="stop-conditions"></a>
## Stop conditions

Stop for: unsafe scope/behavior decision · unowned repo · loop cap · refused missing test · CI infra/secrets · failed required commit mode · failed authorized tracker call · stack still down after one reset/restart · undefined product decision. Record safe assumptions; continue.

Check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) before any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
