---
title: Set up a workspace
description: A workspace is the folder holding your repos. One command creates it — what /troika:setup writes into .troika/, what it asks you, and how to do it by hand.
---

# Set up a workspace

A **workspace** is the folder that holds your repos. Everything Troika needs lives in one
directory inside it, and one command creates that directory:

```
/troika:setup
```

Run it in the folder that holds your repos — not inside a repo. It reads them, drafts the
profile from what it finds, asks you about the handful of things no repo records, and writes:

```
<workspace>/
├── .troika/
│   ├── settings.json   where this workspace keeps its files — committed
│   ├── PROFILE.md      the project profile: what your codebase is — committed
│   ├── .gitignore      keeps the three below out of your history
│   ├── scratchpad/     plans, reviews, work logs, QA proofs
│   ├── worktrees/      one checkout per branch
│   └── memory/         dated observations about this workspace
├── backend/            your repos, each an independent clone
└── frontend/
```

`.troika/` is yours: it stays in your workspace, never in the Troika repository. That
separation is the whole design — [the repo is organisation-neutral](../guides/profile.md),
and everything specific to you is in this one directory.

## What setup asks you

Most of the profile is already written down in your repos, so setup reads before it asks.
Manifests, `Makefile`s, CI workflows, linter configs, git remotes and PR templates give it
the stack, the verification commands, the test framework and naming, the base branch, the
deploy triggers and the release scheme. It drafts those and shows them for confirmation.

What no repo records, it asks:

| It asks about | Because |
| --- | --- |
| the tracker | URL, project key, CLI, and **which writes a role may make** — silence here is read as "the usual transitions", and a role moves someone else's ticket |
| ownership | which role owns which repo or app; a repo nobody owns is a fine answer, and must be said |
| voice | how outward-facing text should sound, with one do and one don't |
| gotchas | destructive commands, production-access rules, the traps a newcomer hits |
| stack limits | what a green local run does **not** prove |

You confirm the whole draft once, not section by section. Then it writes `.troika/PROFILE.md`.

Run it again and it will not touch anything without asking. It reports what is already there
and offers three choices: leave it alone, update it against what the repos now say, or rewrite
the profile from the template. The default is to leave it — anything you wrote by hand survives
unless you ask for a rewrite in words.

## The profile — `.troika/PROFILE.md`

The **anchors are a contract**. Roles cite the profile by anchor id — `` `#commands` ``,
`` `#branches` ``, `` `#tests` ``, `` `#tracker` `` — so a missing section is a role reading
a reference that answers nothing. Keep the ids exactly as
[`PROFILE.template.md`](https://github.com/vsdudakov/troika/blob/main/PROFILE.template.md)
spells them; the headings above them are yours to reword.

Where the profile declares a *limit* — no ticket transitions, one repo and one PR, no build
step, a base branch that is not `origin/main` — **the roles follow the profile**, not the
generic wording in a skill.

[Writing the profile :material-arrow-right:](../guides/profile.md){ .md-button }
[Anchor reference :material-arrow-right:](../reference/profile-anchors.md){ .md-button }

## The paths — `.troika/settings.json`

```json
{
  "profile": ".troika/PROFILE.md",
  "scratchpad": ".troika/scratchpad",
  "worktrees": "/Volumes/fast/acme/worktrees",
  "memory": ".troika/memory"
}
```

Every key is optional. Relative values resolve against the workspace; absolute ones are taken
as-is, so state can live outside it entirely — useful when the worktrees belong on a faster
disk, or when the workspace itself is on a network mount.

Run setup in **each folder that holds a set of repos** — one per organisation, per client,
per checkout. A single installed plugin then serves all of them, because roles resolve the
paths at run time rather than carrying them.

[settings.json reference :material-arrow-right:](../reference/settings-json.md){ .md-button }

## By hand, without a model

The scaffold is one command; only the profile needs reading and asking.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --init <workspace>
```

Then copy [`PROFILE.template.md`](https://github.com/vsdudakov/troika/blob/main/PROFILE.template.md)
to `<workspace>/.troika/PROFILE.md` and fill every anchor.

## Check it

```bash
eval "$(python3 "${CLAUDE_PLUGIN_ROOT}/plugin/resolve.py" --ensure)"
env | grep TROIKA_
```

If the resolver exits non-zero, no ancestor of the current directory holds
`.troika/settings.json` — that is a stop, not a default, and the fix is `/troika:setup`.
[Paths and the resolver](../concepts/paths.md) explains what it looks for.

## Next

[Your first ticket :material-arrow-right:](first-ticket.md){ .md-button .md-button--primary }
