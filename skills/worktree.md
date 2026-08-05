---
name: worktree
description: The one-worktree-per-branch convention — the base ref, creation, dependency wiring, the naming contract QA and release depend on, and cleanup.
---

# Branches and worktrees

One checkout per branch under `$WS/llm/worktrees/`; share primary dependencies.

**Kind** reference · **Used by** [implement-change](implement-change.md) · [internal-review](internal-review.md) · [run-unit-tests](run-unit-tests.md) · [pr-review](pr-review.md) · [qa-verify](qa-verify.md) · [release-pr](release-pr.md) · **When** a branch is created, diffed, reviewed, run by the stack, or cleaned up · **Ends with** a correctly named worktree with shared dependencies, or a removed one

Run git inside target repo. Set `WS`.

<a id="base-ref"></a>
## The base ref — resolved from the profile, never hardcoded

Resolve profile `<BASE>` once:

```bash
BASE=<remote>/<default-branch>      # from AGENTS.md › Branches, e.g. origin/main
git fetch "${BASE%%/*}"             # the remote half; a stale ref makes every diff below wrong
```

Never hardcode base or push default. One worktree per branch.

<a id="naming"></a>
## Naming contract

QA/release depend on exact directory names:

| Work | Directory | Branch |
| --- | --- | --- |
| Ticket work | `$WS/llm/worktrees/<repo>-<TICKET>` | per [AGENTS.md › Branches](../../AGENTS.md#branches) |
| No ticket | `$WS/llm/worktrees/<repo>-<fix-description>` | per the profile |
| Reviewing a PR | `$WS/llm/worktrees/review-<repo>-<N>` | detached at `<remote>/<headRefName>` |

**One worktree per repo per ticket**, not per role: several roles working the same repo share it ([develop-flow › Lanes](develop-flow.md#lanes)).

<a id="claim"></a>
## Lane claim

Sharing a worktree is safe only if the roles take turns, and "one role writes a worktree at a time" is otherwise just an assertion — the work log that records a lane is written when a role *finishes*, so nothing marks a lane that is in progress. `$WS/llm/scratchpad/lanes/<repo>-<TICKET>` closes that window: written before the first edit, removed after the work log, and read by anyone about to join ([implement-change › Claim](implement-change.md#claim)).

It lives in the scratchpad, never in the worktree — a claim file inside the checkout would show up as an untracked `??` entry and land in the review diff.

## Create

**New work** — from inside the repo:

```bash
git fetch <remote>
git worktree add "$WS/llm/worktrees/<repo>-<TICKET>" -b <branch, per the profile> "$BASE"
```

**Reviewing a branch** — check it out read-only:

```bash
git fetch <remote>   # or the ref is stale
git worktree add "$WS/llm/worktrees/review-<repo>-<N>" <remote>/<headRefName>
```

<a id="setup"></a>
## Set up dependencies

Fresh worktrees lack ignored dependencies/env. Symlink/copy per profile; do not reinstall.

- Prefer the absolute form (`ln -s "$WS/<repo>/<dir>" <dir>`). Relative targets are counted from the worktree, three or four levels deep.
- Only run install inside the worktree if the branch itself changes a dependency manifest or lockfile — remove the symlink first so the shared environment isn't mutated.
- Set signing per the profile's rules, once per worktree.

## Clean up

When the PR merges, the review ends, or the run finishes with everything pushed:

```bash
git worktree remove "$WS/llm/worktrees/<dir>"   # --force only to discard uncommitted changes
git worktree prune                              # stale entries
git worktree list                               # what's active
```

<a id="gotchas"></a>
## Gotchas

- **Work stays uncommitted in worktrees until release.** Any workspace command that force-removes worktrees discards it with no prompt — check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) for which ones do, and never run them mid-flow.
- **Never run a formatter in a worktree with a symlinked dependency directory** — it rewrites the shared environment. Remove the symlink first, or format from the primary clone.
- **Never switch branches in place** inside a primary clone, and never scatter worktrees as loose siblings of the repos.
- `ln -s` into a path that already exists as a real directory creates the link *inside* it (`.venv/.venv`). Check with `ls -l` after linking; the formatter guard depends on the path being a symlink.
- A missing worktree at review or QA time means it was removed, not that the branch is gone — cut a fresh worktree from the branch.
