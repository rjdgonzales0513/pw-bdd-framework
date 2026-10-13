"""Step definitions for features/checkout.feature (saucedemo)."""

from faker import Faker
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from qakit.apps.saucedemo.data.customers import build_customer
from qakit.apps.saucedemo.pages import CartPage, CheckoutPage, InventoryPage

scenarios("features/checkout.feature")


@given(parsers.parse('a logged-in shopper with "{product}" in the cart'))
def _(inventory_page: InventoryPage, product: str) -> None:
    inventory_page.add_to_cart(product)


@when("the shopper checks out as a generated customer")
def _(cart_page: CartPage, checkout_page: CheckoutPage, faker: Faker) -> None:
    cart_page.open().checkout()
    checkout_page.fill_info(build_customer(faker))
    checkout_page.finish()


# <field> from the Examples table is filled into the step text first, then parsed out.
@when(parsers.parse("the shopper checks out without a {field}"))
def _(cart_page: CartPage, checkout_page: CheckoutPage, faker: Faker, field: str) -> None:
    cart_page.open().checkout()
    # **{field: ""}: a dict spread into keyword arguments -> build_customer(faker, last_name="").
    checkout_page.fill_info(build_customer(faker, **{field: ""}))


@then(parsers.parse('the order is confirmed with "{message}"'))
def _(checkout_page: CheckoutPage, message: str) -> None:
    expect(checkout_page.complete_header).to_have_text(message)


@then(parsers.parse('the shopper is told "{message}"'))
def _(checkout_page: CheckoutPage, message: str) -> None:
    expect(checkout_page.error).to_have_text(message)
