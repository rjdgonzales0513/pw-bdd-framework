"""https://automationexercise.com/"""

from playwright.sync_api import Page

from qakit.apps.automationexercise.pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.featured_items = page.get_by_role("heading", name="Features Items")
