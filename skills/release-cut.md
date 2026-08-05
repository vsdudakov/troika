---
name: release-cut
description: Cuts a periodic release end-to-end — promote the previous pre-release, branch, pre-release, notes, QA plan, deploy to the pre-production environment, prepare the announcement.
---

# Release cut

Promote previous cut; create, document, deploy next.

**Kind** procedure · **Used by** [releaser](../agents/releaser.md) · **When** the workspace's release cadence says to cut, or a human asks for one · **Ends with** a promoted previous release, a new branch + pre-release, merged release notes, a QA plan issue, a pre-production deploy, and an announcement waiting for the human's go-ahead

Use profile release/branch/deploy facts. No cadence means not applicable.

Write once; non-2xx stops. No blind retry, force-push, moved tag, direct protected-branch push, or production deploy.

## 1. Promote the previous release — after checking its tag still describes it

Before promotion, check branch drift:

```bash
git fetch <remote> --tags
git log --oneline <prev-tag>..<remote>/<prev-release-branch>    # post-cut cherry-picks
```

A non-empty list means the tag no longer describes what shipped, and promoting it leaks those cherry-picks into the **next** changelog, which is generated from that tag. **A cherry-pick onto a release branch is a re-cut**: tag the branch head with the next counter and promote that. Record the tag you promoted — it is `<prev-tag>` for steps 2 and 3. Skip the step when there is no prior pre-release.

## 2. Cut the branch and create the pre-release

Branch from current default, push branch, tag with generated changelog from `<prev-tag>`. Read it back. Earlier-release entries mean stale start tag: recreate; never hand-edit.

## 3. Release notes

Run [release-notes.md](release-notes.md) for this release, diffing the previous release's **branch head** against the new branch — not its tag. Open its PR, get it merged so the notes land on the default branch, and keep its per-item QA blocks: step 4 is built from them.

## 4. QA plan

Create one QA issue from notes QA blocks only; link notes and pre-release.

Cross-check the previous release's QA issues and drop any step already covered. A repeat means the notes' dedup missed a cherry-pick: fix the notes, not just the issue.

## 5. Deploy to pre-production

Dispatch all profile pre-production deploys; watch to completion. Failure URL stops flow.

## 6. Announcement — prepared, not posted

Fill announcement with existing artifact links. Prepare only; post on explicit request.

## Output

New branch and tag · the promoted previous tag (and whether step 1 found drift) · release-notes PR URL and merge state · QA plan issue URL · deploy run URLs and final state · the announcement text, and whether it was posted.

## Stop conditions

Stop and hand back when: step 1 finds drift and the re-cut tag is rejected by the host; the generated changelog still lists earlier work after fixing the start tag; the notes PR cannot merge; a deploy run fails; or any host write returns a non-2xx.
