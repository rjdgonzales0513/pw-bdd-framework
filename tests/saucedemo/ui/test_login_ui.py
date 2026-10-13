"""Login and the product list on saucedemo.com."""

import pytest
from playwright.sync_api import expect

from qakit.apps.saucedemo.config import SauceDemoSettings
from qakit.apps.saucedemo.pages import InventoryPage, LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.account]


@pytest.mark.smoke
def test_standard_user_sees_the_products(inventory_page: InventoryPage) -> None:
    """The standard user lands on the product list after logging in."""
    expect(inventory_page.title).to_have_text("Products")
    expect(inventory_page.items).to_have_count(6)


def test_locked_out_user_is_refused(login_page: LoginPage, settings: SauceDemoSettings) -> None:
    login_page.open().login("locked_out_user", settings.password.get_secret_value())

    expect(login_page.error).to_have_text("Epic sadface: Sorry, this user has been locked out.")


def test_sorting_by_price_low_to_high(inventory_page: InventoryPage) -> None:
    inventory_page.sort_by("lohi")

    # all_inner_texts() reads the values once, AFTER expect has waited for the list: safe
    # here because the sort is synchronous. "$7.99" -> 7.99.
    expect(inventory_page.prices).to_have_count(6)
    prices = [float(text.removeprefix("$")) for text in inventory_page.prices.all_inner_texts()]
    assert prices == sorted(prices)
