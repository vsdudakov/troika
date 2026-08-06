# Contributing to Troika

Issues and pull requests are welcome.

```bash
git clone https://github.com/vsdudakov/troika
cd troika
make check        # structural gate — no model, no spend
make test-check   # behavioural fixtures — no model, no spend
```

Both must be green before you open a pull request. There is nothing to install: the gates run
on a bare `python3`.

**Behavioural changes carry catch rates.** If you change a role's rules or a procedure's
gates, run the behavioural suite on both revisions and put the numbers in the pull request —
that diff is the only evidence that matters for a prompt change.

```bash
python3 tests/run.py --runs 5 > /tmp/before.txt   # on main
python3 tests/run.py --runs 5 > /tmp/after.txt    # on your branch
diff /tmp/before.txt /tmp/after.txt
```

House rules, the full guide, and how to add a role or a skill:
**<https://vsdudakov.github.io/troika/contributing/>**

By contributing you agree that your contributions are licensed under the [MIT
Licence](LICENSE.md).
