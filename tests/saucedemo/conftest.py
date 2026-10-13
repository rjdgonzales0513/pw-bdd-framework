"""Fixtures for saucedemo tests: the same shape as tests/automationexercise/conftest.py.

Compare the two files: settings, test_id_attribute and browser_context_args follow one
pattern; everything else is what this app needs. Nothing in qakit.core had to change to
add this app.
"""

from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page

from qakit.apps.saucedemo.config import SauceDemoSettings
from qakit.apps.saucedemo.pages import CartPage, CheckoutPage, InventoryPage, LoginPage
from qakit.core.config import load_settings


@pytest.fixture(scope="session")
def settings(env_name: str, envs_root: Path) -> SauceDemoSettings:
    """The settings for the env chosen with ``--env``."""
    return load_settings(SauceDemoSettings, env_name, envs_root / "saucedemo")


@pytest.fixture(scope="session")
def test_id_attribute() -> str:
    return "data-test"  # this site marks elements with data-test="..."


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], settings: SauceDemoSettings
) -> dict[str, Any]:
    return {**browser_context_args, "base_url": str(settings.base_url)}


@pytest.fixture
def login_page(page: Page, settings: SauceDemoSettings) -> LoginPage:
    page.set_default_timeout(settings.timeout_ms)
    return LoginPage(page)


@pytest.fixture
def inventory_page(login_page: LoginPage, settings: SauceDemoSettings) -> InventoryPage:
    """Logged in as the standard user, on the products page."""
    login_page.open().login(settings.username, settings.password.get_secret_value())
    return InventoryPage(login_page.page)


@pytest.fixture
def cart_page(inventory_page: InventoryPage) -> CartPage:
    return CartPage(inventory_page.page)


@pytest.fixture
def checkout_page(inventory_page: InventoryPage) -> CheckoutPage:
    return CheckoutPage(inventory_page.page)
