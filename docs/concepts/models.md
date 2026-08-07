---
title: Models and effort
description: Which model and which reasoning effort each role runs on, where those values are declared, why the two dials move independently, and when to raise either.
---

# Models and effort

**Model** sets capability. **Effort** sets depth. They are separate dials.

**The values are your workspace's, not Troika's.** They live in one place — the `#models`
anchor of `.troika/PROFILE.md`, one row per role, one column per host you use.
[`/tr:setup`](../reference/commands.md) writes that table from the defaults below; edit it to
whatever your accounts can actually run. No role file, skill or command names a model id.

## What the roles declare

A role file states what its row *needs* and why. That is stable across workspaces; the ids
are not.

| Role | Needs | Why |
| --- | --- | --- |
| architect | judgment tier · high | every later role trusts the plan |
| backend-dev | judgment tier · high | layering, migrations, a coverage gate it cannot verify by running |
| frontend-dev | execution tier · medium | pattern-following against an existing codebase |
| reviewer | judgment tier · high | adversarial depth |
| tester | execution tier · medium | procedural selection and result validation |
| qa | execution tier · medium | long execution and observation |
| releaser | execution tier · lowest | mechanical; the numbered procedure is the safeguard |
| commenter | judgment tier · lowest | voice comes from the model, not from more thinking |

The **judgment tier** is the strongest model your profile names; the **execution tier** is its
mid one.

## The shipped defaults

What `/tr:setup` writes into `#models` before you touch it:

| Role | Claude model (fallback) | Claude effort | Codex model | Codex effort |
| --- | --- | --- | --- | --- |
| architect | `claude-fable-5` → `claude-opus-5` | high | `gpt-5.6-sol` | high |
| backend-dev | `claude-fable-5` → `claude-opus-5` | high | `gpt-5.6-sol` | high |
| frontend-dev | `claude-sonnet-5` | medium | `gpt-5.6-sol` | medium |
| reviewer | `claude-fable-5` → `claude-opus-5` | high | `gpt-5.6-sol` | high |
| tester | `claude-sonnet-5` | medium | `gpt-5.6-sol` | medium |
| qa | `claude-sonnet-5` | medium | `gpt-5.6-sol` | medium |
| releaser | `claude-sonnet-5` | low | `gpt-5.6-sol` | medium |
| commenter | `claude-fable-5` → `claude-opus-5` | low | `gpt-5.6-sol` | low |

`→` means fallback. Verify an id exists before pinning it.

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
`Raise it when`, `Drop it when` and `Also` notes — as *relative* moves ("one effort step above
the profile's row"), because it does not know your ids.

## Different families on purpose

Plan review runs on a different model family from the one that wrote the plan. A reviewer that
shares the author's blind spots confirms the plan instead of testing it — the point of the
gate is an independent reading, and family diversity is the cheapest way to get one.

Which tool that is, and the exact command for the plan pass and the diff pass, is the
`#review-runner` anchor of your profile. Troika's default is Codex CLI:

```bash
codex exec -m gpt-5.6-sol -c model_reasoning_effort="high" -   # plan pass
codex exec review --uncommitted -                              # diff pass
```

Any tool that reads a prompt on stdin works — swap in whatever second family you have. If you
have only one, say "no separate runner" in that anchor and the pass runs in a fresh session on
the `reviewer` row instead, which the review report then says out loud.

## Values are not automatic

Nothing in the tree sets a model for you: the profile is what *declares* them, and the host
is what applies it. Pass the values at launch or in the session, and if your host cannot vary
them per subagent, run the judgment roles yourself on the stronger model and let the rest
inherit the default.
