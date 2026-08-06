---
name: demo-prep
description: Builds the demo integration branch — reset it from the default branch, merge the demo-labeled PRs in a conflict-minimising order, deploy, and prepare the team notification.
---

# Demo prep

Throwaway branch of demo PRs, deployed pre-production.

**Kind** procedure · **Used by** [releaser](../../agents/releaser.md) · **When** a demo is scheduled and the human asks for the build · **Ends with** a reset integration branch with the demo PRs merged, deployed, and a notification waiting for the human's go-ahead

The integration branch's name, the label that selects the demo PRs, and the deploy dispatch are in [AGENTS.md › Demo prep](../../../AGENTS.md#demo) and [› Deploy](../../../AGENTS.md#deploy).

This skill may reset only the demo branch. Never merge it back, use it as PR base, push protected/demo-PR branches, or deploy production. Demo PRs land separately.

## 1. Collect the demo PRs

List labeled open PR number/title/URL/head/files/author. Resolve ambiguous label. Show list before merge.

## 2. Reset the integration branch

Delete/re-cut from current default in its worktree. Force reset is allowed only here.

## 3. Plan the merge order

Order by dependency, overlapping files, then migration order. State order and reason first.

## 4. Merge, and stop at anything semantic

Fetch and merge heads in order. After each: imports resolve, migration chain intact.

- **Mechanical conflicts** (imports, adjacent lines, lockfiles) are resolved here, in the integration branch.
- **Anything that requires changing a PR** — a renumbered migration, reworked code, a semantic conflict between two PRs — is not resolved here. **Stop and tell the human** which PR needs what change. Fixing it locally makes the demo branch diverge from what will actually land, and that divergence is invisible at demo time.

## 5. Deploy and prepare the notification

Deploy pre-production; watch all runs; failure stops. Prepare author-grouped notification; post only on explicit request.

## Output

The demo PR list with authors · the merge order and its rationale · conflicts resolved here vs handed back · deploy run URLs and final state · the notification text, and whether it was posted.

## Stop conditions

Stop and hand back when: the demo label is ambiguous; a conflict needs a change inside a PR (step 4); the tree is inconsistent after a merge; or a deploy run fails.
