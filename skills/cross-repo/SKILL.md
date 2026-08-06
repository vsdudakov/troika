---
name: cross-repo
description: Features spanning several repos — dependency order, when work can run in parallel, how a shared library's release gates its consumers, and how the PRs link.
---

# Cross-repo features

Order, concurrency, and links for multi-repo work.

**Kind** reference · **Used by** orchestrator · [architect](../../agents/architect.md) · [releaser](../../agents/releaser.md) · **When** the plan spans more than one repo (develop-flow step 3) · **Ends with** a repo order, a parallel/sequential call, and PRs linked in dependency order

One lane/branch/PR per repo. Multi-area single-repo work stays one lane.

## Order: providers before consumers

Use profile dependency order. Same-level independent repos may run in parallel. Skip untouched levels.

## Shared libraries released by tag

Pinned libraries require a release and consumer pin bump:

- The change lands in the library first.
- Each consumer bumps the pin and refreshes its lockfile in its own PR.
- **The release must exist before the consumer merges**, not before its PR opens. A consumer PR pointing at an uncut version fails CI at dependency resolution — mark it blocked rather than guessing a version.
- Pins drift between consumers. Check each one rather than assuming they match, and bump only the ones the plan touches.

## Parallel vs sequential

Pinned contract permits parallel development; otherwise follow dependency order.

## Link the PRs

Every PR after the first declares its upstream PR(s) in the body ([pr-template](../pr-template/SKILL.md)). Use one ticket key across all branches and PRs so they group on the ticket ([tracker](../tracker/SKILL.md)). On the ticket, comment the full PR chain in dependency order so reviewers and deployers merge in the right sequence.

## Verify per repo, then together

After per-repo gates, run the applicable integration suite — then read what its result means ([AGENTS.md › Stack limits](../../../AGENTS.md#stack-limits)): a suite building from its own default-branch checkouts is a regression check, never evidence for the branch.

## Gotchas

- **A change in a pinned library usually cannot be exercised on the local stack** — the stack runs the consumer's installed copy, which is the pinned release, not the worktree. It ships on unit tests plus the consumer PR after the release is cut; say so in the QA report's **Not verified** list.
- A consumer PR that is only waiting on a release is *blocked*, not broken — label it that way rather than forcing CI green.
- One ticket, many PRs: any transition the profile declares runs **once**, when the first PR opens — not per repo. Where the profile declares none, the PR-chain comment is the only tracker write.
