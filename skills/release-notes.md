---
name: release-notes
description: Generates a release's notes from the diff against the previous release branch — dedup by patch-id, label cross-check, classification, QA blocks, and a generation-notes audit trail.
---

# Release notes

The customer-readable record of one release, and the source the QA plan is compiled from.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** a release branch has been cut ([release-cut](release-cut.md) step 3), or a human asks for notes · **Ends with** a notes file on a PR against the default branch, every dropped item recorded

The newest existing notes file is the living **template** — read it first and mirror its sections, headings, and per-item formats exactly. Paths, naming, and the tracker/PR-host commands are in [AGENTS.md › Release](../../AGENTS.md#release) · [› Tracker](../../AGENTS.md#tracker) · [› Pull requests](../../AGENTS.md#pull-requests).

## 1. Collect the range — from the previous release's branch head, never its tag

```bash
git fetch <remote> --tags
git log --oneline <prev-tag>..<remote>/<prev-release-branch>    # post-cut cherry-picks — expect a non-empty list
git log --no-merges <remote>/<prev-release-branch>..<new-release-branch>       # the candidate range
```

The tag marks where the previous release was *cut*; the branch head is what it actually *shipped*. Fixes land on the default branch and are cherry-picked onto the release branch afterwards, so a tag-based range re-reports every post-cut cherry-pick as new work.

Attribution comes from the squash-merge PR-number suffix. A commit without one is not dropped — it goes under **Unattributed commits**.

## 2. Dedup by patch-id, then check each drop for a revert

Cherry-picks carry different SHAs, so ancestry alone will not exclude them:

```bash
git cherry <remote>/<prev-release-branch> <new-release-branch>     # '-' marks patch-equivalent commits
```

A `-` commit already shipped — **unless it was reverted on the previous branch**, in which case this release is its first. Confirm against the **tree**, not the log: pick a symbol the commit adds and check whether it is present in each branch. A dropped item takes its QA block with it; renumber the survivors.

## 3. Cross-check the release labels

For every PR still in the range, read its labels. One labelled for an **earlier** release is a red flag — reconcile it against the branch, never on the label alone, in either direction:

- Present in the previous release branch (step 2) → it shipped; drop it, the label was right.
- In no earlier release branch (`git branch -r --contains <sha>`) → it missed that cut and genuinely ships now; **keep it** and correct the label. Dropping it would leave it documented in no release at all.

Read the earlier notes files too and drop anything already documented there — but as a *secondary* check only: notes are written at cut time, so post-cut cherry-picks never appear in them. Steps 1–2 are the load-bearing guard; this one catches re-cuts.

## 4. Enrich and classify

For each PR, read its title, body, files, and the ticket it links to ([AGENTS.md › Tracker](../../AGENTS.md#tracker)). Classify each into exactly one of the template's sections; when uncertain, pick the best fit and flag it rather than inventing a section.

## 5. Write the file

Per the template, with a QA block for every customer-visible item — those blocks are the entire input to the release's QA plan, so an item without one is untestable by the humans.

End with **Generation notes**: the branch pair and SHAs (naming the previous **branch head**), the post-cut cherry-picks from step 1, count reconciliation, deduped items with their SHA pairs, any patch-equivalent kept because it was reverted, label corrections, inaccessible tickets, classification flags, and redactions. **Every drop is recorded, never silent.**

Customer-facing sections carry no internal IDs, tenant UUIDs, or internal links.

## 6. Open the PR

Through the normal PR path ([AGENTS.md › Pull requests](../../AGENTS.md#pull-requests)) — never pushed straight to the default or a release branch. Text is outward-facing: [commenter](../agents/commenter.md) writes it in the workspace [voice](../../AGENTS.md#voice).

## Output

The notes file path · the branch pair diffed · item count per section · every dropped PR/commit with its reason · label corrections made · the PR URL.

## Stop conditions

Stop and hand back when: the previous release branch cannot be resolved; a range item's ticket is inaccessible and its user-visible effect cannot be described from the diff; or dedup and the label check disagree about the same PR after checking the tree.
