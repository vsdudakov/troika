---
title: Releases and versioning
description: One VERSION file, a tag-driven release workflow, and the three ways to install a pinned version.
---

# Releases and versioning

Troika has nothing to compile, so a release is a **tag plus an archive**: a fixed tree that a
workspace can pin to and stop moving.

## One version, four manifests

`VERSION` is the source. `plugin/version.py` writes it into the three plugin manifests and the
Claude marketplace entry, and `tests/check.py` fails if any of them drifts.

```bash
make version            # print it
make version V=0.2.0    # set it everywhere, then run the structural gate
```

A host keys an installed plugin on name *and* version. Two manifests that disagree install as
two plugins from one tree, and only one of them ever gets updated — hence the check.

## Cutting a release

```bash
make version V=0.2.0
git commit -am "release: v0.2.0"
make release            # runs the gates, tags v0.2.0, pushes the tag
```

The tag triggers `.github/workflows/release.yml`, which re-runs the gates on the tag, refuses
to publish if the tag and `VERSION` disagree, builds `troika-0.2.0.tar.gz` plus a SHA-256, and
publishes a GitHub Release with generated notes.

Build the same archive locally to inspect it:

```bash
make dist
```

The archive carries what a host loads — manifests, `agents/`, `skills/`, `plugin/` — plus the
profile template, `ROLES.md`, the README and the licence. Not the tests, fixtures or docs
sources: those are development inputs.

## Installing a specific version

**Pin the marketplace to a tag (recommended).** In a workspace's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "troika": {
      "source": { "source": "github", "repo": "vsdudakov/troika", "ref": "v0.2.0" }
    }
  },
  "enabledPlugins": { "troika@troika": true }
}
```

Commit that file and every clone of the workspace runs the same version. Bumping is a
one-line diff and a reviewable one.

**Codex takes a ref inline:**

```bash
codex plugin marketplace add vsdudakov/troika@v0.2.0
codex plugin add troika@troika
```

**Or install from the release archive** — no git required at the destination:

```bash
make install-release V=0.2.0
```

which is the scripted form of:

```bash
mkdir -p ~/.troika
curl -fsSL https://github.com/vsdudakov/troika/releases/download/v0.2.0/troika-0.2.0.tar.gz \
  | tar xz -C ~/.troika
claude plugin marketplace add ~/.troika/troika-0.2.0
claude plugin install troika@troika
```

Verify the download against the published checksum first if you are pinning for a team:

```bash
curl -fsSLO https://github.com/vsdudakov/troika/releases/download/v0.2.0/troika-0.2.0.tar.gz.sha256
shasum -a 256 -c troika-0.2.0.tar.gz.sha256
```

## Upgrading an installed plugin

A host caches the marketplace it installed from, so **refreshing the marketplace and
updating the plugin are two steps** in all three. Skipping the first one re-installs the
version you already have.

=== "Claude Code"

    ```bash
    claude plugin marketplace update troika   # refresh the cached marketplace
    claude plugin update troika@troika        # install the new version
    ```

    Restart Claude Code to load it. Confirm what is live:

    ```bash
    claude plugin list                        # troika@troika  0.2.0  enabled
    ```

=== "Codex"

    ```bash
    codex plugin marketplace upgrade          # refresh the Git marketplace snapshots
    codex plugin add troika@troika            # re-install from the refreshed snapshot
    ```

    Codex has no `update` verb — `add` over an installed plugin is the upgrade.

=== "Cursor"

    ```bash
    cursor-agent plugin marketplace update https://github.com/vsdudakov/troika
    ```

    Cursor re-indexes the marketplace from git; there is no separate per-plugin step.

All three in one go, against a checkout of this repo:

```bash
make upgrade
```

!!! warning "A pinned version does not move"
    If the workspace pinned a tag — `"ref": "v0.1.0"` in `.claude/settings.json`, or
    `owner/repo@v0.1.0` on the Codex/Cursor marketplace — the refresh still fetches that
    tag. **Bump the ref first**, then upgrade. That is the point of pinning: the version
    changes in a reviewable diff, not under you.

Installing from a release archive is versioned by directory, so an upgrade is a fresh
install of the new one:

```bash
make install-release V=0.2.0
```

Old `~/.troika/troika-<version>` trees are left in place; remove the ones you no longer
have a marketplace pointing at.

## Bumping the version on every release

Every release bumps `VERSION` **before** the tag, and the manifests are written from it —
never edited by hand. The whole cycle:

```bash
make version V=0.2.0             # VERSION + the four manifests, then the structural gate
git commit -am "release: v0.2.0"
make release                     # gates, tag v0.2.0, push
```

`release.yml` refuses to publish if the tag and `VERSION` disagree, and `tests/check.py`
fails if any manifest drifts from `VERSION` — so a release that forgot the bump cannot
reach a GitHub Release. Two releases sharing one version is the failure this prevents:
a host keys the install on name *and* version, sees no change, and never upgrades.

## What a version means here

Troika versions the **contract**, not an API:

- **patch** — wording, clarifications, a new gotcha, a tightened rule that rejects the same
  work it always should have.
- **minor** — a new skill, a new role, a new command, a new optional profile anchor.
- **major** — a change that makes an existing workspace's `.troika/PROFILE.md` or `settings.json`
  wrong: a renamed anchor, a removed variable, a changed handoff filename.

Anything that would break a written profile is a major, even if it is one word.
