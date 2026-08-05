---
name: release-pr
description: Ships one repo — signed commit, push, PR from the team template with proofs, ticket attachment, comment and transition, then PR review and worktree cleanup.
---

# Release PR

One repo, from a verified worktree to an open, reviewed PR with the ticket updated.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** internal review is `Approve`/`Approve with nits` and QA is `Pass` (develop-flow step 6) · **Ends with** a PR URL, **CI green**, proofs on the ticket, ticket transitioned, worktrees removed

Run once per repo, in [dependency order](../../AGENTS.md#dependency-order). Set `WS` first — the cwd is the worktree, and the scratchpad is not below it.

## 1. Gates

Stop and report instead of releasing if any of these fails:

```bash
ls "$WS/llm/scratchpad/plans/<TICKET>-review-"*.md   # read the highest <n>: Approve / Approve with nits
ls "$WS/llm/scratchpad/plans/<TICKET>-qa-"*.md       # read the highest <n>: Pass
ls "$WS/llm/scratchpad/proofs/<TICKET>/"             # one artifact per user-visible requirement
```

- Both verdicts read from their own files — never taken second-hand ([handoff contract](../agents/README.md#handoff)).
- Repo tests and lint green on the final code; re-run if anything changed since. A zero exit is not always a pass ([AGENTS.md › Gotchas](../../AGENTS.md#gotchas)).
- The QA report's **Not verified** list is carried into the PR body, not dropped.

## 2. Commit

From the worktree, **signed**, uppercase ticket key in the message so the tracker links it. Inspect *before* staging — once `git add -A` has run, a stray `.env` or scratchpad file shows up as a normal staged change and stops looking wrong:

```bash
git status --short                  # expect only your source changes; no .env, no scratchpad, no proofs
git add <paths>                     # explicit paths, or `git add -A` only after the list above is clean
git status --short                  # confirm the staged set
git commit -S -F - <<'EOF'
<type>(<scope>): <summary>

<TICKET>
EOF
```

The heredoc keeps backticks and `$` in the message intact ([shell quoting](../README.md#shell-quoting)).

No AI attribution — no `Co-Authored-By:` naming an AI, no "Generated with …", no agent marker or emoji. Strip anything the tooling appends ([AGENTS.md](../../AGENTS.md#no-ai-attribution)). If signing fails (`Bad passphrase`, locked agent), ask the human to run `! echo test | gpg --clearsign`, then retry — never commit unsigned.

## 3. Push and open the PR

```bash
git push -u origin <branch>
gh pr create --base main --title "<type>(<scope>): <summary>" --body "$(cat <<'EOF'
<template body>
EOF
)"
```

Push quirks (a branch touching CI config may need a different remote or scope) are in [AGENTS.md › Branches](../../AGENTS.md#branches).

Body follows [pr-template](pr-template.md), whose fill rules point at the workspace's actual template ([AGENTS.md › PR body](../../AGENTS.md#pr-template)). If the repo has its own template file and it differs, **the repo's file wins — but strip any AI product name from it first**, HTML comments included ([no-ai-attribution](../../AGENTS.md#no-ai-attribution)).

Answer every question in the template honestly, elaborate on a "yes", and never leave a bare "No" where there is something to say. Cross-repo work declares its upstream PRs ([cross-repo](cross-repo.md)). Testing notes carry the QA steps, the proof list, and the QA report's **Not verified** items.

The body text comes from [commenter](../agents/commenter.md) — pass it the facts (what changed, evidence, links, proof names), post what it returns.

## 4. Proofs

Attach the proofs to the ticket and reference them by name from the PR body — the PR host has no CLI upload for body images ([AGENTS.md › Tracker](../../AGENTS.md#tracker) has the attachment call). Use absolute paths: the cwd is the worktree, and a discarded response body hides the error.

Check the response — an attachment record, not an error. If the human wants a GIF inline in the PR, ask them to drag it into the body; that upload can't be automated.

## 5. Ticket

Comment the PR URL and one line of what changed, then transition the ticket ([AGENTS.md › Tracker](../../AGENTS.md#tracker)) — check what is valid from the current state first, since transition names are not status names and the "PR opened" transition is usually invalid unless the "started" one already ran.

Cross-repo: comment the full PR chain in dependency order so reviewers merge in sequence.

<a id="ci"></a>
## 6. CI — watch until green, fix what it reds

**CI is where the full test suite runs.** Dev roles run only their own tests locally ([implement-change › Verify](implement-change.md#verify)), so this step is the first time the whole suite sees the branch. The PR is not done until CI is green — do not clean up worktrees, do not report the ticket shipped, while a check is red or still running.

Watch every check to completion with the command in [AGENTS.md › Pull requests](../../AGENTS.md#pull-requests). It can run for tens of minutes; background it rather than blocking the session. When it comes back non-zero, list the failing checks and read the failing job's log only, not the whole run.

Then, per failure:

| Failure | Who fixes it | Where |
| --- | --- | --- |
| test failure outside the diff — a regression the targeted local run couldn't see | owning dev role | its worktree, [implement-change](implement-change.md) |
| coverage below the gate on a changed file | owning dev role — write the missing test, never lower the gate | same |
| lint / type / migration-chain check | owning dev role | same |
| flake — passes on re-run, unrelated to the diff | releaser: re-run the failed jobs once, then say so in the report | — |
| infra / secrets / runner failure | stop and hand to the human | — |

The fix goes on the same branch: amend or add a commit (signed, same rules as step 2), push, then watch again. **Max 3 cycles** — after that stop and hand back with the failing job and its decisive log line.

Never make CI pass by weakening it: no coverage threshold lowered, no `skip`/`xfail` on a test that is genuinely failing, no lint rule disabled to clear an error.

<a id="review-bot"></a>
### Automated review comments — same loop, until it stops commenting

If the workspace has a review bot on its PRs ([AGENTS.md › Pull requests](../../AGENTS.md#pull-requests)), it re-reviews after each push, so its comments arrive in waves. Treat a wave exactly like a red check: read it, fix or reject each comment, push, wait for the next wave. **Done means the latest pass produced no new comments** — not "the first batch is handled".

Per comment, one of two outcomes — never silence:

- **Valid** → fix it in the worktree, with a test when it is a behaviour change, then reply on the comment saying what changed.
- **Wrong or not applicable** → reply with the reason (the layering rule it missed, the test that already covers it, the deliberate trade-off from the plan). A bot is a linter with opinions, not a gate; a reasoned rejection is a complete answer.

Reply text is outward-facing — it comes from [commenter](../agents/commenter.md), in the workspace's [voice](../../AGENTS.md#voice), with no AI attribution.

After pushing, the bot normally re-reviews on the new commits; if it doesn't, re-request it, and if that call is rejected, ask the human to press the re-request button — do not skip the wave.

Loop CI and the bot together: push once, wait for both, handle both, push again. **Max 3 waves** — if it is still producing new substantive comments after three, stop and hand back with the open threads listed; a loop that never converges is usually a design disagreement, and that is the human's call.

## 7. PR review

Run [pr-review.md](pr-review.md) on the open PR and post it. Blockers and Majors go back to the owning dev role; after the fix, push, wait for CI (step 6) again, and re-review.

## 8. Clean up

Everything pushed **and CI green** → remove the worktrees. Removing a worktree while CI is still red destroys the place the fix has to happen. `git worktree remove` takes a path; run it from the repo, with the absolute worktree path:

```bash
git worktree remove "$WS/llm/worktrees/<repo>-<TICKET>"   # --force only to discard uncommitted changes
git worktree prune                                        # stale entries
```

The branch survives; cut a fresh worktree if follow-ups land.

## Output

PR URL(s) in dependency order · ticket state after the move · proofs attached, by name · **CI: final state per check, and what was fixed to get there** · **review bot: comments received, fixed vs rejected with the reason** · PR-review verdict · worktrees removed · anything left open or unverified.

## Stop conditions

Stop and hand back when: a gate in step 1 fails; commit signing fails after priming the agent; `git status` shows anything outside the change set; the ticket transition is invalid after checking what the tracker allows; CI is still red or the review bot is still raising new substantive comments after **3 waves** (step 6); a CI failure is infra, secrets, or runner-side; or the PR review is still failing after **3 cycles**.
