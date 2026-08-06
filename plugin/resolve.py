#!/usr/bin/env python3
"""Resolves the workspace a role is standing in, and the paths it writes to.

Roles run with their cwd inside a worktree, several levels below the workspace, and the
troika itself may be a plugin in a host's cache rather than a folder beside them. So
neither end of a path can be assumed: this walks up from cwd to the workspace that owns
the run, and prints the four paths every role uses.

    eval "$(python3 plugin/resolve.py)"     # exports TROIKA_WORKSPACE and the TROIKA_* paths
    python3 plugin/resolve.py --json        # same, machine-readable
    python3 plugin/resolve.py --ensure      # also create the state directories

The workspace is the nearest ancestor holding `.troika.json`; failing that, the nearest
holding both `AGENTS.md` and a `troika/` directory. The second condition matters — repos
carry their own `AGENTS.md`, and a walk that stopped at the first one found would resolve
a worktree as the workspace and scatter handoff files through it.
"""

import json
import os
import shlex
import sys
from pathlib import Path

CONFIG = ".troika.json"
# Relative to the workspace root, and overridable one by one in .troika.json. The defaults
# are the layout of a plain clone, so a workspace that never writes the file behaves exactly
# as it did before there was one.
DEFAULTS = {
    "profile": "AGENTS.md",
    "home": "troika",
    "scratchpad": "troika/scratchpad",
    "worktrees": "troika/worktrees",
    "memory": "troika/memory",
}
# The three the roles write into. `home` is read-only (the Troika tree itself) and
# `profile` is a file, so neither is created.
STATE = ("scratchpad", "worktrees", "memory")


def find_workspace(start):
    """(root, config path or None). Raises SystemExit with a diagnosis when there is none."""
    for d in [start, *start.parents]:
        if (d / CONFIG).is_file():
            return d, d / CONFIG
    for d in [start, *start.parents]:
        if (d / "AGENTS.md").is_file() and (d / "troika").is_dir():
            return d, None
    raise SystemExit(
        f"no workspace above {start}: expected a {CONFIG}, or an AGENTS.md beside a troika/ "
        f"directory. Write {CONFIG} at the workspace root — see troika/plugin/README.md."
    )


def load(config):
    if config is None:
        return {}
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
    root, config = find_workspace(Path(start or os.getcwd()).resolve())
    payload = load(config)
    out = {"TROIKA_WORKSPACE": str(root)}
    for key, default in DEFAULTS.items():
        value = payload.get(key, default)
        if not isinstance(value, str) or not value:
            raise SystemExit(f"{config}: {key} must be a non-empty string")
        # An absolute value wins outright: state can live outside the workspace, which is
        # the point of the file for anyone whose troika is a cached plugin.
        path = Path(value).expanduser()
        out[f"TROIKA_{key.upper()}"] = str(path if path.is_absolute() else root / path)
    return out


def main():
    args = sys.argv[1:]
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
