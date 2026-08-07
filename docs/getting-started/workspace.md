---
title: Set up a workspace
description: A workspace is the folder holding your repos. One command creates it — what /tr:setup writes into .troika/, what it asks you, and how to do it by hand.
---

# Set up a workspace

A **workspace** is the folder that holds your repos. Everything Troika needs lives in one
directory inside it, and one command creates that directory:

```
/tr:setup
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

Setup runs as a **wizard**, in this order:

1. **Fix the root** — the folder that holds your repos, never a repo itself.
2. **Scope** — it lists every repo it found and you tick the ones Troika may touch. An
   unticked repo is written into `#repo-map` by name, marked out of scope, so a role that
   stumbles on it knows that was a decision.
3. **Scaffold** — `settings.json`, the `.gitignore`, the three state directories.
4. **Derive from the code** — one read-only probe per ticked repo, reading real source files
   and not only config: the style a reviewer can cite, the test framework and mirror rule and
   mocking policy, the exact verification commands, the branches, and a *runnable* local-stack
   sequence with its health check and what it cannot prove.
5. **Find credentials already on this machine** — `gh auth status`, then the environment and
   your shell files for a tracker or tool token. It shows the **variable name and the file**
   and asks whether to use it. A value is never printed and never written into the profile.
6. **One batched interview** for what no file records — below.
7. **Confirm the whole draft once**, then write it and verify every anchor exists.

What no repo records, it asks:

| It asks about | Because |
| --- | --- |
| which repos are in scope | a ticked list, not an open question; an unticked repo is recorded as out of scope rather than forgotten |
| the review runner | which second tool reviews the plan and the diff, so the reviewer is not the family that wrote them |
| the base and demo branches | the base ref every diff, worktree and PR is measured against — and the throwaway demo branch, if there is one |
| the tracker | URL, project key, CLI, and **which writes a role may make** — silence here is read as "the usual transitions", and a role moves someone else's ticket |
| investigation tools | a ticked list — Sentry, Datadog, Grafana, CloudWatch, and the rest — and the credential for each, or how to get it |
| ownership | which role owns which repo or app; a repo nobody owns is a fine answer, and must be said |
| voice | **two or three sentences you actually wrote** to your team — a real PR description or Slack message, not a description of how you would like to sound. Setup derives the do and the don't from them |
| gotchas | destructive commands, production-access rules, the traps a newcomer hits |
| stack limits | what a green local run does **not** prove |
| autonomy | who the reporter is and how a `--ask` run reaches them, how long it waits, and what may never be automatic on an unattended run |
| models | which models and efforts the roles run on, and the second tool that reviews independently — the defaults are shown, you correct what your accounts cannot run |

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
`.troika/settings.json` — that is a stop, not a default, and the fix is `/tr:setup`.
[Paths and the resolver](../concepts/paths.md) explains what it looks for.

## Next

[Your first ticket :material-arrow-right:](first-ticket.md){ .md-button .md-button--primary }
