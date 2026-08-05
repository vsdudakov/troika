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

HARNESS_TIMEOUT caps a single run in seconds (default 600); a run that overruns counts
as a miss rather than hanging the suite.
"""

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LLM = ROOT.parent
FIXTURES = ROOT / "fixtures"
CASES = ROOT / "cases"
DEFAULT_CMD = "claude -p --model claude-fable-5 --effort high"
DEFAULT_TIMEOUT = 600

SEVERITIES = ("Blocker", "Major", "Nit")
# The verdict labels agents/reviewer.md § Output actually defines. "Block" is not one of
# them, and adding it would substring-match every "**Blocker**" finding line.
VERDICTS = ("Approve with nits", "Request changes", "Approve")


# --- fixtures ---------------------------------------------------------------

def unquote(value: str) -> str:
    """Drop one layer of YAML quoting. Without this a keyword written `"n + 1"` is matched
    against replies with its quotes attached and can never hit."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_expect(case: Path) -> dict:
    """Minimal YAML subset: scalars, inline lists, nested one level, > folded blocks."""
    spec: dict = {}
    stack = [(-1, spec)]
    lines = (case / "expect.yaml").read_text(encoding="utf-8").splitlines()
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
            node[key] = [unquote(x) for x in value[1:-1].split(",") if x.strip()]
        elif value == "null":
            node[key] = None
        else:
            node[key] = unquote(value)
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
    return (own if own.is_file() else CASES / "_base" / "work-log.md").read_text(encoding="utf-8")


def build_prompt(case: Path, spec: dict, diff: str) -> str:
    """Exactly what the role receives per its Inputs section: profile, role file,
    skill, plan, the dev role's work log, and the diff."""
    read = lambda p: p.read_text(encoding="utf-8")
    parts = [
        ("PROJECT PROFILE (AGENTS.md)", read(FIXTURES / "AGENTS.md")),
        (f"ROLE ({spec['role']}.md)", read(LLM / "agents" / f"{spec['role']}.md")),
        (f"SKILL ({spec['skill']}.md)", read(LLM / "skills" / f"{spec['skill']}.md")),
        ("PLAN ($WS/llm/scratchpad/plans/TOY-1.md)", read(FIXTURES / "plan.md")),
        ("WORK LOG ($WS/llm/scratchpad/plans/TOY-1-backend-dev.md)", work_log(case)),
        ("DIFF UNDER REVIEW (git diff, new files staged with add -N)", diff),
    ]
    body = "\n\n".join(f"===== {name} =====\n{text}" for name, text in parts)
    return (
        body
        + "\n\n===== TASK =====\n"
        + f"Act as the {spec['role']} role and run {spec['skill']} on the diff above.\n"
        + "You cannot execute anything. The work log's Verification section is the only\n"
        + "evidence that the profile's commands were run; judge it against the profile.\n"
        + "Reply with the reviewer output format only — the check rows, the Findings\n"
        + "section, and the Verdict line. No preamble, no explanation outside it.\n"
    )


# --- grading ----------------------------------------------------------------

