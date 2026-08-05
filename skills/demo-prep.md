---
name: demo-prep
description: Builds the demo integration branch — reset it from the default branch, merge the demo-labeled PRs in a conflict-minimising order, deploy, and prepare the team notification.
---

# Demo prep

One throwaway branch carrying every PR that will be shown, deployed to the pre-production environment.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** a demo is scheduled and the human asks for the build · **Ends with** a reset integration branch with the demo PRs merged, deployed, and a notification waiting for the human's go-ahead

The integration branch's name, the label that selects the demo PRs, and the deploy dispatch are in [AGENTS.md › Demo prep](../../AGENTS.md#demo) and [› Deploy](../../AGENTS.md#deploy).

This branch is **owned by this skill**: resetting it is expected, and it is never merged back anywhere and never used as a PR base. Every other branch rule still holds — never push to the default or a release branch, never push to a demo PR's own branch, never dispatch a production deploy. Each demo PR still lands through its own review and merge, separately from this build.

## 1. Collect the demo PRs

List the open PRs carrying the demo label ([AGENTS.md › Demo prep](../../AGENTS.md#demo)), with number, title, URL, head ref, files, and author. If the label is ambiguous, ask the human which one.

Surface the list before merging anything — it drives every later step, and its authors feed step 5.

## 2. Reset the integration branch

Delete it and recut it from the current default branch, in its own worktree under `$WS/llm/worktrees/` ([worktree](worktree.md)), clearing leftovers from the previous demo first. Deleting and force-resetting is allowed **for this branch only**.

## 3. Plan the merge order

Read each PR's diff and file list, then order the merges to minimise conflicts: PRs touching the same files go in dependency order (the one the others build on first), and PRs carrying schema migrations go in migration order. **State the chosen order and why before merging.**

## 4. Merge, and stop at anything semantic

Merge each PR's head ref in the planned order, fetching first so refs are fresh. After each merge, confirm the tree is still consistent — imports resolve, the migration sequence is intact — before moving to the next.

- **Mechanical conflicts** (imports, adjacent lines, lockfiles) are resolved here, in the integration branch.
- **Anything that requires changing a PR** — a renumbered migration, reworked code, a semantic conflict between two PRs — is not resolved here. **Stop and tell the human** which PR needs what change. Fixing it locally makes the demo branch diverge from what will actually land, and that divergence is invisible at demo time.

## 5. Deploy and prepare the notification

Deploy the integration branch to the pre-production environment ([AGENTS.md › Deploy](../../AGENTS.md#deploy)) and watch every run to completion; a failed run stops the flow rather than producing a half-deployed demo.

Then fill the demo notification with the merged PR list **grouped by author**, so each presenter sees their own items at a glance, and tell the human it is ready. **Post only if they explicitly ask** ([AGENTS.md › Announcements](../../AGENTS.md#announcements)).

## Output

The demo PR list with authors · the merge order and its rationale · conflicts resolved here vs handed back · deploy run URLs and final state · the notification text, and whether it was posted.

## Stop conditions

Stop and hand back when: the demo label is ambiguous; a conflict needs a change inside a PR (step 4); the tree is inconsistent after a merge; or a deploy run fails.
