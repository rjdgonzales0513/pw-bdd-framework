# Rebuild notes: where I left off

Sibling training repo (exercises, old `toolkit` framework, explainers):
`..\python-playwright` — its notes are in `exercises/01_core/NOTES.md`.
Quest log: https://claude.ai/artifact/XLPCBsgWBpa83R5GUb2J5Z
Playwright cheat sheet: https://claude.ai/code/artifact/0d88d395-686e-4d76-9b49-dfeba6e73ccc
Fixtures, closures and stars explainer: https://claude.ai/artifact/JnZdKZLiTDoT9fJZqq98Bu

## Why this repo (2026-10-09)

After finishing Phase 5 (BDD) in python-playwright, I paused Phase 6 to rebuild everything
from scratch in one framework: web UI + real API on automationexercise.com, with pytest-bdd.
Claude gives one milestone spec at a time (M0–M7, see CLAUDE.md); I write every file and ask
for a review. M7 (CI + traces on failure) replaces the p6-artifacts quest.

## Status (2026-10-09)

M0 half done: venv (Python 3.14.4), `git init`, `.gitignore`, `pyproject.toml`.
No commit yet. `src/` is empty, no `tests/`, nothing installed in the venv.

First M0 review, things to fix in `pyproject.toml`:

- DELETE `[project.entry-points.pytest11] toolkit = "toolkit.plugin"`. Copied from the old
  repo; there is no such module, so pytest would crash at startup after `pip install -e .`.
  It comes back in M1 as `shopkit = "shopkit.plugin"`.
- `[tool.setuptools.package-data]`: key `toolkit` -> `shopkit`, keep only `py.typed` for now.
- Python version: `requires-python`, ruff `target-version` and mypy `python_version` say 3.12,
  the venv is 3.14. Make all three 3.14 (`>=3.14`, `py314`, `3.14`).
- Remove `httpx`: the API layer uses Playwright's `APIRequestContext`.
- `.gitignore`: the comment about "public saucedemo demo login" is stale.

Good already: `.gitignore` with Java comparisons and saved login state ignored, `pydantic`
listed explicitly, a strong ruff `select` list, the `pydantic.mypy` plugin.

## Next up

1. Fix the items above.
2. Create `src/shopkit/__init__.py` and an empty `src/shopkit/py.typed`.
3. Write `tests/test_smoke.py`: import `shopkit`, assert one trivial thing.
4. Activate THIS repo's venv, then `pip install -e ".[dev]"` and `playwright install chromium`.
5. Run the gates, commit, and ask "review M0":
   ```powershell
   ruff check src tests; ruff format --check src tests
   mypy src tests
   pytest -v
   ```
6. Be ready to answer: what does `py.typed` change for mypy? Why `pip install -e .` and not
   `pip install .`?

## Tips

- Copying a pom/pyproject from an old project: every line you can't explain is a bug waiting.
- Add a dependency when the code needs it, not before.
- Commit messages describe the change ("Add project skeleton"), not "adding notes".
