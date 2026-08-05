---
name: develop-flow
description: The full pipeline from ticket to merge-ready PR — plan, plan review loop, parallel dev, internal review loop, parallel unit tests on the change only, QA on the local stack, release.
---

# Develop flow

Ticket to PR, end to end. The orchestrator runs this and spawns one [role](../agents/README.md) per phase; roles never call each other directly.

Each role names a model and an effort level, and neither is applied by reading the file — the orchestrator passes them when it spawns the role ([agents › Model and effort](../agents/README.md#model-and-effort)). Spawning a role in a fresh CLI session:

```bash
# architect — Claude, high effort
claude --model claude-fable-5 --effort high -p "read $WS/llm/agents/architect.md and act as that role for <TICKET>"
# reviewer — Codex, high effort, different family from whoever wrote the code
codex -m gpt-5.6-sol -c model_reasoning_effort="high" ...
```

Spawning a role as a subagent inside one session instead: the subagent inherits the session's effort, so run the whole session at the highest effort any role in it needs.

**Kind** procedure · **Used by** orchestrator · **When** a ticket or a described change needs shipping · **Ends with** one PR per touched repo — CI green, review bot quiet, proofs attached, ticket moved

```
ticket
  └─ 0 ∥ index refresh per repo · ticket surfaces (comments, attachments, links) · memory
  └─ 1 architect ── plan ◀── ∥ read-only probes, one per repo/area
        │
        ▼ 2 plan review ∥ 2 lenses (other model family) ── rewrite loop (max 3) ── approved
        │
   ┌────┴─────────────────────┬──────────────────────────┬─────────────────────┐
   ▼ backend lane             ▼ frontend lane            ▼ QA pre-warm         │
   3 backend-dev              3 frontend-dev             boot the stack        │
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
        ▼ 8 ∥ per PR: CI watch + review-bot waves + PR review (max 3) ──▶ green + quiet
```

`∥` marks work that runs concurrently. **A lane never waits for a sibling lane** — backend can be in step 5 while frontend is still in step 3. The only true barriers are step 2's verdict, the join before QA (one stack, one branch under test), and CI.

**Who runs tests, and when.** Exactly once locally, in step 5, by one role. Dev roles write tests and stop at lint (step 3); the reviewer reads tests and never runs them (step 4); the [tester](../agents/tester.md) runs the change's tests and only those, in parallel lanes (step 5); the whole suite runs on CI (step 8). Every extra local suite run buys a signal one of those four already gives.

**The human is not a step.** No standing approval gate: step 2's review is the gate. The human is asked only on a real question — a blocking scope or behaviour decision, a loop hitting its cap, an infra or credentials failure ([Stop conditions](#stop-conditions)).

<a id="parallelism"></a>
## Parallelism — what runs at the same time, and what must not

| Runs concurrently | Why it is safe |
| --- | --- |
| Index refresh, one job per repo (step 0) | independent roots, read-only |
| Ticket surface collection — comments, attachments, links — while the code probes run (step 0–1) | different sources, both read-only |
| Read-only code probes, one per repo or area, feeding the architect (step 1) | no writes; the architect synthesizes their reports |
| The two plan-review lenses (step 2) | read-only; findings are merged before the architect rewrites |
| Both dev roles (step 3) | separate worktrees, separate branches — **only with a pinned contract** |
| The three review dimensions inside one repo (step 4) | read-only over one diff |
| Test lanes, one per area, across every ready worktree (step 5) | separate processes, separate test roots |
| Whole per-repo lanes 3→4→5 against each other | a lane touches only its own worktree |
| QA's stack boot, from the moment the first dev role reports done | boot is slow and depends on the checkout, not on review |
| Proof capture per requirement (step 6), where the paths don't share state | independent flows on one running stack |
| PR body drafting during QA (step 6→7) | text work, no repo state |
| Commit and push per repo (step 7) | separate repos |
| CI watch + review-bot waves + PR review, per PR (step 8) | independent PRs, independent checks |

| Must stay sequential | Why |
| --- | --- |
| Plan → any product code | the plan is the contract every lane codes against |
| Review → tests, inside a lane | review removes the defects a test run would find the slow way |
| A fix → re-review → re-test | a fix is a diff, and no diff advances unreviewed |
| Both lanes → QA | one stack, one branch under test at a time |
| Provider PR → consumer PR | dependency order ([cross-repo](cross-repo.md)) |
| A suite the profile marks sequential | correctness, not speed ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)) |
| Migration work inside one repo | migration numbers collide silently |

