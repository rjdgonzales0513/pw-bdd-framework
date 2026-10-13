# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A Python Playwright test framework (package `qakit`) with a BDD layer on pytest-bdd.
It tests two applications: https://automationexercise.com (REST API + UI + BDD) and
https://www.saucedemo.com (UI + BDD).

A `core` package knows no app; each app has its own package under `apps/`. Code moves into
`core` only when a second app needs it; see `docs/adr/0001-core-and-apps-layout.md`.
The guide for engineers is `docs/guide/` (start at `docs/guide/README.md`).

## Layout (as built, 2026-10-12)

```
pyproject.toml                    deps, pytest addopts (reports, traces), markers, ruff/mypy
envs/<app>/                       dev.env, ci.env  (automationexercise: AE_*, saucedemo: SD_*)
src/qakit/
    core/                         knows no app; never imports from apps/
        config.py                 load_settings(settings_cls, env, envs_dir)
        plugin.py                 --env, env_name, envs_root, test_id_attribute (+ autouse apply)
        reporting.py              pytest11 plugin: BDD steps + Description in pytest-html
    apps/automationexercise/      config.py, api/ (client, models), data/ (users, registry),
                                  pages/ (base, pages, components/, ad_blocking.py)
    apps/saucedemo/               config.py, data/customers.py, pages/pages.py
tests/
    core/test_reporting.py        unit + pytester test of the reporting plugin
    <app>/conftest.py             app fixtures (settings, test id, browser args, pages, data)
    <app>/api/ ui/                plain pytest tests
    <app>/bdd/features/*.feature  + bdd/test_*.py (scenarios() + step definitions)
docs/guide/                       framework guide, 10 pages (README.md is the index)
docs/adr/                         0001 layout, 0002 BDD, 0003 reporting
.github/workflows/ci.yml          quality -> api -> ui x [chromium, firefox]; artifacts
```

## automationexercise.com API quirks (checked 2026-10-09)

- **HTTP status is always 200.** The real status is `responseCode` in the JSON body, e.g.
  `POST /api/productsList` gives `{"responseCode": 405, ...}`. The API client must check it,
  or every test passes.
- The JSON body is served as `Content-Type: text/html`; Playwright's `.json()` still parses it.
- Requests send **form fields**: Playwright `form=`, not `data=`/JSON.
- API list: https://automationexercise.com/api_list
- The UI shows ads and a consent dialog: `pages/ad_blocking.py` allows only the site's own host.
- `createAccount` answers responseCode **201**; a wrong password on verifyLogin is 404.
- Product cards render every product twice (hover overlay): scope locators to `.productinfo`.

## Commands

Windows, Python 3.14 venv in `.venv`.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"; playwright install chromium
ruff check src tests; ruff format --check src tests
mypy src tests
pytest -v
pytest tests/automationexercise --env ci     # one app, one environment
```

## Conventions

- ruff line length 100, mypy `strict = true`; every `def` has a return type.
- Fixtures are requested by parameter name, never imported and called.
- `core` never imports from `apps`. App fixtures live in `tests/<app>/conftest.py`, so they are
  visible only to that app's tests.
- Locators: role > label/placeholder/test id > CSS. Assert with `expect(...)`, never with
  `count()` / `is_visible()`.
- Never make a test green by changing the expected value: fix the cause.
- Gherkin is declarative (business actions, not clicks).
- Check a new test can fail: break the key action (in a scratchpad copy) and watch it go red.
