---
name: cross-repo
description: Features spanning several repos — dependency order, when work can run in parallel, how a shared library's release gates its consumers, and how the PRs link.
---

# Cross-repo features

When the plan's requirements span more than one repo: which order, what can overlap, and how the PRs reference each other.

**Kind** reference · **Used by** orchestrator · [architect](../agents/architect.md) · [releaser](../agents/releaser.md) · **When** the plan spans more than one repo (develop-flow step 3) · **Ends with** a repo order, a parallel/sequential call, and PRs linked in dependency order

Split the work into one task per repo and run the per-repo flow for each. **Never mix two repos' changes in one branch or PR** — each repo is an independent clone with its own PR.

## Order: providers before consumers

The workspace's concrete order is [AGENTS.md › Dependency order](../../AGENTS.md#dependency-order). Derive it from who depends on whom; when two repos are on the same level with no contract between them, either order works, or both in parallel. Skip levels the plan doesn't touch.

## Shared libraries released by tag

A library consumed as a **pinned dependency** (a git tag, a published version) is not updated by merging it — the consumer only sees it after the release exists and the consumer bumps the pin in its own PR.

- The change lands in the library first.
- Each consumer bumps the pin and refreshes its lockfile in its own PR.
- **The release must exist before the consumer merges**, not before its PR opens. A consumer PR pointing at an uncut version fails CI at dependency resolution — mark it blocked rather than guessing a version.
- Pins drift between consumers. Check each one rather than assuming they match, and bump only the ones the plan touches.

## Parallel vs sequential

Two repos on different levels may still be developed in parallel when the [architect](../agents/architect.md) pinned the contract between them in the plan — the consumer codes against the pinned shape and declares the provider's PR as its upstream dependency. Without a pinned contract, run them sequentially in dependency order.

## Link the PRs

Every PR after the first declares its upstream PR(s) in the body ([pr-template](pr-template.md)). Use one ticket key across all branches and PRs so they group on the ticket ([tracker](tracker.md)). On the ticket, comment the full PR chain in dependency order so reviewers and deployers merge in the right sequence.

## Verify per repo, then together

Each repo's flow already gates on its own tests and lint. After the last repo, run the workspace's integration suite if it covers the touched services — but read what that result means first ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)): a suite that builds from its own default-branch checkouts is a regression check, not evidence for the branch.

## Gotchas

- **A change in a pinned library usually cannot be exercised on the local stack** — the stack runs the consumer's installed copy, which is the pinned release, not the worktree. It ships on unit tests plus the consumer PR after the release is cut; say so in the QA report's **Not verified** list.
- A consumer PR that is only waiting on a release is *blocked*, not broken — label it that way rather than forcing CI green.
- One ticket, many PRs: the ticket transitions once, when the first PR opens, not per repo.