def as_list(value) -> list:
    """A spec may write one label or several; the grader only ever wants the list form."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def label_in(line: str) -> str:
    """Longest label present, because `Approve with nits` contains `Approve`."""
    return max((v for v in VERDICTS if v in line), key=len, default="")


def is_finding(line: str) -> bool:
    return bool(re.search(r"\*\*(Blocker|Major|Nit)\*\*", line))


def verdict_of(reply: str) -> str:
    """The label under the `### Verdict` heading, else the last non-finding line carrying
    one. Skipping finding lines matters: a reply that omits the verdict must read as absent,
    not borrow the label out of a finding."""
    lines = reply.strip().splitlines()
    for i, line in enumerate(lines):
        if re.match(r"#{1,6}\s+Verdict\b", line.strip()):
            # `### Verdict: Approve` carries the label on the heading itself; the template's
            # `### Verdict` puts it on the line below.
            return label_in(line) or next((label_in(l) for l in lines[i + 1:] if l.strip()), "")
    for line in reversed(lines):
        if not is_finding(line) and label_in(line):
            return label_in(line)
    return ""


def grade(reply: str, spec: dict) -> tuple[bool, str]:
    want_verdict = as_list(spec.get("verdict"))
    got = verdict_of(reply)
    verdict_ok = got in want_verdict

    findings = [l for l in reply.splitlines() if is_finding(l)]

    want = spec.get("expect_finding")
    if want is None:
        forbidden = [s for s in as_list(spec.get("forbid_severity"))
                     if any(f"**{s}**" in l for l in findings)]
        if forbidden:
            return False, f"false positive: raised {'/'.join(forbidden)} on a clean diff"
        return (verdict_ok, "ok" if verdict_ok else f"verdict {got or '?'} not in {want_verdict}")

    # `file: any` — the finding is real but its citation is not predictable (it may name
    # the work log, a plan section, or nothing). Severity plus keywords carry those.
    wanted_file = want.get("file", "any")
    in_file = (lambda _l: True) if wanted_file == "any" else \
        (lambda l: wanted_file.split("/")[-1] in l)

    # A list where reviewer.md pins no single severity and more than one gating rating is
    # defensible; a scalar where it pins one, so a downgrade is still a miss.
    wanted_sev = as_list(want["severity"])
    sev_label = "/".join(wanted_sev)

    hits = [
        l for l in findings
        if any(f"**{s}**" in l for s in wanted_sev)
        and in_file(l)
        and any(k.lower() in l.lower() for k in want["keywords_any"])
    ]
    if not hits:
        near = [l for l in findings if in_file(l)]
        if near:
            return False, f"found it but not as {sev_label}: {near[0].strip()[:90]}"
        return False, f"missed: no {sev_label} on {wanted_file}"
    if not verdict_ok:
        return False, f"caught it but verdict was {got or '?'}, expected {want_verdict}"
    return True, "ok"


# --- driver -----------------------------------------------------------------

def run_agent(cmd: str, prompt: str, timeout: int) -> tuple:
    """Run one agent in its own process group.

    `shell=True` plus `subprocess.run(timeout=...)` kills the shell and nothing under it, so
    a hung agent survives its own timeout and keeps spending. Killing the group takes the
    whole tree down. Raises TimeoutExpired once the group is gone.
    """
    proc = subprocess.Popen(cmd, shell=True, text=True, start_new_session=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    try:
        out, err = proc.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        else:
            proc.kill()
        proc.communicate()
        raise
    return proc.returncode, out, err


def env_timeout() -> int:
    raw = os.environ.get("HARNESS_TIMEOUT", "")
    return int(raw) if raw.isdigit() else DEFAULT_TIMEOUT


def check_spec(spec: dict) -> list:
    """A typo in a severity or verdict label makes a case unpassable, and only shows up
    after a paid run — so catch it here instead."""
    problems = []
    for v in as_list(spec.get("verdict")):
        if v not in VERDICTS:
            problems.append(f"verdict '{v}' is not one of {list(VERDICTS)}")
    for s in as_list(spec.get("forbid_severity")):
        if s not in SEVERITIES:
            problems.append(f"forbid_severity '{s}' is not one of {list(SEVERITIES)}")
    # A role or skill named here that does not exist crashes the run at prompt-build time,
    # after the other cases have already been paid for.
    for field, folder in (("role", "agents"), ("skill", "skills")):
        name = spec.get(field)
        if not name:
            problems.append(f"no {field} named")
        elif not (LLM / folder / f"{name}.md").is_file():
            problems.append(f"{field} '{name}' has no {folder}/{name}.md")
    want = spec.get("expect_finding")
    if not want:
        return problems
    for s in as_list(want.get("severity")):
        if s not in SEVERITIES:
            problems.append(f"severity '{s}' is not one of {list(SEVERITIES)}")
    if not want.get("severity"):
        problems.append("expect_finding needs severity")
    if not want.get("keywords_any"):
        problems.append("expect_finding needs keywords_any")
    return problems


def check_fixtures() -> int:
    problems = []
    if not (FIXTURES / "repo" / "app").is_dir():
        problems.append("fixtures/repo missing")
    profile = (FIXTURES / "AGENTS.md").read_text(encoding="utf-8")
    anchors = set(re.findall(r'<a id="([^"]+)"', profile))
    needed = set()
    for f in list((LLM / "agents").glob("*.md")) + list((LLM / "skills").glob("*.md")):
        for _, target in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", f.read_text(encoding="utf-8")):
            path, _, frag = target.partition("#")
            if frag and path.endswith("AGENTS.md"):
                needed.add(frag)
    for miss in sorted(needed - anchors):
        problems.append(f"fixtures/AGENTS.md lacks #{miss} — a role would read a dead link")
    for case in sorted(CASES.iterdir()):
        if not case.is_dir() or case.name.startswith("_"):
            continue
        try:
            spec = load_expect(case)
        except Exception as exc:
            problems.append(f"{case.name}/expect.yaml unparseable: {exc}")
            continue
        problems += [f"{case.name}/expect.yaml: {p}" for p in check_spec(spec)]
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
    ap.add_argument("--timeout", type=int, default=env_timeout(),
                    help="seconds per run before it counts as a miss")
    args = ap.parse_args()

    if args.runs < 1:
        ap.error("--runs must be at least 1")

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
            try:
                code, out, err = run_agent(cmd, prompt, args.timeout)
            except subprocess.TimeoutExpired:
                notes.append(f"agent exceeded {args.timeout}s; process group killed")
                continue
            if code != 0:
                notes.append(f"agent exited {code}: {(err or '').strip()[:120]}")
                continue
            ok, why = grade(out, spec)
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
