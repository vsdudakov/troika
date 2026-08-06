---
title: Writing the profile
description: .troika/PROFILE.md is the only file that knows your organisation. What each section must answer, how the anchor contract works, and the sections that pay off first.
---

# Writing the profile

`.troika/PROFILE.md` in your workspace is the single place Troika learns what your codebase is. Every
role reads it; no role hardcodes anything it contains.

Start from
[`PROFILE.template.md`](https://github.com/vsdudakov/troika/blob/main/PROFILE.template.md) —
it carries the full anchor list with a one-line brief for each section.

## The anchor contract

Roles link into the profile **by anchor**, not by heading text:

```markdown
<a id="commands"></a>
## Commands, per repo
```

Keep the anchor ids exactly as the template writes them; the headings above them are yours to
reword. A missing anchor is a role following a dead link, so the structural gate checks that
every anchor the tree needs exists:

```bash
python3 tests/check.py
```

An anchor with **no content** is worse than a missing section — it reads as "this does not
apply here" to a role that then proceeds without the fact.

## Write the limits, not just the capabilities

The profile is also where you say what is *not* available, and roles follow the profile over
their own generic wording:

- *"No transitions — the board's state does not exist"* → the releaser stops trying to move
  tickets and records the equivalent write instead.
- *"One repo, one PR"* → the architect stops planning cross-repo lanes.
- *"No build step"* → a dev role stops treating a missing build as a failure.
- *"Base branch is `origin/develop`"* → every diff and worktree uses that ref.

## The sections that pay off first

| Anchor | Why it pays first |
| --- | --- |
| `#commands` | the dev roles' verification gate. A command not in that table **is not a gate** — say so explicitly, or a role will count one that is not |
| `#tests` | tells the reviewer what a mirror test looks like, which is check 6 of nine |
| `#branches` | the base ref for every diff and worktree; get this wrong and reviews read the wrong changes |
| `#stack` / `#stack-limits` | whether QA can verify at all, and what it must report as unverifiable |
| `#layering` | turns "this feels wrong" into a citable rule the reviewer can enforce |
| `#gotchas` | the commands that destroy uncommitted work; roles are told never to run them mid-flow |

## Migrations deserve a sentence

`#commands` should state the generator command **and** whether an already-applied revision may
be hand-edited or renumbered. Without it the reviewer's migrations check has nothing to cite,
and hand-edited migrations are the defect that surfaces in production rather than in review.

## Keep it a profile, not a manual

One home per fact:

- Specific to your organisation → the profile.
- One role's craft, true anywhere → a role file.
- Ordered steps, true anywhere → a skill.
- Observed, dated, and possibly temporary →
  [memory](https://github.com/vsdudakov/troika/blob/main/skills/memory/SKILL.md).

Everything else links.
