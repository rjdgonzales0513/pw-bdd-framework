"""The "Added!" dialog that opens after "Add to cart"."""

from playwright.sync_api import Page


class CartModal:
    def __init__(self, page: Page) -> None:
        self.page = page
        # The dialog is a Bootstrap modal without an ARIA role, so its id is the only stable
        # handle (CSS is the last resort in our locator order, used when nothing better exists).
        self.root = page.locator("#cartModal")
        self.title = self.root.get_by_role("heading", name="Added!")
        self.view_cart_link = self.root.get_by_role("link", name="View Cart")
        self.continue_button = self.root.get_by_role("button", name="Continue Shopping")

    def view_cart(self) -> None:
        self.view_cart_link.click()

    def continue_shopping(self) -> None:
        self.continue_button.click()
