"""qakit's pytest plugin: options and fixtures every app uses. Knows no application.

Registered via [project.entry-points.pytest11] in pyproject.toml, so pytest loads it
automatically in any project where qakit is installed (Java: META-INF/services + ServiceLoader).
Entry points are install metadata: after editing them, run pip install -e . again.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from playwright.sync_api import Playwright


# A hook: pytest calls it because of its exact name, there is no decorator or interface.
# A typo in the name (pytest_add_option) means it is silently never called.
# Runs once at startup, before the command line is parsed.
def pytest_addoption(parser: pytest.Parser) -> None:
    """Add ``--env``: which ``envs/<app>/<env>.env`` file to load."""
    # The group puts the option under a "qakit:" heading in pytest --help.
    group = parser.getgroup("qakit")
    group.addoption(
        "--env",
        default="dev",  # plain `pytest` runs against dev; CI passes --env ci explicitly
        # No choices=[...]: core doesn't know which envs each app has. load_settings checks
        # that envs/<app>/<env>.env exists, per app.
        help="environment to run against, e.g. dev or ci (default: dev)",
    )


# scope="session": built once per run and shared by every test (Java: a static field set in
# @BeforeAll, or a singleton bean). --env can't change mid-run, so once is enough.
# pytestconfig is a built-in fixture holding the run's configuration.
@pytest.fixture(scope="session")
def env_name(pytestconfig: pytest.Config) -> str:
    """The value of ``--env``."""
    # getoption returns Any; mypy strict rejects returning Any from a "-> str" function.
    # str(...) makes it a real str (Java: (String) config.get("env"), but checked at runtime).
    return str(pytestconfig.getoption("--env"))


@pytest.fixture(scope="session")
def envs_root(pytestconfig: pytest.Config) -> Path:
    """The ``envs/`` folder at the project root (pytest's rootdir, not the cwd)."""
    # rootpath is the folder with pyproject.toml, wherever pytest is started from.
    # Not Path.cwd() (breaks when run from a subfolder) and not Path(__file__) (points into
    # the installed package, wrong once qakit is installed without -e).
    return pytestconfig.rootpath / "envs"


# Playwright's default. Each app overrides this fixture in tests/<app>/conftest.py with the
# attribute its HTML uses (automationexercise: data-qa, saucedemo: data-test).
# Java: a default @Bean that an app's @Configuration replaces.
@pytest.fixture(scope="session")
def test_id_attribute() -> str:
    """The HTML attribute ``page.get_by_test_id(...)`` matches."""
    return "data-testid"


# A context manager: `with use_test_id_attribute(playwright, "data-qa"): ...` sets the
# attribute for the block and puts Playwright's default back afterwards, even on an error
# (Java: try-with-resources). @contextmanager turns a generator into one: the code before
# yield is the setup, the code after it the cleanup.
@contextmanager
def use_test_id_attribute(playwright: Playwright, attribute: str) -> Iterator[None]:
    """Point ``get_by_test_id`` at ``attribute`` inside the ``with`` block."""
    playwright.selectors.set_test_id_attribute(attribute)
    try:
        yield
    finally:
        playwright.selectors.set_test_id_attribute("data-testid")  # Playwright's default


# autouse=True: runs for every test without being asked for. The leading _ marks it internal.
# The attribute is a global Playwright setting, not a per-page one, so it is set again before
# EVERY test: when one run mixes apps, each test gets its own app's attribute.
# Session-scoped fixtures run BEFORE this one (wider scopes are set up first), so a session
# fixture that uses get_by_test_id must wrap its work in use_test_id_attribute().
@pytest.fixture(autouse=True)
def _apply_test_id_attribute(playwright: Playwright, test_id_attribute: str) -> Iterator[None]:
    """Point ``get_by_test_id`` at this app's attribute for the duration of one test."""
    with use_test_id_attribute(playwright, test_id_attribute):
        yield
