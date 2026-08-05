---
name: release-pr
description: Ships one repo — profile-compliant commit, push, PR from the team template with proofs, ticket attachment and comment (plus a transition where the profile declares one), then PR review and worktree cleanup.
---

# Release PR

One repo, from a verified worktree to an open, reviewed PR with the ticket updated.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** internal review is `Approve`/`Approve with nits`, the tester's verdict is `Pass`, and QA is `Pass` (develop-flow step 7) · **Ends with** a PR URL, **CI green**, proofs on the ticket, the ticket updated as the profile allows, worktrees removed

Run once per repo — **one PR per repository, however many roles contributed to it** ([develop-flow › Lanes](develop-flow.md#lanes)). **Commit and push run concurrently across repos; the PRs open in [dependency order](../../AGENTS.md#dependency-order)** — the provider's PR must exist before the consumer's body can link it ([cross-repo](cross-repo.md)). Set `WS` first — the cwd is the worktree, and the scratchpad is not below it.

## 1. Gates

Stop and report instead of releasing if any of these fails:

```bash
ls "$WS/llm/scratchpad/plans/<TICKET>-review-"*.md   # read the highest <n>: Approve / Approve with nits
ls "$WS/llm/scratchpad/plans/<TICKET>-tests-"*.md    # read the highest <n>: Pass
ls "$WS/llm/scratchpad/plans/<TICKET>-qa-"*.md       # read the highest <n>: Pass
ls "$WS/llm/scratchpad/proofs/<TICKET>/"             # one artifact per requirement ([qa-verify](qa-verify.md#8-proofs-for-the-pr))
```

- All three verdicts read from their own files, never second-hand ([handoff contract](../agents/README.md#handoff)).
- The tester's run covers the **final** code: anything changed after `-tests-<n>.md` goes back through review and the tester, not around them. This role runs no tests.
- The QA report's **Not verified** list goes into the PR body, not the bin.

## 2. Commit

From the worktree, use the profile's exact commit-signing rule: sign when it requires signing, pass its no-signing option when it forbids signing, and add neither when it declares neither. Put the ticket key in the message **in the form the profile's tracker contract asks for** — a tracker with a VCS integration wants the key in the casing it detects; a tracker without one links from the PR body instead ([tracker › Link](tracker.md#link-the-branch-and-pr)). Inspect *before* staging — once `git add -A` has run, a stray `.env` or scratchpad file shows up as a normal staged change and stops looking wrong:

```bash
git status --short                  # expect only your source changes; no .env, no scratchpad, no proofs
git add <paths>                     # explicit paths, or `git add -A` only after the list above is clean
git status --short                  # confirm the staged set
git commit <profile-required-signing-option, if any> -F - <<'EOF'
<type>(<scope>): <summary>

<TICKET>
EOF
```

The heredoc keeps backticks and `$` in the message intact ([shell quoting](../README.md#shell-quoting)).

No AI attribution — no `Co-Authored-By:` naming an AI, no "Generated with …", no agent marker or emoji. Strip anything the tooling appends ([AGENTS.md](../../AGENTS.md#no-ai-attribution)). If the profile requires signing and it fails, follow the profile's documented recovery and never fall back to an unsigned commit. If the profile forbids signing, a signing attempt is the defect: retry with its required no-signing option.

## 3. Push and open the PR

```bash
git push -u <remote> <branch>
gh pr create --base <default-branch> --title "<title, per the profile's format>" --body "$(cat <<'EOF'
<template body>
EOF
)"
```

Push quirks (a branch touching CI config may need a different remote or scope) are in [AGENTS.md › Branches](../../AGENTS.md#branches).

Body follows [pr-template](pr-template.md), whose fill rules point at the workspace's actual template ([AGENTS.md › PR body](../../AGENTS.md#pr-template)). If the repo has its own template file and it differs, **the repo's file wins — but strip any AI product name from it first**, HTML comments included ([no-ai-attribution](../../AGENTS.md#no-ai-attribution)).

Answer every template question honestly, elaborate on a "yes", never leave a bare "No" where there is something to say. Cross-repo work declares its upstream PRs ([cross-repo](cross-repo.md)). Testing notes carry the QA steps, the proof list, and the **Not verified** items.

The body text comes from [commenter](../agents/commenter.md) — pass it the facts (what changed, evidence, links, proof names), post what it returns. **Draft it during QA**, while the stack work is running: only the QA verdict and the proof names arrive late.

## 4. Proofs

Attach every file in the ticket's proof directory — both sides of each before/after pair — and reference them by name from the PR body against their requirement; PR hosts generally have no CLI upload for body images ([AGENTS.md › Tracker](../../AGENTS.md#tracker) has the attachment call). Use absolute paths, and check the response is an attachment record, not an error — a discarded body hides it. A GIF inline in the PR needs the human to drag it in.

## 5. Ticket

Comment the PR URL and one line of what changed. Then transition the ticket **only if the profile declares a "PR opened" transition** ([AGENTS.md › Tracker](../../AGENTS.md#tracker) · [tracker › Transitions](tracker.md#transitions)) — check what is valid from the current state first, since transition names are not status names and that transition is usually invalid unless the "started" one already ran. Where the profile declares none, the comment above is the entire tracker write for this step; do not touch the ticket's state.

Cross-repo: comment the full PR chain in dependency order so reviewers merge in sequence.

<a id="ci"></a>
## 6. CI — watch until green, fix what it reds

**CI is where the full suite runs** — dev roles ran none ([implement-change › Tests](implement-change.md#tests)) and the tester ran only the change's own ([run-unit-tests](run-unit-tests.md)), so this is the first time anything outside the diff sees the branch. The PR is not done until CI is green: no worktree cleanup, no "shipped", while a check is red or running.

Watch every check to completion with the command in [AGENTS.md › Pull requests](../../AGENTS.md#pull-requests) — background it (suites run tens of minutes), watch **every PR concurrently**, and run [step 7](#7-pr-review) meanwhile; it reads the diff, not the checks. On non-zero, list the failing checks and read only the failing job's log.

Then, per failure:

| Failure | Who fixes it | Where |
| --- | --- | --- |
| test failure outside the diff — a regression the change's own tests could not see | owning dev role | its worktree, [implement-change](implement-change.md) |
| coverage below the gate on a changed file | owning dev role — write the missing test, never lower the gate | same |
| lint / type / migration-chain check | owning dev role | same |
| flake — passes on re-run, unrelated to the diff | releaser: re-run the failed jobs once, then say so in the report | — |
| infra / secrets / runner failure | stop and hand to the human | — |

Fixes go on the same branch: amend or add a commit (same rules as step 2), push, watch again. **Max 3 cycles**, then hand back with the failing job and its decisive log line.

Never make CI pass by weakening it: no coverage threshold lowered, no `skip`/`xfail` on a test that is genuinely failing, no lint rule disabled to clear an error.

<a id="review-bot"></a>
### Automated review comments — same loop, until it stops commenting

Where the profile documents a review bot ([AGENTS.md › Pull requests](../../AGENTS.md#pull-requests)), it re-reviews after each push, so comments arrive in waves. Treat a bot wave like a red check: read, fix or reject each comment, push, then wait for the next automated pass. **For a configured bot, done means the latest pass produced no new comments.**

Where the profile documents no review bot, skip the wave wait entirely. Handle human review comments that already exist using the same valid/reject rules below, but do not wait for a human to produce a silent follow-up pass and do not re-request review unless the profile explicitly makes that a gate.

Per comment, one of two outcomes — never silence:

- **Valid** → fix in the worktree, with a test when behaviour changes, then reply saying what changed.
- **Wrong or not applicable** → reply with the reason (the layering rule it missed, the test that covers it, the plan's deliberate trade-off). A reasoned rejection is a complete answer.

Reply text is outward-facing — it comes from [commenter](../agents/commenter.md), in the workspace's [voice](../../AGENTS.md#voice), with no AI attribution.

If a configured bot doesn't re-review after a push, re-request it; if that call is rejected, ask the human to press the button — never skip a required bot wave. This does not apply when the profile declares no bot.

With a configured bot, loop CI and automated review together: push once, wait for both, handle both, push again. **Max 3 bot waves**, then hand back with the open threads listed — a loop that never converges is usually a design disagreement, and that is the human's call. Without a bot, CI remains the asynchronous gate; handle existing human comments without adding a silence requirement.

<a id="7-pr-review"></a>
## 7. PR review

Run [pr-review.md](pr-review.md) on the open PR and post it — concurrently with the CI watch in step 6, not after it. Blockers and Majors go back to the owning dev role; after the fix, push, wait for CI (step 6) again, and re-review.

## 8. Clean up

Everything pushed **and CI green** → remove the worktrees; removing one while CI is red destroys the place the fix has to happen. Run from the repo, with the absolute path:

```bash
git worktree remove "$WS/llm/worktrees/<repo>-<TICKET>"   # --force only to discard uncommitted changes
git worktree prune                                        # stale entries
```

The branch survives; cut a fresh worktree if follow-ups land.

## Output

PR URL(s) in dependency order · ticket state after the run · proofs attached, by name · **CI: final state per check, and what was fixed to get there** · **automated review, when configured: comments received, fixed vs rejected with the reason** · existing human comments handled · PR-review verdict · worktrees removed · anything left open or unverified.

## Stop conditions

Stop and hand back when: a gate in step 1 fails; the profile's required commit mode cannot be completed; `git status` shows anything outside the change set; a transition the profile declares is invalid after checking what the tracker allows; CI is still red or a configured review bot is still raising new substantive comments after **3 waves** (step 6); a CI failure is infra, secrets, or runner-side; or the PR review is still failing after **3 cycles**.
