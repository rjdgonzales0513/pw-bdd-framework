"""Products, search and cart in the browser."""

import pytest
from playwright.sync_api import expect

from qakit.apps.automationexercise.api.client import AutomationExerciseApi
from qakit.apps.automationexercise.pages import CartPage, ProductsPage

pytestmark = [pytest.mark.ui, pytest.mark.shopping]


@pytest.mark.smoke
def test_products_page_lists_the_catalogue(
    products_page: ProductsPage, ae_api: AutomationExerciseApi
) -> None:
    """The UI shows exactly as many products as the API returns."""
    expected = len(ae_api.products().products)  # an independent source for the count

    products_page.open()

    expect(products_page.all_products_heading).to_be_visible()
    expect(products_page.product_names).to_have_count(expected)


def test_search_shows_only_matching_products(
    products_page: ProductsPage, ae_api: AutomationExerciseApi
) -> None:
    """The UI search shows the same products as the API search, in the same order."""
    expected = [product.name for product in ae_api.search_products("jean").products]
    assert expected, "the API should know some jeans"

    products_page.open().search("jean")

    expect(products_page.searched_products_heading).to_be_visible()
    # to_have_text with a list: exactly these texts, in this order, retried until true.
    expect(products_page.product_names).to_have_text(expected)


def test_added_product_is_in_the_cart(products_page: ProductsPage, cart_page: CartPage) -> None:
    products_page.open()

    modal = products_page.add_to_cart("Blue Top")
    expect(modal.title).to_be_visible()
    modal.view_cart()

    expect(cart_page.product_names).to_have_text(["Blue Top"])


def test_removed_product_leaves_the_cart_empty(
    products_page: ProductsPage, cart_page: CartPage
) -> None:
    products_page.open().add_to_cart("Men Tshirt").view_cart()
    expect(cart_page.product_names).to_have_text(["Men Tshirt"])

    cart_page.remove("Men Tshirt")

    expect(cart_page.items).to_have_count(0)
    expect(cart_page.empty_message).to_be_visible()
