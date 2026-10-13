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

Since M1 I ask for the code one file at a time ("file 1", "file 2", ...), with comments and
Java comparisons, already tested by Claude in a scratchpad. I type it and run the gates.

**2026-10-12: switched to pair programming with Claude driving.** I asked Claude to finish the
whole framework (multi-app, BDD, reporting, docs). I review the code to understand it, and
can take the keyboard back at any time.

## Status (2026-10-12)

- **M0–M1 done** (commits `f8e5278`, `a2f8616`).
- **M2–M7 built by Claude on 2026-10-12, NOT committed yet.** Gates green; `pytest --env ci`:
  53 passed (core 3, AE API 15, AE UI 10, AE BDD 9, AE config 9, saucedemo 7). `-m smoke` = 8.
  - M2 API client: `api/client.py` (`send()` raw, typed methods check `responseCode`, `ApiError`),
    `api/models.py`; tests in `tests/automationexercise/api/`.
  - M3 data: `data/users.py` (`build_user`, uuid emails), `data/registry.py` (`UserRegistry`,
    deletes on close); fixtures `user_factory`, `registered_user`, `new_user`.
  - M4 web: `pages/` (BasePage, Header, CartModal, Login/Signup/Products/Cart/Home),
    `ad_blocking.py` (allow only own host, via an overridden `new_context` fixture).
  - M5 hybrid: users via API; `shopper` + `shopper_state` (session, UI login once,
    storage state) + `logged_in_page`.
  - M6 BDD: `account.feature`, `shopping.feature` (+ saucedemo `checkout.feature`);
    ADR 0002.
  - M7 CI: `.github/workflows/ci.yml` (quality → api → ui × chromium/firefox, reports always,
    traces on failure). Not run on GitHub yet.
  - Extra: second app **saucedemo**; core gained `test_id_attribute` + `use_test_id_attribute`;
    reporting plugin `core/reporting.py` (pytest-html + Cucumber JSON), ADR 0003;
    `docs/guide/` (10 pages) + README.md.
- Mutants checked (all went red): client ignores responseCode; registry never deletes;
  reporting drops failed steps (it survived at first, and the test was tightened); cart
  remove does nothing.
- Bug found while building: session fixtures run BEFORE function autouse fixtures, so
  `shopper_state` couldn't use `get_by_test_id` → `use_test_id_attribute()` context manager.

## Next up

1. Review the code, layer by layer, in this order: `core/plugin.py` + `core/reporting.py` →
   `api/` → `data/` → `pages/` → `tests/automationexercise/conftest.py` → tests → `bdd/`.
   Ask Claude "why" about anything unclear. Read `docs/guide/` alongside.
2. Commit in logical pieces, gates first (Claude can do it when asked), e.g.
   "Add API client with responseCode check", "Add user factory with API cleanup",
   "Add page objects and UI tests", "Add BDD journeys", "Add saucedemo app",
   "Add HTML reporting", "Add CI workflow", "Add framework guide".
3. Push and watch CI; then break a UI test on purpose and download its trace (M7 done-criterion).
4. Optional: `.gitattributes` with `* text=auto eol=lf`; pytest-xdist for parallel runs
   (`logged_in_page` shares one session: check that's still safe).

## Open review questions (not answered yet)

- M0: `ruff format` compared with `ruff check`: what does each catch? (Hint: the blank first
  line compared with the missing final newline.) How should CI keep a 0-test run from
  passing? Why `pip install -e .` and not `pip install .`?
- M2: why is `api_request_context` session-scoped? Why does `send()` not raise on a bad code
  while `products()` does? What does `all([])` return, and which test would lie without a
  non-empty check? Why `extra="forbid"` on the models?

## Answered (M1)

- Fixture scope decides how often it is rebuilt, not whether it runs: a fixture only runs
  when something asks for it by name. Without `scope="session"` everything still passes, but
  in M2 a session-scoped API fixture depending on `settings` would give `ScopeMismatch`.
- The override test can't use `settings`: that session fixture is built and cached before the
  test's `monkeypatch.setenv` runs.
- `rootpath`, not `cwd`: `cd tests\automationexercise; pytest` broke the cwd version
  (6 failed, 1 error) and the rootpath version passed.

## Tips

- Copying a pom/pyproject from an old project: every line you can't explain is a bug waiting.
- Add a dependency when the code needs it, not before.
- Commit messages describe the change in the imperative ("Add typed config with --env
  option"), one idea per commit, never "updates docs and configurations".
- Run the gates BEFORE `git commit`, not after: `a2f8616` went in red.
- A green run can lie: 0 tests collected, a conftest.py in `src/` that is never loaded, a
  fixture nobody uses, `all([])` on an empty list. Make the test fail once on purpose.
- A test must compare against an independent source: `settings.env_name == env_name` passed
  even when `env_name` ignored `--env`; comparing with `pytestconfig.getoption("--env")` caught it.
- Tests must not depend on the machine: clear `AE_*` env vars with `monkeypatch.delenv`.
- After renaming a package: `pip uninstall <old name>`, then `pip install -e ".[dev]"` again
  (entry points are install metadata).
- `pydantic.v1` is the old API; always import `BaseSettings` from `pydantic_settings`.
- Only ONE `py.typed`, in the top package; every package folder needs `__init__.py`.
- automationexercise API: HTTP status is always 200, the real code is `responseCode`; a search
  with no match returns 200 with `products: []`.
