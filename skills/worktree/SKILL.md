---
name: worktree
description: The one-worktree-per-branch convention — the base ref, creation, dependency wiring, the naming contract QA and release depend on, and cleanup.
---

# Branches and worktrees

One checkout per branch under `$TROIKA_WORKTREES/`; share primary dependencies.

**Kind** reference · **Used by** [implement-change](../implement-change/SKILL.md) · [internal-review](../internal-review/SKILL.md) · [run-unit-tests](../run-unit-tests/SKILL.md) · [pr-review](../pr-review/SKILL.md) · [qa-verify](../qa-verify/SKILL.md) · [release-pr](../release-pr/SKILL.md) · **When** a branch is created, diffed, reviewed, run by the stack, or cleaned up · **Ends with** a correctly named worktree with shared dependencies, or a removed one

Run git inside target repo. Set `TROIKA_WORKSPACE`.

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
| Ticket work | `$TROIKA_WORKTREES/<repo>-<TICKET>` | per [AGENTS.md › Branches](../../../AGENTS.md#branches) |
| No ticket | `$TROIKA_WORKTREES/<repo>-<fix-description>` | per the profile |
| Reviewing a PR | `$TROIKA_WORKTREES/review-<repo>-<N>` | detached at `<remote>/<headRefName>` |
| Fixing a PR | the ticket lane if it exists, else `$TROIKA_WORKTREES/fix-<repo>-<N>` | `<headRefName>`, tracking `<remote>/<headRefName>` |

**One worktree per repo per ticket**, not per role: several roles working the same repo share it ([develop-flow › Lanes](../develop-flow/SKILL.md#lanes)).

<a id="claim"></a>
## Lane claim

Sharing a worktree is safe only if the roles take turns, and "one role writes a worktree at a time" is otherwise just an assertion — the work log that records a lane is written when a role *finishes*, so nothing marks a lane that is in progress. `$TROIKA_SCRATCHPAD/lanes/<repo>-<TICKET>` closes that window: written before the first edit, removed after the work log, and read by anyone about to join ([implement-change › Claim](../implement-change/SKILL.md#claim)).

It lives in the scratchpad, never in the worktree — a claim file inside the checkout would show up as an untracked `??` entry and land in the review diff.

## Create

**New work** — from inside the repo:

```bash
git fetch <remote>
git worktree add "$TROIKA_WORKTREES/<repo>-<TICKET>" -b <branch, per the profile> "$BASE"
```

**Reviewing a branch** — check it out read-only:

```bash
git fetch <remote>   # or the ref is stale
git worktree add "$TROIKA_WORKTREES/review-<repo>-<N>" <remote>/<headRefName>
```

**Fixing a PR** — the same checkout cannot be used: it is detached, so nothing committed in
it can be pushed. Track the branch instead ([fix-pr](../fix-pr/SKILL.md)):

```bash
git fetch <remote>
git worktree add --track -b <headRefName> "$TROIKA_WORKTREES/fix-<repo>-<N>" <remote>/<headRefName>
```

<a id="setup"></a>
## Set up dependencies

Fresh worktrees lack ignored dependencies/env. Symlink/copy per profile; do not reinstall.

- Prefer the absolute form (`ln -s "$TROIKA_WORKSPACE/<repo>/<dir>" <dir>`). Relative targets are counted from the worktree, three or four levels deep.
- Only run install inside the worktree if the branch itself changes a dependency manifest or lockfile — remove the symlink first so the shared environment isn't mutated.
- Set signing per the profile's rules, once per worktree.

## Clean up

When the PR merges, the review ends, or the run finishes with everything pushed:

```bash
git worktree remove "$TROIKA_WORKTREES/<dir>"   # --force only to discard uncommitted changes
git worktree prune                              # stale entries
git worktree list                               # what's active
```

## The directory itself

Every checkout lives under `$TROIKA_WORKTREES`, untracked and per-workspace; `python3
plugin/resolve.py --ensure` creates it. Each subfolder is a worktree of a *product* repo and
carries its own `.git` file pointing back at that repo — nothing in there is ever committed to
this tree, and a host loading it never recurses into the directory.

<a id="gotchas"></a>
## Gotchas

- **`git clean -xfd` from this tree destroys every branch in progress.** The directory is
  ignored, and `-x` is exactly the flag that removes ignored files — one command takes every
  uncommitted worktree, plus the [scratchpad](../scratchpad/SKILL.md) and
  [memory](../memory/SKILL.md). Clean with explicit paths (`git clean -fd agents skills`) or
  not at all.
- **Work stays uncommitted in worktrees until release.** Any workspace command that force-removes worktrees discards it with no prompt — check [AGENTS.md › Gotchas](../../../AGENTS.md#gotchas) for which ones do, and never run them mid-flow.
- **Never run a formatter in a worktree with a symlinked dependency directory** — it rewrites the shared environment. Remove the symlink first, or format from the primary clone.
- **Never switch branches in place** inside a primary clone, and never scatter worktrees as loose siblings of the repos.
- `ln -s` into a path that already exists as a real directory creates the link *inside* it (`.venv/.venv`). Check with `ls -l` after linking; the formatter guard depends on the path being a symlink.
- A missing worktree at review or QA time means it was removed, not that the branch is gone — cut a fresh worktree from the branch.
