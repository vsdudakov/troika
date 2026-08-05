---
name: develop-flow
description: The full pipeline from ticket to merge-ready PR — plan, plan review loop, parallel dev, internal review loop, parallel unit tests on the change only, QA on the local stack, release.
---

# Develop flow

Ticket to PR, end to end. The orchestrator runs this and spawns one [role](../agents/README.md) per phase; roles never call each other.

Model and effort are passed at spawn, never read from the file ([agents › Model and effort](../agents/README.md#model-and-effort)):

```bash
# architect — Claude, high effort
claude --model claude-fable-5 --effort high -p "read $WS/llm/agents/architect.md and act as that role for <TICKET>"
# reviewer — Codex, high effort, different family from whoever wrote the code
codex -m gpt-5.6-sol -c model_reasoning_effort="high" ...
```

As subagents in one session: a subagent inherits the session's effort, so run the session at the highest effort any role in it needs.

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

`∥` marks concurrent work. **A lane is a repository, not a role** ([Lanes](#lanes)) — a monorepo has one lane however many roles touch it. **No lane waits for a sibling**: repo A can be in step 5 while repo B is in step 3. True barriers: step 2's verdict, the join before QA (one stack, one branch under test), CI.

**Who runs tests, and when.** Once locally, in step 5, by one role. Dev roles write tests and stop at the profile's verification commands (3); the reviewer reads tests, never runs them (4); the [tester](../agents/tester.md) runs the change's tests and only those, in parallel lanes (5); CI runs the whole suite (8). Any extra local run buys a signal one of those four already gives.

**The human is not a step.** Step 2's review is the gate. Ask the human only on a real question — a blocking scope or behaviour decision, a loop at its cap, an infra or credentials failure ([Stop conditions](#stop-conditions)).

<a id="lanes"></a>
## Lanes — one per repository

A worktree, a branch, and a PR are per repository, so the unit of parallelism is a repository.

- **Two repos** → two lanes, each with its own worktree, branch, PR — concurrent **only with a pinned contract** (step 1).
- **One repo, several roles** (a monorepo backend+frontend change) → **one lane**: one worktree, one branch, one PR. Roles share it, work in the repo's [dependency order](../../AGENTS.md#dependency-order), each inside its own [ownership](../../AGENTS.md#ownership) paths — never two agents writing one worktree at once, never a second role-owned branch.

**Two agents in one worktree at once is overwriting, not parallelism.** Split by repo, never by feature or role inside a repo.

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

**Report wall clock per lane**, not only the total: an idling lane is a barrier that should not be there.

Set `WS` once at the start — every handoff path below is absolute ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 0. Fan out — index, ticket, memory, all at once

Three independent jobs; start together, join before planning:

1. **Index refresh per repo** the ticket touches, from its own root ([AGENTS.md › Code search](../../AGENTS.md#code-search)) — seconds, and the difference between planning against current code and against a snapshot. Dev roles repeat it in their worktree, a separate index root (step 3).
2. **Ticket surfaces** — description, every comment in order, attachments and screenshots downloaded *and viewed*, links followed, fields ([plan-review › Every surface](plan-review.md#ticket-surfaces)). Does not wait on the code reading.
3. **Memory** — `ls $WS/llm/memory/*.md` and read them; an entry can invalidate the plan before it is written ([memory](../memory/README.md)).

## 1. Collect requirements and plan

Run [agents/architect.md](../agents/architect.md) on the step 0 material — tracker access and auth check in [AGENTS.md › Tracker](../../AGENTS.md#tracker).

**Fan out the reading, not the deciding.** Where the ticket touches several repos or areas, send one **read-only probe per area**, concurrently: each answers a bounded question — where the behaviour lives, its shape, what already tests it — with file:line evidence. The architect decides everything itself. Probes never plan, never write, never reach into another probe's area.

Ticket keys use the casing the profile specifies. A tracker read failing like a missing issue is a stale token first.

The architect writes `$WS/llm/scratchpad/plans/<TICKET>.md` per [plan-template.md](plan-template.md).

## 2. Plan review + rewrite loop — gate, no human

Run [plan-review.md](plan-review.md) with [agents/reviewer.md](../agents/reviewer.md), **in a different model family than wrote the plan** ([› in Codex](plan-review.md#runner)). No product code before this passes.

1. Review the plan against ticket and code: coverage, testable requirements, symbols that exist, repo split and ownership, pinned contracts, test plan, stated assumptions.
2. Blockers and Majors go back to the architect, which rewrites `<TICKET>.md` in place; re-review.
3. **Cap: 3 cycles**, then stop and report. The plan is the cheapest place to stop.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-plan-review-<n>.md`.

**Ask the human only when the answer is theirs**: a scope or user-visible behaviour question with no safe assumption, a repo no role owns, a ticket that never said what "done" means, or the cap ([› When the human is asked](plan-review.md#human)). Otherwise decide here — `Approve` authorizes everything downstream, commits and PR included.

On `Approve`, **if the profile declares an in-progress transition** ([AGENTS.md › Tracker](../../AGENTS.md#tracker) · [tracker › Transitions](tracker.md#transitions)), run it here — the flow's only chance, and step 7's transition is invalid from the initial state. Where the profile declares none, make **no** tracker write here.

## 3. Development — one lane per repo, no barrier downstream

Dev roles run [implement-change.md](implement-change.md). Lanes are per repository ([Lanes](#lanes)): one worktree, one branch, one PR each. A finished lane advances to step 4 immediately.

- [agents/backend-dev.md](../agents/backend-dev.md) — the plan's backend paths, in [dependency order](../../AGENTS.md#dependency-order).
- [agents/frontend-dev.md](../agents/frontend-dev.md) — only the client app(s) it owns. Work in an app no role owns → stop and report.
- Both in the **same repo** → they share its worktree and branch, sequentially in dependency order; the second starts from the first's work log and does not re-cut a branch.

**Parallel across repos needs the architect's pinned contract** (step 1): the consumer codes against the pinned shape and declares the provider's PR as its upstream. No pinned contract → provider first, consumer after.

Each dev role ships unit tests with the code ([AGENTS.md › Tests](../../AGENTS.md#tests)) and **does not run them** — step 5 does, once. The dev gate is exactly the verification commands the profile lists for the touched areas ([AGENTS.md › Commands](../../AGENTS.md#commands) · [implement-change › Verify](implement-change.md#verify)) — none it does not list, none it does skipped.

No red-green loop means the tests must be complete and correct on the first pass: every changed line, every branch, every changed source file's mirror test. Skip a phase whose repos the plan doesn't touch.

**Start QA's stack boot here**, as soon as the first lane reports done ([qa-verify › Pre-warm](qa-verify.md#prewarm)) — boot and seed cost minutes and depend on the checkout, not on review.

## 4. Internal review + fix loop — lint only, no tests run

Run [internal-review.md](internal-review.md) with [agents/reviewer.md](../agents/reviewer.md) on each repo's **local branch diff**, before any push. Nothing leaves the workspace.

1. Review each repo's diff against the plan and the profile — **repo lanes concurrent**, and within a lane the three dimensions too: **lint and type check** (the profile's commands), **tests** (present, honest, able to run), **design** (requirements, layering, queries, contracts, hygiene). One merged verdict. Never run a test.
2. **Tests present** carries the weight: every changed source file has its mirror test in the diff, tests assert real behaviour, every branch covered. Missing now is cheap; in step 5 it costs a cycle; on CI, a red PR.
3. Blockers and Majors go back to the owning dev role, which fixes and re-runs the profile's verification commands. Nits when cheap.
4. Re-review the updated diff until `Approve` / `Approve with nits`.
5. **Cap: 3 cycles**, then stop and report the unresolved findings.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md`; release reads the highest `<n>`.

## 5. Unit tests — the change's tests only, in parallel

Run [run-unit-tests.md](run-unit-tests.md) with [agents/tester.md](../agents/tester.md). First execution of any test in this flow, per repo as soon as **that repo** clears review.

1. **Selection from the diff**, three tiers: every test file the diff added or modified · the mirror test of every changed source file · existing tests naming a changed symbol. Anything that merely *might* be affected is regression, and regression is CI's job (step 8) ([› Selection](run-unit-tests.md#selection)).
2. **One lane per area, all concurrent** — each backend package, client app, extension, compiled service gets its own command from [AGENTS.md › Commands](../../AGENTS.md#commands), narrowed to that lane's node IDs, plus the runner's parallel flag where the profile documents one ([› Lanes](run-unit-tests.md#lanes)).
3. **A zero exit code is not a pass** — the run must collect the named tests, match counts, reach the coverage summary ([› Reading the result](run-unit-tests.md#reading)).
4. `Fail` → back to the owning dev role. A stale test is fixed as a *test*; production code is never loosened to green one. Then step 4 again on the new diff, then this step.
5. **Cap: 3 cycles**, then stop and report the failing node IDs.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-tests-<n>.md` plus one log per lane; release reads the highest `<n>`.

## 6. QA on the local stack + fix loop

Run [qa-verify.md](qa-verify.md) with [agents/qa.md](../agents/qa.md) against the dev worktrees, on the [local stack](../../AGENTS.md#stack).

1. The stack is up already if step 3 pre-warmed it. QA exercises every requirement on it — **requirements whose flows don't share state run concurrently** — plus adjacent regression paths, capturing a proof per requirement into `$WS/llm/scratchpad/proofs/<TICKET>/`: before/after GIFs for UI work, a request + datastore transcript for API and async work.
2. `Fail` on any Blocker or Major → back to the owning dev role; after the fix, re-run steps 4 and 5, then QA.
3. **Cap: 3 QA cycles**, then stop and report.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md`. Read its **Not verified** section — the stack cannot exercise everything ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)), and what is listed ships on unit tests alone.

## 7. Release

Run [release-pr.md](release-pr.md) with [agents/releaser.md](../agents/releaser.md): commits, push, one PR per repo with the [template body](pr-template.md) and proofs, cross-repo PRs linked in dependency order, proofs attached to the ticket, PR URL commented, and a transition **only if the profile declares one** ([tracker › Transitions](tracker.md#transitions)).

**Commit and push per repo run concurrently; opening the PRs does not** — the provider's PR must exist before the consumer's body links it ([cross-repo](cross-repo.md)). Have [commenter](../agents/commenter.md) draft PR bodies **during step 6**; QA's verdict and proof names arrive late.

Every text leaving the workspace here — PR body and comments, tracker comment, review replies — is written by [commenter](../agents/commenter.md) from the facts the posting role hands it, and posted through a quoted heredoc ([shell quoting](../README.md#shell-quoting)).

## 8. CI + review watch loop — the PR is not done until this is quiet

The full suite runs here: step 5 ran only the change's own tests. Where the profile has a review bot, it re-reviews every push and the releaser holds the PR until CI and the bot are both quiet ([release-pr › CI](release-pr.md#ci) · [› Review bot](release-pr.md#review-bot)). Where the profile has no bot, CI is the only asynchronous wait; handle existing human comments without waiting for a silent follow-up review. Watch commands are in [AGENTS.md › Pull requests](../../AGENTS.md#pull-requests).

0. **Watch every PR concurrently**, and run the [PR review](pr-review.md) pass while CI runs — it reads the diff, not the checks. Background each watch; suites run for tens of minutes.
1. Red check → read the failing job's log and route: test regression, missing coverage, lint or migration chain → the owning dev role, in its worktree. Flake → one re-run, then say so. Infra or secrets → the human.
2. Configured review-bot wave → fix what is valid, answer what is not with a reason; never leave a thread silent. With no bot, handle human comments already present once and add no silence gate.
3. Push fixes on the same branch, back to 1 — a push restarts CI and, only where configured, the bot.
4. **Cap configured bot review at 3 waves**, then stop and report the open items. Human review has no automated-wave loop.

Never make CI pass by weakening it — no lowered coverage threshold, no `skip`/`xfail` on a genuinely failing test, no disabled lint rule.

Worktree cleanup last — **only after CI is green**, because removing a worktree removes the place a fix would happen.

## Output

Final answer to the human: PR URLs in dependency order · ticket state · plan-review verdict · code-review verdict · **unit tests: what ran per lane, what was left to CI** · QA verdict with proof paths · **CI state per PR and what was fixed** · **review comments fixed vs rejected, with reasons** · anything not verified, undone, or assumed.

<a id="stop-conditions"></a>
## Stop conditions

Stop and ask the human when: an open question changes scope or user-visible behaviour with no safe assumption; the plan needs a repo no role owns; any applicable loop hits its 3-cycle cap; a changed source file has no test and the dev role won't add one; a CI failure is infra, secrets, or runner-side; the profile's required commit mode fails; a tracker call the profile authorizes fails (auth, comment, attachment, declared transition); the local stack won't come up after one documented reset and restart; or the ticket needs a decision nobody made.

Nothing else is a stop. A question with a defensible assumption gets the assumption, recorded in the plan or the report.

Check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) before any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
