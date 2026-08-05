#!/usr/bin/env python3
"""Fault injection for the agent harness.

Each case plants one known defect in a toy repo and asserts the gate that claims to
catch it actually does. The claim under test is not "the model is good" — it is
"a defect of type X is caught at gate Y, with severity Z". That is falsifiable.

    python3 tests/run.py --dry-run           # print the prompt, spend nothing
    python3 tests/run.py --runs 5            # real runs, report catch rate
    python3 tests/run.py --case clean        # one case
    python3 tests/run.py --check             # fixtures only, no model

Models are stochastic, so a single run proves nothing: --runs 5 and read the rate.
Compare rates across two versions of agents/ and skills/ to measure a prompt change.

The agent command is configurable; it must accept a prompt on stdin and write the
role's reply to stdout:

    HARNESS_CMD='claude -p --model claude-fable-5 --effort high'  python3 tests/run.py
    HARNESS_CMD='codex exec -m gpt-5.6-sol -'                     python3 tests/run.py
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LLM = ROOT.parent
FIXTURES = ROOT / "fixtures"
CASES = ROOT / "cases"
DEFAULT_CMD = "claude -p --model claude-fable-5 --effort high"

SEVERITIES = ("Blocker", "Major", "Nit")


# --- fixtures ---------------------------------------------------------------

def load_expect(case: Path) -> dict:
    """Minimal YAML subset: scalars, inline lists, nested one level, > folded blocks."""
    spec: dict = {}
    stack = [(-1, spec)]
    lines = (case / "expect.yaml").read_text().splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        key, _, value = raw.strip().partition(":")
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        node = stack[-1][1]
        if value == ">":
            folded = []
            while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                folded.append(lines[i].strip())
                i += 1
            node[key] = " ".join(folded)
        elif value == "":
            node[key] = {}
            stack.append((indent, node[key]))
        elif value.startswith("["):
            node[key] = [x.strip() for x in value[1:-1].split(",") if x.strip()]
        elif value == "null":
            node[key] = None
        else:
            node[key] = value
    return spec


def apply_overlay(overlay: Path, dest: Path) -> None:
    for src in overlay.rglob("*"):
        if src.is_file():
            out = dest / src.relative_to(overlay)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)


def build_worktree(case: Path, spec: dict, dest: Path) -> str:
    """Toy repo, then _base (a correct implementation of the plan), then the case's delta.

    Every case is the clean diff plus exactly one planted defect, so a miss is the gate
    failing rather than the diff being ambiguous. That is why the shared implementation
    lives in _base and each case directory holds only what it changes.
    """
    shutil.copytree(FIXTURES / "repo", dest,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    run = lambda *a: subprocess.run(a, cwd=dest, check=True, capture_output=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "add", "-A")
    run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base tree")

    apply_overlay(CASES / "_base" / "files", dest)
    if (case / "files").is_dir():
        apply_overlay(case / "files", dest)
    for rel in spec.get("remove", []):
        (dest / rel).unlink(missing_ok=True)

    run("git", "add", "-N", "--", ".")  # untracked files must enter the diff
    return subprocess.run(["git", "--no-pager", "diff"], cwd=dest,
                          capture_output=True, text=True).stdout


def work_log(case: Path) -> str:
    """The dev role's handoff file. A case overrides it when its defect changes what
    the dev role would honestly have reported — otherwise the log would itself be a
    second planted defect, and a miss would not say which one the gate caught."""
    own = case / "work-log.md"
    return (own if own.is_file() else CASES / "_base" / "work-log.md").read_text()


def build_prompt(case: Path, spec: dict, diff: str) -> str:
    """Exactly what the role receives per its Inputs section: profile, role file,
    skill, plan, the dev role's work log, and the diff."""
    parts = [
        ("PROJECT PROFILE (AGENTS.md)", (FIXTURES / "AGENTS.md").read_text()),
        (f"ROLE ({spec['role']}.md)", (LLM / "agents" / f"{spec['role']}.md").read_text()),
        (f"SKILL ({spec['skill']}.md)", (LLM / "skills" / f"{spec['skill']}.md").read_text()),
        ("PLAN ($WS/llm/scratchpad/plans/TOY-1.md)", (FIXTURES / "plan.md").read_text()),
        ("WORK LOG ($WS/llm/scratchpad/plans/TOY-1-backend-dev.md)", work_log(case)),
        ("DIFF UNDER REVIEW (git diff, new files staged with add -N)", diff),
    ]
    body = "\n\n".join(f"===== {name} =====\n{text}" for name, text in parts)
    return (
        body
        + "\n\n===== TASK =====\n"
        + f"Act as the {spec['role']} role and run {spec['skill']} on the diff above.\n"
        + "The verification command is the profile's lint command; assume it passes.\n"
        + "Reply with the reviewer output format only — the check rows, the Findings\n"
        + "section, and the Verdict line. No preamble, no explanation outside it.\n"
    )


