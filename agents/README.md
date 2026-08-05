# Agents

Tool-neutral roles. Frontmatter enables discovery. Every role inherits workspace [AGENTS.md](../../AGENTS.md); role files add organization-neutral craft only.

## Who does what

| Role | Owns |
| --- | --- |
| [architect](architect.md) | requirements, plan, repo split, contracts; writes no product code |
| [backend-dev](backend-dev.md) | server-side repos + their unit tests (written, never run) |
| [frontend-dev](frontend-dev.md) | the client app(s) named in [AGENTS.md › Ownership](../../AGENTS.md#ownership) + their unit tests (written, never run) |
| [reviewer](reviewer.md) | plan review, internal (pre-PR) review, and PR review; read-only, never runs tests |
| [tester](tester.md) | the local unit-test run — the change's own tests only, in parallel lanes; writes nothing |
| [qa](qa.md) | the local stack, manual + integration verification, proofs |
| [releaser](releaser.md) | commits (the only ones in the flow), PR, proofs, tracker |
| [commenter](commenter.md) | every outward-facing text, in the workspace's [voice](../../AGENTS.md#voice) |

Profile ownership splits paths, not branches: one repo, worktree, branch, PR.

## Model and effort

**Model** sets capability; **effort** sets depth.

| Role | Claude model (fallback) | Claude effort | Codex effort |
| --- | --- | --- | --- |
| [architect](architect.md) | `claude-fable-5` → `claude-opus-5` | high | high |
| [backend-dev](backend-dev.md) | `claude-fable-5` → `claude-opus-5` | high | high |
| [frontend-dev](frontend-dev.md) | `claude-sonnet-5` | medium | medium |
| [reviewer](reviewer.md) | `claude-fable-5` → `claude-opus-5` | high | high |
| [tester](tester.md) | `claude-sonnet-5` | medium | medium |
| [qa](qa.md) | `claude-sonnet-5` | medium | medium |
| [releaser](releaser.md) | `claude-sonnet-5` | low | medium |
| [commenter](commenter.md) | `claude-fable-5` → `claude-opus-5` | low | low |

Codex uses `gpt-5.6-sol`; effort varies. `→` means fallback. Fable leads where the work is judgment — planning, code design, review, written text. Sonnet carries the roles whose work is long, tool-heavy execution against a documented procedure. [backend-dev](backend-dev.md) sits on the judgment side despite being an execution role: layering, migrations, and a coverage gate it cannot verify by running punish shallow reasoning. Each role file states its own case.

**The dials move independently.** [commenter](commenter.md) runs the strongest model at the lowest effort: voice comes from the model, not from more thinking. [releaser](releaser.md) runs a mid model at low effort: the numbered procedure is the safeguard. Raise **effort** when a role loses to depth on a task it understands; raise the **model** when it loses to capability. Each role file carries its own `Why` / `Raise it when` / `Drop it when`.

Values are not automatic; pass them at launch/session.

| Tool | Model | Effort |
| --- | --- | --- |
| Claude Code | `/model` in-session · `claude --model claude-fable-5` at launch · `model:` in a `.claude/agents/*.md` subagent | `/effort` in-session · `claude --effort high` at launch |
| Codex | `codex -m gpt-5.6-sol` · profile in `~/.codex/config.toml` | `-c model_reasoning_effort="high"` · same profile |
| Cursor | equivalent tier in the model picker | no effort control — take the next model tier up for a `high`+ role |

Claude effort: `low|medium|high|xhigh|max`. Subagents inherit session effort. Defaults are not gates; verify available IDs before pinning.

Usage: `read llm/agents/backend-dev.md and act as that role for <TICKET>`. Full flow: [develop-flow](../skills/develop-flow.md).

## File shape

Shape: frontmatter · purpose · **Owns/Runs/Model** · five sections below, in order. Model nests Claude, Codex, Why, optional override.

| Section | Answers |
| --- | --- |
| `Scope` | what it may touch, what it must never touch, where it stops and hands back |
| `Inputs` | what it receives and from which file |
| `Rules` | the rules this role owns, on top of AGENTS.md |
| `Gates` | numbered conditions that must hold before it reports done |
| `Output` | exact shape of what it returns, and the handoff file it writes |

<a id="handoff"></a>
## Handoff contract

Roles communicate through files. Use absolute `$WS` paths.

| File | Written by | Read by |
| --- | --- | --- |
| `$WS/llm/scratchpad/plans/<TICKET>.md` | [architect](architect.md) | everyone |
| `$WS/llm/scratchpad/plans/<TICKET>-plan-review-<n>.md` | [reviewer](reviewer.md), plan pass | architect, orchestrator |
| `$WS/llm/scratchpad/plans/<TICKET>-<role>.md` | each dev role | reviewer, qa, release |
| `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md` | [reviewer](reviewer.md), internal pass | dev roles, release |
| `$WS/llm/scratchpad/plans/<TICKET>-tests-<n>.md` | [tester](tester.md) | dev roles, release |
| `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md` | [qa](qa.md) | dev roles, release |
| `$WS/llm/scratchpad/proofs/<TICKET>/*.gif\|png` | [qa](qa.md) | release |
| `$WS/llm/scratchpad/lanes/<repo>-<TICKET>` | whoever holds the lane | any role about to join it ([claim](../skills/worktree.md#claim)) |

`<role>` is frontmatter name; `<n>` starts at 1. Release reads highest review/tests/QA files. Lane logs are evidence, not gates.

A role that finishes returns: branch name, worktree path, what changed, commands run with results, anything left undone.

Follow [parallelism](../skills/develop-flow.md#parallelism). One role writes a worktree at a time.
