---
name: develop-flow
description: The full pipeline from ticket to merge-ready PR — bug tickets reproduce first, feature tickets plan first, then parallel dev, internal review loop, unit tests on the change only, QA before/after on the local stack, release, CI.
---

# Develop flow

Ticket to PR. The orchestrator spawns one [role](../../ROLES.md) per phase; roles never call each other.

Model and effort are passed at spawn, never read from a role file, and their values come from the workspace — PROFILE.md › Models and effort (`#models`), one row per role ([agents › Model and effort](../../ROLES.md#model-and-effort)):

```bash
# architect — its row's model and effort
claude --model <the architect row's model> --effort <its effort> -p "read ${CLAUDE_PLUGIN_ROOT}/agents/architect.md and act as that role for <TICKET>"
# reviewer — its row, on a different family from whoever wrote the code (PROFILE.md › `#review-runner`)
```

Subagents inherit session effort; use the highest effort any role needs.

**Kind** procedure · **Used by** orchestrator · **When** a ticket or described change needs shipping · **Ends with** one PR per touched repo — CI green, review quiet, proofs attached, ticket updated per the profile

**The ticket's kind picks steps 1 and 2, and nothing else.** A bug is reproduced before it is fixed; a feature is planned before it is built. From step 3 on, the two paths are the same flow ([Kind](#kind)).

```
ticket
  └─ 0 ∥ index refresh per repo · ticket surfaces (comments, attachments, links) · memory
        └─ classify: bug | feature ────────────────────────┐
        │                                                  │
   ┌────┴──── bug ────────────────────┐   ┌──── feature ───┴──────────────────────┐
   ▼ 1b ∥ steps to reproduce (brief)  │   ▼ 1f architect ── plan ◀── ∥ read-only  │
        ∥ cause probes, read-only     │        probes, one per repo/area          │
        ∥ QA stack pre-warm starts    │                                           │
   ▼ 2b QA reproduces on the base ────┤   ▼ 2f plan review ∥ 2 lenses (other      │
        checkout — the failing        │        model family) ── rewrite loop      │
        capture IS the `before` proof │        (max 3) ── approved                │
   └────┬─────────────────────────────┘   └───────────────┬───────────────────────┘
        ▼ 2r reporter review ── change requested ──▶ back to 1b / 1f (max 2)
        │    runs only under `--ask` ([Autonomy](#autonomy))
        ▼ join — reproduced or planned, and confirmed
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
        ▼ 6 QA on local stack — before/after per requirement (∥ capture) + fix loop (max 3)
        ▼ 7 release ── ∥ commit+push per repo · PR bodies drafted during 6
        │              PRs opened in dependency order, QA proofs attached
        ▼ 8 ∥ per PR: CI watch + review waves + PR review (max 3) ──▶ green + quiet
        ▼   post-PR actions: profile's tracker writes · worktree cleanup
```

`∥` means concurrent. **A lane is a repo, not a role** ([Lanes](#lanes)). Sibling lanes do not wait. Barriers: the step-2 join (a confirmed reproduction or an approved plan, plus the reporter where the mode asks for one), the pre-QA join, CI.

Tests run locally once: dev writes (3), reviewer reads (4), [tester](../../agents/tester.md) runs change tests (5), CI runs all (8). Exactly one gate waits for a person — [2r](#reporter-review), and only in `ask` mode ([Autonomy](#autonomy)); everywhere else the human is reached only under [Stop conditions](#stop-conditions).

<a id="kind"></a>
## Kind — bug or feature, decided at step 0

Decide it once, from evidence, and say which and why before any lane starts.

| Kind | What the ticket looks like | Steps 1 – 2 |
| --- | --- | --- |
| **Bug** | behaviour that already exists is wrong — observed versus expected, a stack trace, an error, a screenshot of the wrong screen, a Sentry link | 1b steps to reproduce · 2b **reproduce it on the base checkout** |
| **Feature** | behaviour that does not exist yet, or a deliberate change to what is correct today | 1f plan · 2f **plan review loop** |

Read the evidence in this order: the tracker's own type or label field first, where the profile declares one (`#tracker`); then the ticket's text. A `Bug` type on a ticket asking for a new export format is a mislabelled feature — the text wins, and the report says the label disagreed.

Two rules for the awkward cases:

- **Both in one ticket** — a fix *and* new behaviour — runs the **feature** path. The plan carries the fix as a numbered requirement, and the reproduction becomes that requirement's QA proof.
- **Not decidable from the evidence** — run the **feature** path and name what was ambiguous. Planning a bug costs one step; skipping the plan for a feature ships an unplanned change.

A bug that turns out to need a design decision, or to span repos with a contract between them, **escalates to the feature path**: write the plan, run step 2f, then continue. Escalate once; a second escalation is a stop.

<a id="autonomy"></a>
## Autonomy — unattended by default, `--ask` to stop for the reporter

One gate in this flow waits for a person: [2r, the reporter review](#reporter-review). It runs **only when the run asks for it**:

```
/tr:dev SCRUM-123            # unattended: no gate waits for a person
/tr:dev SCRUM-123 --ask      # stop at 2r and wait for the reporter's answer
```

There is no opposite flag, because there is nothing to turn off: a plain run is already the autonomous one.

| Run | Step 2r | An open question with a safe assumption | An open question with no safe assumption |
| --- | --- | --- | --- |
| no flag | skipped | assume, record it, continue | **stop** — running unattended removes the approval, not the judgment |
| `--ask` | runs | assume, record it, continue | ask the reporter |

Say in the first line of the run's output whether it ran unattended or with `--ask`. A run whose mode nobody can name afterwards is one nobody can audit.

Unattended **never** silences a [stop condition](#stop-conditions). A hit loop cap, an unowned repo, a bug that will not reproduce, a failed tracker write, a stack that will not boot: all still stop the run. Nor does it override the decisions the profile marks as never-automatic (PROFILE.md › Autonomy (`#autonomy`)) — scope changes, irreversible migrations, public contract changes, production deploys. Reaching one of those without `--ask` is a stop, and the report says which one.

Everything an unattended run assumed is written twice: in the plan's **Assumed** lines and in the PR body, so the human reading the PR sees what was decided without them.

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
| Classification while the index refreshes (0) | it reads the ticket, not the code |
| Read-only code probes, one per repo or area (1f, 1b) | no writes; the architect synthesizes them |
| Repro-step collection, cause probes and the stack pre-warm (1b) | the first two are read-only, the third writes only stack state |
| The reproduction pass and the lanes cutting their worktrees (2b) | a worktree checkout is not a product edit, and no code is written until 2b returns |
| The two plan-review lenses (2f) | read-only; findings merged before the rewrite |
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
| Classification → step 1 | it picks which step 1 runs |
| The reporter review (2r) → any product code, under `--ask` | its answer can change the requirements the lanes would code against |
| Plan → any product code (feature) | the plan is the contract every lane codes against |
| Reproduction → any fix (bug) | a fix for a bug nobody has seen fail is a guess, and its regression test has nothing to encode |
| The reproduction pass → any dev branch on the stack | 2b runs on the base checkout; a dev branch under it would hide the bug it exists to show |
| Dev roles sharing one repo's worktree (3) | one checkout, one branch — they take turns in dependency order |
| Review → tests, inside a lane | review removes what a test run finds the slow way |
| A fix → re-review → re-test | a fix is a diff, and no diff advances unreviewed |
| All lanes → QA | one stack, one branch under test |
| Provider PR → consumer PR | dependency order ([cross-repo](../cross-repo/SKILL.md)) |
| A suite the profile marks sequential | correctness, not speed (PROFILE.md › Gotchas (`#gotchas`)) |
| Migration work inside one repo | migration numbers collide silently |

Report wall clock per lane. Resolve the paths once (`plugin/resolve.py`); all handoff paths are absolute (workspace paths (`#workspace-paths`)).

## 0. Fan out — index, ticket, memory, kind, all at once

Start together; join before step 1:

1. Refresh each repo index from its root (code search (`#code-search`)); dev repeats this in its worktree.
2. Read every ticket surface ([plan-review](../plan-review/SKILL.md#ticket-surfaces)).
3. Run `ls $TROIKA_MEMORY/*.md`; read every entry ([memory](../memory/SKILL.md)).
4. Classify the ticket — bug or feature ([Kind](#kind)) — and report the kind and the evidence for it. It picks steps 1 and 2.

## 1b. Bug — collect the steps to reproduce

Runs when step 0 classified the ticket as a bug. Three things start at once:

1. **The steps to reproduce.** [architect](../../agents/architect.md) collects them from every ticket surface — the reporter's own words, the attachments, the stack trace, the linked incident ([incident-triage](../incident-triage/SKILL.md) where the source is the observability platform) — and writes `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` as a [bug brief](../plan-template/SKILL.md#bug-brief): environment, exact steps, observed, expected, numbered fix requirements, and the regression test the fix must carry. Where the ticket has no steps, derive candidates from the code and **say they are derived** — a derived repro that fails at 2b is a finding about the ticket, not about the code.
2. **Cause probes**, read-only, one per repo or area: where the reported behaviour is produced, with `file:line`. They locate; they never fix.
3. **QA's stack pre-warm** ([qa-verify › Pre-warm](../qa-verify/SKILL.md#prewarm)) — earlier than on the feature path, because step 2b needs a running stack on the **base checkout**.

## 2b. Bug — reproduce on the base checkout, before any fix

Run [qa-verify.md](../qa-verify/SKILL.md#reproduce) in its reproduction pass, against the base ref (`#branches`), not a dev branch. This is the bug path's gate, and it replaces the plan-review loop: a reproduction is evidence, where a review of an unverified guess is an opinion.

1. Walk the brief's steps on the running stack and capture the failure — GIF for a user-visible bug, request plus datastore transcript for a backend one.
2. **That capture is the `before` proof** for the matching requirement; step 6 records only the `after` side and never re-stages it.
3. Write `$TROIKA_SCRATCHPAD/plans/<TICKET>-repro-<n>.md` and update the brief with what actually happened.

| Verdict | What happens |
| --- | --- |
| **Reproduced** | the flow is authorized to code — go to step 3 |
| **Reproduced differently** | the brief's observed behaviour is corrected to what was seen, and *that* becomes the requirement |
| **Not reproduced** | **stop and report.** Never fix blind. Say what was tried, on which ref, with which data, and what the reporter must supply — an environment, a data shape, a user role, a version |

Cap at 2 reproduction attempts before stopping; a third variation of the steps is a question for the reporter, not another run.

On **Reproduced**, run the profile's in-progress transition if it declares one (PROFILE.md › Tracker (`#tracker`) · [tracker › Transitions](../tracker/SKILL.md#transitions)) — the flow's only chance, exactly as `Approve` is on the feature path.

## 1f. Feature — collect requirements and plan

Runs when step 0 classified the ticket as a feature. Run [agents/architect.md](../../agents/architect.md) on the step 0 material — tracker access and auth check in PROFILE.md › Tracker (`#tracker`).

Fan out reading, not decisions: one read-only probe per area finds behavior, shape, and tests with `file:line` evidence. Architect decides. Ticket keys use profile casing; a false "missing" issue suggests stale auth.

The architect writes `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` per [plan-template.md](../plan-template/SKILL.md).

## 2f. Feature — plan review + rewrite loop — gate, no human

Run [plan-review.md](../plan-review/SKILL.md) with [reviewer](../../agents/reviewer.md), using a **different model family** from the architect ([runner](../plan-review/SKILL.md#runner)). No code before approval.

1. Check ticket coverage, testability, symbols, ownership, contracts, tests, assumptions.
2. Blocker/Major → architect rewrites `<TICKET>.md`; re-review.
3. Cap at 3 cycles; then stop.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-plan-review-<n>.md`.

Ask the human only for scope/behavior with no safe assumption, unowned scope, undefined completion, or a hit cap ([human](../plan-review/SKILL.md#human)). `Approve` authorizes downstream commits and PRs.

On `Approve`, **if the profile declares an in-progress transition** (PROFILE.md › Tracker (`#tracker`) · [tracker › Transitions](../tracker/SKILL.md#transitions)), run it here — the flow's only chance, and step 7's transition is invalid from the initial state. Where the profile declares none, make **no** tracker write here.

<a id="reporter-review"></a>
## 2r. Reporter review — the one gate that waits for a person

Runs on both paths, after step 2 has produced its evidence: an approved plan, or a confirmed reproduction. **Only a run carrying `--ask` reaches this step** ([Autonomy](#autonomy)); without it the flow goes straight to step 3. Asked for but impossible — no reporter and no channel in the profile (`#autonomy`) — is a stop, not a silent skip: the run was told to wait for somebody nobody named.

The point is not approval as ceremony. The reviewer already checked the plan against the ticket; the reporter is the only party who can say the *ticket* itself described the wrong thing.

1. [commenter](../../agents/commenter.md) writes one message, in the workspace's voice (`#voice`), to the reporter and the channel the profile names (`#autonomy`): what will be built or fixed, as numbered requirements; every assumption made for them; and — on the bug path — what was reproduced and whether it matches what they reported.
2. Ask for one of three answers: **go ahead**, **change this** (with what), **not this at all**.
3. Wait as long as the profile declares. When the wait runs out, do exactly what the profile says — proceed and record it, or stop. Where it says neither, stop and ask the operator: a silent timeout that starts writing code is `auto` nobody chose.

| Answer | What happens |
| --- | --- |
| **go ahead** | step 3 starts; the approval and its author go in the plan file and the PR body |
| **change this** | back to 1f (plan) or 1b (brief and, where the steps changed, a fresh reproduction). **Cap at 2 rounds**, then stop and hand it back |
| **not this at all** | stop. Report it; the ticket needs a human decision, not another cycle |

Nothing is committed or pushed here — this gate is before any code exists, and it is the last cheap place to be wrong.

## 3. Development — one lane per repo, no barrier downstream

Dev roles run [implement-change.md](../implement-change/SKILL.md). One worktree, branch, and PR per repo. Finished lanes advance immediately. On the bug path the brief is the plan: same numbered requirements, same ownership rules.

**A bug fix carries a regression test that encodes the reproduction** — the reproduced steps expressed as a test at the layer the cause lives in, failing for the reported reason before the fix and passing after. It is written here with the rest ([collect](../implement-change/SKILL.md#collect)), run at step 5, and checked at step 4 against `-repro-<n>.md`: a fix whose test would pass on the base checkout has not encoded the bug and is a Blocker.

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

## 6. QA on the local stack + fix loop — before and after

Run [qa-verify.md](../qa-verify/SKILL.md) on the dev worktrees and local stack (`#stack`).

1. Verify every requirement and adjacent regression; parallelize independent flows. Save a **before and an after** proof per requirement under `$TROIKA_SCRATCHPAD/proofs/<TICKET>/` — the before side on the base checkout, the after side on the branch. Net-new behaviour has no before: `n/a — new`, never a staged one.
2. **On the bug path the before proof already exists** — step 2b captured the failure. Reuse that file; recording it again on the base checkout costs a stack restart and proves nothing new.
3. Blocker/Major → owner fixes; repeat review, tests, QA.
4. Cap at 3 cycles.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-qa-<n>.md`. Read its **Not verified** section — the stack cannot exercise everything (PROFILE.md › Stack limits (`#stack-limits`)), and what is listed ships on unit tests alone.

## 7. Release

Run [release-pr.md](../release-pr/SKILL.md): commit, push, one PR per repo, proofs, PR-link comment, and only profile-declared tracker transitions.

Commit/push repos concurrently; open PRs in dependency order so consumers link providers. Draft bodies during QA.

All outward text comes from [commenter](../../agents/commenter.md) and uses a quoted heredoc ([shell quoting](../../README.md#shell-quoting)).

## 8. CI watch + post-PR actions — the PR is not done until this is quiet

CI runs the full suite. A configured bot must also go quiet; without one, wait only for CI and handle existing human comments once ([release](../release-pr/SKILL.md#ci)).

0. Watch PRs concurrently; run [PR review](../pr-review/SKILL.md) during CI.
1. Red check → read failing log; route code failures, rerun one flake, escalate infra/secrets.
2. Bot comment → fix or reject with reason; never leave a thread silent. No bot → handle current human comments, no silence gate.
3. Push fixes on the same branch, back to 1 — a push restarts CI and, only where configured, the bot.
4. Cap bot waves at 3.

Never weaken CI — no lowered coverage threshold, no `skip`/`xfail` on a genuinely failing test, no disabled lint rule.

**Post-PR actions, only once every PR is green and quiet**, in this order:

1. The tracker writes the profile declares for a PR that is ready — comment, transition, attachment (`#tracker` · [tracker](../tracker/SKILL.md)). Where it declares none, none happen, and the report says the ticket state is the humans'.
2. Remove the worktrees ([worktree › Clean up](../worktree/SKILL.md#clean-up)) — **after** green, never before: removing one destroys the place a fix would happen.
3. Report the PR URLs in dependency order. The merge itself is nobody's here; no role merges.

## Output

Kind and the evidence for it · whether the run was unattended or `--ask` · PR URLs in dependency order · ticket state · reproduction verdict (bug) or plan review verdicts (feature) · the reporter's answer, or that the run was unattended · code review verdicts · unit tests per lane and CI remainder · QA before/after proofs · CI state/fixes · review responses · gaps and assumptions.

<a id="stop-conditions"></a>
## Stop conditions

Stop for: a bug that will not reproduce · a reporter answering "not this at all", or a hit reporter-review cap · a decision the profile marks never-automatic, reached without `--ask` · an open question with no safe assumption on an unattended run · a second escalation from the bug path to the feature path · unsafe scope/behavior decision · unowned repo · loop cap · refused missing test · CI infra/secrets · failed required commit mode · failed authorized tracker call · stack still down after one reset/restart · undefined product decision. Record safe assumptions; continue.

Check PROFILE.md › Gotchas (`#gotchas`) before any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
