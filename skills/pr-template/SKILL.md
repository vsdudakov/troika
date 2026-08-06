---
name: pr-template
description: How to fill the workspace's PR body and title honestly — section by section, with the rules for a repo's own template and for stripping AI product names.
---

# PR body

Fill profile PR title/body.

**Kind** template · **Used by** [releaser](../../agents/releaser.md) via [commenter](../../agents/commenter.md) · **When** opening the PR (release-pr step 3) · **Ends with** a PR title and body ready to post, with no AI product named

## Which template wins

1. The repo's own `.github/PULL_REQUEST_TEMPLATE.md`, if it has one and it differs.
2. Otherwise the workspace template in [AGENTS.md › PR body](../../../AGENTS.md#pr-template).

Strip AI product names, including HTML comments.

## Fill rules

- List actual changes; delete empty/inapplicable sections.
- Link the ticket ([tracker](../tracker/SKILL.md)).
- Answer every question; elaborate yes answers. Link upstream PRs.
- A "prompts used" section, where the template has one, carries the task the work was done from — **without naming any AI product**.
- Testing notes: QA steps, proof filenames, **Not verified**. Never inflate coverage.
- Include plan assumptions.
- Tick the checkboxes that apply, and only those.
- Text is written by [commenter](../../agents/commenter.md) and posted through a quoted heredoc ([shell quoting](../../README.md#shell-quoting)).

## Title

Conventional Commit: `<type>(<scope>): <summary>`; type `feat|fix|chore|docs|refactor|test|perf|ci`. Profile may pin scopes.

The commit message uses the same title, with the ticket key on its own line in the body ([release-pr › Commit](../release-pr/SKILL.md#2-commit)).