**Two lanes, one repo, is not parallelism** — it is two agents in one worktree overwriting each other. Split by repo (a worktree each), never by feature inside a repo.

**Report the wall clock per lane**, not only the total: a lane that idles waiting on a sibling is a barrier that should not be there.

Set `WS` once at the start — every handoff path below is absolute ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 0. Fan out — index, ticket, memory, all at once

Three independent jobs; start them together and join before planning:

1. **Index refresh, one job per repo** the ticket touches, from its own root ([AGENTS.md › Code search](../../AGENTS.md#code-search)). Seconds per repo, and it is the difference between the architect planning against the current code and against a snapshot. Dev roles repeat it inside their worktree, which is a separate index root (step 3).
2. **Ticket surfaces** — description, every comment in order, attachments and screenshots downloaded *and viewed*, every link followed, fields ([plan-review › Every surface](plan-review.md#ticket-surfaces)). This is a distinct job from reading code and does not have to wait for it.
3. **Memory** — `ls $WS/llm/memory/*.md` and read them; an entry can invalidate the plan before it is written ([memory](../memory/README.md)).

## 1. Collect requirements and plan

Run [agents/architect.md](../agents/architect.md) on the step 0 material — CLI, project key, and the auth check are in [AGENTS.md › Tracker](../../AGENTS.md#tracker).

**Fan out the reading, not the deciding.** Where the ticket touches more than one repo or area, send one **read-only probe per area** and let them run concurrently: each answers a bounded question — where this behaviour lives, what the current shape is, what already tests it — and reports file:line evidence. The architect reads their reports and makes every decision itself. Probes never plan, never write, and never reach into another probe's area; a probe's report is evidence, not a plan fragment.

Ticket keys are uppercase everywhere (branches, commits, PR titles). If tracker reads fail in a way that looks like a missing issue, suspect a stale token before a missing ticket.

The architect writes `$WS/llm/scratchpad/plans/<TICKET>.md` per [plan-template.md](plan-template.md).

## 2. Plan review + rewrite loop — gate, no human

Run [plan-review.md](plan-review.md) with [agents/reviewer.md](../agents/reviewer.md), **in a different model family than the one that wrote the plan** — Codex when the architect ran on Claude ([plan-review › Running this pass in Codex](plan-review.md#runner)). No product code before this passes.

1. Review the plan against the ticket and the code: ticket coverage, testable requirements, symbols that actually exist, repo split and ownership, pinned contracts, test plan, stated assumptions.
2. Blockers and Majors go back to the architect, which rewrites `<TICKET>.md` in place; re-review the rewritten plan.
3. **Cap: 3 cycles.** Third pass still blocked → stop and report to the human. The plan is the cheapest place to stop.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-plan-review-<n>.md`.

**Ask the human only when the answer is theirs**: an open question that changes scope or user-visible behaviour with no safe assumption, a repo no role owns, a ticket that never said what "done" means, or the cap above ([plan-review › When the human is asked](plan-review.md#human)). Otherwise decide here — an `Approve` verdict authorizes everything downstream, commits and PR included.

On `Approve`, move the ticket into its in-progress state ([AGENTS.md › Tracker](../../AGENTS.md#tracker)) — this is the flow's only chance to do it, and step 7's transition is invalid from the initial state.

## 3. Development — parallel lanes, no barrier downstream

Both dev roles run [implement-change.md](implement-change.md), each in **its own worktree**, at the same time when the plan allows. A lane that finishes advances to step 4 immediately — it never waits for the other lane ([Parallelism](#parallelism)):

- [agents/backend-dev.md](../agents/backend-dev.md) — the plan's backend repos, in [dependency order](../../AGENTS.md#dependency-order). One worktree, one branch, one PR per repo.
- [agents/frontend-dev.md](../agents/frontend-dev.md) — its own app only. If the plan needs work in an app no role owns, stop and report to the human.

**Parallel is allowed only when the architect pinned the API contract** (step 1). The consumer then codes against the pinned shape; the provider's PR is the upstream dependency, declared in the consumer's PR body. No pinned contract → provider first, consumer after.

Each dev role ships unit tests with the code ([AGENTS.md › Tests](../../AGENTS.md#tests)) and **does not run them** — step 5 does, once, for both repos at the same time. The dev gate is the repo's **full lint** plus the build where the type check lives inside it ([implement-change › Verify](implement-change.md#verify)).

Not running them raises the bar on writing them: a dev role gets no red-green loop, so the tests must be complete and correct on the first pass — every changed line, every branch, every changed source file's mirror test. Skip a phase whose repos the plan doesn't touch.

**Start QA's stack boot here**, in parallel, as soon as the first lane reports done ([qa-verify › Pre-warm](qa-verify.md#prewarm)). Boot and seed data cost minutes and depend on the checkout, not on review — running them behind step 5 is dead wall clock.

## 4. Internal review + fix loop — lint only, no tests run

Run [internal-review.md](internal-review.md) with [agents/reviewer.md](../agents/reviewer.md) on the **local branch diff** of each repo, before anything is pushed, tested, or QA'd. Nothing is posted outside the workspace in this phase.

1. Review each repo's diff independently against the plan and the project profile — **repo lanes run concurrently**, and within a lane the three dimensions run concurrently too: **lint + type check** (a command), **tests** (present, honest, and able to run at all), **design** (requirements, layering, queries, contracts, hygiene). Merge the three into one verdict. Never run a test — nothing has run them yet, and reading them is what this pass is for.
2. **Tests present** carries the weight here: every changed source file has its mirror test in the diff, tests assert real behaviour, every branch covered. A missing test found now is cheap; found in step 5 it costs a cycle, on CI it costs a red PR.
3. Blockers and Majors go back to the owning dev role, which fixes them and re-runs lint. Nits are fixed when cheap.
4. Re-review the updated diff. Repeat until the verdict is `Approve` / `Approve with nits`.
5. **Cap: 3 cycles.** If the third review still has Blockers or Majors, stop the flow and report the unresolved findings to the human — don't advance on a failing review.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md`; release reads the highest `<n>`.

## 5. Unit tests — the change's tests only, in parallel

Run [run-unit-tests.md](run-unit-tests.md) with [agents/tester.md](../agents/tester.md). First execution of any test in this flow. A repo's tests run as soon as **that repo** clears review — every worktree that is ready contributes its lanes, and a repo still in step 3 holds nothing up.

1. **Selection comes from the diff**, three tiers and nothing else: every test file the diff added or modified · the mirror test of every changed source file · existing tests that name a changed symbol (import the module, exercise the function, endpoint, or migration). Anything that merely *might* be affected is regression, and regression is CI's job in step 8 ([run-unit-tests › Selection](run-unit-tests.md#selection)).
2. **One lane per area, all lanes concurrent** — a backend package, a client app, an extension, a compiled service each get their own command from [AGENTS.md › Commands](../../AGENTS.md#commands), narrowed to that lane's node IDs, plus the runner's own parallel flag where the profile documents one. Wall clock is the slowest lane, not the sum ([› Lanes](run-unit-tests.md#lanes)).
3. **A zero exit code is not a pass** — the run must have collected the tests named, matched the counts, and reached the coverage summary ([› Reading the result](run-unit-tests.md#reading)).
4. `Fail` → back to the owning dev role. A stale test is fixed as a *test*; production code is never loosened to green one. After the fix, re-run internal review on the new diff (step 4), then this step again.
5. **Cap: 3 cycles**, then stop and report the failing node IDs to the human.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-tests-<n>.md` plus one log per lane; release reads the highest `<n>`.

## 6. QA on the local stack + fix loop

Run [qa-verify.md](qa-verify.md) with [agents/qa.md](../agents/qa.md) against the dev worktrees, on the workspace's [local stack](../../AGENTS.md#stack).

1. The stack is already up if step 3 pre-warmed it; otherwise boot it now. QA exercises every requirement on the running stack — **requirements whose flows don't share state are exercised concurrently** — plus the adjacent regression paths, and captures a proof per requirement into `$WS/llm/scratchpad/proofs/<TICKET>/` — before/after GIFs of the browser flow for UI work, a request + datastore transcript for API and async work.
2. `Fail` on any Blocker or Major → back to the owning dev role; after the fix, re-run internal review on the new diff (step 4) and the change's tests (step 5), then QA again.
3. **Cap: 3 QA cycles**, then stop and report to the human.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md`. Read its **Not verified** section — the stack cannot exercise everything ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)), and anything listed there ships on unit tests alone.

## 7. Release

Run [release-pr.md](release-pr.md) with [agents/releaser.md](../agents/releaser.md): signed commits, push, PR per repo with the [template body](pr-template.md) and proofs, cross-repo PRs linked in dependency order, proofs attached to the ticket, PR URL commented, ticket transitioned.

**Commit and push per repo run concurrently; opening the PRs does not** — the provider's PR must exist before the consumer's body can link it ([cross-repo](cross-repo.md)). Have [commenter](../agents/commenter.md) draft the PR bodies **during step 6** from the facts already known; QA's verdict and proof names are the only late additions.

Every text that leaves the workspace in this phase — PR body, PR comments, tracker comment, replies to the review bot — is written by [agents/commenter.md](../agents/commenter.md) from the facts the posting role hands it, and posted through a quoted heredoc ([shell quoting](../README.md#shell-quoting)).

## 8. CI + review-bot watch loop — the PR is not done until this is quiet

The full test suite runs here, not on anyone's laptop — step 5 ran only the change's own tests, so this is the first time anything outside the diff is exercised. The review bot re-reviews every push. The releaser holds the PR until both go quiet ([release-pr › CI](release-pr.md#ci) · [› Review bot](release-pr.md#review-bot)); the watch commands are in [AGENTS.md › Pull requests](../../AGENTS.md#pull-requests).

0. **Watch every PR concurrently**, and run the [PR review](pr-review.md) pass while CI is still running — it reads the diff, not the checks. Background each watch; suites run for tens of minutes.
1. Red check → read the failing job's log and route it: test regression, missing coverage, lint or migration chain → the owning dev role, in its worktree. Flake → one re-run, then say so. Infra or secrets → the human.
2. Review-bot wave → fix what is valid, reply with a reason to what is not; never leave a thread unanswered.
3. Push the fixes on the same branch and go back to 1 — a push restarts CI *and* the bot.
4. **Cap: 3 waves.** Still red, or the bot still raising new substantive comments → stop and report the open items.

Never make CI pass by weakening it — no coverage threshold lowered, no `skip`/`xfail` on a genuinely failing test, no lint rule disabled.

Worktree cleanup last — **only after CI is green**, because removing a worktree removes the place a fix would happen.

## Output

Final answer to the human: PR URLs in dependency order · ticket state · plan-review verdict · code-review verdict · **unit-test result: which tests ran, per lane, and what was deliberately left to CI** · QA verdict with proof paths · **CI state per PR and what was fixed to get it green** · **review-bot comments fixed vs rejected, with reasons** · anything not verified, left undone, or assumed.

<a id="stop-conditions"></a>
## Stop conditions

Stop and ask the human when: an open question changes scope or user-visible behaviour and no assumption is safe; the plan needs a repo no role owns; a plan-review, code-review, unit-test, QA, or CI/review-bot loop hits its 3-cycle cap; a changed source file has no test and the dev role won't add one; a CI failure is infra, secrets, or runner-side; commit signing fails; tracker auth or a transition fails; the local stack won't come up after one documented reset and restart; or the ticket turns out to need a decision nobody made.

Nothing else is a stop. A question with a defensible assumption gets the assumption, recorded in the plan or the report.

Check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) before running any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
