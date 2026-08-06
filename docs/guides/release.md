---
title: Releasing a change
description: What the releaser does after QA passes — the gates it checks first, the commit and PR it produces, and the CI loop it will not exit early.
---

# Releasing a change

`release-pr` is the only procedure that produces history. Everything before it is worktrees
and files.

It has no `/` command: `/troika:dev` runs it as step 7, and on its own you ask for it by
name, after review and QA have passed.

```
run release-pr for SCRUM-123
```

## 1. Gates first

The releaser reads the **highest-numbered** review, tests and QA files for the ticket. All
three must exist and must read `Approve` / `Approve with nits`, `Pass`, and `Pass`. A missing
file is a stop, not an assumption — an absent QA report means QA did not run, not that it had
nothing to say.

## 2. Commit

One commit, in the profile's format, from the profile's rules. No AI attribution anywhere in
the message, the branch name, the PR, or the ticket.

## 3. Push and open the PR

Title and body come from the workspace's PR template, filled honestly by the commenter:
sections filled with facts, supporting questions answered, and any "yes" elaborated. The
proofs QA captured are attached — the PR carries evidence, not adjectives.

## 4. Ticket

Attachments and a comment, plus a transition **only where the profile declares one**. If the
profile says there are no transitions, the releaser records the equivalent write and moves on
rather than inventing a workflow.

## 5. CI, and the loop it will not exit early

The PR is not done when it is opened. The releaser watches until CI is green and the review
bots are quiet — review comments arrive in waves, so "done" means the latest pass produced no
new inline comments and nobody is left waiting.

!!! warning "Never green a check by weakening it"
    No lowered coverage threshold, no `skip`/`xfail`, no disabled lint rule. A red check is
    routed back to the owning dev role and fixed with a test. When a test is the stale party
    and the production contract moved deliberately, **the test changes** — never widen
    production code to make it pass.

## 6. Clean up

The worktree is removed by path once everything is pushed and CI is green. Work stays
uncommitted in a worktree until this point, so a stray force-removal destroys it — which is
why the profile's `#gotchas` should list every workspace command that does exactly that.

## Bigger releases

Shipping one change is `release-pr`. Two other procedures cover the wider cycle:

- `release-cut` — promote the previous pre-release, branch, tag, notes, QA plan, deploy to
  pre-production, prepare the announcement.
- `release-notes` — generate customer-readable notes from the diff against the previous
  release branch, deduplicated by patch-id, cross-checked against labels, with a
  generation-notes audit trail.

Both follow the profile's release scheme; neither invents one.
