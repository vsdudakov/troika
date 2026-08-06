---
name: develop-flow
description: The full pipeline from ticket to merge-ready PR — plan, plan review loop, parallel dev, internal review loop, parallel unit tests on the change only, QA on the local stack, release.
---

# Develop flow

Ticket to PR. The orchestrator spawns one [role](../../ROLES.md) per phase; roles never call each other.

Model and effort are passed at spawn, never read from the file ([agents › Model and effort](../../ROLES.md#model-and-effort)):

```bash
# architect — Claude, high effort
claude --model claude-fable-5 --effort high -p "read ${CLAUDE_PLUGIN_ROOT}/agents/architect.md and act as that role for <TICKET>"
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

Tests run locally once: dev writes (3), reviewer reads (4), [tester](../../agents/tester.md) runs change tests (5), CI runs all (8). The human is not a gate; ask only under [Stop conditions](#stop-conditions).

<a id="lanes"></a>
## Lanes — one per repository

- **Two repos:** two worktrees, branches, PRs; parallel only with a pinned contract.
- **One repo, many roles:** one worktree, branch, PR. Roles take turns in dependency order (`#dependency-order`), inside their ownership (`#ownership`).

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
| Provider PR → consumer PR | dependency order ([cross-repo](../cross-repo/SKILL.md)) |
| A suite the profile marks sequential | correctness, not speed (PROFILE.md › Gotchas (`#gotchas`)) |
| Migration work inside one repo | migration numbers collide silently |

Report wall clock per lane. Resolve the paths once (`plugin/resolve.py`); all handoff paths are absolute (workspace paths (`#workspace-paths`)).

## 0. Fan out — index, ticket, memory, all at once

Start together; join before planning:

1. Refresh each repo index from its root (code search (`#code-search`)); dev repeats this in its worktree.
2. Read every ticket surface ([plan-review](../plan-review/SKILL.md#ticket-surfaces)).
3. Run `ls $TROIKA_MEMORY/*.md`; read every entry ([memory](../memory/SKILL.md)).

## 1. Collect requirements and plan

Run [agents/architect.md](../../agents/architect.md) on the step 0 material — tracker access and auth check in PROFILE.md › Tracker (`#tracker`).

Fan out reading, not decisions: one read-only probe per area finds behavior, shape, and tests with `file:line` evidence. Architect decides. Ticket keys use profile casing; a false "missing" issue suggests stale auth.

The architect writes `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` per [plan-template.md](../plan-template/SKILL.md).

## 2. Plan review + rewrite loop — gate, no human

Run [plan-review.md](../plan-review/SKILL.md) with [reviewer](../../agents/reviewer.md), using a **different model family** from the architect ([runner](../plan-review/SKILL.md#runner)). No code before approval.

1. Check ticket coverage, testability, symbols, ownership, contracts, tests, assumptions.
2. Blocker/Major → architect rewrites `<TICKET>.md`; re-review.
3. Cap at 3 cycles; then stop.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-plan-review-<n>.md`.

Ask the human only for scope/behavior with no safe assumption, unowned scope, undefined completion, or a hit cap ([human](../plan-review/SKILL.md#human)). `Approve` authorizes downstream commits and PRs.

On `Approve`, **if the profile declares an in-progress transition** (PROFILE.md › Tracker (`#tracker`) · [tracker › Transitions](../tracker/SKILL.md#transitions)), run it here — the flow's only chance, and step 7's transition is invalid from the initial state. Where the profile declares none, make **no** tracker write here.

## 3. Development — one lane per repo, no barrier downstream

Dev roles run [implement-change.md](../implement-change/SKILL.md). One worktree, branch, and PR per repo. Finished lanes advance immediately.

- [agents/backend-dev.md](../../agents/backend-dev.md) — the plan's backend paths, in dependency order (`#dependency-order`).
- [agents/frontend-dev.md](../../agents/frontend-dev.md) — only the client app(s) it owns. Work in an app no role owns → stop and report.
- Both in the **same repo** → they share its worktree and branch, sequentially in dependency order; the second starts from the first's work log and does not re-cut a branch.

Parallel repos require a pinned contract; otherwise provider precedes consumer. Dev writes complete mirrored tests and **collects but never executes** them ([collect](../implement-change/SKILL.md#collect)) — collection costs a second and catches the mechanical defects blind writing produces, each of which otherwise costs a full step 4 + 5 cycle. Run exactly the profile's verification commands ([verify](../implement-change/SKILL.md#verify)).

**Start QA's stack boot here**, as soon as the first lane reports done ([qa-verify › Pre-warm](../qa-verify/SKILL.md#prewarm)) — boot and seed cost minutes and depend on the checkout, not on review.

## 4. Internal review + fix loop — lint only, no tests run

Run [internal-review.md](../internal-review/SKILL.md) on each local diff before push. Nothing leaves the workspace.

1. Concurrently check profile commands, tests, and design; merge verdict. Never run tests.
2. Require a real mirror test for every source and branch.
3. Blocker/Major → owner fixes and verifies; re-review. Fix cheap nits.
4. Cap at 3 cycles.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-review-<n>.md`; release reads the highest `<n>`.

## 5. Unit tests — the change's tests only, in parallel

Run [run-unit-tests.md](../run-unit-tests/SKILL.md) per repo as soon as review passes. This is the first test execution.

1. Select changed tests, source mirrors, and tests naming changed symbols ([selection](../run-unit-tests/SKILL.md#selection)).
2. Run one concurrent lane per profile area ([lanes](../run-unit-tests/SKILL.md#lanes)).
3. Verify collection, counts, and coverage — not only exit zero.
4. Fail → owner fixes; repeat review, then tests. Cap at 3 cycles.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-tests-<n>.md` plus one log per lane; release reads the highest `<n>`.

## 6. QA on the local stack + fix loop

Run [qa-verify.md](../qa-verify/SKILL.md) on the dev worktrees and local stack (`#stack`).

1. Verify every requirement and adjacent regression; parallelize independent flows. Save one proof per requirement under `$TROIKA_SCRATCHPAD/proofs/<TICKET>/`.
2. Blocker/Major → owner fixes; repeat review, tests, QA.
3. Cap at 3 cycles.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-qa-<n>.md`. Read its **Not verified** section — the stack cannot exercise everything (PROFILE.md › Stack limits (`#stack-limits`)), and what is listed ships on unit tests alone.

## 7. Release

Run [release-pr.md](../release-pr/SKILL.md): commit, push, one PR per repo, proofs, PR-link comment, and only profile-declared tracker transitions.

Commit/push repos concurrently; open PRs in dependency order so consumers link providers. Draft bodies during QA.

All outward text comes from [commenter](../../agents/commenter.md) and uses a quoted heredoc ([shell quoting](../../README.md#shell-quoting)).

## 8. CI + review watch loop — the PR is not done until this is quiet

CI runs the full suite. A configured bot must also go quiet; without one, wait only for CI and handle existing human comments once ([release](../release-pr/SKILL.md#ci)).

0. Watch PRs concurrently; run [PR review](../pr-review/SKILL.md) during CI.
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

Check PROFILE.md › Gotchas (`#gotchas`) before any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
