# qakit: Playwright + pytest-bdd test framework

A Python test framework for **web UIs and REST APIs**, with **BDD** (Gherkin) on top of
plain pytest. It can test **several applications** from one code base. Every run produces an
**HTML report**, plus a Playwright **trace** for each failed test.

| | |
| --- | --- |
| Browser automation | [Playwright](https://playwright.dev/python/) (Chromium, Firefox, WebKit) |
| Test runner | [pytest](https://docs.pytest.org/) |
| BDD | [pytest-bdd](https://pytest-bdd.readthedocs.io/) (`.feature` files, Gherkin) |
| API testing | Playwright `APIRequestContext` + [pydantic](https://docs.pydantic.dev/) response models |
| Test data | [Faker](https://faker.readthedocs.io/) factories, created/deleted through the API |
| Config | `pydantic-settings`, one `.env` file per app and environment |
| Reporting | [pytest-html](https://pytest-html.readthedocs.io/) (self-contained), Cucumber JSON, Playwright traces |
| Quality gates | ruff (lint + format), mypy `--strict` |
| CI | GitHub Actions: quality → API → UI × browser matrix |

Applications covered today:

| App | What is tested | Test id attribute |
| --- | --- | --- |
| [automationexercise.com](https://automationexercise.com) | REST API, UI, BDD journeys, hybrid API+UI | `data-qa` |
| [saucedemo.com](https://www.saucedemo.com) | UI, BDD checkout | `data-test` |

## Quick start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
playwright install chromium

pytest --env dev                      # everything
start reports\report.html             # open the report
```

macOS/Linux: `source .venv/bin/activate`, then the same commands (`open reports/report.html`).

## Everyday commands

```powershell
pytest tests/automationexercise --env ci     # one app, one environment
pytest -m smoke                              # the must-pass set (Gherkin @smoke + plain tests)
pytest -m "api"                              # API tests only (no browser)
pytest -m "ui and not smoke"                 # marker expressions work
pytest tests/saucedemo/bdd -v                # one app's BDD scenarios
pytest -k "cart" --headed --slowmo 500       # watch tests that mention "cart"
pytest --browser firefox                     # another browser
playwright show-trace test-results/<test>/trace.zip   # replay a failed test

ruff check src tests; ruff format --check src tests; mypy src tests   # quality gates
```

## Project layout

```
src/qakit/
    core/                  knows no application (never imports from apps/)
        config.py          load_settings(SettingsClass, env, envs_dir)
        plugin.py          --env option, env fixtures, per-app test id attribute
        reporting.py       BDD steps + descriptions in the HTML report
    apps/
        automationexercise/
            config.py      typed settings (AE_*)
            api/           client.py (typed client), models.py (pydantic models)
            data/          users.py (Faker factory), registry.py (create + clean up)
            pages/         page objects, components/, ad_blocking.py
        saucedemo/         config.py, data/, pages/
envs/<app>/<env>.env       settings per app and environment (dev, ci)
tests/
    core/                  tests for the framework itself
    <app>/conftest.py      the app's fixtures (only that app's tests see them)
    <app>/api|ui/          plain pytest tests
    <app>/bdd/features/    .feature files; bdd/test_*.py hold the step definitions
docs/guide/                the framework guide (start here)
docs/adr/                  architecture decisions and why they were made
.github/workflows/ci.yml   the CI pipeline
```

## Documentation

Start with the **[framework guide](docs/guide/README.md)**:

1. [Architecture](docs/guide/01-architecture.md): layers, core vs apps, how a test runs
2. [Running tests](docs/guide/02-running-tests.md): options, environments, markers, debugging
3. [Writing BDD tests](docs/guide/03-writing-bdd-tests.md): features, steps, tags
4. [Page objects and locators](docs/guide/04-page-objects.md)
5. [API testing](docs/guide/05-api-testing.md)
6. [Test data and hybrid tests](docs/guide/06-test-data.md)
7. [Reports, traces and CI](docs/guide/07-reporting-and-ci.md)
8. [Adding an application](docs/guide/08-adding-an-application.md)
9. [Java → Python cheat sheet](docs/guide/09-java-to-python.md): for Selenium/Cucumber/RestAssured engineers
10. [Troubleshooting](docs/guide/10-troubleshooting.md)
