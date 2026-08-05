---
name: ticket-intake
description: Turns a short request into a well-shaped tracker ticket, or reshapes an existing one — written once, with the original description preserved.
---

# Ticket intake

Create a developable ticket.

**Kind** procedure · **Used by** [architect](../agents/architect.md) · [commenter](../agents/commenter.md) · **When** the human asks for a ticket to be created or cleaned up · **Ends with** one ticket created or updated, its URL reported

Use profile tracker/template/allowed fields. Commenter writes ticket text.

**Never** touch triage state — list/status, labels, assignees, due dates belong to the humans. This skill writes title and description only.

## 1. Read what exists

Create: read request and referenced code. Reshape: read ticket/comments/links; preserve all human requirements.

## 2. Fill the template

Use profile template. Drop empty optional sections; keep summary and verifiable acceptance criteria. Record ambiguity.

## 3. Write once

Reshape: archive old description, then update title/description. Write once; non-2xx surfaces body and stops. Read back before deliberate retry.

## Output

The ticket URL · what was created or changed · the archive comment's ID when reshaping · any open question left in the ticket.

## Stop conditions

Stop and hand back when: the write returns a non-2xx; a reshape would drop content the human wrote and the correct structure is unclear; or the request needs triage state (a list, label, or assignee) that no role may set.
