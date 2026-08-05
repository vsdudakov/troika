# Skills

Tool-neutral procedures, references, templates. Run: `run harness/skills/develop-flow.md for <TICKET>`. Frontmatter enables discovery.

**Kind** fixes shape:

| Kind | Body | Read it as |
| --- | --- | --- |
| procedure | numbered `## 1.` … steps, then `## Output`, `## Stop conditions` | every step is a gate — don't advance until it holds |
| reference | topic sections, then `## Gotchas` | look up what you need |
| template | `## Fill rules`, then `## Template` | copy the block, fill it, delete what doesn't apply |

## Procedures

| Skill | File | Run by |
| --- | --- | --- |
| Develop flow (ticket → merge-ready PR) | [develop-flow.md](develop-flow.md) | orchestrator |
| Plan review (pre-code gate, replaces human approval) | [plan-review.md](plan-review.md) | [reviewer](../agents/reviewer.md) |
| Implement change (one repo) | [implement-change.md](implement-change.md) | [backend-dev](../agents/backend-dev.md) · [frontend-dev](../agents/frontend-dev.md) |
| Internal review (pre-PR, local diff) | [internal-review.md](internal-review.md) | [reviewer](../agents/reviewer.md) |
| Run unit tests (changed only, parallel lanes) | [run-unit-tests.md](run-unit-tests.md) | [tester](../agents/tester.md) |
| QA verify (local stack) | [qa-verify.md](qa-verify.md) | [qa](../agents/qa.md) |
| Release PR (commit, PR, proofs, ticket) | [release-pr.md](release-pr.md) | [releaser](../agents/releaser.md) |
| PR review (post-PR, posted to the PR host) | [pr-review.md](pr-review.md) | [reviewer](../agents/reviewer.md) |
| Ticket intake (create or reshape a ticket) | [ticket-intake.md](ticket-intake.md) | [architect](../agents/architect.md) · [commenter](../agents/commenter.md) |
| Incident triage (read-only, from observability) | [incident-triage.md](incident-triage.md) | [architect](../agents/architect.md) · [backend-dev](../agents/backend-dev.md) |
| Demo prep (integration branch → deployed demo) | [demo-prep.md](demo-prep.md) | [releaser](../agents/releaser.md) |
| Release cut (periodic release, end to end) | [release-cut.md](release-cut.md) | [releaser](../agents/releaser.md) |
| Release notes (diff → customer-readable notes) | [release-notes.md](release-notes.md) | [releaser](../agents/releaser.md) |

## References

| Skill | File | Used by |
| --- | --- | --- |
| Branches and worktrees | [worktree.md](worktree.md) | all dev / review / QA roles |
| Cross-repo order and PR linking | [cross-repo.md](cross-repo.md) | orchestrator · [releaser](../agents/releaser.md) |
| Tracker — auth, read, comment, attachments, transitions where the profile declares any | [tracker.md](tracker.md) | [architect](../agents/architect.md) · [releaser](../agents/releaser.md) |

## Templates

| Skill | File | Filled by |
| --- | --- | --- |
| Plan | [plan-template.md](plan-template.md) | [architect](../agents/architect.md) |
| PR body and title | [pr-template.md](pr-template.md) | [releaser](../agents/releaser.md) via [commenter](../agents/commenter.md) |

Skills contain no organization facts; read them from workspace [AGENTS.md](../../AGENTS.md). Missing anchor means not applicable. See [conventions](../README.md#conventions).
