---
name: release-cut
description: Cuts a periodic release end-to-end — promote the previous pre-release, branch, pre-release, notes, QA plan, deploy to the pre-production environment, prepare the announcement.
---

# Release cut

The periodic release, from the previous cut's pre-release to a deployed, documented new one.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** the workspace's release cadence says to cut, or a human asks for one · **Ends with** a promoted previous release, a new branch + pre-release, merged release notes, a QA plan issue, a pre-production deploy, and an announcement waiting for the human's go-ahead

Every fact this needs — branch and tag naming, the release commands, the deploy dispatch, the announcement template — is in [AGENTS.md › Release](../../AGENTS.md#release), [› Branches](../../AGENTS.md#branches), [› Deploy](../../AGENTS.md#deploy). Nothing here is invented: if the workspace has no release cadence, this skill does not apply.

Each host write happens **once**. On a non-2xx, surface the response and stop; never retry blindly. Never force-push or move a tag, never push to the default or a release branch directly, never dispatch a production deploy.

## 1. Promote the previous release — after checking its tag still describes it

The release still flagged *pre-release* is the previous cut and is now stable. Before promoting it, check whether its branch moved past its tag during QA:

```bash
git fetch origin --tags
git log --oneline <prev-tag>..origin/<prev-release-branch>    # post-cut cherry-picks
```

**A non-empty list means the tag no longer describes what shipped.** Fixes merged to the default branch and cherry-picked onto the release branch after the cut carry different SHAs, so promoting the original tag leaks them into the *next* changelog, which is generated from that tag. **A cherry-pick onto a release branch is a re-cut**: tag the branch head with the next counter and promote that instead ([AGENTS.md › Release](../../AGENTS.md#release)).

Note the tag you end up promoting — it is `<prev-tag>` for steps 2 and 3 from here on. Skip the whole step when there is no prior pre-release.

## 2. Cut the branch and create the pre-release

Branch from the current default branch and push it; this adds **no** commit to the default branch. Then tag the new branch with an auto-generated changelog starting from step 1's tag.

Read the generated changelog back before continuing. Entries belonging to an **earlier** release are the visible symptom of a stale start tag — fix the start tag and recreate the release. Never hand-edit a generated changelog: the next cut reads the tag, not the text.

## 3. Release notes

Run [release-notes.md](release-notes.md) for this release, diffing the previous release's **branch head** against the new branch — not its tag. Open its PR, get it merged so the notes land on the default branch, and keep its per-item QA blocks: step 4 is built from them.

## 4. QA plan

One issue on the PR host holding the manual test plan, compiled from the notes' QA blocks as a checklist, linking back to the notes and the pre-release. The notes are the **only** source — anything the notes deduped is already gone, and re-adding it here resurrects a shipped item.

Cross-check against the previous release's QA issues and drop any step already covered there. A repeat is a signal the notes' dedup missed a cherry-pick: fix the notes, not just the issue.

## 5. Deploy to pre-production

Dispatch the workspace's pre-production deploy against the new branch with every deploy option enabled ([AGENTS.md › Deploy](../../AGENTS.md#deploy)), and watch each run to completion. If any run fails, surface its URL and stop — a half-deployed release is worse than a late one, and announcing it is worse still.

## 6. Announcement — prepared, not posted

Fill the workspace's release announcement with the real links (pre-release/changelog, QA plan, release notes), drop any line whose artifact does not exist, and tell the human it is ready. **Post only if they explicitly ask** ([AGENTS.md › Announcements](../../AGENTS.md#announcements)).

## Output

New branch and tag · the promoted previous tag (and whether step 1 found drift) · release-notes PR URL and merge state · QA plan issue URL · deploy run URLs and final state · the announcement text, and whether it was posted.

## Stop conditions

Stop and hand back when: step 1 finds drift and the re-cut tag is rejected by the host; the generated changelog still lists earlier work after fixing the start tag; the notes PR cannot merge; a deploy run fails; or any host write returns a non-2xx.
