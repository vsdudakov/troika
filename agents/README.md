# Agents

Tool-neutral role definitions. Any agent tool (Claude Code, Cursor, Codex, …) loads a role by reading its file; the YAML frontmatter (`name`, `description`) lets tools that auto-discover roles pick the right one.

Every role inherits the workspace's [AGENTS.md](../../AGENTS.md) — the project profile: repo map, ownership, commands, style, tracker, voice. A role file adds only the craft that is true in any organisation; every concrete repo, command, and URL is read from there ([why](../README.md)).

## Who does what

| Role | Owns |
| --- | --- |
| [architect](architect.md) | requirements, plan, repo split, contracts; writes no product code |
| [backend-dev](backend-dev.md) | server-side repos + their unit tests |
| [frontend-dev](frontend-dev.md) | the client app named in [AGENTS.md › Ownership](../../AGENTS.md#ownership) + its unit tests |
| [reviewer](reviewer.md) | internal (pre-PR) and PR review; read-only, never runs tests |
| [qa](qa.md) | the local stack, manual + integration verification, proofs |
| [releaser](releaser.md) | commits (the only ones in the flow), PR, proofs, tracker |
| [commenter](commenter.md) | every outward-facing text, in the workspace's [voice](../../AGENTS.md#voice) |

Which repos each dev role may touch is per-workspace: [AGENTS.md › Ownership](../../AGENTS.md#ownership).

## Model and effort

Two dials, set separately. **Model** decides what the role *can* do; **effort** decides how much thinking it spends before acting.

| Role | Claude model (fallback) | Claude effort | Codex effort |
| --- | --- | --- | --- |
| [architect](architect.md) | `claude-fable-5` → `claude-opus-5` | high | high |
| [backend-dev](backend-dev.md) | `claude-fable-5` → `claude-opus-5` | high | high |
| [frontend-dev](frontend-dev.md) | `claude-sonnet-5` | medium | medium |
| [reviewer](reviewer.md) | `claude-fable-5` → `claude-opus-5` | high | high |
| [qa](qa.md) | `claude-sonnet-5` | medium | medium |
| [releaser](releaser.md) | `claude-sonnet-5` | low | medium |
| [commenter](commenter.md) | `claude-fable-5` → `claude-opus-5` | low | low |

Codex runs `gpt-5.6-sol` for every role — only the effort differs, so it gets no column of its own. `→` means fallback: use the first, drop to the next when the tool or plan doesn't offer it.

**Why these.** Fable is the top pick where the output is judgment or prose — plan, code design, review, written text. The three execution roles stay on Sonnet on purpose: long, tool-heavy sessions where the work is following a procedure, not reasoning about it.

**Why the two dials don't move together.** [commenter](commenter.md) runs the strongest model at the lowest effort — voice comes from the model, not from more thinking. [releaser](releaser.md) runs a mid model at low effort — the numbered procedure is the safeguard, not reasoning. Raise **effort** when a role is losing to *depth* on a task it already understands; raise the **model** when it is losing to *capability*. Each role file carries its own `Why` / `Raise it when` / `Drop it when` lines.

**Setting them.** Nothing here is auto-applied: this tree is documentation, and a tool told to `read llm/agents/qa.md` still runs on whatever model and effort the session was started with. The values above take effect only when someone passes them.

| Tool | Model | Effort |
| --- | --- | --- |
| Claude Code | `/model` in-session · `claude --model claude-fable-5` at launch · `model:` in a `.claude/agents/*.md` subagent | `/effort` in-session · `claude --effort high` at launch |
| Codex | `codex -m gpt-5.6-sol` · profile in `~/.codex/config.toml` | `-c model_reasoning_effort="high"` · same profile |
| Cursor | equivalent tier in the model picker | no effort control — take the next model tier up for a `high`+ role |

Claude Code effort levels: `low` · `medium` · `high` · `xhigh` · `max`; an unrecognised value is ignored with a warning and the default is used. A session that sets no effort runs the default, not the role's. Subagent frontmatter honours `model:`; it has **no** verified `effort:` key — an effort override for a subagent has to come from the launching session's effort.

These are defaults, not gates — each role file says *why* its model and effort are what they are, so override with that reason in mind. Model IDs and effort levels move faster than this file: check the tool's own list (`/model`, `/effort` in Claude Code) before pinning one, and fall back down the chain rather than guessing at a name.

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

Roles run in separate contexts and communicate through files. `$WS` is the workspace root ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)) — always absolute, because every role's cwd is inside a worktree.

| File | Written by | Read by |
| --- | --- | --- |
| `$WS/llm/scratchpad/plans/<TICKET>.md` | [architect](architect.md) | everyone |
| `$WS/llm/scratchpad/plans/<TICKET>-<role>.md` | each dev role | reviewer, qa, release |
| `$WS/llm/scratchpad/plans/<TICKET>-review-<n>.md` | [reviewer](reviewer.md), internal pass | dev roles, release |
| `$WS/llm/scratchpad/plans/<TICKET>-qa-<n>.md` | [qa](qa.md) | dev roles, release |
| `$WS/llm/scratchpad/proofs/<TICKET>/*.gif\|png` | [qa](qa.md) | release |

`<role>` is the role's frontmatter `name` (`backend-dev`, `frontend-dev`). `<n>` is the cycle number, starting at 1. [releaser](releaser.md) gates on the **highest-numbered** `-review-<n>.md` and `-qa-<n>.md`; both must exist.

A role that finishes returns: branch name, worktree path, what changed, commands run with results, anything left undone.
