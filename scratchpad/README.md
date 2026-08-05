# Scratchpad

The handoff files roles write to each other during one ticket: plans, work logs, review and QA reports, and the proof artifacts the PR and the ticket carry.

**Gitignored.** Only this README is tracked — these files belong to one ticket in one workspace, never to the harness repo. Every product repo is a sibling of this tree, so these files sit outside all of them, but a worktree-relative `git add` can still pull them in: [release-pr](../skills/release-pr.md) runs `git status --short` before staging and expects no scratchpad entries and no proofs.

**Not configuration.** A tool loading the `llm/` tree reads [`../agents/`](../agents/README.md) and [`../skills/`](../skills/README.md) only, and never recurses into here. Nothing in this directory instructs a role; it is the output of one and the input of the next.

**Absolute paths only.** Every role runs with its cwd inside a worktree, so `llm/scratchpad/` is not below it. Set `WS` once per session ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)) and use it verbatim:

```bash
ls "$WS/llm/scratchpad/plans/<TICKET>.md"
```

A relative path does not error loudly — it writes a file no later role finds, and uploads nothing to the ticket.

## Layout

```
plans/<TICKET>.md                    the plan — requirements, repo split, pinned contracts
plans/<TICKET>-plan-review-<n>.md    plan review (the pre-code gate), cycle <n>
plans/<TICKET>-<role>.md             one dev role's work log
plans/<TICKET>-review-<n>.md         internal review, cycle <n>
plans/<TICKET>-tests-<n>.md          unit-test run, cycle <n>
plans/<TICKET>-tests-<n>-<area>.log  one test lane's raw output
plans/<TICKET>-qa-<n>.md             QA report, cycle <n>
proofs/<TICKET>/                     one artifact per user-visible requirement
```

Who writes and who reads each file is the [handoff contract](../agents/README.md#handoff). `<role>` is the role's frontmatter `name` (`backend-dev`, `frontend-dev`). `<n>` is the cycle number, from 1 — a new cycle adds a file, it never overwrites the previous one, so the history of what was rejected stays readable. [releaser](../agents/releaser.md) gates on the **highest-numbered** `-review-<n>.md`, `-tests-<n>.md`, and `-qa-<n>.md`; all three must exist and must read `Approve` / `Approve with nits`, `Pass`, and `Pass`.

Plan files follow [plan-template](../skills/plan-template.md). Proofs are named after the requirement they prove (`req-2-portfolio-filter.gif`) — see [qa-verify › Proofs](../skills/qa-verify.md#8-proofs-for-the-pr) for what counts as one per kind of change. Never fabricate a proof; unexercised requirements go under **Not verified** in the QA report.

Lanes that run concurrently write **different files** — that is what keeps them safe to parallelise ([develop-flow › Parallelism](../skills/develop-flow.md#parallelism)). Two roles never append to one handoff file.

Test-data and one-off scripts a role needs mid-flow also live here ([qa](../agents/qa.md), which may never edit product code). Keep them under the ticket they belong to.

## Lifecycle

One ticket's files stay until its PR is merged — [reviewer](../agents/reviewer.md), [qa](../agents/qa.md), and [releaser](../agents/releaser.md) each read files written cycles earlier, and `release-pr` uploads the proofs from disk. After the merge they are disposable: delete `plans/<TICKET>*.md` and `proofs/<TICKET>/` per ticket, since the proofs already live on the ticket and the reasoning on the PR.

A fact worth keeping past the ticket is not a scratchpad file — write it to [`../memory/`](../memory/README.md), or promote it into the workspace `AGENTS.md`, or into `agents/` / `skills/` if it is true in any organisation.
