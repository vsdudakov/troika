---
title: Contributing
description: How to propose a change to Troika, what the gates expect, and the evidence a behavioural change needs.
---

# Contributing

Issues and pull requests are welcome.

```bash
git clone https://github.com/vsdudakov/troika
cd troika
make check        # structural gate — no model, no spend
make test-check   # behavioural fixtures — no model, no spend
```

Both must be green before you open a pull request. There is nothing to install: the gates run
on a bare `python3`.

## What a good change looks like

**Prose changes carry their own evidence.** If you tighten a rule, say what it now rejects that
it did not before. "Clearer" is not a reason a reviewer can check.

**Behavioural changes carry catch rates.** If you change a role's rules or a procedure's gates,
run the behavioural suite and put the numbers in the pull request:

```bash
python3 tests/run.py --runs 5 > /tmp/before.txt   # on main
python3 tests/run.py --runs 5 > /tmp/after.txt    # on your branch
diff /tmp/before.txt /tmp/after.txt
```

That diff is the only evidence that matters for a prompt change. A rate that drops is a
regression even when the wording reads better.

**New gates come with a case.** A gate is a claim that something gets caught. Add a case that
plants exactly that defect — see [Adding a role](guides/adding-a-role.md) and
[Testing](testing.md).

## House rules

- **Nothing names an organisation.** No repo, command, branch, tracker, URL or person in
  `agents/` or `skills/`. Facts come from the profile by anchor; the gate enforces it.
- **No hardcoded paths.** Use the resolved `$TROIKA_*` variables.
- **Generated files are generated.** Edit the procedure, then `python3 plugin/generate.py`.
  Never hand-edit `plugin/commands/*.md` or the manifest's command list.
- **Roles only in `agents/`.** Hosts load every file there as a subagent.
- **Em dashes take spaces around them.** The gate checks this, because an unspaced one changes
  how a sentence renders.

## Adding a profile anchor

If a role needs a fact no anchor covers, add the anchor to `AGENTS.template.md` **in the same
change** as the role or skill that reads it. The template is the contract every workspace
writes against, and `check.py` fails a link into an anchor the template does not have.

## Releasing

Maintainers cut releases with `make version V=x.y.z` and `make release`; the tag drives the
rest. See [Releases and versioning](reference/releases.md).

## Licence

By contributing you agree that your contributions are licensed under the
[MIT Licence](https://github.com/vsdudakov/troika/blob/main/LICENSE.md).
