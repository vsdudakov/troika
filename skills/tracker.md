---
name: tracker
description: Working with the issue tracker — verifying auth, reading a ticket, commenting, transitioning, attaching proofs, and linking the branch and PR to the ticket.
---

# Tracker

How roles talk to the issue tracker. The tracker's URL, project key, CLI, transition names, and auth check are per-workspace: [AGENTS.md › Tracker](../../AGENTS.md#tracker). This file is the part that does not change between workspaces.

**Kind** reference · **Used by** [architect](../agents/architect.md) (develop-flow step 1) · [releaser](../agents/releaser.md) (step 7) · **When** reading a ticket, commenting, transitioning, or attaching a proof · **Ends with** the ticket read or updated, with the response checked

## Verify auth before blaming the ticket

A CLI's "who am I" command usually echoes local config and succeeds with a dead token. Verify with a real API call against the tracker instead ([AGENTS.md › Tracker](../../AGENTS.md#tracker) has it) — expect a 200.

**A stale token fails misleadingly.** Reads come back as "issue does not exist" or "no projects found" rather than a clear 401, so the first suspicion on a failed read is the token, not the ticket key. Check the *exported* environment variable, not the file that is supposed to export it.

## Read

Pull the ticket's requirements, status, and discussion before starting work — including comments, which is where scope usually changed. Follow every link in it (designs, docs, related tickets, PRs). Never plan from the ticket title alone.

## Comment

Comments are outward-facing: they are written by [commenter](../agents/commenter.md) in the workspace's [voice](../../AGENTS.md#voice) — no agent marker, no emoji, no AI attribution of any kind ([no-ai-attribution](../../AGENTS.md#no-ai-attribution)). Pass the text through a quoted heredoc so backticks and `$` survive ([shell quoting](../README.md#shell-quoting)).

One comment per event, carrying the facts and the links: PR URL, what changed in a line, proof attachment names.

## Transition

**Transition names are not status names.** List what is valid from the current state before moving; a transition that is invalid from the current state fails, and the cause is usually a state the flow skipped earlier.

The flow uses two: one when the plan clears review ([develop-flow](develop-flow.md) step 2) and one when the PR opens (step 7). The second is normally invalid unless the first has run — which is why the plan-review gate does it rather than leaving it to release.

## Attach proofs

Proofs live on the ticket, not in the PR body — most PR hosts have no CLI upload for body images. Attach with the call in [AGENTS.md › Tracker](../../AGENTS.md#tracker), using an **absolute** path: the calling role's cwd is a worktree.

**Read the response.** Attachment errors are silent when the body is discarded (`-o /dev/null`) — a successful call returns the attachment record.

## Link the branch and PR

Put the issue key, in the casing the tracker's VCS integration expects, in the **branch name** and in **commit messages** ([AGENTS.md › Branches](../../AGENTS.md#branches)). The integration then attaches the branch, its commits, and the PR to the ticket automatically. Also link the ticket in the PR body, transition the ticket after opening the PR, and comment the PR URL on it.

Cross-repo work uses one ticket key across every branch and PR so they group on the ticket ([cross-repo](cross-repo.md)).

## Gotchas

- Casing of the issue key matters to the VCS integration — a lowercase key is silently not detected, anywhere: branch, commit, PR title.
- Creating tickets from a CLI is unreliable against some project types; if it fails, create in the web UI or POST to the REST API with the same credentials as the auth check.
- Tokens expire. When several tracker calls fail at once, rotate the token before debugging anything else.
