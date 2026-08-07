---
name: fix-pr
description: Fixes an open PR — either what you asked for in words, or every unresolved review comment on it — through the owning dev roles, then re-reviews, re-tests, pushes to the same branch and answers every thread.
---

# Fix PR

Change an open PR without opening a new one. Same branch, same PR, one push per cycle.

**Kind** procedure · **Used by** orchestrator · **When** a PR exists and needs work — a review left comments, CI or a human found a defect, or the change itself must be different · **Ends with** the fix pushed to the PR's head branch, CI green, every comment thread answered, and a fix report per cycle

```
/tr:fix <PR> [what to fix]
  └─ 1 read the PR ── ticket key · head branch · files · unresolved threads
  └─ 2 worktree on the head branch (writable, tracking)
  └─ 3 fix list ── instruction mode │ comment mode (fix ∥ reject with a reason)
  └─ 4 ∥ dev roles by ownership ── implement-change, tests written not run
  └─ 5 internal review (max 3) ──▶ 6 unit tests on the change ──▶ 7 QA if user-visible
  └─ 8 releaser commits + pushes the same branch — no new PR
  └─ 9 commenter answers every thread ──▶ 10 CI green ──▶ 11 clean up
```

Set `TROIKA_WORKSPACE` first. This procedure never creates a PR, never rebases, never
force-pushes, and never resolves a thread it did not answer.

<a id="modes"></a>
## Modes — the argument decides which

| Argument | Mode | What gets fixed |
| --- | --- | --- |
| `<PR>` alone | **comment** | every unresolved review comment on the PR, bot and human |
| `<PR>` plus a description | **instruction** | exactly what the description asks for, and nothing else |
| `<PR>` plus a description naming the comments | **both** | the description, plus the threads it points at |

In instruction mode the comments are still **read** (step 1) and reported as unhandled — a
fix that lands beside three untouched Blocker comments is a half-done PR, and the report is
where that becomes visible instead of being discovered at merge time.

## 1. Read the PR

From inside the target repo:

```bash
gh pr view <N> --json number,title,body,url,state,isDraft,author,headRefName,headRepositoryOwner,baseRefName,files,comments,reviews
gh pr diff <N>
```

Unresolved inline threads are not in that payload — resolution state is GraphQL only:

```bash
gh api graphql -f query='
  query($owner:String!,$repo:String!,$pr:Int!){
    repository(owner:$owner,name:$repo){ pullRequest(number:$pr){
      reviewThreads(first:100){ nodes{ id isResolved isOutdated path line
        comments(first:20){ nodes{ databaseId author{login} body url } } } } } } }
' -F owner=<owner> -F repo=<repo> -F pr=<N>
```

Pin, and state in the report: PR state (a merged or closed PR is a stop condition), head
branch, head repository owner, base branch, changed files, and the ticket key from the branch
name, PR title, or body (PROFILE.md › Branches (`#branches`)).

`<KEY>` below is that ticket key where the PR has one, and `pr-<N>` where it does not. Every
handoff file in this run is named from it.

Read the workspace memory too — `ls $TROIKA_MEMORY/*.md`, there is no index file
([memory](../memory/SKILL.md)).

## 2. Worktree — writable, on the head branch itself

