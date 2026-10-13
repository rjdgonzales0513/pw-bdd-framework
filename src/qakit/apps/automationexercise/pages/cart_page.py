"""https://automationexercise.com/view_cart"""

from playwright.sync_api import Page

from qakit.apps.automationexercise.pages.base_page import BasePage


class CartPage(BasePage):
    path = "/view_cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # One table row per product. The table has no accessible name, so its id scopes it.
        self.items = page.locator("#cart_info_table tbody tr")
        # Each row names its product in a level-4 heading.
        self.product_names = self.items.get_by_role("heading", level=4)
        self.empty_message = page.get_by_text("Cart is empty!")

    def remove(self, product_name: str) -> None:
        """Click the row's delete (x) icon; the row disappears without a page reload."""
        # The x is an icon-only link, so CSS is the only handle.
        self.items.filter(has_text=product_name).locator(".cart_quantity_delete").click()
