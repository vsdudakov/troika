---
title: Adding a skill
description: Create a procedure, reference or template, get a slash command for free, and keep the generated surface from drifting.
---

# Adding a skill

A skill is a directory with one `SKILL.md` in it:

```bash
mkdir skills/backport
$EDITOR skills/backport/SKILL.md
python3 plugin/generate.py     # add it to COMMANDS first if it needs a /tr: entry
python3 tests/check.py
```

## The shape

```markdown
---
name: backport
description: <one line — this becomes the command's description and the host's skill blurb>
---

# Backport

**Kind** procedure · **Used by** [releaser](../../agents/releaser.md) · **When** a fix must land on a release branch · **Ends with** a PR against that branch

## 1. <first gate>
## 2. <next gate>
## Output
## Stop conditions
```

`**Kind**` fixes the body:

| Kind | Body | Gets a command |
| --- | --- | --- |
| procedure | numbered steps, then `## Output`, `## Stop conditions` | yes |
| reference | topic sections, then `## Gotchas` | no |
| template | `## Fill rules`, then `## Template` | no |

References and templates get no command on purpose — they are read *by* a procedure or filled
by one, and neither can be "finished".

## Write steps as gates

Each numbered step should be something that can *fail*. If a step cannot fail, it is context
and belongs in the header or a reference. `## Stop conditions` is where you say what makes the
procedure abort rather than improvise — a command the profile does not define, a stack that
will not boot, a proof that cannot be captured.

## Name no organisation facts

Say *"the profile's verification commands"*, not `pytest -q`. Say *"the base ref"*, not
`origin/main`. Link the fact by anchor:

```markdown
Run the verification commands (PROFILE.md › Commands (`#commands`)).
```

The link depth is three levels up from inside a skill directory, and `check.py` will tell you
if you get it wrong. If you need an anchor the template does not have, add it to
`PROFILE.template.md` in the same change — that is the contract every workspace writes against.

## Regenerate and check

```bash
python3 plugin/generate.py
python3 tests/check.py
```

The generator writes `plugin/commands/<name>.md` and the `commands` list in the Claude
manifest. Never hand-edit either: `check.py` fails a stale command, a command with no
procedure behind it, and a manifest list that has drifted.

## Adding it to a flow

A skill nobody runs is dead weight. Reference it from the role that runs it (`- **Runs**`), and
from `develop-flow` if it belongs in the pipeline — plus the table in `skills/README.md`.
