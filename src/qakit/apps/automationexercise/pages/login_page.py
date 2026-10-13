"""https://automationexercise.com/login: the login form and the start of the signup form."""

from playwright.sync_api import Page

from qakit.apps.automationexercise.pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Both forms have a textbox labelled "Email Address", so role + name can't tell them
        # apart. The site's data-qa attributes can: the app conftest sets data-qa as the
        # test id attribute, so get_by_test_id("login-email") means [data-qa="login-email"].
        self.login_email = page.get_by_test_id("login-email")
        self.login_password = page.get_by_test_id("login-password")
        self.login_button = page.get_by_test_id("login-button")
        self.signup_name = page.get_by_test_id("signup-name")
        self.signup_email = page.get_by_test_id("signup-email")
        self.signup_button = page.get_by_test_id("signup-button")
        # The red messages under each form, e.g. "Your email or password is incorrect!".
        self.login_error = page.get_by_text("Your email or password is incorrect!")
        self.signup_error = page.get_by_text("Email Address already exist!")

    def login(self, email: str, password: str) -> None:
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()

    def start_signup(self, name: str, email: str) -> None:
        """Fill the "New User Signup!" form; the site then opens the account details form."""
        self.signup_name.fill(name)
        self.signup_email.fill(email)
        self.signup_button.click()
