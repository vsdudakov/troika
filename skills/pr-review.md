---
name: pr-review
description: Reviews an open PR in an isolated worktree and posts one review comment. Read-only and lint-only — never runs tests, edits code, or merges.
---

# PR review

The post-PR pass on an open pull request; the report is posted as a PR comment. For the pre-push pass on a local diff use [internal-review.md](internal-review.md).

**Kind** procedure · **Used by** [reviewer](../agents/reviewer.md) · **When** the PR is open (release-pr step 7, or on request) · **Ends with** one review comment on the PR and a verdict

Read-only — never run tests, edit code, or merge; tests belong to the tester before the PR and to CI after it. Set `WS` first ([AGENTS.md › Workspace paths](../../AGENTS.md#workspace-paths)).

## 1. Requirements

From inside the target repo:

```bash
gh pr view <N> --json title,body,comments,baseRefName,headRefName,files
gh pr diff <N>
```

Combine the PR body, the linked ticket, and any linked issues into the requirements the change must meet.

## 2. Worktree

Review the branch's latest code in isolation — fetch first or the ref is stale:

```bash
git fetch <remote>
git worktree add "$WS/llm/worktrees/review-<repo>-<N>" <remote>/<headRefName>
```

Remote and default branch come from [AGENTS.md › Branches](../../AGENTS.md#branches) ([base ref](worktree.md#base-ref)). Wire up dependencies per [worktree › setup](worktree.md#setup). The repo name is in the path because PRs in different repos share numbers.

## 3. Checks

Run all nine from [reviewer › Rules](../agents/reviewer.md#rules): requirements, code style, lint, layering, queries, tests present, migrations, contract match, hygiene.

Two notes specific to this pass:

- **Lint** — run the verification commands the profile lists for the touched areas ([AGENTS.md › Commands](../../AGENTS.md#commands)) in the review worktree; report failures verbatim.
- **Tests present** — verify from the diff that each changed or created file has a corresponding test and that it covers the change. Do not run it; the coverage gate is [AGENTS.md › Tests](../../AGENTS.md#tests).

## 4. Post

The findings go to [commenter](../agents/commenter.md) first, then post what it returns. Use a quoted heredoc — the finding format wraps `file:line` and identifiers in backticks, and inside `"…"` the shell would execute them as command substitutions and post a comment with the citations silently deleted ([shell quoting](../README.md#shell-quoting)):

```bash
gh pr comment <N> --body "$(cat <<'EOF'
<commenter's text>
EOF
)"
```

## 5. Clean up

```bash
git worktree remove "$WS/llm/worktrees/review-<repo>-<N>"
```

## Output

Post the [reviewer output format](../agents/reviewer.md#output) as the comment body, headed `## Review of PR #<N> (base: <branch>)`, and return the verdict to the caller.

## Stop conditions

Resolve every Blocker and Major, plus Nits where the fix is cheap; the author commits, pushes, and this skill runs again. Remaining Nits don't gate. **Cap at three cycles**: if the third review still doesn't pass, stop, leave the latest review on the PR, and report the unresolved findings to the human.
