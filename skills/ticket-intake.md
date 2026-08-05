---
name: ticket-intake
description: Turns a short request into a well-shaped tracker ticket, or reshapes an existing one — written once, with the original description preserved.
---

# Ticket intake

A request in a sentence becomes a ticket a [develop-flow](develop-flow.md) run can start from.

**Kind** procedure · **Used by** [architect](../agents/architect.md) · [commenter](../agents/commenter.md) · **When** the human asks for a ticket to be created or cleaned up · **Ends with** one ticket created or updated, its URL reported

The tracker's API, auth check, card/issue template, and the fields a role may touch are in [AGENTS.md › Tracker](../../AGENTS.md#tracker). Ticket text is outward-facing: [commenter](../agents/commenter.md) writes it in the workspace [voice](../../AGENTS.md#voice), with no AI attribution.

**Never** touch triage state — list/status, labels, assignees, due dates belong to the humans. This skill writes title and description only.

## 1. Read what exists

Creating: read the human's description, and the code it points at before writing the ticket — a "suggested area" pinned to a symbol that moved is worse than none ([AGENTS.md › Code search](../../AGENTS.md#code-search)).

Reshaping: read the current ticket, its comments, and anything it links to. **Preserve the real content** — reshaping means restructuring and sharpening, never dropping requirements the humans wrote.

## 2. Fill the template

The workspace's ticket template ([AGENTS.md › Tracker](../../AGENTS.md#tracker)) is the shape. Drop a section that has nothing real to say rather than padding it; keep the summary and the acceptance criteria. Acceptance criteria are phrased so each one is verifiable — a criterion no one can check is a wish.

Anything genuinely ambiguous is written down as an open question in the ticket, not silently decided.

## 3. Write once

**Reshaping first posts the old description as an archive comment**, then updates title and description — in that order, so nothing is lost if the update fails.

Then the write, exactly once: branch on the response status, and on a non-2xx surface the body and **stop**. Never retry blindly — a blind retry on a create is how duplicate tickets appear. Before any deliberate retry, read back whether the first call actually landed.

## Output

The ticket URL · what was created or changed · the archive comment's ID when reshaping · any open question left in the ticket.

## Stop conditions

Stop and hand back when: the write returns a non-2xx; a reshape would drop content the human wrote and the correct structure is unclear; or the request needs triage state (a list, label, or assignee) that no role may set.