The review worktree is detached and read-only ([worktree › Naming](../worktree/SKILL.md#naming)); a fix
needs a branch it can commit and push:

```bash
git fetch <remote>
git worktree list | grep "<repo>-<KEY>"          # the flow's own lane, if this ticket has one
git worktree add --track -b <headRefName> "$TROIKA_WORKTREES/fix-<repo>-<N>" <remote>/<headRefName>
```

- **The flow's lane already exists** (`$TROIKA_WORKTREES/<repo>-<KEY>`) — join it, read the
  work logs in it, and do not cut a second checkout of the same branch. Two worktrees on one
  branch is how a fix gets pushed and then overwritten.
- **The local branch already exists** — `git worktree add "$TROIKA_WORKTREES/fix-<repo>-<N>" <headRefName>`
  then `git pull --ff-only`. A branch behind its remote produces a push that rejects after all
  the work is done.

Claim the lane before the first edit and release it after the report
([implement-change › Claim](../implement-change/SKILL.md#claim)). Wire dependencies per
[worktree › Setup](../worktree/SKILL.md#setup) — symlink, never reinstall.

**A PR from a fork cannot be pushed to** unless maintainer edits are enabled. Check
`headRepositoryOwner` against the repo owner before any code is written, and stop there if
they differ and the push would fail — the work is otherwise done and then stranded.

<a id="fix-list"></a>
## 3. The fix list — written down before anything is edited

One numbered list, each item with the file and the reason, in `$TROIKA_SCRATCHPAD/plans/<KEY>-fix-<n>.md`.

**Instruction mode:** turn the description into requirements the way the plan does
([plan-template](../plan-template/SKILL.md)) — small enough that no plan-review gate is
needed, but written down, because "what was asked" is what step 9 reports against. A
description that cannot be turned into a concrete change in this PR's scope is a stop
condition, not a guess; a description that is really a new feature belongs in
[develop-flow](../develop-flow/SKILL.md), not here.

**Comment mode:** every unresolved, non-outdated thread gets exactly one of two outcomes,
decided now and recorded — never silence ([release-pr › Automated review](../release-pr/SKILL.md#review-bot)):

| Outcome | When | What step 9 posts |
| --- | --- | --- |
| **fix** | the comment is right, or cheap enough that arguing costs more | what changed, and the test that now covers it |
| **reject** | the comment misses a layering rule, a covering test, or a deliberate trade-off | the reason, with the `file:line` or plan line that carries it |

A rejection is a complete answer. Outdated threads on code the PR no longer contains are
answered as such and not fixed. A thread asking for a change the PR was not asked to make is
rejected with that reason and named in the report — scope creep enters a PR through review
comments more often than through the plan.

## 4. Implement — the owning dev role, one per repo

Route each item by PROFILE.md › Ownership (`#ownership`), then run
[implement-change](../implement-change/SKILL.md) for the items that role owns:

- [backend-dev](../../agents/backend-dev.md) — server-side paths.
- [frontend-dev](../../agents/frontend-dev.md) — only the client app(s) it owns. An app no
  role owns is a stop, not a judgement call.
- Both in one repo — they share the worktree and take turns in
  dependency order (`#dependency-order`); the second starts from the first's
  work log.

The dev roles keep every rule they have in the flow: tests written with the code and
**collected, never executed** ([tests](../implement-change/SKILL.md#tests) ·
[collect](../implement-change/SKILL.md#collect)), and the profile's verification commands
green before reporting ([verify](../implement-change/SKILL.md#verify)).

They write `$TROIKA_SCRATCHPAD/plans/<KEY>-fix-<n>-<role>.md`, not the flow's
`<KEY>-<role>.md` — a fix cycle that overwrites the original work log destroys the record of
what the PR was before it.

A comment answered by a code change needs a test that fails without it. A comment answered
in words needs none.

## 5. Internal review — the fix diff, before it is pushed

Run [internal-review](../internal-review/SKILL.md) over the diff this cycle added. The review
is of the fix, not of the PR — the PR already had its pass ([pr-review](../pr-review/SKILL.md)),
and re-reviewing the whole diff every cycle is how a two-line fix costs an hour.

Blocker/Major → owner fixes and re-verifies; re-review. Cap at 3 cycles. Each pass writes
`$TROIKA_SCRATCHPAD/plans/<KEY>-review-<n>.md` at the next free `<n>`, continuing the PR's
existing numbering.

## 6. Unit tests — the change's own, in parallel lanes

Run [run-unit-tests](../run-unit-tests/SKILL.md) over the tests this cycle wrote plus the
existing tests tied to the sources it touched ([selection](../run-unit-tests/SKILL.md#selection)).
This is the first execution of anything in this cycle. Failures route back to the owning role;
cap at 3. Writes `$TROIKA_SCRATCHPAD/plans/<KEY>-tests-<n>.md`.

## 7. QA — only when the fix is user-visible

A fix that changes behaviour a person can see runs [qa-verify](../qa-verify/SKILL.md) against
this worktree, with one proof per changed behaviour; a PR-only start point uses
[qa-verify › From a PR](../qa-verify/SKILL.md#from-pr). Writes
`$TROIKA_SCRATCHPAD/plans/<KEY>-qa-<n>.md` and proofs under `$TROIKA_SCRATCHPAD/proofs/<KEY>/`.

A rename, a comment reply, a test-only change, or an internal refactor with no behaviour
change skips this — and the report says it skipped it and why. Skipping QA silently is how a
"tiny" fix ships a broken screen.

## 8. Commit and push — same branch, no new PR

[releaser](../../agents/releaser.md) owns this, with the profile's exact signing mode and
ticket-key form ([release-pr › Commit](../release-pr/SKILL.md#2-commit)):

```bash
git status --short                 # only the fix; no .env, no scratchpad, no proofs
git add <paths>
git commit <profile-required-signing-option, if any> -F - <<'EOF'
fix(<scope>): <what this cycle changed>

<KEY>
EOF
git push <remote> <headRefName>    # no -u, no --force, no rebase
```

**No AI attribution** anywhere in the message (`#no-ai-attribution`).
The PR already exists: `gh pr create` here opens a duplicate against the same branch. Update
the PR body only if the fix changed what the PR does, and then only the sections that are now
wrong ([pr-template](../pr-template/SKILL.md)).

## 9. Answer every thread

All outward text comes from [commenter](../../agents/commenter.md), posted with a quoted
heredoc ([shell quoting](../../README.md#shell-quoting)). Reply on the thread, not as a new
top-level comment — a reply nobody can trace to the comment it answers reads as silence:

```bash
gh api repos/<owner>/<repo>/pulls/<N>/comments/<comment-id>/replies -f body="$(cat <<'EOF'
<commenter's text>
EOF
)"
```

One summary comment for the cycle goes on the PR itself: what was fixed, what was rejected
and why, and what is still open. Resolve only threads this cycle actually answered, and only
where the profile allows it (PROFILE.md › Pull requests (`#pull-requests`)).

## 10. CI — green before this is done

A push restarts CI and, where configured, the review bot. Watch every check with the command
in PROFILE.md › Pull requests (`#pull-requests`) — background it, suites run
tens of minutes — and handle failures exactly as the release flow does
([release-pr › CI](../release-pr/SKILL.md#ci)): code failures to the owning role, one re-run
for a flake, infra and secrets to the human.

A new bot wave is a new fix cycle: back to step 3 with `<n>` incremented, capped at 3 waves
total. **Never make CI pass by weakening it** — no lowered coverage gate, no `skip`/`xfail` on
a genuinely failing test, no disabled lint rule.

## 11. Clean up

Only after the push is green:

```bash
git worktree remove "$TROIKA_WORKTREES/fix-<repo>-<N>"
git worktree prune
rm -f "$TROIKA_SCRATCHPAD/lanes/<repo>-<KEY>"
```

A joined flow lane is left where it was — the flow still owns it.

## Output

`$TROIKA_SCRATCHPAD/plans/<KEY>-fix-<n>.md`, and the same back to the caller:

PR URL and head branch · mode ([modes](#modes)) · the fix list as decided, item by item · for
each comment: fixed or rejected, with the reason · files changed and by which role · the node
IDs of tests written, and the collected count · internal review verdict · unit-test verdict ·
QA verdict and proofs, or the reason QA was skipped · commit SHA pushed · threads answered ·
CI final state per check · comments left unhandled and why · anything still open.

Unhandled comments are reported even in instruction mode, where not handling them was the
point.

## Stop conditions

Write a [memory](../memory/SKILL.md) entry when something failed for a reason the docs did
not predict, with the cost.

Stop and hand back when: the PR is merged, closed, or a draft nobody asked to fix; the head
branch is on a fork the token cannot push to; the instruction cannot be turned into a concrete
change, or describes a new feature rather than a fix to this PR; a comment demands work in a
repo or app no role owns; the branch has diverged such that the push needs a rebase or a force
([release-pr](../release-pr/SKILL.md) never force-pushes either); the internal review, the
tests, QA, or a bot wave is still failing after **3 cycles**; or a CI failure is infra,
secrets, or runner-side.
