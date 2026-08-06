---
title: Handoff and worktrees
description: Roles communicate through files, not shared memory. The handoff contract, the naming rules, and the lane claim that makes parallel work safe.
---

# Handoff and worktrees

Roles run in separate contexts. They communicate through **files** — never a shared
conversation — so nothing downstream inherits an earlier role's reasoning, only its stated
result.

## The handoff contract

| File | Written by | Read by |
| --- | --- | --- |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` | architect | everyone |
| `…/<TICKET>-plan-review-<n>.md` | reviewer, plan pass | architect, orchestrator |
| `…/<TICKET>-<role>.md` | each dev role | reviewer, qa, release |
| `…/<TICKET>-review-<n>.md` | reviewer, internal pass | dev roles, release |
| `…/<TICKET>-tests-<n>.md` | tester | dev roles, release |
| `…/<TICKET>-qa-<n>.md` | qa | dev roles, release |
| `$TROIKA_SCRATCHPAD/proofs/<TICKET>/*` | qa | release |
| `$TROIKA_SCRATCHPAD/lanes/<repo>-<TICKET>` | whoever holds the lane | any role about to join it |

`<role>` is the role's frontmatter name. `<n>` starts at 1, and **a new cycle adds a file, it
never overwrites one** — so the history of what was rejected stays readable, and the releaser
gates on the highest-numbered review, tests and QA files, all of which must exist and read
`Approve` / `Pass`.

A role that finishes returns: branch name, worktree path, what changed, commands run with
their results, and anything left undone.

## Absolute paths, always

Every role's cwd is inside a worktree, so the scratchpad is not below it. A relative path does
not fail loudly — it writes a file no later role finds, and uploads nothing to the ticket.
Roles resolve the paths once and use them verbatim:

```bash
eval "$(python3 plugin/resolve.py --ensure)"
```

[Paths and the resolver :material-arrow-right:](paths.md){ .md-button }

## One worktree per branch

```
$TROIKA_WORKTREES/
  <repo>-<TICKET>/        ticket work
  <repo>-<description>/   no-ticket work
  review-<repo>-<N>/      reviewing PR #N, detached
```

The directory name is a **contract**, not a convention: QA builds the stack's path overrides
from it, and the releaser removes the worktree by path. `<repo>` appears in every name because
all repos share one folder and PRs in different repos can share a number.

Dependencies are symlinked from the primary clone rather than reinstalled — which is why no
role may run a formatter inside a worktree with a symlinked dependency directory: it would
rewrite the shared environment.

## The lane claim

"One role writes a worktree at a time" is only enforceable if in-progress work is visible. A
work log is written when a role *finishes*, so nothing marks a lane that is mid-flight —
`$TROIKA_SCRATCHPAD/lanes/<repo>-<TICKET>` closes that window. It is written before the first
edit, removed after the work log, and read by anyone about to join.

It lives in the scratchpad, never in the worktree: a claim file inside the checkout would show
up as an untracked entry and land in the review diff.

!!! danger "`git clean -xfd` inside the Troika clone"
    The three state directories are *ignored*, and `-x` is exactly the flag that deletes
    ignored files. One command takes every uncommitted worktree, every plan and proof, and all
    of memory. Clean with explicit paths (`git clean -fd agents skills`) or not at all.
