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

**Effort is per pass, not per role.** The row's effort is what a role's *first* pass costs. A pass that re-enters a gate after a fix ([Re-entry](#reentry)) reads a fraction of the work the first one did, so it runs **one effort tier down** from the row — a re-review of a four-line fix does not need the depth that found it. Two exceptions keep their row's effort: a re-entry that [widened to full scope](#reentry), and the last cycle the loop cap allows, which is the one whose verdict stops the flow. Say in each cycle's report which tier it ran at; a cycle nobody can price is one nobody can tune.

**Kind** procedure · **Used by** orchestrator · **When** a ticket or described change needs shipping · **Ends with** one PR per touched repo — CI green, review quiet, proofs attached, ticket updated per the profile

**The ticket's kind picks steps 1 and 2, and nothing else.** A bug is reproduced before it is fixed; a feature is planned before it is built. From step 3 on, the two paths are the same flow ([Kind](#kind)).

| Step | Who runs it | Advance only when | Cap | Writes |
| --- | --- | --- | --- | --- |
| 0 | orchestrator ∥ index · ticket · memory | the kind is decided from evidence | — | — |
| 1b *(bug)* | architect ∥ cause probes ∥ QA pre-warm | the brief has steps, observed, expected | — | `plans/<TICKET>.md` |
| 2b *(bug)* | qa, on the **base checkout** | `Reproduced`, or `Reproduced differently` | 2 attempts | `-repro-<n>.md` + the `before` proof |
| 1f *(feature)* | architect ∥ read-only probes | the plan follows [plan-template](../plan-template/SKILL.md) | — | `plans/<TICKET>.md` |
| 2f *(feature)* | reviewer, other model family ∥ 2 lenses | `Approve` / `Approve with nits` | `#loops` | `-plan-review-<n>.md` |
| 2r | commenter asks, the reporter answers — **only under `--ask`** | *go ahead* | 2 | the answer, in the plan file |
| 3 | dev roles, one lane per repo | profile verification commands green, tests written and collected | — | `-<role>.md` |
| 4 | reviewer ∥ 3 dimensions per lane | no Blocker or Major open | `#loops` | `-review-<n>.md` |
| 5 | tester ∥ one lane per area, started with 4, not after it | the change's tests green, counts checked | `#loops` | `-tests-<n>.md` |
| 6 | qa, on the local stack | `Pass`, one before/after proof per requirement | `#loops` | `-qa-<n>.md`, `proofs/<TICKET>/` |
| 7 | releaser | one PR per repo, proofs attached, PRs in dependency order | — | the PRs |
| 8 | releaser ∥ per PR | CI green and the bots quiet, then the post-PR actions | `#loops` waves | tracker writes · worktree cleanup |

`#loops` in the Cap column is the profile's loop cap (PROFILE.md › Loop cap (`#loops`)), default 3. Failed gate → back to the owning role, never forward. `∥` means concurrent, and **a lane is a repo, not a role** ([Lanes](#lanes)); sibling lanes do not wait. Barriers: the step-2 join (a confirmed reproduction or an approved plan, plus the reporter under `--ask`), the pre-QA join, CI.

Tests run locally once: dev writes (3), reviewer reads (4), [tester](../../agents/tester.md) runs change tests (5), CI runs all (8). Exactly one gate waits for a person — [2r](#reporter-review), and only under `--ask` ([Autonomy](#autonomy)); everywhere else the human is reached only under [Stop conditions](#stop-conditions).

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
| Internal review and the change's unit tests, in one lane (4 ∥ 5) | the reviewer is read-only and the tester writes nothing, so neither can disturb the other's view of the worktree ([4 ∥ 5](#review-tests)) |
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
| A fix → its re-review and its re-test | a fix is a diff, and no diff advances unreviewed — but the two gates it re-enters run concurrently, exactly as they do on the first pass |
| All lanes → QA | one stack, one branch under test |
| Provider PR → consumer PR | dependency order ([cross-repo](../cross-repo/SKILL.md)) |
| A suite the profile marks sequential | correctness, not speed (PROFILE.md › Gotchas (`#gotchas`)) |
| Migration work inside one repo | migration numbers collide silently |

Resolve the paths once (`plugin/resolve.py`); all handoff paths are absolute (workspace paths (`#workspace-paths`)).

<a id="reentry"></a>
## Re-entry — a fix re-runs the fix, not the whole change

Steps 4, 5 and 6 all loop the same way: a Blocker goes back to the owning dev role, and the gates run again. **The second run is scoped to the fix.** Re-reviewing a diff that already passed, re-running tests that already went green and re-capturing proofs of requirements nobody touched is the single most expensive habit in this flow — one late QA finding otherwise costs a full 4 → 5 → 6 cascade on a four-line change, up to `#loops` times.

Nothing about the gates weakens. What narrows is their input.

<a id="snapshot"></a>
### The snapshot — what makes the fix diff computable

Nothing is committed before step 7, so there is no ref to diff a fix against. Make one: **every role that passes a gate hashes the diff's files before it reports**, in each worktree it cleared.

```bash
cd "$TROIKA_WORKTREES/<repo>-<TICKET>"
git add -N -- .                                        # untracked files count as changed
{ git --no-pager diff --name-only "$BASE"...HEAD; git --no-pager diff --name-only; } \
  | sort -u | xargs -r shasum > "$TROIKA_SCRATCHPAD/plans/<TICKET>-<repo>-cycle-<n>.sha"
```

At the next cycle, re-run the same command and compare: **the fix's files are the ones whose hash changed, plus the ones the list gained.** That is checkable evidence, not a dev role's account of what it touched — a fixer who quietly edited a fourth file cannot narrow a gate away from it.

A missing snapshot is not a licence to guess: the cycle runs at full scope and the report says the snapshot was missing.

<a id="reentry-scope"></a>
### What each gate re-runs

| Gate | Cycle 1 | Cycle 2+ |
| --- | --- | --- |
| **4 · review** | the whole diff, nine checks | the fix's files, nine checks, plus every finding the previous cycle raised — including the ones it accepted as fixed |
| **5 · tests** | the full [selection](../run-unit-tests/SKILL.md#selection) | the node IDs that failed · the mirror tests of the fix's files · every test the fix added or changed |
| **6 · QA** | before and after per requirement | the after proof of each failed requirement, and of any requirement whose code path the fix's files sit on. **Before proofs are never re-captured** — the base checkout did not move |

The findings from earlier cycles travel with the scope. A narrowed re-review still reads `-review-<n-1>.md` and confirms each Blocker is actually gone; narrowing the diff never narrows the verdict.

<a id="widen"></a>
### When re-entry widens back to full scope

Some files have a blast radius the fix diff cannot express. If any of the fix's files is one of these, the cycle runs at **cycle-1 scope**, and the report says which file widened it:

- a shared model, base class, utility, config, middleware or public contract — the same classes [internal review](../internal-review/SKILL.md) already names as regression risk
- a migration, in any repo
- a test fixture or conftest other tests inherit from
- anything the profile marks as sequential or fragile (PROFILE.md › Gotchas (`#gotchas`))

Also widen when the fix changed the plan's contract, when the previous cycle's snapshot is missing, and on the **last cycle the loop cap allows** — the one whose verdict stops the flow deserves the full read.

<a id="timing"></a>
## Timing — every step is stamped, or none of this is tunable

Take a UTC stamp when each step starts and when it ends, per lane where the step has lanes:

```bash
date -u +%FT%TZ
```

Report the elapsed time of every step in the run's [Output](#output), including the ones that waited on something outside the flow — a stack boot, a CI queue, a person under `--ask`. **Separate waiting from working**: a step that took forty minutes because CI was queued and a step that took forty minutes of review are the same number and completely different problems, and a report that cannot tell them apart sends the next tuning pass at the wrong target.

Write a [`memory/`](../memory/SKILL.md) entry, with its `**Cost:**` line, when a step cost far more than the run's shape predicts — a gate that looped to its cap, a suite whose narrow selection still took tens of minutes, a stack that needed three boots. Those entries are what turn one slow run into a rule.

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

On **Reproduced**, run the profile's in-progress transition if it declares one (PROFILE.md › Tracker (`#tracker`) · [tracker › Transitions](../tracker/SKILL.md#transitions)) — the flow's only chance, exactly as `Approve` is on the feature path. **Under `--ask`, run it after [2r](#reporter-review) answers**: a ticket moved to in progress and then rejected by its own reporter is a board state nobody can explain.

## 1f. Feature — collect requirements and plan

Runs when step 0 classified the ticket as a feature. Run [agents/architect.md](../../agents/architect.md) on the step 0 material — tracker access and auth check in PROFILE.md › Tracker (`#tracker`).

Fan out reading, not decisions: one read-only probe per area finds behavior, shape, and tests with `file:line` evidence. Architect decides. Ticket keys use profile casing; a false "missing" issue suggests stale auth.

The architect writes `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` per [plan-template.md](../plan-template/SKILL.md).

## 2f. Feature — plan review + rewrite loop — gate, no human

Run [plan-review.md](../plan-review/SKILL.md) with [reviewer](../../agents/reviewer.md), using a **different model family** from the architect ([runner](../plan-review/SKILL.md#runner)). No code before approval.

1. Check ticket coverage, testability, symbols, ownership, contracts, tests, assumptions.
2. Blocker/Major → architect rewrites `<TICKET>.md`; re-review.
3. Cap at the profile's loop cap (`#loops`, default 3) cycles; then stop.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-plan-review-<n>.md`.

Ask the human only for scope/behavior with no safe assumption, unowned scope, undefined completion, or a hit cap ([human](../plan-review/SKILL.md#human)). `Approve` authorizes downstream commits and PRs.

On `Approve`, **if the profile declares an in-progress transition** (PROFILE.md › Tracker (`#tracker`) · [tracker › Transitions](../tracker/SKILL.md#transitions)), run it here — the flow's only chance, and step 7's transition is invalid from the initial state. **Under `--ask`, run it after [2r](#reporter-review) answers** instead, for the same reason. Where the profile declares none, make **no** tracker write here.

<a id="reporter-review"></a>
## 2r. Reporter review — the one gate that waits for a person

Runs on both paths, after step 2 has produced its evidence: an approved plan, or a confirmed reproduction. **Only a run carrying `--ask` reaches this step** ([Autonomy](#autonomy)); without it the flow goes straight to step 3. Asked for but impossible — no reporter and no channel in the profile (`#autonomy`) — is a stop, not a silent skip: the run was told to wait for somebody nobody named.

The point is not approval as ceremony. The reviewer already checked the plan against the ticket; the reporter is the only party who can say the *ticket* itself described the wrong thing.

1. [commenter](../../agents/commenter.md) writes one message, in the workspace's voice (`#voice`), to the reporter and the channel the profile names (`#autonomy`): what will be built or fixed, as numbered requirements; every assumption made for them; and — on the bug path — what was reproduced and whether it matches what they reported.
2. Ask for one of three answers: **go ahead**, **change this** (with what), **not this at all**.
3. Wait as long as the profile declares. When the wait runs out, do exactly what the profile says — proceed and record it, or stop. Where it says neither, stop and ask the operator: a silent timeout that starts writing code is an unattended run nobody asked for.

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
3. Blocker/Major → owner fixes and verifies; re-review, at [re-entry scope](#reentry). Fix cheap nits.
4. Cap at the profile's loop cap (`#loops`, default 3) cycles.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-review-<n>.md`; release reads the highest `<n>`.

<a id="review-tests"></a>
### 4 ∥ 5 — review and the tests run at the same time

Both start the moment the lane reports done. The reviewer is read-only and the tester writes nothing, so one worktree carries both without breaking the one-writer rule.

They were once ordered, on the argument that review removes what a test run finds the slow way. That argument is about *tokens*, and the tests are the cheap half — a machine run of a narrow node-ID selection. Ordering them spends a full test cycle of wall clock to save a test run the flow usually needs anyway.

| Outcome | What happens to the concurrent run |
| --- | --- |
| review `Approve` / `Approve with nits` | the test result already in hand is the step-5 result — nothing re-runs |
| review Blocker or Major, fix touches **no** source the tests cover | the test result stands; only the fix's own new tests are added at step 5's next cycle |
| review Blocker or Major, fix touches a covered source | discard that lane's run and re-run at [re-entry scope](#reentry) — a green result for code that no longer exists is worse than no result |

The gate order does not move: release still needs both a passing review and a passing test report, and a lane reaching QA on one of the two is a stop.

## 5. Unit tests — the change's tests only, in parallel

Run [run-unit-tests.md](../run-unit-tests/SKILL.md) per repo as soon as the lane reports done — **concurrently with step 4**, not after it ([4 ∥ 5](#review-tests)). This is the first test execution.

1. Select changed tests, source mirrors, and tests naming changed symbols ([selection](../run-unit-tests/SKILL.md#selection)).
2. Run one concurrent lane per profile area ([lanes](../run-unit-tests/SKILL.md#lanes)).
3. Verify collection, counts, and coverage — not only exit zero.
4. Fail → owner fixes; review and tests run again together, both at [re-entry scope](#reentry). Cap at the profile's loop cap (`#loops`, default 3) cycles.

Each pass writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-tests-<n>.md` plus one log per lane; release reads the highest `<n>`.

## 6. QA on the local stack + fix loop — before and after

Run [qa-verify.md](../qa-verify/SKILL.md) on the dev worktrees and local stack (`#stack`).

1. Verify every requirement and adjacent regression; parallelize independent flows. Save a **before and an after** proof per requirement under `$TROIKA_SCRATCHPAD/proofs/<TICKET>/` — the before side on the base checkout, the after side on the branch. Net-new behaviour has no before: `n/a — new`, never a staged one.
2. **On the bug path the before proof already exists** — step 2b captured the failure. Reuse that file; recording it again on the base checkout costs a stack restart and proves nothing new.
3. Blocker/Major → owner fixes; review, tests and QA run again at [re-entry scope](#reentry) — the fix's files, the failed tests, the failed requirement's after proof, and nothing else unless the fix [widened](#widen) it.
4. Cap at the profile's loop cap (`#loops`, default 3) cycles.

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

Then the [timing](#timing) table — one row per step, per lane where the step has lanes:

```markdown
| Step | Lane | Elapsed | Of which waiting | Cycles | Effort tier |
| --- | --- | --- | --- | --- | --- |
| 4 review | <repo> | 12m | — | 2 (1 narrowed) | high, then medium |
| 8 CI | <repo> | 41m | 38m — queue + suite | 1 wave | — |
| **Total** | | **<wall clock>** | **<sum>** | | |
```

A cycle counted here says whether it ran at cycle-1 or [re-entry](#reentry) scope, and a widened one says [which file widened it](#widen). Wall clock is the run's, not the sum of the rows — the lanes overlap, and that overlap is the point.

<a id="stop-conditions"></a>
## Stop conditions

Stop for: a bug that will not reproduce · a reporter answering "not this at all", or a hit reporter-review cap · a decision the profile marks never-automatic, reached without `--ask` · an open question with no safe assumption on an unattended run · a second escalation from the bug path to the feature path · unsafe scope/behavior decision · unowned repo · loop cap · refused missing test · CI infra/secrets · failed required commit mode · failed authorized tracker call · stack still down after one reset/restart · undefined product decision. Record safe assumptions; continue.

Check PROFILE.md › Gotchas (`#gotchas`) before any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
