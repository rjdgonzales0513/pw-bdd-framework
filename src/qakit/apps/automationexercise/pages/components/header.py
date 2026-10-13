"""The navigation bar shown at the top of every page."""

from playwright.sync_api import Page


class Header:
    """Component object: used by composition from every page (``page_object.header``)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Scope to the <header> landmark (role "banner"): "Products" and "Cart" links also
        # appear lower on some pages. Link names start with an icon glyph, so match by
        # substring (Playwright's default, exact=False).
        bar = page.get_by_role("banner")
        self.home_link = bar.get_by_role("link", name="Home")
        self.products_link = bar.get_by_role("link", name="Products")
        self.cart_link = bar.get_by_role("link", name="Cart")
        self.signup_login_link = bar.get_by_role("link", name="Signup / Login")
        self.logout_link = bar.get_by_role("link", name="Logout")
        self.delete_account_link = bar.get_by_role("link", name="Delete Account")
        self.logged_in_as = bar.get_by_text("Logged in as")  # "Logged in as <name>"

    def go_to_products(self) -> None:
        self.products_link.click()

    def go_to_cart(self) -> None:
        self.cart_link.click()

    def go_to_signup_login(self) -> None:
        self.signup_login_link.click()

    def logout(self) -> None:
        self.logout_link.click()

    def delete_account(self) -> None:
        self.delete_account_link.click()
