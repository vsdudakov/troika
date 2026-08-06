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

## What a version means here

Troika versions the **contract**, not an API:

- **patch** — wording, clarifications, a new gotcha, a tightened rule that rejects the same
  work it always should have.
- **minor** — a new skill, a new role, a new command, a new optional profile anchor.
- **major** — a change that makes an existing workspace's `AGENTS.md` or `.troika.json`
  wrong: a renamed anchor, a removed variable, a changed handoff filename.

Anything that would break a written profile is a major, even if it is one word.
