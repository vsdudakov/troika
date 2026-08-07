# Roles

Tool-neutral roles. Frontmatter enables discovery. Every role inherits the workspace profile (`$TROIKA_PROFILE`); role files add organization-neutral craft only.

## Who does what

| Role | Owns |
| --- | --- |
| [architect](agents/architect.md) | requirements, plan or bug brief with the steps to reproduce, repo split, contracts; writes no product code |
| [backend-dev](agents/backend-dev.md) | server-side repos + their unit tests (written, never run) |
| [frontend-dev](agents/frontend-dev.md) | the client app(s) named in PROFILE.md › Ownership (`#ownership`) + their unit tests (written, never run) |
| [reviewer](agents/reviewer.md) | plan review, internal (pre-PR) review, and PR review; read-only, never runs tests |
| [tester](agents/tester.md) | the local unit-test run — the change's own tests only, in parallel lanes; writes nothing |
| [qa](agents/qa.md) | the local stack, bug reproduction on the base checkout, manual + integration verification, proofs |
| [releaser](agents/releaser.md) | commits (the only ones in the flow), PR, proofs, tracker |
| [commenter](agents/commenter.md) | every outward-facing text, in the workspace's voice (`#voice`) |

Profile ownership splits paths, not branches: one repo, worktree, branch, PR.

## Model and effort

**Model** sets capability; **effort** sets depth. **Neither value lives here.** The ids and efforts are the workspace's, one row per role, in PROFILE.md › Models and effort (`#models`) — written by `/tr:setup` from Troika's shipped defaults and edited to whatever your accounts can actually run. A role file declares only what its row *needs*:

| Role | Needs | Why |
| --- | --- | --- |
| [architect](agents/architect.md) | judgment tier · high | every later role trusts the plan |
| [backend-dev](agents/backend-dev.md) | judgment tier · high | layering, migrations, a coverage gate it cannot verify by running |
| [frontend-dev](agents/frontend-dev.md) | execution tier · medium | pattern-following against an existing codebase |
| [reviewer](agents/reviewer.md) | judgment tier · high | adversarial depth |
| [tester](agents/tester.md) | execution tier · medium | procedural selection and result validation |
| [qa](agents/qa.md) | execution tier · medium | long execution and observation |
| [releaser](agents/releaser.md) | execution tier · lowest | mechanical; the numbered procedure is the safeguard |
| [commenter](agents/commenter.md) | judgment tier · lowest | voice comes from the model, not from more thinking |

The **judgment tier** is the strongest model the profile names; the **execution tier** is its mid one. Judgment leads where the work is planning, code design, review or written text. [backend-dev](agents/backend-dev.md) sits on the judgment side despite being an execution role. Each role file states its own case.

**The dials move independently.** [commenter](agents/commenter.md) takes the strongest model at the lowest effort. [releaser](agents/releaser.md) takes a mid model at low effort. Raise **effort** when a role loses to depth on a task it understands; raise the **model** when it loses to capability. Each role file carries its own `Why` / `Raise it when` / `Drop it when` / `Also`.

**A row's effort is what the role's first pass costs.** A pass re-entering a gate after a fix reads a fraction of what the first one read, so it runs one tier down ([develop-flow › Re-entry](skills/develop-flow/SKILL.md#reentry)) — a widened cycle and the last cycle the loop cap allows are the two that keep the row's effort, because both are deciding the flow's outcome rather than confirming a small change.

The [reviewer](agents/reviewer.md)'s independent pass runs on a different family from the author's — which tool, and the exact command, is PROFILE.md › Review runner (`#review-runner`).

Values are not automatic; pass them at launch/session, from the profile's rows.

| Tool | Model | Effort |
| --- | --- | --- |
| Claude Code | `/model` in-session · `claude --model <the row's model>` at launch · `model:` in a `.claude/agents/*.md` subagent | `/effort` in-session · `claude --effort <the row's effort>` at launch |
| Codex | `codex -m <the row's model>` · profile in `~/.codex/config.toml` | `-c model_reasoning_effort="<the row's effort>"` · same profile |
| Cursor | equivalent tier in the model picker | no effort control — take the next model tier up for a `high`+ role |

Claude effort: `low|medium|high|xhigh|max`. Subagents inherit session effort. Defaults are not gates; verify available IDs before pinning one in the profile.

Usage: `read troika/agents/backend-dev.md and act as that role for <TICKET>`. Full flow: [develop-flow](skills/develop-flow/SKILL.md).

## File shape

Shape: frontmatter · purpose · **Owns/Runs/Model** · five sections below, in order. Model cites the role's row in `#models` and nests Needs, Why, optional override — never a model id or a host's name.

| Section | Answers |
| --- | --- |
| `Scope` | what it may touch, what it must never touch, where it stops and hands back |
| `Inputs` | what it receives and from which file |
| `Rules` | the rules this role owns, on top of the profile |
| `Gates` | numbered conditions that must hold before it reports done |
| `Output` | exact shape of what it returns, and the handoff file it writes |

<a id="handoff"></a>
## Handoff contract

Roles communicate through files. Use the absolute paths from `plugin/resolve.py`.

| File | Written by | Read by |
| --- | --- | --- |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>.md` | [architect](agents/architect.md) | everyone |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-plan-review-<n>.md` | [reviewer](agents/reviewer.md), plan pass | architect, orchestrator |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-repro-<n>.md` | [qa](agents/qa.md), reproduction pass (bug path) | dev roles, reviewer, orchestrator |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-<role>.md` | each dev role | reviewer, qa, release |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-fix-<n>.md` | orchestrator, [fix-pr](skills/fix-pr/SKILL.md) | dev roles, reviewer, commenter |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-fix-<n>-<role>.md` | each dev role, in a fix cycle | reviewer, commenter |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-review-<n>.md` | [reviewer](agents/reviewer.md), internal pass | dev roles, release |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-tests-<n>.md` | [tester](agents/tester.md) | dev roles, release |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-qa-<n>.md` | [qa](agents/qa.md) | dev roles, release |
| `$TROIKA_SCRATCHPAD/proofs/<TICKET>/*.gif\|png` | [qa](agents/qa.md) | release |
| `$TROIKA_SCRATCHPAD/lanes/<repo>-<TICKET>` | whoever holds the lane | any role about to join it ([claim](skills/worktree/SKILL.md#claim)) |
| `$TROIKA_SCRATCHPAD/plans/<TICKET>-<repo>-cycle-<n>.sha` | [reviewer](agents/reviewer.md), at the end of every internal pass | reviewer, tester, qa — it is what a [re-entry scope](skills/develop-flow/SKILL.md#reentry) is computed from |

`<role>` is frontmatter name; `<n>` starts at 1. Release reads highest review/tests/QA files. Lane logs are evidence, not gates.

A role that finishes returns: branch name, worktree path, what changed, commands run with results, anything left undone.

Follow [parallelism](skills/develop-flow/SKILL.md#parallelism). One role writes a worktree at a time.
