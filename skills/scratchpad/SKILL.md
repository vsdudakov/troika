---
name: scratchpad
description: The handoff files roles write to each other during one ticket — plans, work logs, review, test and QA reports, and the proof artifacts the PR carries.
---

# Scratchpad

**Kind** reference · **Used by** every role · **When** writing or reading a handoff file · **Ends with** a file written at an absolute path the next role can find

The handoff files roles write to each other during one ticket: plans, work logs, review and
QA reports, and the proof artifacts the PR and the ticket carry. The directory is
`$TROIKA_SCRATCHPAD` ([workspace paths](../../../AGENTS.md#workspace-paths)); `python3
plugin/resolve.py --ensure` creates it.

**Untracked, and never committed.** These files belong to one ticket in one workspace. Every
product repo is a sibling of this tree, so they sit outside all of them — but a
worktree-relative `git add` can still pull them in, which is why
[release-pr](../release-pr/SKILL.md) runs `git status --short` before staging and expects no
scratchpad entries and no proofs.

**Not configuration.** A host loading this tree reads [`agents/`](../../ROLES.md) and
[`skills/`](../README.md) only, and never recurses into the scratchpad. Nothing in it
instructs a role; it is the output of one and the input of the next.

**Absolute paths only.** Every role runs with its cwd inside a worktree, so the scratchpad is
not below it. Resolve the paths once per session and use them verbatim:

```bash
eval "$(python3 plugin/resolve.py)"
ls "$TROIKA_SCRATCHPAD/plans/<TICKET>.md"
```

A relative path does not error loudly — it writes a file no later role finds, and uploads
nothing to the ticket.

## Layout

```
plans/<TICKET>.md                    the plan — requirements, repo split, pinned contracts
plans/<TICKET>-plan-review-<n>.md    plan review (the pre-code gate), cycle <n>
plans/<TICKET>-<role>.md             one dev role's work log
plans/<TICKET>-fix-<n>.md            one fix cycle on an already-open PR, cycle <n>
plans/<TICKET>-fix-<n>-<role>.md     one dev role's work log inside that fix cycle
plans/<TICKET>-review-<n>.md         internal review, cycle <n>
plans/<TICKET>-tests-<n>.md          unit-test run, cycle <n>
plans/<TICKET>-tests-<n>-<area>.log  one test lane's raw output
plans/<TICKET>-qa-<n>.md             QA report, cycle <n>
proofs/<TICKET>/                     one artifact per user-visible requirement
lanes/<repo>-<TICKET>                the claim on a worktree currently being written
```

Who writes and who reads each file is the [handoff contract](../../ROLES.md#handoff).
`<role>` is the role's frontmatter `name` (`backend-dev`, `frontend-dev`). `<n>` is the cycle
number, from 1 — a new cycle adds a file, it never overwrites the previous one, so the history
of what was rejected stays readable. [releaser](../../agents/releaser.md) gates on the
**highest-numbered** `-review-<n>.md`, `-tests-<n>.md`, and `-qa-<n>.md`; all three must exist
and must read `Approve` / `Approve with nits`, `Pass`, and `Pass`.

The `-fix-<n>` pair is written by [fix-pr](../fix-pr/SKILL.md) and uses `pr-<N>` in place of
`<TICKET>` where the PR carries no ticket key. It never overwrites the flow's own
`<TICKET>-<role>.md`: the record of what the PR looked like before the fix is what a reviewer
reads to judge the fix.

Plan files follow [plan-template](../plan-template/SKILL.md). Proofs are named after the
requirement they prove (`req-2-portfolio-filter.gif`) — see
[qa-verify › Proofs](../qa-verify/SKILL.md#8-proofs-for-the-pr) for what counts as one per
kind of change. Never fabricate a proof; unexercised requirements go under **Not verified** in
the QA report.

Test-data and one-off scripts a role needs mid-flow also live here
([qa](../../agents/qa.md), which may never edit product code). Keep them under the ticket
they belong to.

## Lifecycle

One ticket's files stay until its PR is merged — [reviewer](../../agents/reviewer.md),
[qa](../../agents/qa.md), and [releaser](../../agents/releaser.md) each read files written
cycles earlier, and `release-pr` uploads the proofs from disk. After the merge they are
disposable: delete `plans/<TICKET>*.md` and `proofs/<TICKET>/` per ticket, since the proofs
already live on the ticket and the reasoning on the PR.

## Gotchas

- **Lanes that run concurrently write different files.** That is what makes them safe to
  parallelise ([develop-flow › Parallelism](../develop-flow/SKILL.md#parallelism)). Two roles
  never append to one handoff file.
- **A fact worth keeping past the ticket is not a scratchpad file.** Write it to
  [memory](../memory/SKILL.md), or promote it into the workspace `AGENTS.md`, or into
  `agents/` / `skills/` if it is true in any organisation.
- **`git clean -xfd` deletes all of it** ([worktree › Gotchas](../worktree/SKILL.md)).
