---
name: qa-verify
description: Verifies a change on the real local stack — browser E2E with before/after GIFs for frontend work, API calls plus datastore checks for backend work — and returns proofs and a Pass/Fail verdict.
---

# QA verify (local stack)

Verify on the local stack; produce proofs.

**Kind** procedure · **Used by** [qa](../../agents/qa.md) · **When** every lane has cleared review and its tests (develop-flow step 6); the stack boot starts earlier, in parallel with step 3 · **Ends with** a QA report file, a proof per user-visible requirement on disk, and a `Pass`/`Fail` verdict

Never edit product code. Put test-data scripts in scratchpad. Use profile stack commands only.

<a id="from-pr"></a>
## 0a. Starting from a PR link — outside the flow

Inside develop-flow the branch, the worktree and the plan already exist; step 0 pre-warms and step 1 points the stack at them. Invoked on its own with a **PR link or number**, build that context first:

```bash
gh pr view <N> --json title,body,headRefName,baseRefName,files,url
git fetch <remote> && git worktree add <path> <remote>/<headRefName>
```

Worktree path, base ref and cleanup follow [worktree](../worktree/SKILL.md#naming) — the same naming contract, so nothing collides with a lane the flow owns.

Then assemble what steps 1 – 5 read:

| Normally from | With only a PR | 
| --- | --- |
| the branch in the dev work log | the PR's head branch, checked out above |
| requirements in `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` | that plan if the ticket key in the branch or PR title has one; otherwise the ticket's own surfaces ([ticket surfaces](../plan-review/SKILL.md#ticket-surfaces)), and failing that the PR body |
| the dev work logs' setup notes | the PR's changed files, to split frontend from backend at step 3 |

Say in the report which of these you used. Requirements taken from a PR body are the PR author's summary of the change, not the ticket's statement of what was asked for — a Pass against them proves less, and the report must not hide that.

Multi-repo change: one PR link per repo, and the stack is pointed at every one of those worktrees before step 2. Verifying one repo's PR against the primary clone of the others tests a combination nobody is shipping.

<a id="prewarm"></a>
## 0. Pre-warm — start this the moment the first dev lane reports done

Run boot/seeding during steps 3–5:

- Boot the first finished lane; seed required data.
- Restart after later fixes.
- Same repo: wait for all roles. Separate repos: pre-warm independently.

A pre-warmed stack failing its health check is a stack problem reported now, not at step 6 with everything waiting on it.

## 1. Point the stack at the branch under test

Use only the profile's worktree override. Never check a dev branch into the primary clone or edit stack config.

Take paths from work logs. Check linked dependencies/env; do not install. Record command and cwd.

## 2. Bring the stack up

Gate on: dependencies · all processes · clean logs · expected health status.

A narrower route (single services, container fallback) usually ignores the worktree and tests the primary clone — say so in the report if you used one.

## 3. Split the change

From the dev work logs, classify each requirement in `$TROIKA_SCRATCHPAD/plans/<TICKET>.md`:

| Change | Verify with | Proof |
| --- | --- | --- |
| user-visible UI | step 4 — browser E2E | before/after GIF |
| API, task, or data only | step 5 — API call + datastore | before/after transcript |
| both | steps 4 **and** 5 | both |

A change that touches frontend code but no user-visible behaviour is verified as backend and said so in the report.

## 4. Frontend — browser E2E, before/after GIF

Drive the running app along the plan's click path with a browser automation tool that records GIFs (Claude in Chrome, or equivalent); fall back to before/after screenshots only if none exists. Per requirement:

- **before** — the same path on the base checkout, showing the old behaviour. Net-new screens have none: write `n/a — new` rather than faking one.
- **after** — the same path on the branch worktree, showing the requirement met.

Capture a few frames around each action so playback reads, and end on the state that proves the requirement, not the click. **Watch the browser console and network log** — an error there is a defect even when the screen looks right. Batch all before captures, restart once, then all after.

## 5. Backend — API E2E + datastore

Per requirement, capture:

1. **Datastore before** — the query and the rows the change should affect.
2. **The call** — `curl` with the documented auth, showing status, headers that matter, and body. Real requests only; never a client library wrapper hiding the wire.
3. **Datastore after** — the same query, showing the state effect.
4. **Error cases** — bad auth, missing field, not-found — status and body shape checked against the pinned contract.

Async adds pickup/completion logs. Success without state change fails.

## 6. Regression and integration suite

Exercise adjacent paths and the applicable integration suite. A suite using default-branch checkouts proves only default health; label it regression-only.

## 7. Stack limits

List applicable [stack limits](../../../AGENTS.md#stack-limits) and alternate coverage.

## 8. Proofs for the PR

One directory per ticket, `$TROIKA_SCRATCHPAD/proofs/<TICKET>/`, one file per requirement per side, named after the requirement:

```
req-2-portfolio-filter-before.gif
req-2-portfolio-filter-after.gif
req-3-export-endpoint.md          # backend: the step-5 transcript
```

Map filenames to requirements. Never fabricate; unexercised work goes under **Not verified** with reason.

## 9. Clean up

Run profile teardown; verify no worktree process survives:

```bash
pgrep -fl "$TROIKA_WORKTREES" || echo "no worktree processes left"
```

Kill leftovers; close tabs. Leave running only by request and report it.

## Output

Write the report to `$TROIKA_SCRATCHPAD/plans/<TICKET>-qa-<n>.md` (`<n>` = QA cycle, from 1) **and** return it to the orchestrator — [releaser](../../agents/releaser.md) runs in a separate context and gates on that file ([handoff contract](../../ROLES.md#handoff)).

Use the [QA report format](../../agents/qa.md#output) and include: the exact command and directory that started the stack, the branches under test, every requirement's result with its proof filenames, the **Not verified** list, and each defect with its repro.

## Stop conditions

- Stack won't come up after the profile's documented reset and one restart → stop and report; don't debug the environment for hours.
- Browser tool unresponsive or a page failing after 2–3 attempts → stop and report; don't retry the same action or wander the app.
- `Fail` on any Blocker or Major sends the work back to the owning dev role; after the fix, internal review runs again, then this skill, writing `-qa-<n+1>.md`. **Cap at 3 QA cycles**, then stop and report to the human.
- A worktree named in a work log is missing → stop and report ([worktree › Gotchas](../worktree/SKILL.md#gotchas)).
