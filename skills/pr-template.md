---
name: pr-template
description: How to fill the workspace's PR body and title honestly — section by section, with the rules for a repo's own template and for stripping AI product names.
---

# PR body

The rules for filling the PR body and the title above it. **The body itself is per-workspace** — [AGENTS.md › PR body](../../AGENTS.md#pr-template).

**Kind** template · **Used by** [releaser](../agents/releaser.md) via [commenter](../agents/commenter.md) · **When** opening the PR (release-pr step 3) · **Ends with** a PR title and body ready to post, with no AI product named

## Which template wins

1. The repo's own `.github/PULL_REQUEST_TEMPLATE.md`, if it has one and it differs.
2. Otherwise the workspace template in [AGENTS.md › PR body](../../AGENTS.md#pr-template).

Either way, **strip any AI product name before posting** — including inside HTML comments, which are not exempt ([no-ai-attribution](../../AGENTS.md#no-ai-attribution)).

## Fill rules

- List what actually changed; delete the sections that don't apply rather than leaving an empty heading or a placeholder.
- Link the ticket ([tracker](tracker.md)).
- **Answer every question honestly** — elaborate instead of a bare "No" when the answer is yes. Cross-repo work declares its upstream PRs with links ([cross-repo](cross-repo.md)).
- A "prompts used" section, where the template has one, carries the task the work was done from — **without naming any AI product**.
- **Testing notes** carry the QA steps, the proof list by filename (UI: before/after GIF pair; API: request + datastore transcript), and the QA report's **Not verified** items. Never claim coverage the stack didn't give ([AGENTS.md › Stack limits](../../AGENTS.md#stack-limits)).
- Any assumption the architect recorded in the plan goes in the body — that is where a reviewer sees the judgment call.
- Tick the checkboxes that apply, and only those.
- Text is written by [commenter](../agents/commenter.md) and posted through a quoted heredoc ([shell quoting](../README.md#shell-quoting)).

## Title

[Conventional Commits](https://www.conventionalcommits.org/): `<type>(<scope>): <summary>`. `type` is one of `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`; `scope` is the repo or affected area. The workspace may pin its own scope vocabulary ([AGENTS.md › Pull requests](../../AGENTS.md#pull-requests)).

The commit message uses the same title, with the ticket key on its own line in the body ([release-pr › Commit](release-pr.md#2-commit)).
