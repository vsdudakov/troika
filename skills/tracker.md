---
name: tracker
description: Working with the issue tracker — verifying auth, reading a ticket, commenting, transitioning, attaching proofs, and linking the branch and PR to the ticket.
---

# Tracker

Generic tracker rules. Profile owns URL, auth, commands, and allowed writes.

**Kind** reference · **Used by** [architect](../agents/architect.md) (develop-flow step 1) · [releaser](../agents/releaser.md) (step 7) · **When** reading a ticket, commenting, transitioning, or attaching a proof · **Ends with** the ticket read or updated, with the response checked

## Verify auth before blaming the ticket

Run the profile's **real API call** and expect a 200 — a CLI's "who am I" usually echoes local config and succeeds with a dead token. A stale token reads back as "issue does not exist" or "no projects found", never a clear 401, so suspect the token before the ticket key. Check the **exported** environment variable, not the file meant to export it.

## Read

Read requirements, state, ordered comments, attachments, fields, and every link. Never plan from title.

## Comment

[Commenter](../agents/commenter.md) writes one factual comment per event. Post through a quoted heredoc.

<a id="transitions"></a>
## Transition — only if the profile declares one

Profile alone authorizes and names transitions:

| Profile says | What every "transition the ticket" instruction in `llm/` means |
| --- | --- |
| Transitions exist, with names | run the named transition at the step that calls for it |
| **No transitions** — the board's state is the humans' | do nothing to the state; the profile names the equivalent write instead (usually a comment), and that is the whole obligation |

Never infer transitions or touch triage state without explicit authority.

Where transitions do exist: **transition names are not status names.** List what is valid from the current state before moving; a transition that is invalid from the current state fails, and the cause is usually a state the flow skipped earlier.

When declared: "started" runs after plan review; "PR opened" after PR. No transitions means neither action.

## Attach proofs

Attach proofs with absolute paths using profile call. Validate returned attachment record.

## Link the branch and PR

With VCS integration, use the exact key casing in the branch name and in commit messages. Without one, keep the key out of branch names and link the ticket from the PR body instead.

Either way: link the ticket in the PR body, comment the PR URL on it, and run the "PR opened" transition **if the profile declares one** ([above](#transitions)).

Cross-repo uses one ticket key.

## Gotchas

- Casing of the issue key matters to the VCS integration — a lowercase key is silently not detected, anywhere: branch, commit, PR title.
- Creating tickets from a CLI is unreliable against some project types; if it fails, create in the web UI or POST to the REST API with the same credentials as the auth check.
- Tokens expire. When several tracker calls fail at once, rotate the token before debugging anything else.
