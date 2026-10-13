"""Step definitions for features/account.feature.

The steps hold no setup logic: users come from the user factory fixtures (created through the
API, deleted afterwards), pages from the page object fixtures in ../conftest.py.

CUCUMBER-JVM -> PYTEST-BDD
    @CucumberOptions(features = ...)      scenarios("features/account.feature")
    @Given("a registered shopper")        @given("a registered shopper", target_fixture="account")
    glue-class field shared by steps      target_fixture: the step's return value becomes a
                                          fixture named "account" for the later steps
    @When("adds {string}")                @when(parsers.parse('adds "{product}"'))
"""

from playwright.sync_api import expect
from pytest_bdd import given, scenarios, then, when

from qakit.apps.automationexercise.api.client import AutomationExerciseApi
from qakit.apps.automationexercise.data.users import NewUser
from qakit.apps.automationexercise.pages import LoginPage, SignupPage

# One line turns every scenario in the file into a pytest test (test_a_registered_shopper_...).
# The path is relative to this file.
scenarios("features/account.feature")


# Step functions are all named `_`: the decorator registers the step, the name is never used.


@given("a registered shopper", target_fixture="account")
def _(registered_user: NewUser) -> NewUser:
    return registered_user


@given("a new shopper without an account", target_fixture="account")
def _(new_user: NewUser) -> NewUser:
    return new_user


@when("the shopper logs in")
def _(login_page: LoginPage, account: NewUser) -> None:
    login_page.open().login(account.email, account.password)


@when("the shopper logs in with a wrong password")
def _(login_page: LoginPage, account: NewUser) -> None:
    login_page.open().login(account.email, account.password + "-wrong")


@when("the shopper signs up")
def _(login_page: LoginPage, signup_page: SignupPage, account: NewUser) -> None:
    login_page.open().start_signup(account.name, account.email)
    signup_page.create_account(account)
    signup_page.continue_to_site()  # the whole journey: the site logs the new user in


@when("someone else signs up with the same email address")
def _(login_page: LoginPage, account: NewUser) -> None:
    login_page.open().start_signup("Someone Else", account.email)


@then("the shopper is welcomed by name")
def _(login_page: LoginPage, account: NewUser) -> None:
    # Any page object would do: they all share the same `page` and header.
    expect(login_page.header.logged_in_as).to_contain_text(account.name)


@then("the shopper is told the login details are incorrect")
def _(login_page: LoginPage) -> None:
    expect(login_page.login_error).to_be_visible()


@then("the shopper is not logged in")
def _(login_page: LoginPage) -> None:
    expect(login_page.header.logged_in_as).to_be_hidden()


@then("the account is created")
def _(ae_api: AutomationExerciseApi, account: NewUser) -> None:
    # Checked through the API, an independent source: the UI could show "Account Created!"
    # without saving anything. (The plain UI test checks that page itself.)
    detail = ae_api.user_detail(account.email).user
    assert (detail.name, detail.country) == (account.name, account.country)


@then("they are told the email address is already registered")
def _(login_page: LoginPage) -> None:
    expect(login_page.signup_error).to_be_visible()
