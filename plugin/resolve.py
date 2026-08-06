#!/usr/bin/env python3
"""Resolves the workspace a role is standing in, and the paths it writes to.

Roles run with their cwd inside a worktree, several levels below the workspace, and
Troika itself is an installed plugin in the host's cache, nowhere near the repos. So
neither end of a path can be assumed: this walks up from cwd to the workspace that owns
the run, and prints the paths every role uses. The tree's own location is the host's to
say — `${CLAUDE_PLUGIN_ROOT}` — and is deliberately not among them.

    eval "$(python3 plugin/resolve.py)"     # exports TROIKA_WORKSPACE and the TROIKA_* paths
    python3 plugin/resolve.py --json        # same, machine-readable
    python3 plugin/resolve.py --ensure      # also create the state directories
    python3 plugin/resolve.py --init DIR    # create .troika/ in DIR and stop

The workspace is the nearest ancestor holding `.troika/settings.json`. That file is the
only marker, and it is not optional: a folder with no `.troika/` is one nobody has run
`/troika:setup` in yet, and guessing paths for it scatters handoff files through whatever
directory the caller happened to be standing in.
"""

import json
import os
import shlex
import sys
from pathlib import Path

DIR = ".troika"
CONFIG = f"{DIR}/settings.json"
# Relative to the workspace root, and overridable one by one in .troika/settings.json.
# Everything the workspace owns lives in that one directory, so a workspace is a folder of
# repos plus `.troika/` and nothing else of Troika's.
DEFAULTS = {
    "profile": f"{DIR}/PROFILE.md",
    "scratchpad": f"{DIR}/scratchpad",
    "worktrees": f"{DIR}/worktrees",
    "memory": f"{DIR}/memory",
}
# The three the roles write into. `profile` is a file, so it is not created.
#
# Nothing here points at Troika's own tree. It is installed as a plugin, so the host
# exports where it put it — `${CLAUDE_PLUGIN_ROOT}` — and a second, workspace-declared
# copy of that path would only be a way to disagree with the host.
STATE = ("scratchpad", "worktrees", "memory")

# Written into `.troika/` by --init. The state directories are per-person: plans, proofs,
# uncommitted dev branches. settings.json and the profile are the workspace's shared
# contract and belong in its history.
GITIGNORE = """\
# Written by troika's resolver. The three state directories are per-person and never
# shared; settings.json and PROFILE.md are the workspace's contract and are committed.
#
# WARNING: `git clean -xfd` removes exactly these three — uncommitted dev branches,
# plans, proofs, memory. Use explicit paths instead.
/scratchpad/
/worktrees/
/memory/
"""


def find_workspace(start):
    """The directory holding `.troika/settings.json`. SystemExit with the fix when there is none."""
    for d in [start, *start.parents]:
        if (d / CONFIG).is_file():
            return d
    raise SystemExit(
        f"no workspace above {start}: expected a {CONFIG} in it or in an ancestor. "
        f"Run /troika:setup in the folder that holds your repos."
    )


def load(config):
    try:
        payload = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{config}: invalid JSON: {e}")
    if not isinstance(payload, dict):
        raise SystemExit(f"{config}: must contain a JSON object")
    unknown = sorted(set(payload) - set(DEFAULTS))
    if unknown:
        raise SystemExit(f"{config}: unknown key(s) {', '.join(unknown)}; expected {', '.join(DEFAULTS)}")
    return payload


def resolve(start=None):
    root = find_workspace(Path(start or os.getcwd()).resolve())
    config = root / CONFIG
    payload = load(config)
    out = {"TROIKA_WORKSPACE": str(root)}
    for key, default in DEFAULTS.items():
        value = payload.get(key, default)
        if not isinstance(value, str) or not value:
            raise SystemExit(f"{config}: {key} must be a non-empty string")
        # An absolute value wins outright: state can live outside the workspace — a
        # faster disk, or somewhere the workspace's own backup does not reach.
        path = Path(value).expanduser()
        out[f"TROIKA_{key.upper()}"] = str(path if path.is_absolute() else root / path)
    return out


def init(target):
    """Create `<target>/.troika/` with settings.json, a .gitignore, and the state dirs.

    Idempotent, and only the scaffold: the profile is the setup procedure's to write,
    because that is the part needing the repos read and the caller asked. Returns
    (root, [paths written])."""
    root = Path(target).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"{root}: not a directory")
    (root / DIR).mkdir(exist_ok=True)
    created = []
    config = root / CONFIG
    if not config.is_file():
        # Written out in full rather than as an empty object. This file is what a person
        # edits when they move state onto a faster disk, and a default they cannot see is
        # a default they do not know they may change.
        config.write_text(json.dumps(DEFAULTS, indent=2) + "\n", encoding="utf-8")
        created.append(config)
    ignore = root / DIR / ".gitignore"
    if not ignore.is_file():
        ignore.write_text(GITIGNORE, encoding="utf-8")
        created.append(ignore)
    for key in STATE:
        Path(resolve(str(root))[f"TROIKA_{key.upper()}"]).mkdir(parents=True, exist_ok=True)
    return root, created


def main():
    args = sys.argv[1:]
    if "--init" in args:
        i = args.index("--init")
        target = args[i + 1] if len(args) > i + 1 and not args[i + 1].startswith("-") else os.getcwd()
        root, created = init(target)
        for path in created:
            print(f"wrote {path}")
        print(f"workspace {root}" + ("" if created else " — already set up, nothing changed"))
        return 0
    start = None
    if "--from" in args:
        start = args[args.index("--from") + 1]
    out = resolve(start)
    if "--ensure" in args:
        for key in STATE:
            Path(out[f"TROIKA_{key.upper()}"]).mkdir(parents=True, exist_ok=True)
    if "--json" in args:
        print(json.dumps(out, indent=2))
    else:
        for key, value in out.items():
            print(f"export {key}={shlex.quote(value)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
