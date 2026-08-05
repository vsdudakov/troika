# Agents

Tool-neutral role definitions. Any agent tool (Claude Code, Cursor, Codex, …) loads a role by reading its file; the frontmatter (`name`, `description`) lets auto-discovering tools pick the right one.

Every role inherits the workspace's [AGENTS.md](../../AGENTS.md) — repo map, ownership, commands, style, tracker, voice. A role file adds only craft that is true in any organisation; every concrete repo, command, and URL is read from there ([why](../README.md)).

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

Which paths each dev role may touch is per-workspace: [AGENTS.md › Ownership](../../AGENTS.md#ownership). Ownership splits *paths*, not branches — a repo has one worktree, one branch, and one PR however many roles contribute ([develop-flow › Lanes](../skills/develop-flow.md#lanes)).

## Model and effort

Two dials. **Model** decides what the role *can* do; **effort** how much thinking it spends before acting.

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

Codex runs `gpt-5.6-sol` for every role — only effort differs, so it gets no column. `→` means fallback: use the first, drop to the next when the tool doesn't offer it.

**Why these.** Fable leads where the output is judgment or prose — plan, code design, review, written text. The four execution roles stay on Sonnet deliberately: long, tool-heavy sessions following a procedure, not reasoning about one.

**Why the dials don't move together.** [commenter](commenter.md) runs the strongest model at the lowest effort — voice comes from the model, not more thinking. [releaser](releaser.md) runs a mid model at low effort — the numbered procedure is the safeguard. Raise **effort** when a role loses to *depth* on a task it understands; raise the **model** when it loses to *capability*. Each role file carries its own `Why` / `Raise it when` / `Drop it when`.

**Setting them.** Nothing here is auto-applied: a tool told to `read llm/agents/qa.md` still runs on the session's model and effort. These values take effect only when someone passes them.

| Tool | Model | Effort |
| --- | --- | --- |
| Claude Code | `/model` in-session · `claude --model claude-fable-5` at launch · `model:` in a `.claude/agents/*.md` subagent | `/effort` in-session · `claude --effort high` at launch |
| Codex | `codex -m gpt-5.6-sol` · profile in `~/.codex/config.toml` | `-c model_reasoning_effort="high"` · same profile |
| Cursor | equivalent tier in the model picker | no effort control — take the next model tier up for a `high`+ role |

Claude Code effort levels: `low` · `medium` · `high` · `xhigh` · `max`; an unrecognised value is ignored with a warning and the default used. A session setting no effort runs the default, not the role's. Subagent frontmatter honours `model:` but has **no** verified `effort:` key — a subagent's effort comes from the launching session.

These are defaults, not gates; override with the role file's reason in mind. Model IDs move faster than this file: check `/model` and `/effort` before pinning one, and fall back down the chain rather than guessing a name.

**Usage.** Point the tool at the role file, e.g. `read llm/agents/backend-dev.md and act as that role for <TICKET>`. For the full ticket-to-PR pipeline use [skills/develop-flow.md](../skills/develop-flow.md), which runs these roles in order.

## File shape

Every role file carries frontmatter, then a purpose paragraph, then a header block (**Owns** · **Runs** · **Model**), then exactly these five sections in this order. **Model** is a nested list, one line each: `**Claude**` · `**Codex**` · `**Why**`, plus `**Raise it when**` / `**Drop it when**` where the role has a real override case.

| Section | Answers |
| --- | --- |
| `Scope` | what it may touch, what it must never touch, where it stops and hands back |
| `Inputs` | what it receives and from which file |
| `Rules` | the rules this role owns, on top of AGENTS.md |
| `Gates` | numbered conditions that must hold before it reports done |
| `Output` | exact shape of what it returns, and the handoff file it writes |

<a id="handoff"></a>
## Handoff contract

Roles run in separate contexts and communicate through files. `$WS` is the workspace root ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)) — always absolute, since every role's cwd is inside a worktree.

| File | Written by | Read by |
| --- | --- | --- |
| `$WS/llm/scratchpad/plans/<TICKET>.md` | [architect](architect.md) | everyone |
| `$WS/llm/scratchpad/plans/<TICKET>-plan-review-<n>.md` | [reviewer](reviewer.md), plan pass | architect, orchestrator |
| `$WS/llm/scratchpad/plans/<TICKET>-<role>.md` | each dev role | reviewer, qa, release |
| `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md` | [reviewer](reviewer.md), internal pass | dev roles, release |
| `$WS/llm/scratchpad/plans/<TICKET>-tests-<n>.md` | [tester](tester.md) | dev roles, release |
| `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md` | [qa](qa.md) | dev roles, release |
| `$WS/llm/scratchpad/proofs/<TICKET>/*.gif\|png` | [qa](qa.md) | release |

`<role>` is the frontmatter `name` (`backend-dev`, `frontend-dev`); `<n>` is the cycle number from 1. [releaser](releaser.md) gates on the **highest-numbered** `-review-<n>.md`, `-tests-<n>.md`, `-qa-<n>.md`, all three of which must exist. Test lanes also leave `-tests-<n>-<area>.log` — evidence, not a gate.

A role that finishes returns: branch name, worktree path, what changed, commands run with results, anything left undone.

**Roles run concurrently wherever the flow says so** ([develop-flow › Parallelism](../skills/develop-flow.md#parallelism)) — one lane per repo, review dimensions inside a lane, test lanes per area, CI watches per PR. Files are what makes that safe: a role writes only its own handoff file, and only one role writes a given worktree at a time. Two roles writing one worktree *simultaneously* is the one thing the contract cannot protect — which is why roles sharing a repo take turns ([Lanes](../skills/develop-flow.md#lanes)).
