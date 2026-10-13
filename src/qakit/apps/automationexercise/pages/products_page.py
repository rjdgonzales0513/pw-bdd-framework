"""https://automationexercise.com/products: the product list and the search box."""

from playwright.sync_api import Locator, Page

from qakit.apps.automationexercise.pages.base_page import BasePage
from qakit.apps.automationexercise.pages.components import CartModal


class ProductsPage(BasePage):
    path = "/products"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.all_products_heading = page.get_by_role("heading", name="All Products")
        self.searched_products_heading = page.get_by_role("heading", name="Searched Products")
        self.search_box = page.get_by_placeholder("Search Product")
        # The search button holds only an icon: no text, label or test id to find it by.
        self.search_button = page.locator("#submit_search")
        # Each card shows the product twice: once in the card (.productinfo) and once in a
        # hover overlay. Always look inside .productinfo, or every name counts twice.
        self.cards = page.locator(".product-image-wrapper")
        self.product_names = self.cards.locator(".productinfo p")
        self.cart_modal = CartModal(page)

    def search(self, term: str) -> None:
        self.search_box.fill(term)
        self.search_button.click()

    def card(self, product_name: str) -> Locator:
        """The card of one product, found by its exact name."""
        # has=: keep cards that contain an element with exactly this text (Java: a
        # findElements filter on a child). exact=True: "Blue Top" must not match "Top".
        return self.cards.filter(has=self.page.get_by_text(product_name, exact=True))

    def add_to_cart(self, product_name: str) -> CartModal:
        """Click the product's "Add to cart"; returns the dialog that opens."""
        self.card(product_name).locator(".productinfo").get_by_text("Add to cart").click()
        return self.cart_modal
