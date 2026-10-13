"""Page objects for saucedemo.com. The app is small, so all pages live in one module.

The app conftest sets data-test as the test id attribute, so get_by_test_id("username")
means [data-test="username"]. Same rules as every page object: no assertions, locators
exposed for expect(), methods named after user actions.
"""

from typing import ClassVar, Self

from playwright.sync_api import Page

from qakit.apps.saucedemo.data.customers import Customer


class SauceDemoPage:
    """Base class: the Page, the header, and a path to open."""

    path: ClassVar[str] = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.get_by_test_id("title")  # "Products", "Your Cart", ...
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")  # the red number

    def open(self) -> Self:
        self.page.goto(self.path)
        return self

    def open_cart(self) -> None:
        self.cart_link.click()


class LoginPage(SauceDemoPage):
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()


class InventoryPage(SauceDemoPage):
    path = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.prices = page.get_by_test_id("inventory-item-price")
        self.sort = page.get_by_test_id("product-sort-container")

    def add_to_cart(self, product_name: str) -> None:
        # All cards -> the one containing the name -> its "Add to cart" button. No index.
        self.items.filter(has_text=product_name).get_by_role("button", name="Add to cart").click()

    def sort_by(self, value: str) -> None:
        """Sort by an <option> value: az, za, lohi or hilo."""
        self.sort.select_option(value)


class CartPage(SauceDemoPage):
    path = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")

    def checkout(self) -> None:
        self.checkout_button.click()


class CheckoutPage(SauceDemoPage):
    """Both checkout steps (/checkout-step-one.html and two) and the confirmation."""

    path = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.error = page.get_by_test_id("error")
        self.finish_button = page.get_by_test_id("finish")
        self.complete_header = page.get_by_test_id("complete-header")

    def fill_info(self, customer: Customer) -> None:
        self.first_name.fill(customer.first_name)
        self.last_name.fill(customer.last_name)
        self.postal_code.fill(customer.postal_code)
        self.continue_button.click()

    def finish(self) -> None:
        self.finish_button.click()
