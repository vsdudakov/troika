---
title: AGENTS.md anchors
description: The twenty-five anchors roles link into, what each must answer, and which roles read it.
---

# `AGENTS.md` anchors

The profile is linked **by anchor**. Keep these ids exactly as written; the headings above them
are yours. `python3 tests/check.py` verifies that every anchor the tree needs exists in
`AGENTS.template.md`, so a fresh workspace never inherits a dead link.

| Anchor | Must answer | Read by |
| --- | --- | --- |
| `#rules` | the rules binding every session, with or without a role | everyone |
| `#comments` | when a comment is allowed in code | dev roles, reviewer |
| `#no-ai-attribution` | what may never appear in commits, PRs, tracker text | everyone |
| `#voice` | how outward-facing text sounds | commenter |
| `#repo-map` | which repos exist, what each is, what is out of scope | everyone |
| `#ownership` | which role owns which repo or app | everyone |
| `#workspace-paths` | the workspace root, the resolver, the absolute-path rule | everyone |
| `#code-search` | the code search tool and how to refresh its index | architect, dev roles, reviewer, tester |
| `#branches` | **remote and default branch (the base ref)**, naming, worktree dependency setup, push quirks | dev roles, reviewer, tester, releaser |
| `#dependency-order` | provider → consumer order, and how shared libraries are released | architect, releaser |
| `#commands` | per repo or area: narrowed tests, **the exact verification commands a dev role must run**, full suite, parallel flags; for migrations, the generator command and what may be done to an applied revision | dev roles, reviewer, tester |
| `#parallel-tests` | one lane per area, the parallel flag each runner takes, suites that must stay sequential | tester |
| `#style` | per-language style rules | dev roles, reviewer |
| `#layering` | the architectural layers, if the codebase has them | backend-dev, reviewer |
| `#tests` | framework, naming, location, coverage gate, who runs them and when | dev roles, reviewer, tester |
| `#stack` | how to run the product locally and point it at a worktree | qa |
| `#stack-limits` | what the local stack cannot verify | qa, architect |
| `#tracker` | tracker URL, project key, CLI or API, auth check, **which writes a role may make** — transition names, or an explicit "there are none" | architect, releaser |
| `#pull-requests` | PR host, title format, CI watch, review-bot loop | releaser |
| `#pr-template` | the PR body the team uses | releaser, commenter |
| `#deploy` | environments, what triggers each, how a deploy is dispatched and watched | releaser |
| `#release` | version scheme, release branches and tags, the procedure, which steps are the human's | releaser |
| `#demo` | the demo label, integration branch and environment — or that there is no demo cadence | releaser |
| `#announcements` | where releases and demos are announced, and in what form | commenter, releaser |
| `#observability` | the platform, how to query it, what is instrumented | architect, backend-dev |
| `#gotchas` | traps specific to this workspace, including commands that destroy uncommitted work | everyone |

## Writing rules that hold

- **State the limits.** "There are no transitions" is a fact a role can follow. Silence is not.
- **Name commands exactly.** A command not in `#commands` is not a verification gate — say so,
  or a role will count one that is not.
- **An empty anchor is worse than a missing one.** It reads as "not applicable here".
- **Do not restate a skill.** If the procedure already says it and it is true anywhere, it
  belongs in the skill, not the profile.

[Writing the profile :material-arrow-right:](../guides/profile.md){ .md-button }
