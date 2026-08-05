---
name: worktree
description: The one-worktree-per-branch convention — the base ref, creation, dependency wiring, the naming contract QA and release depend on, and cleanup.
---

# Branches and worktrees

Every branch gets its own checkout under the workspace-root `llm/worktrees/`, sharing the primary clone's installed dependencies.

**Kind** reference · **Used by** [implement-change](implement-change.md) · [internal-review](internal-review.md) · [run-unit-tests](run-unit-tests.md) · [pr-review](pr-review.md) · [qa-verify](qa-verify.md) · [release-pr](release-pr.md) · **When** a branch is created, diffed, reviewed, run by the stack, or cleaned up · **Ends with** a correctly named worktree with shared dependencies, or a removed one

All git commands run **from inside the target repo** — never from the workspace root, which may not be a git repo. Set `WS` first ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

<a id="base-ref"></a>
## The base ref — resolved from the profile, never hardcoded

Remote name and default branch are per-workspace: [AGENTS.md › Branches](../../AGENTS.md#branches). Every worktree creation and every branch diff in `llm/` is written against `<BASE>` — resolve it once per session and use the variable:

```bash
BASE=<remote>/<default-branch>      # from AGENTS.md › Branches, e.g. origin/main
git fetch "${BASE%%/*}"             # the remote half; a stale ref makes every diff below wrong
```

A skill that hardcodes `origin/main` is wrong in any workspace whose remote or default branch differs. Nothing is pushed to the default branch directly; every branch lives in exactly one worktree.

<a id="naming"></a>
## Naming contract

The worktree directory name is a contract: [qa-verify](qa-verify.md) builds the stack's path overrides from it and [release-pr](release-pr.md) removes it by path. A wrong name doesn't fall back to a default — the stack starts in a directory that doesn't exist and the processes die at boot.

| Work | Directory | Branch |
| --- | --- | --- |
| Ticket work | `$WS/llm/worktrees/<repo>-<TICKET>` | per [AGENTS.md › Branches](../../AGENTS.md#branches) |
| No ticket | `$WS/llm/worktrees/<repo>-<fix-description>` | per the profile |
| Reviewing a PR | `$WS/llm/worktrees/review-<repo>-<N>` | detached at `<remote>/<headRefName>` |

`<repo>` is in every path because all repos share the one `llm/worktrees/` folder and PRs in different repos can share a number.

**One worktree per repo per ticket**, not per role: several roles working the same repo share it ([develop-flow › Lanes](develop-flow.md#lanes)).

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

A fresh worktree has no gitignored files — no installed dependencies, no `.env`. **Do not re-run install**: symlink the primary clone's dependency directory and copy any `.env` the repo needs. Exact links per repo: [AGENTS.md › Branches](../../AGENTS.md#branches).

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
