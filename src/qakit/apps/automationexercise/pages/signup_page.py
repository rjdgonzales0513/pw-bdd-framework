"""https://automationexercise.com/signup: "Enter Account Information", then "Account Created!"."""

from playwright.sync_api import Page

from qakit.apps.automationexercise.data.users import NewUser
from qakit.apps.automationexercise.pages.base_page import BasePage


class SignupPage(BasePage):
    """Reached from LoginPage.start_signup(); name and email are already filled in there."""

    path = "/signup"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Enter Account Information")
        self.password = page.get_by_test_id("password")
        self.birth_day = page.get_by_test_id("days")
        self.birth_month = page.get_by_test_id("months")
        self.birth_year = page.get_by_test_id("years")
        self.first_name = page.get_by_test_id("first_name")
        self.last_name = page.get_by_test_id("last_name")
        self.company = page.get_by_test_id("company")
        self.address1 = page.get_by_test_id("address")
        self.address2 = page.get_by_test_id("address2")
        self.country = page.get_by_test_id("country")
        self.state = page.get_by_test_id("state")
        self.city = page.get_by_test_id("city")
        self.zipcode = page.get_by_test_id("zipcode")
        self.mobile_number = page.get_by_test_id("mobile_number")
        self.create_account_button = page.get_by_test_id("create-account")
        # The page shown after "Create Account".
        self.account_created = page.get_by_test_id("account-created")
        self.continue_button = page.get_by_test_id("continue-button")

    def create_account(self, user: NewUser) -> None:
        """Fill every field from ``user`` and submit.

        Takes the whole NewUser, not 15 strings: callers can't mix up the order, and a new
        field later changes this method, not every test.
        """
        # exact=True: "Mr." must not match "Mrs." (get_by_label matches substrings by default).
        self.page.get_by_label(f"{user.title}.", exact=True).check()
        self.password.fill(user.password)
        # select_option matches an option's value or its label (Java: Select.selectByValue).
        self.birth_day.select_option(str(user.birth_day))
        self.birth_month.select_option(str(user.birth_month))
        self.birth_year.select_option(str(user.birth_year))
        self.first_name.fill(user.first_name)
        self.last_name.fill(user.last_name)
        self.company.fill(user.company)
        self.address1.fill(user.address1)
        self.address2.fill(user.address2)
        self.country.select_option(user.country)
        self.state.fill(user.state)
        self.city.fill(user.city)
        self.zipcode.fill(user.zipcode)
        self.mobile_number.fill(user.mobile_number)
        self.create_account_button.click()

    def continue_to_site(self) -> None:
        """Leave the "Account Created!" page; the new user is logged in afterwards."""
        self.continue_button.click()
