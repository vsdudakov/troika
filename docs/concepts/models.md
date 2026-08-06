---
title: Models and effort
description: Which model and which reasoning effort each role runs on, why they move independently, and when to raise either.
---

# Models and effort

**Model** sets capability. **Effort** sets depth. They are separate dials, and each role file
states its own case for the values it carries.

| Role | Claude model (fallback) | Claude effort | Codex effort |
| --- | --- | --- | --- |
| architect | `claude-fable-5` → `claude-opus-5` | high | high |
| backend-dev | `claude-fable-5` → `claude-opus-5` | high | high |
| frontend-dev | `claude-sonnet-5` | medium | medium |
| reviewer | `claude-fable-5` → `claude-opus-5` | high | high |
| tester | `claude-sonnet-5` | medium | medium |
| qa | `claude-sonnet-5` | medium | medium |
| releaser | `claude-sonnet-5` | low | medium |
| commenter | `claude-fable-5` → `claude-opus-5` | low | low |

Codex uses `gpt-5.6-sol`; effort varies by role. `→` means fallback.

## The split

The strongest model leads where the work is **judgment** — planning, code design, review, and
written text. The mid model carries the roles whose work is long, tool-heavy **execution
against a documented procedure**.

`backend-dev` sits on the judgment side despite being an execution role: layering, migrations
and a coverage gate it cannot verify by running all punish shallow reasoning.

## The dials move independently

Two instructive cases:

- **commenter** — strongest model, *lowest* effort. Voice comes from the model, not from more
  thinking.
- **releaser** — mid model, low effort. The numbered procedure is the safeguard; depth adds
  nothing to executing it faithfully.

Raise **effort** when a role loses to depth on a task it clearly understands. Raise the
**model** when it loses to capability. Every role file carries its own `Why`,
`Raise it when`, `Drop it when` and `Also` notes.

## Different families on purpose

Plan review runs on a different model family from the one that wrote the plan. A reviewer that
shares the author's blind spots confirms the plan instead of testing it — the point of the
gate is an independent reading, and family diversity is the cheapest way to get one.

## Values are not automatic

Nothing in the tree sets a model for you: the table is what the roles *declare*, and the host
is what applies it. Pass the values at launch or in the session, and if your host cannot vary
them per subagent, run the judgment roles yourself on the stronger model and let the rest
inherit the default.
