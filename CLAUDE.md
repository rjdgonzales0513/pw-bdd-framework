# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A learning project: a **from-scratch rebuild** of a senior-level Python Playwright framework.
It tests both the web UI and the REST API of https://automationexercise.com, and adds a BDD
layer with pytest-bdd.

The user is an experienced Java Selenium/Cucumber/RestAssured engineer. They already did an
11–12 week training in the sibling repo `..\python-playwright` (exercises ex01–ex18, a
`toolkit` framework against saucedemo, phases 1–5 done). This repo consolidates that work into
one framework, built properly from the start. Progress lives in `NOTES.md`.

## How we work (important)

- **The user writes every file.** Claude gives one milestone spec at a time (goal, target
  structure, Java comparisons, done-criteria), then reviews when asked ("review M3").
  Don't write framework code or tests unless the user explicitly asks. Give hints, explain
  failures, show Java side by side with Python (the user knows the concepts, not always the
  Python syntax).
- **Reviews:** run ruff, mypy and pytest; check the code does what the spec asks; check tests
  can fail (break the key action in a scratchpad copy, or ask the user to, and watch it go red).
  Ask 2–3 "why" questions about lines the user wrote.
- When the user says "save the session", update `NOTES.md` (Status, Next up, tips).

## Milestones

| # | Milestone | Practises | Done when |
| --- | --- | --- | --- |
| M0 | Project skeleton | src layout, pyproject, venv, ruff/mypy strict | `pytest` runs, quality gates pass, first commit |
| M1 | Config | pydantic Settings, `--env` option, session fixture, pytest plugin entry point | same tests run against `dev` or `ci` |
| M2 | API client | Playwright `APIRequestContext`, typed response models, `responseCode` check | API tests: products, search, verifyLogin, 405 |
| M3 | Test data | Faker factory + factory fixture with `yield` cleanup | a test creates 3 users, none left behind |
| M4 | Web layer | page objects, components, ad blocking via `page.route`, locator strategy | UI tests: signup, login, products, cart |
| M5 | Hybrid | create user via API, test via UI, delete via API; storage state | login test needs no UI signup |
| M6 | BDD | declarative features, steps reuse fixtures, tags, ADR | `pytest -m smoke` runs the journeys |
| M7 | CI | GitHub Actions, browser matrix, traces uploaded on failure | a deliberately red run gives a downloadable trace |

## Target layout

```
pyproject.toml            deps + pytest/ruff/mypy config
envs/                     dev.env, ci.env
src/shopkit/              the framework (pip install -e .)
    config.py             typed Settings
    api/                  client.py, models.py
    pages/                base page, components/, one class per page
    data/                 Faker factories
    plugin.py             all fixtures, registered via [project.entry-points.pytest11]
tests/
    api/  ui/             plain pytest tests
    bdd/features/         .feature files + step modules
docs/adr/                 decisions (port ADR 0001 on BDD from ../python-playwright/docs/adr/)
.github/workflows/ci.yml
```

## automationexercise.com API quirks (checked 2026-10-09)

- **HTTP status is always 200.** The real status is `responseCode` in the JSON body, e.g.
  `POST /api/productsList` gives `{"responseCode": 405, ...}`. The API client must check it,
  or every test passes.
- The JSON body is served as `Content-Type: text/html`; Playwright's `.json()` still parses it.
- Requests send **form fields**: Playwright `form=`, not `data=`/JSON.
- API list: https://automationexercise.com/api_list
- The UI shows ads and a consent dialog: block ad hosts with `page.route` (M4).

## Commands

Windows, Python 3.14 venv in `.venv` (activate THIS repo's venv, not python-playwright's).

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"; playwright install chromium
ruff check src tests; ruff format --check src tests
mypy src tests
pytest -v
```

## Conventions carried over from the training

- ruff line length 100, mypy `strict = true`; every `def` has a return type.
- Fixtures are requested by parameter name, never imported and called.
- Locators: role > label/placeholder/test id > CSS. Assert with `expect(...)`, never with
  `count()` / `is_visible()`.
- Never make a test green by changing the expected value: fix the cause.
- Gherkin is declarative (business actions, not clicks).
