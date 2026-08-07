---
title: Adding a role
description: The file shape a role must have, the directory rule that has nothing to do with taste, and how to prove the new role's gate actually catches something.
---

# Adding a role

A role is one markdown file in `agents/`. It carries craft that is true in **any**
organisation — never a repo name, a command, or a URL.

## The shape

```markdown
---
name: <slug matching the filename>
description: <one line — the host shows this when picking a subagent>
---

# <Role>

- **Owns** — …
- **Runs** — [skill](../skills/<name>/SKILL.md) · **Step** … of develop-flow
- **Model** — the `<slug>` row of PROFILE.md › Models and effort (`#models`)
  - **Needs** — <judgment tier | execution tier> · <effort>
  - **Why** — …
  - **Raise it when** — …        (optional)
  - **Drop it when** — …         (optional)

## Scope
## Inputs
## Rules
## Gates
## Output
```

Those five sections, in that order, and the three header bullets, are enforced by
`tests/check.py`. The list markers matter: three bare lines collapse into one paragraph in
every markdown renderer.

**No model id belongs in the file.** A role says what its row needs — the judgment tier or the
execution tier, and an effort — and the workspace says which model that is, in the `#models`
anchor of its profile. A new role also means a new row there, so add it to the template's
default table in the same change; `check.py` rejects a `Claude` or `Codex` sub-bullet.

!!! danger "Only roles go in `agents/`"
    Hosts load **every** file in that directory as a subagent. A README, a note, or a draft in
    there is offered to users as a role. That is why the roles index lives at
    [`ROLES.md`](https://github.com/vsdudakov/troika/blob/main/ROLES.md) in the repo root.

## Write the refusals

The `Rules` section is where a role earns its place, and the strongest rules are negative:
what this role will not do, and what it hands to someone else. A role that may do anything
cannot be checked by the next role in the chain.

Then make the gate explicit in `Gates`: the condition under which this role refuses to pass
work on. A gate with no failure mode is documentation, not a gate.

## Say what it returns

`Output` states the exact shape — the handoff file it writes, and the fields it returns to the
orchestrator. Roles downstream parse that shape; if it is vague, the next role guesses.

## Prove it

A new gate is a claim. Turn it into a behavioural case: plant exactly the defect the gate
claims to catch and assert that it is caught.

```bash
mkdir tests/cases/<name>          # expect.yaml + only the files that differ from _base
python3 tests/run.py --check
python3 tests/run.py --dry-run --case <name>
python3 tests/run.py --runs 5 --case <name>
```

[Testing :material-arrow-right:](../testing.md){ .md-button }

## Wire it up

Nothing to register: `agents/` is auto-loaded by the host. Add the role to the tables in
`ROLES.md` — the who-does-what table and the model table — and run:

```bash
python3 tests/check.py
```
