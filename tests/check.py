#!/usr/bin/env python3
"""Structural checks for the agents/ and skills/ trees.

The anchors this tree links into the project profile are a contract
(harness/README.md); so are the file shapes in agents/README.md and skills/README.md.
Nothing here validates prose — only the things that break silently.

    python3 tests/check.py        # exits non-zero on any failure

Companion to run.py: this one asks whether the tree is structurally intact, run.py asks
whether a gate still catches what it claims to. Neither needs a model.
"""

import glob
import os
import re
import sys
from pathlib import Path

# Runnable from anywhere; every path below is relative to the repo root.
os.chdir(Path(__file__).resolve().parent.parent)

FAIL = []
# These files are read several times over; the tree is small enough to hold all of it.
TEXT = {}
# The one path outside this repo that a role is allowed to link to: the workspace profile,
# a sibling of the repo root. Absent in CI, so it cannot be checked by existence.
PROFILE = os.path.join(os.pardir, "AGENTS.md")


def fail(where, msg):
    FAIL.append(f"{where}: {msg}")


def text_of(path):
    if path not in TEXT:
        TEXT[path] = Path(path).read_text(encoding="utf-8")
    return TEXT[path]


def links_in(path):
    return re.findall(r"\[([^\]]*)\]\(([^)]+)\)", text_of(path))


def anchors_of(path):
    """Every fragment a markdown link can resolve to in `path`."""
    text = text_of(path)
    found = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        found.add(re.sub(r"[^\w\s-]", "", heading).strip().lower().replace(" ", "-"))
    return found


def role_and_skill_files():
    return sorted(glob.glob("agents/*.md") + glob.glob("skills/*.md"))


def body_files():
    return [f for f in role_and_skill_files() if not f.endswith("README.md")]


# --- 1. every link resolves, in-tree and out ---------------------------------

def check_links():
    cache = {}
    for f in role_and_skill_files():
        for _, target in links_in(f):
            if target.startswith(("http", "mailto")):
                continue
            path, _, frag = target.partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
            if not os.path.exists(resolved):
                # The workspace profile lives outside this repo and is absent in CI, so it
                # is exempt from the existence check — but only at the one depth that is
                # correct. Matching on the basename alone would wave through `../AGENTS.md`
                # from `skills/`, which is exactly the dead link this check exists to catch.
                if resolved == PROFILE:
                    continue
                if os.path.basename(resolved) == "AGENTS.md":
                    fail(f, f"{target} resolves to {resolved}, not the profile at {PROFILE}")
                    continue
                fail(f, f"dead link {target}")
                continue
            if not frag:
                continue
            if resolved not in cache:
                cache[resolved] = anchors_of(resolved)
            if frag not in cache[resolved]:
                fail(f, f"dead anchor {target}")


# --- 2. profile anchors exist in the template, not just this workspace --------

def check_profile_anchors():
    template = "AGENTS.template.md"
    if not os.path.exists(template):
        fail(template, "missing — the profile contract cannot be verified")
        return
    known = anchors_of(template)
    for f in role_and_skill_files():
        for _, target in links_in(f):
            path, _, frag = target.partition("#")
            if not frag or os.path.basename(path) != "AGENTS.md":
                continue
            if frag not in known:
                fail(f, f"#{frag} is not an anchor in {template}; a fresh workspace reads a dead link")


# --- 3. the nine checks are duplicated by hand in three files ----------------

def same_check(item, rule):
    """The copies abbreviate — "tests present" for "Tests" — so compare by prefix."""
    return item.startswith(rule) or rule.startswith(item)


def check_sequence(where, items, rules, what):
    """Order is part of the contract, not just membership: a reviewer works down its rule
    list and fills the output rows in the order it reads them, and a copy that reorders
    them silently pairs the wrong evidence with the wrong row."""
    if len(items) != len(rules):
        fail(where, f"{what} has {len(items)} entries; agents/reviewer.md defines {len(rules)}")
        return
    for i, (item, rule) in enumerate(zip(items, rules), 1):
        if not same_check(item, rule):
            fail(where, f"{what} entry {i} is '{item}'; agents/reviewer.md rule {i} is '{rule}'")


