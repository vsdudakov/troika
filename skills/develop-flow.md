---
name: develop-flow
description: The full pipeline from ticket to merge-ready PR — plan, human approval, parallel dev, internal review loop, QA on the local stack, release.
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
  └─ 1 architect ── plan ──▶ 2 human approval loop
                                 │ approved
       ┌─────────────────────────┴─────────────────────────┐
       ▼ 3 backend-dev (parallel)      ▼ 3 frontend-dev (parallel)
       └─────────────────────────┬─────────────────────────┘
                                 ▼ 4 internal review + fix loop (max 3)
                                 ▼ 5 QA on local stack + fix loop (max 3)
                                 ▼ 6 release: PR + proofs + ticket
                                 ▼ 7 CI + review-bot watch loop (max 3) ──▶ green + quiet
```

Set `WS` once at the start — every handoff path below is absolute ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 0. Refresh the code index — before any step reads code

Every repo the ticket touches, from its own root — command and the loop over repos in [AGENTS.md › Code search](../../AGENTS.md#code-search).

Seconds per repo, and it is the difference between the architect planning against the current code and against a snapshot. Dev roles repeat it inside their worktree, which is a separate index root (step 3).

## 1. Collect requirements and plan

Run [agents/architect.md](../agents/architect.md). Read the ticket first — CLI, project key, and the auth check are in [AGENTS.md › Tracker](../../AGENTS.md#tracker).

Ticket keys are uppercase everywhere (branches, commits, PR titles). If tracker reads fail in a way that looks like a missing issue, suspect a stale token before a missing ticket.

The architect writes `$WS/llm/scratchpad/plans/<TICKET>.md` per [plan-template.md](plan-template.md).

## 2. Human approval — gate

Present the plan (requirements, repo split, contracts, test plan, out of scope, open questions) and **stop**. Do not write product code before approval.

- Human requests changes → architect rewrites, present again. Loop until approved; no cap, the human ends it.
- Open questions that change scope or user-visible behaviour must be answered here, not assumed.
- Approval of the plan authorizes everything downstream including commits and the PR.

On approval, move the ticket into its in-progress state ([AGENTS.md › Tracker](../../AGENTS.md#tracker)) — this is the flow's only chance to do it, and step 6's transition is invalid from the initial state.

## 3. Development — parallel

Both dev roles run [implement-change.md](implement-change.md), each in **its own worktree**, at the same time when the plan allows:

- [agents/backend-dev.md](../agents/backend-dev.md) — the plan's backend repos, in [dependency order](../../AGENTS.md#dependency-order). One worktree, one branch, one PR per repo.
- [agents/frontend-dev.md](../agents/frontend-dev.md) — its own app only. If the plan needs work in an app no role owns, stop and report to the human.

**Parallel is allowed only when the architect pinned the API contract** (step 1). The consumer then codes against the pinned shape; the provider's PR is the upstream dependency, declared in the consumer's PR body. No pinned contract → provider first, consumer after.

Each dev role ships unit tests with the code ([AGENTS.md › Tests](../../AGENTS.md#tests)) and must have **its own tests** and the repo's **full lint** green before reporting done. It runs only the tests for what it changed, not the repo suite — the suite runs on CI when the PR opens (step 7), which is also where a regression outside the diff surfaces ([implement-change › Verify](implement-change.md#verify)). That trade only works if the tests are complete: every changed line and every branch covered, because CI gates over the whole package. Skip a phase whose repos the plan doesn't touch.

## 4. Internal review + fix loop — before QA

Run [internal-review.md](internal-review.md) with [agents/reviewer.md](../agents/reviewer.md) on the **local branch diff** of each repo, before anything is pushed or QA'd. Nothing is posted outside the workspace in this phase.

1. Review each repo's diff independently against the plan and the project profile.
2. Blockers and Majors go back to the owning dev role, which fixes them and re-runs its tests and lint. Nits are fixed when cheap.
3. Re-review the updated diff. Repeat until the verdict is `Approve` / `Approve with nits`.
4. **Cap: 3 cycles.** If the third review still has Blockers or Majors, stop the flow and report the unresolved findings to the human — don't advance to QA on a failing review.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md`; release reads the highest `<n>`.

## 5. QA on the local stack + fix loop

Run [qa-verify.md](qa-verify.md) with [agents/qa.md](../agents/qa.md) against the dev worktrees, on the workspace's [local stack](../../AGENTS.md#stack).

1. QA exercises every requirement on the running stack, plus the adjacent regression paths, and captures a proof per requirement into `$WS/llm/scratchpad/proofs/<TICKET>/` — before/after GIFs of the browser flow for UI work, a request + datastore transcript for API and async work.
2. `Fail` on any Blocker or Major → back to the owning dev role; after the fix, re-run internal review on the new diff (step 4), then QA again.
3. **Cap: 3 QA cycles**, then stop and report to the human.

Each pass writes `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md`. Read its **Not verified** section — the stack cannot exercise everything ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)), and anything listed there ships on unit tests alone.

## 6. Release

Run [release-pr.md](release-pr.md) with [agents/releaser.md](../agents/releaser.md): signed commits, push, PR per repo with the [template body](pr-template.md) and proofs, cross-repo PRs linked in dependency order, proofs attached to the ticket, PR URL commented, ticket transitioned.

Every text that leaves the workspace in this phase — PR body, PR comments, tracker comment, replies to the review bot — is written by [agents/commenter.md](../agents/commenter.md) from the facts the posting role hands it, and posted through a quoted heredoc ([shell quoting](../README.md#shell-quoting)).

## 7. CI + review-bot watch loop — the PR is not done until this is quiet

The full test suite runs here, not on anyone's laptop, and the review bot re-reviews every push. The releaser holds the PR until both go quiet ([release-pr › CI](release-pr.md#ci) · [› Review bot](release-pr.md#review-bot)); the watch commands are in [AGENTS.md › Pull requests](../../AGENTS.md#pull-requests).

1. Red check → read the failing job's log and route it: test regression, missing coverage, lint or migration chain → the owning dev role, in its worktree. Flake → one re-run, then say so. Infra or secrets → the human.
2. Review-bot wave → fix what is valid, reply with a reason to what is not; never leave a thread unanswered.
3. Push the fixes on the same branch and go back to 1 — a push restarts CI *and* the bot.
4. **Cap: 3 waves.** Still red, or the bot still raising new substantive comments → stop and report the open items.

Never make CI pass by weakening it — no coverage threshold lowered, no `skip`/`xfail` on a genuinely failing test, no lint rule disabled.

Then [pr-review.md](pr-review.md) on the open PR, and worktree cleanup last — **only after CI is green**, because removing a worktree removes the place a fix would happen.

## Output

Final answer to the human: PR URLs in dependency order · ticket state · QA verdict with proof paths · review verdict · **CI state per PR and what was fixed to get it green** · **review-bot comments fixed vs rejected, with reasons** · anything not verified, left undone, or assumed.

## Stop conditions

Stop and ask the human when: the plan needs a repo no role owns; a review, QA, or CI/review-bot loop hits its 3-cycle cap; a CI failure is infra, secrets, or runner-side; commit signing fails; tracker auth or a transition fails; the local stack won't come up after one documented reset and restart; or the ticket turns out to need a decision nobody made.

Check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) before running any workspace-level maintenance command mid-flow — dev work stays uncommitted in worktrees until step 6, and some of those commands delete worktrees without a prompt.
