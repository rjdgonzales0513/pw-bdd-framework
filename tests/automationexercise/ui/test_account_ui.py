"""Signup, login and logout in the browser."""

import re

import pytest
from playwright.sync_api import Page, expect

from qakit.apps.automationexercise.data.users import NewUser
from qakit.apps.automationexercise.pages import HomePage, LoginPage, SignupPage

pytestmark = [pytest.mark.ui, pytest.mark.account]


def test_signup_creates_an_account(
    login_page: LoginPage, signup_page: SignupPage, new_user: NewUser
) -> None:
    """A new user can sign up through the UI and is logged in afterwards."""
    login_page.open().start_signup(new_user.name, new_user.email)
    expect(signup_page.heading).to_be_visible()

    signup_page.create_account(new_user)

    expect(signup_page.account_created).to_have_text("Account Created!")
    signup_page.continue_to_site()
    expect(signup_page.header.logged_in_as).to_contain_text(new_user.name)
    # new_user is tracked by the user factory, so it is deleted through the API afterwards.


def test_signup_with_existing_email_is_refused(
    login_page: LoginPage, registered_user: NewUser
) -> None:
    """An email address can only be registered once."""
    login_page.open().start_signup("Someone Else", registered_user.email)

    expect(login_page.signup_error).to_be_visible()


@pytest.mark.smoke
def test_login_with_valid_credentials(login_page: LoginPage, registered_user: NewUser) -> None:
    """M5 hybrid: the user comes from the API, so this UI test needs no UI signup."""
    login_page.open().login(registered_user.email, registered_user.password)

    expect(login_page.header.logged_in_as).to_contain_text(registered_user.name)


def test_login_with_wrong_password_shows_error(
    login_page: LoginPage, registered_user: NewUser
) -> None:
    login_page.open().login(registered_user.email, "wrong-password")

    expect(login_page.login_error).to_be_visible()
    expect(login_page.header.logged_in_as).to_be_hidden()


def test_logout_returns_to_login_page(
    page: Page, login_page: LoginPage, registered_user: NewUser
) -> None:
    """Logging out ends the session. Uses its own user: logging out the shared one would
    break every test that uses logged_in_page."""
    login_page.open().login(registered_user.email, registered_user.password)

    login_page.header.logout()

    # A regex: the URL ends in /login (Java: assertThat(url).matches(".*/login$")).
    expect(page).to_have_url(re.compile(r"/login$"))
    expect(login_page.header.signup_login_link).to_be_visible()


def test_saved_login_skips_the_login_form(logged_in_page: Page) -> None:
    """M5 storage state: the page starts logged in, without filling any form."""
    home = HomePage(logged_in_page).open()

    expect(home.header.logged_in_as).to_be_visible()
    expect(home.header.signup_login_link).to_be_hidden()
