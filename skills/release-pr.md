---
name: release-pr
description: Ships one repo — profile-compliant commit, push, PR from the team template with proofs, ticket attachment and comment (plus a transition where the profile declares one), then PR review and worktree cleanup.
---

# Release PR

Verified worktree to reviewed PR.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** internal review is `Approve`/`Approve with nits`, the tester's verdict is `Pass`, and QA is `Pass` (develop-flow step 7) · **Ends with** a PR URL, **CI green**, proofs on the ticket, the ticket updated as the profile allows, worktrees removed

Run once per repo: one PR regardless of contributing roles. Commit/push repos concurrently; open PRs in [dependency order](../../AGENTS.md#dependency-order). Set `WS` first.

## 1. Gates

All must pass:

```bash
ls "$WS/harness/scratchpad/plans/<TICKET>-review-"*.md   # read the highest <n>: Approve / Approve with nits
ls "$WS/harness/scratchpad/plans/<TICKET>-tests-"*.md    # read the highest <n>: Pass
ls "$WS/harness/scratchpad/plans/<TICKET>-qa-"*.md       # read the highest <n>: Pass
ls "$WS/harness/scratchpad/proofs/<TICKET>/"             # one artifact per requirement ([qa-verify](qa-verify.md#8-proofs-for-the-pr))
```

- Read verdict files directly. Tests must cover final code; later changes return to review/test. Carry QA's **Not verified** into the PR.

## 2. Commit

Use the profile's exact signing mode and ticket-key form ([tracker](tracker.md#link-the-branch-and-pr)). Inspect before staging:

```bash
git status --short                  # expect only your source changes; no .env, no scratchpad, no proofs
git add <paths>                     # explicit paths, or `git add -A` only after the list above is clean
git status --short                  # confirm the staged set
git commit <profile-required-signing-option, if any> -F - <<'EOF'
<type>(<scope>): <summary>

<TICKET>
EOF
```

The heredoc preserves shell-sensitive text. **No AI attribution** — no `Co-Authored-By:` naming an AI, no "Generated with …", no agent marker or emoji; strip anything the tooling appends ([AGENTS.md](../../AGENTS.md#no-ai-attribution)). Required signing failure follows profile recovery; forbidden signing retries with the profile's no-sign option.

## 3. Push and open the PR

```bash
git push -u <remote> <branch>
gh pr create --base <default-branch> --title "<title, per the profile's format>" --body "$(cat <<'EOF'
<template body>
EOF
)"
```

Follow profile push rules and the repo template (repo file wins). Strip AI attribution, including HTML comments. Answer every field; link upstream PRs; include QA, proofs, and **Not verified**. [Commenter](../agents/commenter.md) drafts during QA.

## 4. Proofs

Attach every proof, including both before/after files. Map names to requirements in the PR. Use absolute paths and validate attachment responses. An inline GIF in the PR body needs the human to drag it in — say so rather than attempting it.

## 5. Ticket

Comment PR URL + summary. Run only a profile-declared "PR opened" transition, after validating state. No declared transition means no state write. For cross-repo work, comment the ordered PR chain.

<a id="ci"></a>
## 6. CI — watch until green, fix what it reds

**CI is the only place the full suite runs** — dev roles ran no tests and the tester ran only the change's own. Watch every check to completion with the command in [AGENTS.md › Pull requests](../../AGENTS.md#pull-requests) — **background it, suites run tens of minutes** — watching every PR concurrently and running [step 7](#7-pr-review) meanwhile. On failure, read only failing logs. Never clean or claim shipped before green.

Then, per failure:

| Failure | Who fixes it | Where |
| --- | --- | --- |
| test failure outside the diff — a regression the change's own tests could not see | owning dev role | its worktree, [implement-change](implement-change.md) |
| coverage below the gate on a changed file | owning dev role — write the missing test, never lower the gate | same |
| lint / type / migration-chain check | owning dev role | same |
| flake — passes on re-run, unrelated to the diff | releaser: re-run the failed jobs once, then say so in the report | — |
| infra / secrets / runner failure | stop and hand to the human | — |

Fix on the same branch; push and watch. Cap at 3 cycles. **Never make CI pass by weakening it** — no lowered coverage threshold, no `skip`/`xfail` on a genuinely failing test, no disabled lint rule.

<a id="review-bot"></a>
### Automated review comments — same loop, until it stops commenting

Configured bot: handle each wave, push, wait for silence. No bot: handle existing human comments once; no quiet-pass gate.

Per comment, one of two outcomes — never silence:

- **Valid** → fix in the worktree, with a test when behaviour changes, then reply saying what changed.
- **Wrong or not applicable** → reply with the reason (the layering rule it missed, the test that covers it, the plan's deliberate trade-off). A reasoned rejection is a complete answer.

Replies come from [commenter](../agents/commenter.md). If a configured bot stalls, re-request it; if rejected, ask the human. Loop bot with CI, capped at 3 waves.

<a id="7-pr-review"></a>
## 7. PR review

Run [pr-review.md](pr-review.md) during CI. Blocker/Major → owner fixes; push, rewatch, re-review.

## 8. Clean up

After push and green CI, remove worktrees from the repo using absolute paths:

```bash
git worktree remove "$WS/harness/worktrees/<repo>-<TICKET>"   # --force only to discard uncommitted changes
git worktree prune                                        # stale entries
```

## Output

PR URL(s) in dependency order · ticket state after the run · proofs attached, by name · **CI: final state per check, and what was fixed to get there** · **automated review, when configured: comments received, fixed vs rejected with the reason** · existing human comments handled · PR-review verdict · worktrees removed · anything left open or unverified.

## Stop conditions

Stop and hand back when: a gate in step 1 fails; the profile's required commit mode cannot be completed; `git status` shows anything outside the change set; a transition the profile declares is invalid after checking what the tracker allows; CI is still red or a configured review bot is still raising new substantive comments after **3 waves** (step 6); a CI failure is infra, secrets, or runner-side; or the PR review is still failing after **3 cycles**.
