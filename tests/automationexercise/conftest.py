"""Fixtures for automationexercise tests. pytest finds this file by its name and shows its
fixtures only to tests in this folder and below, so other apps never see them.

This is the one place that knows both core and the app and wires them together
(Java: a Spring @Configuration class). Sections:
    config      settings, test id attribute
    api         api_request_context, ae_api
    test data   user_factory, registered_user, new_user
    browser     browser_context_args, new_context (ad blocking + timeout), page objects
    hybrid      shopper, shopper_state, logged_in_page (logged in without the login form)
"""

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright, expect

from qakit.apps.automationexercise.api.client import AutomationExerciseApi
from qakit.apps.automationexercise.config import AutomationExerciseSettings
from qakit.apps.automationexercise.data.registry import UserRegistry
from qakit.apps.automationexercise.data.users import NewUser, build_user
from qakit.apps.automationexercise.pages import (
    CartPage,
    HomePage,
    LoginPage,
    ProductsPage,
    SignupPage,
)
from qakit.apps.automationexercise.pages.ad_blocking import allow_only_own_host
from qakit.core.config import load_settings
from qakit.core.plugin import use_test_id_attribute

# --- config ---------------------------------------------------------------------------------


# Session-scoped: the file is read once per run. env_name and envs_root are session
# fixtures from qakit.core.plugin; a fixture may only depend on fixtures with the same
# or a wider scope.
# Tests that change env vars with monkeypatch must call load_settings themselves:
# this fixture is built before they run and is never rebuilt.
@pytest.fixture(scope="session")
def settings(env_name: str, envs_root: Path) -> AutomationExerciseSettings:
    """The settings for the env chosen with ``--env``."""
    return load_settings(AutomationExerciseSettings, env_name, envs_root / "automationexercise")


# Overrides core's fixture of the same name: this site marks elements with data-qa="...".
@pytest.fixture(scope="session")
def test_id_attribute() -> str:
    return "data-qa"


# --- api ------------------------------------------------------------------------------------


# Session-scoped: one HTTP client (its connection pool and cookies) for the whole run.
# yield splits setup from teardown (Java: @BeforeAll ... @AfterAll in one method). The code
# after yield runs once the last test using it is done, even when tests failed.
@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright, settings: AutomationExerciseSettings
) -> Iterator[APIRequestContext]:
    """Playwright's HTTP client, pointed at the site (Java: a RestAssured RequestSpecification)."""
    context = playwright.request.new_context(
        base_url=str(settings.base_url), timeout=settings.timeout_ms
    )
    yield context
    context.dispose()  # closes connections; the client never disposes what it didn't create


@pytest.fixture(scope="session")
def ae_api(api_request_context: APIRequestContext) -> AutomationExerciseApi:
    """The typed API client."""
    return AutomationExerciseApi(api_request_context)


# --- test data ------------------------------------------------------------------------------


# `faker` is a fixture from Faker's own pytest plugin, reseeded to 0 for every test, so
# names and addresses repeat run after run and a failure reproduces with the same data.
@pytest.fixture
def user_factory(ae_api: AutomationExerciseApi, faker: Faker) -> Iterator[UserRegistry]:
    """Create users with ``user_factory.create()``; all are deleted after the test."""
    with UserRegistry(ae_api, faker) as users:
        yield users


@pytest.fixture
def registered_user(user_factory: UserRegistry) -> NewUser:
    """A user that already exists (created through the API) and is deleted afterwards."""
    return user_factory.create()


@pytest.fixture
def new_user(user_factory: UserRegistry, faker: Faker) -> NewUser:
    """A user that does NOT exist yet, for signup tests. Deleted afterwards if it was created."""
    return user_factory.track(build_user(faker))


# --- browser --------------------------------------------------------------------------------


# Overrides pytest-playwright's fixture: the options every new browser context starts with.
# The parameter is the ORIGINAL fixture (same name); we copy its dict and add base_url,
# so page.goto("/login") means <base_url>/login.
@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], settings: AutomationExerciseSettings
) -> dict[str, Any]:
    return {**browser_context_args, "base_url": str(settings.base_url)}


def _prepare(context: BrowserContext, settings: AutomationExerciseSettings) -> None:
    """What every context for this site needs: no ads, and the env's timeout."""
    allow_only_own_host(context, settings.base_url.host or "")
    context.set_default_timeout(settings.timeout_ms)


# Overrides pytest-playwright's `new_context` factory. Its `context` and `page` fixtures are
# built on top of it, so they get ad blocking too, and so does every context a test creates
# itself (logged_in_page below). Tracing and screenshots keep working: we wrap, not replace.
@pytest.fixture
def new_context(
    new_context: Callable[..., BrowserContext], settings: AutomationExerciseSettings
) -> Callable[..., BrowserContext]:
    def create(**kwargs: Any) -> BrowserContext:
        context = new_context(**kwargs)
        _prepare(context, settings)
        return context

    return create


# Page objects. They don't navigate: the test or step calls .open() when it needs to.
@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def signup_page(page: Page) -> SignupPage:
    return SignupPage(page)


@pytest.fixture
def products_page(page: Page) -> ProductsPage:
    return ProductsPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


# --- hybrid: API for setup, UI for the test, storage state to skip the login form ----------


@pytest.fixture(scope="session")
def shopper(ae_api: AutomationExerciseApi) -> Iterator[NewUser]:
    """One user for the whole run, created through the API and deleted at the end."""
    # Faker() and not the `faker` fixture: that one is function-scoped, and a session
    # fixture can't depend on a narrower scope (pytest raises ScopeMismatch).
    with UserRegistry(ae_api, Faker()) as users:
        yield users.create()


@pytest.fixture(scope="session")
def shopper_state(
    browser: Browser,
    browser_context_args: dict[str, Any],
    settings: AutomationExerciseSettings,
    shopper: NewUser,
    playwright: Playwright,
    test_id_attribute: str,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Log the shopper in through the UI ONCE per run and save the cookies to a file.

    Java/Selenium: log in once, save driver.manage().getCookies(), add them to every new
    driver. Playwright saves cookies + localStorage in one call: storage_state().
    """
    context = browser.new_context(**browser_context_args)
    _prepare(context, settings)
    # Session fixtures run before core's per-test autouse fixture that sets data-qa, so this
    # one sets it for itself (LoginPage finds its fields with get_by_test_id).
    with use_test_id_attribute(playwright, test_id_attribute):
        page = context.new_page()
        LoginPage(page).open().login(shopper.email, shopper.password)
        # A fixture may check its own setup: if login failed, stop here with a clear message
        # instead of letting every logged-in test fail later for an unclear reason.
        expect(HomePage(page).header.logged_in_as).to_contain_text(shopper.name)
    state_file = tmp_path_factory.mktemp("auth") / "shopper.json"
    context.storage_state(path=state_file)
    context.close()
    return state_file


@pytest.fixture
def logged_in_page(new_context: Callable[..., BrowserContext], shopper_state: Path) -> Page:
    """A page that is already logged in as ``shopper``: no login form, no signup.

    The session is SHARED by every test that uses this fixture: never log out or delete the
    account with it. Tests that do that use registered_user + the login form instead.
    """
    return new_context(storage_state=shopper_state).new_page()
