"""What every automationexercise page has: the Page, the header, and a path to open it."""

from typing import ClassVar, Self

from playwright.sync_api import Page

from qakit.apps.automationexercise.pages.components import Header


class BasePage:
    """Base class for page objects.

    Rules for every page object (checked in review):
      1. No assertions. Pages expose Locators and do user actions; the test decides what is
         correct with expect(locator). expect retries, a value read once doesn't.
      2. Methods are user actions in the page's language: add_to_cart("Blue Top"),
         not click_button_3().
      3. Locators: role > label/placeholder/test id (data-qa here) > CSS.
    """

    # ClassVar: belongs to the class, not each instance (Java: static final String PATH).
    # Subclasses override it; open() uses it. Relative: the context's base_url adds the host.
    path: ClassVar[str] = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)  # composition: this.header = new Header(page);

    def open(self) -> Self:
        """Navigate straight to this page. Returns self so calls can chain."""
        # Self: "the class this is called on", so LoginPage(page).open() is typed LoginPage.
        self.page.goto(self.path)
        return self
