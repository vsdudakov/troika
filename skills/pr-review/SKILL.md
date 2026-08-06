---
name: pr-review
description: Reviews an open PR in an isolated worktree and posts one review comment. Read-only and lint-only — never runs tests, edits code, or merges.
---

# PR review

Review open PR and post one comment. Local diff uses [internal-review](../internal-review/SKILL.md).

**Kind** procedure · **Used by** [reviewer](../../agents/reviewer.md) · **When** the PR is open (release-pr step 7, or on request) · **Ends with** one review comment on the PR and a verdict

Read-only: no test, edit, merge. Set `WS`.

## 1. Requirements

From inside the target repo:

```bash
gh pr view <N> --json title,body,comments,baseRefName,headRefName,files
gh pr diff <N>
```

Combine PR body, ticket, and linked issues into requirements.

## 2. Worktree

Fetch and isolate latest branch:

```bash
git fetch <remote>
git worktree add "$TROIKA_WORKTREES/review-<repo>-<N>" <remote>/<headRefName>
```

Resolve profile remote/base; wire dependencies per [setup](../worktree/SKILL.md#setup).

## 3. Checks

Run all nine from [reviewer › Rules](../../agents/reviewer.md#rules): requirements, code style, verification, layering, queries, tests present, migrations, contract match, hygiene.

PR-pass specifics:

- **Verification** — run the verification commands the profile lists for the touched areas ([AGENTS.md › Commands](../../../AGENTS.md#commands)) in the review worktree; report failures verbatim.
- **Tests present** — verify from the diff that each changed or created file has a corresponding test and that it covers the change. Do not run it; the coverage gate is [AGENTS.md › Tests](../../../AGENTS.md#tests).

## 4. Post

Send findings through [commenter](../../agents/commenter.md); post via quoted heredoc:

```bash
gh pr comment <N> --body "$(cat <<'EOF'
<commenter's text>
EOF
)"
```

## 5. Clean up

```bash
git worktree remove "$TROIKA_WORKTREES/review-<repo>-<N>"
```

## Output

Post [reviewer format](../../agents/reviewer.md#output) headed `## Review of PR #<N> (base: <branch>)`; return verdict.

## Stop conditions

Blocker/Major → author fixes/pushes; re-review. Cheap nits fix; others do not gate. **Cap at 3 cycles** — then stop, leave the latest review on the PR, and report the unresolved findings to the human.