# --- grading ----------------------------------------------------------------

def grade(reply: str, spec: dict) -> tuple[bool, str]:
    verdict_line = ""
    for line in reversed(reply.strip().splitlines()):
        if any(v in line for v in ("Approve", "Request changes", "Block")):
            verdict_line = line
            break

    want_verdict = spec.get("verdict", [])
    # "Approve with nits" contains "Approve"; match the longest label present.
    got = max((v for v in ("Approve with nits", "Request changes", "Approve", "Block")
               if v in verdict_line), key=len, default="")
    verdict_ok = got in want_verdict

    findings = [l for l in reply.splitlines() if re.search(r"\*\*(Blocker|Major|Nit)\*\*", l)]

    want = spec.get("expect_finding")
    if want is None:
        forbidden = [s for s in spec.get("forbid_severity", [])
                     if any(f"**{s}**" in l for l in findings)]
        if forbidden:
            return False, f"false positive: raised {'/'.join(forbidden)} on a clean diff"
        return (verdict_ok, "ok" if verdict_ok else f"verdict {got or '?'} not in {want_verdict}")

    # `file: any` — the finding is real but its citation is not predictable (it may name
    # the work log, a plan section, or nothing). Severity plus keywords carry those.
    wanted_file = want.get("file", "any")
    in_file = (lambda _l: True) if wanted_file == "any" else \
        (lambda l: wanted_file.split("/")[-1] in l)

    hits = [
        l for l in findings
        if f"**{want['severity']}**" in l
        and in_file(l)
        and any(k.lower() in l.lower() for k in want["keywords_any"])
    ]
    if not hits:
        near = [l for l in findings if in_file(l)]
        if near:
            return False, f"found it but not as {want['severity']}: {near[0].strip()[:90]}"
        return False, f"missed: no {want['severity']} on {wanted_file}"
    if not verdict_ok:
        return False, f"caught it but verdict was {got or '?'}, expected {want_verdict}"
    return True, "ok"


# --- driver -----------------------------------------------------------------

def check_fixtures() -> int:
    problems = []
    if not (FIXTURES / "repo" / "app").is_dir():
        problems.append("fixtures/repo missing")
    profile = (FIXTURES / "AGENTS.md").read_text()
    anchors = set(re.findall(r'<a id="([^"]+)"', profile))
    needed = set()
    for f in list((LLM / "agents").glob("*.md")) + list((LLM / "skills").glob("*.md")):
        for _, target in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", f.read_text()):
            path, _, frag = target.partition("#")
            if frag and path.endswith("AGENTS.md"):
                needed.add(frag)
    for miss in sorted(needed - anchors):
        problems.append(f"fixtures/AGENTS.md lacks #{miss} — a role would read a dead link")
    for case in sorted(CASES.iterdir()):
        if case.is_dir() and not case.name.startswith("_"):
            try:
                load_expect(case)
            except Exception as exc:
                problems.append(f"{case.name}/expect.yaml unparseable: {exc}")
    for p in problems:
        print(f"  {p}")
    print(f"{'FAIL' if problems else 'ok'} — fixtures, {len(needed)} profile anchors required")
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", help="case name; repeatable")
    ap.add_argument("--runs", type=int, default=1, help="runs per case (models are stochastic)")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, call nothing")
    ap.add_argument("--check", action="store_true", help="validate fixtures only")
    args = ap.parse_args()

    if args.check:
        return check_fixtures()

    names = args.case or sorted(c.name for c in CASES.iterdir()
                                if c.is_dir() and not c.name.startswith("_"))
    cmd = os.environ.get("HARNESS_CMD", DEFAULT_CMD)
    results, failed = {}, False

    for name in names:
        case = CASES / name
        spec = load_expect(case)
        with tempfile.TemporaryDirectory() as tmp:
            diff = build_worktree(case, spec, Path(tmp) / "toyapp")
            prompt = build_prompt(case, spec, diff)

        if args.dry_run:
            print(f"===== {name} — {len(prompt)} chars, ~{len(prompt)//4} tokens =====")
            print(prompt)
            continue

        caught, notes = 0, []
        for _ in range(args.runs):
            proc = subprocess.run(cmd, shell=True, input=prompt,
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                notes.append(f"agent exited {proc.returncode}: {proc.stderr.strip()[:120]}")
                continue
            ok, why = grade(proc.stdout, spec)
            caught += ok
            if not ok:
                notes.append(why)

        rate = caught / args.runs
        results[name] = rate
        mark = "PASS" if rate == 1 else ("FLAKY" if rate else "FAIL")
        if rate < 1:
            failed = True
        print(f"{mark:6} {name:32} {caught}/{args.runs}")
        for n in dict.fromkeys(notes):
            print(f"       {n}")

    if results:
        overall = sum(results.values()) / len(results)
        print(f"\ncatch rate {overall:.0%} across {len(results)} case(s), {args.runs} run(s) each")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
