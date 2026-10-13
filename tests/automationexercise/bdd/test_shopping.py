"""Step definitions for features/shopping.feature.

Who is shopping decides which browser page the steps use: a logged-in shopper gets the saved
login (logged_in_page), a guest a fresh page. The Given step returns that page as the
`shopper_page` fixture, and every later step builds its page objects on it.
"""

from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from qakit.apps.automationexercise.api.client import AutomationExerciseApi
from qakit.apps.automationexercise.pages import CartPage, ProductsPage

scenarios("features/shopping.feature")


@given("a logged-in shopper", target_fixture="shopper_page")
def _(logged_in_page: Page) -> Page:
    return logged_in_page


@given("a guest shopper", target_fixture="shopper_page")
def _(page: Page) -> Page:
    return page


# parsers.parse pulls {product} out of the step text and passes it as the `product` argument
# (Java: Cucumber expression "a guest shopper with {string} in the cart").
@given(parsers.parse('a guest shopper with "{product}" in the cart'), target_fixture="shopper_page")
def _(page: Page, product: str) -> Page:
    ProductsPage(page).open().add_to_cart(product).continue_shopping()
    return page


@when(parsers.parse('the shopper adds "{product}" to the cart'))
def _(shopper_page: Page, product: str) -> None:
    ProductsPage(shopper_page).open().add_to_cart(product).continue_shopping()


@when(parsers.parse('the shopper removes "{product}" from the cart'))
def _(shopper_page: Page, product: str) -> None:
    CartPage(shopper_page).open().remove(product)


@when(parsers.parse('the shopper searches for "{term}"'))
def _(shopper_page: Page, term: str) -> None:
    ProductsPage(shopper_page).open().search(term)


@then(parsers.parse('the cart contains "{product}"'))
def _(shopper_page: Page, product: str) -> None:
    cart = CartPage(shopper_page).open()
    # Contains, not "is exactly": the logged-in shopper's session (and cart) is shared by
    # every scenario that uses it, so other products may be there too.
    expect(cart.product_names.filter(has_text=product)).to_have_count(1)


@then("the cart is empty")
def _(shopper_page: Page) -> None:
    cart = CartPage(shopper_page)
    expect(cart.items).to_have_count(0)
    expect(cart.empty_message).to_be_visible()


@then(parsers.parse('the products matching "{term}" are shown'))
def _(shopper_page: Page, ae_api: AutomationExerciseApi, term: str) -> None:
    # The API is the independent source of truth for what the search should find.
    expected = [product.name for product in ae_api.search_products(term).products]
    assert expected, f"the catalogue has nothing for {term!r}: pick another example"
    expect(ProductsPage(shopper_page).product_names).to_have_text(expected)
