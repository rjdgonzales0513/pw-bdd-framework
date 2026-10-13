# 1. Core and apps layout

Date: 2026-10-09
Status: Accepted

## Context

The framework starts with one application under test: https://automationexercise.com (web UI
and REST API). Other applications are expected later, for example saucedemo and Salesforce.

Those applications have little in common. saucedemo and automationexercise are simple shops;
Salesforce has Lightning web components, shadow DOM, OAuth logins and a large REST/SOAP API.
With only one application built, we can't yet tell which code is truly shared. A "generic"
base page or API client written now would be shaped by one app and likely be wrong for the
next one.

But if app code is mixed into the framework from the start (a package named after the app,
app settings in the shared plugin), adding a second application later means untangling
everything.

## Decision

- One installable package (`qakit`, name not final) with two parts:
  - `qakit.core`: code that knows no application: the generic settings loader, the `--env`
    option, generic fixtures. It is the pytest plugin registered via the `pytest11` entry point.
  - `qakit.apps.<app>`: one package per application: its Settings class, API client, page
    objects and data factories.
- **Dependencies point one way: `apps` may import `core`; `core` never imports `apps`.**
- Per-app files sit in per-app folders: `envs/<app>/`, `tests/<app>/`.
- App fixtures (`settings`, API client, pages) live in `tests/<app>/conftest.py`, so pytest
  shows them only to that app's tests. One app is run with `pytest tests/<app> --env ci`.
- **No multi-app machinery is built ahead of time**: no `--app` option, no app registry, no
  abstract base classes without a second implementation. Code moves from an app package into
  `core` when a second app needs it (rule of three).

## Consequences

### Good

- Adding an application is additive: a new `apps/<app>/`, `envs/<app>/` and `tests/<app>/`,
  with no changes to the existing app.
- The core/apps boundary is visible in the folder structure and checkable in review (search for
  `apps` imports inside `core`).
- If teams later need separate release cycles, `core` can move to its own repository and be
  published as a package, with each app in its own test repository. The boundary already
  exists, so this is a move, not a rewrite.

### Bad / costs

- Slightly deeper paths and more folders than a single-app layout, for a benefit that may
  never come.
- Settings need a generic loader (`load_settings(settings_cls, ...)`) instead of one concrete
  function, since core can't know each app's Settings class.
- Test files with the same name in different app folders (`test_login.py`) clash under pytest's
  default import mode. We need `__init__.py` files in test folders or `--import-mode=importlib`.

## Alternatives considered

- **Single-app layout** (`src/shopkit/` with everything inside). Simplest now, but the package
  name and structure are tied to one app, and a second app means a large refactor.
- **Full multi-app framework now** (app registry, `--app` option, abstract base classes).
  Rejected: it designs for applications we haven't seen yet.
- **Separate repositories from day one** (core library + one test repo per app). Right for
  several teams, too much overhead for one person and one app.

## Update 2026-10-12: second application

saucedemo was added as `apps/saucedemo/`, `envs/saucedemo/` and `tests/saucedemo/`, with no
change to automationexercise. One thing moved into `core` because both apps needed it: the
per-app test id attribute (`test_id_attribute` fixture + `use_test_id_attribute()`). Ad
blocking, the user registry and the base page stay app-specific. The reporting plugin
(`core/reporting.py`) was app-agnostic from the start. See
[the guide on adding an application](../guide/08-adding-an-application.md).
