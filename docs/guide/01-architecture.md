# 1. Architecture

## The big picture

qakit is **one installable package** (`pip install -e .`) with two halves:

- **`qakit.core`** knows no application. It holds the settings loader, the `--env` option,
  the test id mechanism and the reporting plugin. It is loaded automatically as a **pytest
  plugin** (a `pytest11` entry point in `pyproject.toml`).
- **`qakit.apps.<app>`**, one package per application under test. It holds that app's
  settings class, API client, page objects and test data factories.

The tests live outside the package, in `tests/<app>/`. Each app's `conftest.py` wires core
and app together into fixtures.

```mermaid
flowchart TB
    subgraph tests["tests/ (what you write most)"]
        F[".feature files<br/>Gherkin"] --> S["step definitions<br/>bdd/test_*.py"]
        P["plain pytest tests<br/>api/ ui/"]
        C["tests/&lt;app&gt;/conftest.py<br/>fixtures: settings, api client,<br/>users, pages, logged-in page"]
        S --> C
        P --> C
    end
    subgraph apps["src/qakit/apps/&lt;app&gt;/"]
        PO["pages/<br/>page objects + components"]
        API["api/<br/>client + pydantic models"]
        D["data/<br/>Faker factories + registry"]
        CFG["config.py<br/>typed settings"]
    end
    subgraph core["src/qakit/core/ (knows no app)"]
        L["config.py<br/>load_settings()"]
        PL["plugin.py<br/>--env, test id attribute"]
        R["reporting.py<br/>BDD steps in HTML report"]
    end
    C --> PO & API & D & CFG
    C --> L
    CFG -.->|loaded by| L
    PW["Playwright<br/>browser + HTTP"]
    PO --> PW
    API --> PW
```

**Dependencies point one way:** tests → apps → core. `core` never imports from `apps`. You
can check that with a search: `grep -r "qakit.apps" src/qakit/core` must find nothing.

## Layers, top to bottom

| Layer | Lives in | Knows about | Example |
| --- | --- | --- | --- |
| Feature | `tests/<app>/bdd/features/*.feature` | business language only | `When the shopper logs in` |
| Step definition | `tests/<app>/bdd/test_*.py` | fixtures, page objects | `login_page.open().login(...)` |
| Plain test | `tests/<app>/api/`, `ui/` | fixtures, page objects, API client | `test_search_finds_matching_products` |
| Fixtures | `tests/<app>/conftest.py` | everything of one app + core | `registered_user`, `logged_in_page` |
| Page objects / API client / data | `src/qakit/apps/<app>/` | Playwright, the app's HTML and API | `ProductsPage.add_to_cart()` |
| Core | `src/qakit/core/` | pytest, Playwright, pytest-html, pytest-bdd | `load_settings()` |

## What happens when you run a BDD scenario

Take `Scenario: A registered shopper logs in` from
`tests/automationexercise/bdd/features/account.feature`:

```mermaid
sequenceDiagram
    autonumber
    participant Py as pytest
    participant Fx as fixtures (conftest.py)
    participant St as step definitions
    participant API as AutomationExerciseApi
    participant UI as LoginPage (browser)
    Py->>Fx: settings ← envs/automationexercise/ci.env (once per run)
    Py->>Fx: test id attribute = data-qa (per test)
    St->>Fx: Given a registered shopper → registered_user
    Fx->>API: POST /api/createAccount (Faker data)
    St->>UI: When the shopper logs in → login_page.open().login(email, password)
    St->>UI: Then the shopper is welcomed by name → expect(header.logged_in_as)
    Py->>Fx: teardown: user registry
    Fx->>API: DELETE /api/deleteAccount
    Py->>Py: report: Feature > Scenario + every step's status
```

Points to notice:

- The **step definitions contain no setup code**. "A registered shopper" is just the
  `registered_user` fixture: created through the API before the step, deleted after the test.
- The **browser is only started if a step asks for a page**. API-only tests never start one.
- **Teardown always runs**, even when a step fails, because cleanup lives after `yield` in a
  fixture.

## Fixture scopes used

| Fixture | Scope | Why |
| --- | --- | --- |
| `env_name`, `envs_root`, `settings` | session | `--env` can't change during a run |
| `api_request_context`, `ae_api` | session | one HTTP client, reused |
| `shopper`, `shopper_state` | session | log in through the UI once, reuse the cookies |
| `browser` (pytest-playwright) | session | starting a browser is slow |
| `context`, `page`, page objects | function | every test gets a clean browser context |
| `user_factory`, `registered_user`, `new_user` | function | each test owns its users and cleans them up |

A fixture can only use fixtures with the **same or a wider** scope. A session fixture asking
for a function fixture fails with `ScopeMismatch`.

## Why this layout?

See [ADR 0001](../adr/0001-core-and-apps-layout.md). In short:

- Adding an app is **additive**: new `apps/<app>/`, `envs/<app>/`, `tests/<app>/`, and nothing
  else changes. saucedemo was added this way.
- Code moves into `core` only when a **second app needs it**. The test id attribute mechanism
  went into `core` because both apps needed it. Ad blocking stayed in automationexercise,
  because only that site shows ads.
