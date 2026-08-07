---
title: The nine review checks
description: What the reviewer checks on every diff, which severities are pinned, and why two of the twenty-one test cases are controls rather than defects.
---

# The nine review checks

The reviewer runs the same nine checks in the same order on the whole diff, whether it is a
pre-push internal review or a review posted to a PR. Order is part of the contract: the report
rows follow the rule order, so evidence stays paired with the right row.

1. **Requirements** — all *and only* the planned work. Scope creep is a finding.
2. **Code style** — the profile's rules, per language, cited `file:line`. **An import inside a
   function or method is a Major**, not a nit: it hides a circular import, so the finding names
   the cycle and the layering fix. A comment that restates the code is a nit, every time.
3. **Verification** — the profile's commands only, with the decisive failure quoted. A command
   the profile does not define is not a gate that was passed.
4. **Layering** — no layer skipped, no cross-layer reach-around.
5. **Queries** — N+1, missing prefetch or eager loading, unindexed or unbounded queries.
6. **Tests** — a mirror test for every changed source and branch; real behaviour; only external
   services mocked; the form the profile requires. **The work log's collected count must match
   the tests written** — missing, short, or overstated is a Blocker, and overstated is the worse
   case because it reads as coverage that was never written.
7. **Migrations** — generated, not hand-edited; no applied migration modified.
8. **Contract match** — the implemented API shape equals the plan's pinned contract, and the
   consumer uses exactly that shape.
9. **Hygiene** — no secrets, no `.env`, no debug prints, no commented-out code, no AI
   attribution, no truncated or empty new files.

## Severity, and where it comes from

Two rules pin a severity in the role file itself — check 2's deferred import (**Major**) and
check 6's collection count (**Blocker**). Every other rule leaves the rating to judgment, and
findings are graded as either gating (`Blocker`/`Major`) or not.

That is deliberate, and it was measured. In a full behavioural run, cases that pinned `Major`
on an *unpinned* check came back rated `Blocker` — while identifying the defect correctly in
all of those runs. Nothing escaped the gate; the rating simply is not stable unless the role
file states it. **To make a rule carry a severity, state it in the role file.**

## Nits must not gate

`Approve with nits` is a pass. A reviewer that blocks the flow on style the profile calls a
nit is failing at its job just as surely as one that waves a Blocker through — which is why
one of the twenty-one behavioural cases is a diff whose only problems are nits, and it *fails*
if the reviewer gates on them.

## The reviewer never runs anything

No tests, no scripts, no fixes. It reads the diff, the plan, the work log and the rest of the
worktree, and it writes a numbered report. A reviewer with a shell starts debugging, and a
debugging reviewer stops reviewing.

## Where reviews land

Internal review writes `$TROIKA_SCRATCHPAD/plans/<TICKET>-review-<n>.md` and posts nothing
outside the workspace. PR review posts exactly one comment, through the commenter, with the
findings passed through a quoted heredoc — backticks in a double-quoted shell argument are
command substitutions, and they silently swallow the text.

[Testing :material-arrow-right:](../testing.md){ .md-button }