def check_duplicated_enumerations():
    reviewer = text_of("agents/reviewer.md")
    rules = [r.lower() for r in re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", reviewer, re.M)]

    inline = {}
    for f in ("skills/internal-review.md", "skills/pr-review.md"):
        m = re.search(r"reviewer › Rules\]\([^)]+\):\s*(.+?)\.$", text_of(f), re.M)
        if not m:
            fail(f, "no inline copy of the reviewer check list found")
            continue
        inline[f] = [x.strip().lower() for x in m.group(1).split(",")]

    if len(set(map(tuple, inline.values()))) > 1:
        fail("skills/", "internal-review.md and pr-review.md list the reviewer checks differently")

    for f, items in inline.items():
        check_sequence(f, items, rules, "inline check list")

    # the output template must carry one row per rule, in the order the rules are stated
    rows = [r.lower() for r in re.findall(r"^- ([A-Z][A-Za-z ]+): <Pass", reviewer, re.M)]
    check_sequence("agents/reviewer.md", rows, rules, "output template")


# --- 4. file shapes declared in the two READMEs -----------------------------

AGENT_SECTIONS = ["Scope", "Inputs", "Rules", "Gates", "Output"]
MODEL_SUBS = ["Claude", "Codex", "Why"]
MODEL_SUBS_OPTIONAL = ["Raise it when", "Drop it when", "Also"]


def check_agent_shape():
    for f in sorted(glob.glob("agents/*.md")):
        if f.endswith("README.md"):
            continue
        text = text_of(f)
        body = re.sub(r"```.*?```", "", text, flags=re.S)  # fenced examples are not sections
        sections = re.findall(r"^## (.+)$", body, re.M)
        if sections != AGENT_SECTIONS:
            fail(f, f"sections {sections} != {AGENT_SECTIONS}")
        header = re.findall(r"^- \*\*(Owns|Runs|Model)\*\*", text, re.M)
        if header != ["Owns", "Runs", "Model"]:
            fail(f, f"header list {header} != ['Owns', 'Runs', 'Model']")
        # Only the bullets nested under **Model**, not every two-space bullet in the file:
        # a nested list anywhere else is legal prose, and reporting it as a Model sub-bullet
        # would fail the build with the wrong reason.
        block = re.search(r"^- \*\*Model\*\*.*?(?=^\S|\Z)", text, re.M | re.S)
        sub = re.findall(r"^  - \*\*([A-Za-z ]+)\*\*", block.group(0) if block else "", re.M)
        if sub[:3] != MODEL_SUBS:
            fail(f, f"Model sub-bullets start {sub[:3]} != {MODEL_SUBS}")
        # An undeclared sub-bullet is drift the README does not describe.
        for extra in [s for s in sub[3:] if s not in MODEL_SUBS_OPTIONAL]:
            fail(f, f"Model sub-bullet '{extra}' is not one of {MODEL_SUBS_OPTIONAL}")


def check_skill_shape():
    for f in sorted(glob.glob("skills/*.md")):
        if f.endswith("README.md"):
            continue
        text = text_of(f)
        kind = re.search(r"\*\*Kind\*\* (\w+)", text)
        if not kind:
            fail(f, "no **Kind** declared")
        elif kind.group(1) not in ("procedure", "reference", "template"):
            fail(f, f"unknown Kind '{kind.group(1)}'")
        for field in ("Used by", "When", "Ends with"):
            if f"**{field}**" not in text:
                fail(f, f"header line missing **{field}**")


def check_frontmatter():
    for f in body_files():
        m = re.match(r"---\nname: (\S+)\ndescription: (.+)\n", text_of(f))
        if not m:
            fail(f, "frontmatter must open with name: then description:")
            continue
        if m.group(1) != os.path.basename(f)[:-3]:
            fail(f, f"frontmatter name '{m.group(1)}' != filename")


# --- 5. house style ---------------------------------------------------------

def check_style():
    for f in role_and_skill_files():
        for i, line in enumerate(text_of(f).splitlines(), 1):
            if re.search(r"[^\s]—[^\s]", line):
                fail(f, f"line {i}: em dash needs spaces around it")


def main():
    check_links()
    check_profile_anchors()
    check_duplicated_enumerations()
    check_agent_shape()
    check_skill_shape()
    check_frontmatter()
    check_style()

    if FAIL:
        print(f"{len(FAIL)} problem(s):\n")
        for f in FAIL:
            print(f"  {f}")
        return 1
    print(f"ok — {len(role_and_skill_files())} files, no structural problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
