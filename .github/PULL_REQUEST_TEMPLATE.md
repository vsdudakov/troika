## What changed

<!-- One paragraph. What this changes, and for whom. -->

## Why

<!-- The problem. For a rule change: what it now rejects that it did not before. -->

## Evidence

- [ ] `make check` is green
- [ ] `make test-check` is green
- [ ] Behavioural change? Catch rates before and after (`make test RUNS=5`) pasted below
- [ ] New gate? A case that plants exactly the defect it claims to catch

```
<!-- paste the diff of before.txt / after.txt, or "no behavioural change" -->
```

## Checklist

- [ ] Nothing in `agents/` or `skills/` names a repo, command, tracker, URL or person
- [ ] No hardcoded paths — the resolved `$TROIKA_*` variables only
- [ ] Generated files regenerated (`python3 plugin/generate.py`), not hand-edited
- [ ] New profile anchor? Added to `AGENTS.template.md` in this same change
