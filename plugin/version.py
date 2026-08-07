#!/usr/bin/env python3
"""The one version number, and the four manifests that have to agree with it.

A host identifies an installed plugin by name *and* version. Two manifests that
disagree install as two different plugins from the same tree, and only one of them
ever gets updated — so `VERSION` is the source and everything else is written from it.

    python3 plugin/version.py                # print the current version
    python3 plugin/version.py 0.2.0          # set it everywhere
    python3 plugin/version.py --check        # exit non-zero if anything disagrees
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = ROOT / "VERSION"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

# (path, how to read the version out of it, how to write it back in)
MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
)
MARKETPLACE = ".claude-plugin/marketplace.json"
# Marketplace files apply() does not write. Their entries carry no version today; one
# gaining a version key would rot silently outside the gate, so drift() rejects it until
# the key is either removed or brought under apply().
UNMANAGED = (
    ".cursor-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)


def current():
    return VERSION.read_text(encoding="utf-8").strip()


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def save(rel, payload):
    (ROOT / rel).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def declared():
    """Every place a version is written, as {where: value}."""
    out = {rel: load(rel).get("version") for rel in MANIFESTS}
    for entry in load(MARKETPLACE).get("plugins", []):
        out[f"{MARKETPLACE}#{entry.get('name')}"] = entry.get("version")
    return out


def drift():
    want = current()
    problems = []
    if not SEMVER.fullmatch(want):
        problems.append(f"VERSION: {want!r} is not strict semver — Codex rejects the plugin")
    for where, got in declared().items():
        if got != want:
            problems.append(f"{where}: version {got!r} != {want!r} in VERSION")
    for rel in UNMANAGED:
        if not (ROOT / rel).is_file():
            continue
        for entry in load(rel).get("plugins", []):
            if "version" in entry:
                problems.append(f"{rel}#{entry.get('name')}: has a version key this script "
                                "does not write — remove it or add the file to apply()")
    return problems


def apply(want):
    if not SEMVER.fullmatch(want):
        raise SystemExit(f"{want!r} is not strict semver (x.y.z)")
    VERSION.write_text(want + "\n", encoding="utf-8")
    for rel in MANIFESTS:
        payload = load(rel)
        payload["version"] = want
        save(rel, payload)
    payload = load(MARKETPLACE)
    for entry in payload.get("plugins", []):
        entry["version"] = want
    save(MARKETPLACE, payload)


def main():
    args = [a for a in sys.argv[1:] if a != "--check"]
    if "--check" in sys.argv:
        problems = drift()
        for p in problems:
            print(f"  {p}")
        return 1 if problems else 0
    if not args:
        print(current())
        return 0
    apply(args[0])
    print(f"version {args[0]} written to VERSION and {len(MANIFESTS) + 1} manifest(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
