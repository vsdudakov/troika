# Worktrees

One git checkout per branch, all in this folder — mechanics and naming in [../skills/worktree.md](../skills/worktree.md).

**Gitignored.** Only this README is tracked; the checkouts belong to the workspace, not to the harness repo. Each subfolder is a worktree of a *product* repo and carries its own `.git` file pointing back at that repo — nothing here is ever committed to `llm/`.

**Not configuration.** A tool loading the `llm/` tree reads [`../agents/`](../agents/README.md) and [`../skills/`](../skills/README.md) only; never recurse into here.

## Layout

```
<repo>-<TICKET>/        ticket work      — branch <dev>/<TICKET>-<fix-description>
<repo>-<description>/   no-ticket work   — branch <dev>/<fix-description>
review-<repo>-<N>/      reviewing PR #N  — detached at origin/<headRefName>
```

The directory name is a contract: [qa-verify](../skills/qa-verify.md) builds the stack's path overrides from it and [release-pr](../skills/release-pr.md) removes it by path. `<repo>` is in every name because all repos share this one folder and PRs in different repos can share a number.

A worktree's dependencies are symlinked from the primary clone, never reinstalled ([AGENTS.md › Branches](../../AGENTS.md#branches)).

## Lifecycle

Created by [implement-change](../skills/implement-change.md) or [pr-review](../skills/pr-review.md), removed by [release-pr](../skills/release-pr.md) once everything is pushed and CI is green. Work stays uncommitted in here until release, so a stray `git worktree remove --force` destroys it — check [AGENTS.md › Gotchas](../../AGENTS.md#gotchas) for the workspace commands that do exactly that.

A missing worktree means it was removed, not that the branch is gone: the branch survives; cut a fresh one from it.
