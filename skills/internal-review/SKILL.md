---
name: internal-review
description: Reviews the local branch diff before QA and before any push — catches layering, coverage, style, and hygiene defects that QA cannot see. Posts nothing outside the workspace.
---

# Internal review (pre-PR)

Pre-push local diff review.

**Kind** procedure · **Used by** [reviewer](../../agents/reviewer.md) · **When** dev roles report done, before the tests run and before any push (develop-flow step 4) · **Ends with** a verdict file and a loop back to the dev role, nothing posted outside the workspace

Read-only: no edit, push, or test. Set `TROIKA_WORKSPACE`.

## 1. Requirements

Read plan and dev work log; they define scope.

<a id="diff-new-files"></a>
## 2. Diff

From the dev role's worktree. `<BASE>` is the profile's base ref, resolved once ([worktree › The base ref](../worktree/SKILL.md#base-ref)) — never hardcoded:

```bash
BASE=<remote>/<default-branch>                   # PROFILE.md › Branches
git fetch "${BASE%%/*}"
git status --short                               # untracked files show as ??
git add -N -- .                                  # intent-to-add, so new files enter the diff
git --no-pager diff "$BASE"...HEAD               # committed work
git --no-pager diff                              # uncommitted, now including new files
git --no-pager diff --stat "$BASE"...HEAD
```

Account for every `??` — an untracked, unreviewed file ships unseen. `git add -N` records intent-to-add so new files enter the diff; their content stays unstaged and release commits normally afterwards. Review the whole diff and needed context.

<a id="runner"></a>
### Running this pass on the other family

Preferred for independent review. **The tool and the exact command are the workspace's** — PROFILE.md › Review runner (`#review-runner`), diff pass — and it must cover staged, unstaged **and** untracked files, which is what step 2's `git add -N` prepares:

```bash
cd "$TROIKA_WORKTREES/<repo>-<TICKET>"
cat "$TROIKA_PROFILE" \
    "${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md" \
    "${CLAUDE_PLUGIN_ROOT}/skills/internal-review/SKILL.md" \
    "$TROIKA_SCRATCHPAD/plans/<TICKET>.md" \
    "$TROIKA_SCRATCHPAD/plans/<TICKET>-<role>.md" \
  | <the profile's diff-pass review command>
```

For work already committed on the branch, use the profile's base-ref form of that command. Model and effort come from the `reviewer` row of PROFILE.md › Models and effort (`#models`); where the profile declares no separate runner, run the pass in a fresh session on that row. Follow [output](#output).

## 3. Checks

The nine checks and their definitions are in [reviewer › Rules](../../agents/reviewer.md#rules): requirements, code style, verification, layering, queries, tests present, migrations, contract match, hygiene.

Internal-pass specifics:

- **Verification:** run only profile commands; quote decisive failure.
- **Tests:** mirror every source/branch; real behavior; node IDs match diff. Missing/hollow is Blocker.
- **Runnable:** the work log must carry a collected count matching the tests written ([collect](../implement-change/SKILL.md#collect)); a missing or short count is a Blocker, because nothing else has proved these files even import. Read for what collection cannot see: a fixture that resolves but returns the wrong shape, an assertion that passes for the wrong reason.
- **Regression:** name shared model/base/util/config/middleware/migration/public-contract blast radius left to CI.
- **Bug tickets:** the diff must carry a regression test that encodes what `$TROIKA_SCRATCHPAD/plans/<TICKET>-repro-<n>.md` recorded — same input, same path, asserting the corrected behaviour. Read it against the reproduction, not against the brief's prose: a test that would pass on the base ref has not encoded the bug, and that is a Blocker under check 6.

## 4. Report

Use the [reviewer output format](../../agents/reviewer.md#output).

## 5. Loop

Blocker/Major → owner fixes/verifies; re-review. Fix cheap nits.

## Output

Write the report to `$TROIKA_SCRATCHPAD/plans/<TICKET>-review-<n>.md` (`<n>` = cycle, from 1) **and** return it to the orchestrator. That file is the release gate's evidence — [releaser](../../agents/releaser.md) runs in a separate context and reads the highest-numbered one ([handoff contract](../../ROLES.md#handoff)).

Nothing leaves the workspace, so this report skips [commenter](../../agents/commenter.md) — internal, terse, for the dev role to act on.

## Stop conditions

**Cap at 3 cycles.** Third review still holding Blockers or Majors → stop the flow and report the unresolved findings. Also stop if the diff no longer matches the plan's scope, or a worktree named in the work log is missing ([worktree › Gotchas](../worktree/SKILL.md#gotchas)).
