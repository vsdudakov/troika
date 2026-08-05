---
name: release-notes
description: Generates a release's notes from the diff against the previous release branch — dedup by patch-id, label cross-check, classification, QA blocks, and a generation-notes audit trail.
---

# Release notes

Customer record and QA-plan source.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** a release branch has been cut ([release-cut](release-cut.md) step 3), or a human asks for notes · **Ends with** a notes file on a PR against the default branch, every dropped item recorded

Mirror the newest notes file exactly. Use profile paths and host commands.

## 1. Collect the range — from the previous release's branch head, never its tag

```bash
git fetch <remote> --tags
git log --oneline <prev-tag>..<remote>/<prev-release-branch>    # post-cut cherry-picks — expect a non-empty list
git log --no-merges <remote>/<prev-release-branch>..<new-release-branch>       # the candidate range
```

Diff previous branch head: tag is cut state, head is shipped state. Attribute by squash PR suffix; otherwise **Unattributed commits**.

## 2. Dedup by patch-id, then check each drop for a revert

Cherry-picks carry different SHAs, so ancestry alone will not exclude them:

```bash
git cherry <remote>/<prev-release-branch> <new-release-branch>     # '-' marks patch-equivalent commits
```

`-` means shipped unless reverted. Verify symbol presence in each tree. Dropped items lose QA blocks; renumber.

## 3. Cross-check the release labels

For every PR still in the range, read its labels. One labelled for an **earlier** release is a red flag — reconcile it against the branch, never on the label alone, in either direction:

- Present in the previous release branch (step 2) → it shipped; drop it, the label was right.
- In no earlier release branch (`git branch -r --contains <sha>`) → it missed that cut and genuinely ships now; **keep it** and correct the label. Dropping it would leave it documented in no release at all.

Earlier notes are secondary dedup only; steps 1–2 govern.

## 4. Enrich and classify

Read PR and ticket; classify into exactly one existing section. Flag uncertainty.

## 5. Write the file

Add QA block per customer-visible item.

End with **Generation notes**: the branch pair and SHAs (naming the previous **branch head**), the post-cut cherry-picks from step 1, count reconciliation, deduped items with their SHA pairs, any patch-equivalent kept because it was reverted, label corrections, inaccessible tickets, classification flags, and redactions. **Every drop is recorded, never silent.**

Customer-facing sections carry no internal IDs, tenant UUIDs, or internal links.

## 6. Open the PR

Use normal PR path; never direct-push protected branches. Commenter writes text.

## Output

The notes file path · the branch pair diffed · item count per section · every dropped PR/commit with its reason · label corrections made · the PR URL.

## Stop conditions

Stop and hand back when: the previous release branch cannot be resolved; a range item's ticket is inaccessible and its user-visible effect cannot be described from the diff; or dedup and the label check disagree about the same PR after checking the tree.
