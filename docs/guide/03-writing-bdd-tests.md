# 3. Writing BDD tests

## When to write a scenario (and when not to)

From [ADR 0002](../adr/0002-bdd-with-pytest-bdd.md):

- **Write a scenario** for a business journey that someone outside the automation team
  (PO, BA, manual tester) reads or reviews: signup, login, add to cart, checkout.
- **Write a plain pytest test** for everything else: API contract checks, edge cases,
  data-heavy variations, framework tests. They are shorter and easier to debug.

## Where things go

```
tests/<app>/bdd/
    features/
        account.feature        the scenarios (business language)
    test_account.py            scenarios("features/account.feature") + its step definitions
```

One test module per feature file. It calls `scenarios(...)` once, which turns every scenario
in the file into a pytest test, and then defines the steps that feature uses.

## A feature, step by step

```gherkin
@ui @account                                   # tags = pytest markers (registered in pyproject.toml)
Feature: Customer accounts
  Shoppers create an account once, then log in to see their details and buy faster.

  @smoke
  Scenario: A registered shopper logs in
    Given a registered shopper                 # who / what state
    When the shopper logs in                   # ONE business action
    Then the shopper is welcomed by name       # the observable outcome
```

```python
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("features/account.feature")          # path relative to this file


@given("a registered shopper", target_fixture="account")
def _(registered_user: NewUser) -> NewUser:      # a fixture does the work (API signup)
    return registered_user                       # becomes the fixture "account"


@when("the shopper logs in")
def _(login_page: LoginPage, account: NewUser) -> None:
    login_page.open().login(account.email, account.password)


@then("the shopper is welcomed by name")
def _(login_page: LoginPage, account: NewUser) -> None:
    expect(login_page.header.logged_in_as).to_contain_text(account.name)
```

### The rules

1. **Declarative, not imperative.** Describe *what* the user does, never *how*.

   | ❌ Imperative | ✅ Declarative |
   | --- | --- |
   | `When I type "a@b.c" in the "Email Address" field` | `When the shopper logs in` |
   | `And I click the "Login" button` | |
   | `Then I see the text "Logged in as Megan"` | `Then the shopper is welcomed by name` |

2. **Steps hold no setup logic.** They ask for fixtures (`registered_user`, `login_page`,
   `logged_in_page`) by parameter name. Setup and cleanup live in fixtures.
3. **One step per business action.** Look for an existing step before writing a new one.
4. **Then steps assert with `expect(...)`** (it retries), or compare against an independent
   source such as the API.
5. **Name step functions `_`.** The decorator registers the step, so the name is never used.

## Passing values between steps: `target_fixture`

In Cucumber-JVM you share state through fields of the glue class (or PicoContainer). In
pytest-bdd, a step's **return value becomes a fixture** when you give it `target_fixture`:

```python
@given("a guest shopper", target_fixture="shopper_page")
def _(page: Page) -> Page:
    return page

@given("a logged-in shopper", target_fixture="shopper_page")
def _(logged_in_page: Page) -> Page:
    return logged_in_page

@when(parsers.parse('the shopper adds "{product}" to the cart'))
def _(shopper_page: Page, product: str) -> None:      # works for both Givens
    ProductsPage(shopper_page).open().add_to_cart(product).continue_shopping()
```

## Parameters in step text

```python
@when(parsers.parse('the shopper searches for "{term}"'))   # {term} → parameter `term: str`
@when(parsers.parse("the shopper buys {count:d} items"))    # :d → int (Cucumber: {int})
```

The step text must match the decorator **exactly** (after the parameters are filled in). A
typo shows up when the test runs, as `StepDefinitionNotFoundError`.

## Scenario Outline

```gherkin
  Scenario Outline: A missing detail is reported
    When the shopper checks out without a <field>
    Then the shopper is told "<message>"

    Examples:
      | field       | message                        |
      | first_name  | Error: First Name is required  |
      | last_name   | Error: Last Name is required   |
```

Each row becomes its own test. `<field>` is filled into the step text before matching, so
the step is written as `parsers.parse("the shopper checks out without a {field}")`.

## Background

Steps under `Background:` run before every scenario of the feature, like `@Before` scoped to
one feature (see `tests/saucedemo/bdd/features/checkout.feature`).

## Running and reading results

```powershell
pytest tests/automationexercise/bdd -v          # test names come from the scenario titles
pytest -m smoke                                 # tag selection
pytest tests/saucedemo/bdd --gherkin-terminal-reporter -vv  # print every Gherkin step in the terminal
```

In `reports/report.html`, every scenario row has a **Description** ("Feature > Scenario").
Expanding the row shows each step as **passed**, **failed** (with the error) or
**not run**. `reports/cucumber.json` holds the same results in Cucumber's format, so you can
feed it into any Cucumber report tool or Jira/Xray.

## Cucumber-JVM → pytest-bdd

| Cucumber-JVM | pytest-bdd |
| --- | --- |
| `@CucumberOptions(features = "...")` runner class | `scenarios("features/x.feature")` in the test module |
| `@Given("...") public void ...()` | `@given("...") def _(...) -> None:` |
| `{string}`, `{int}` | `parsers.parse('"{name}"')`, `{n:d}` |
| glue-class fields, PicoContainer | fixtures + `target_fixture` |
| `@Before` / `@After` hooks | fixtures with `yield` |
| `--tags "@smoke and not @wip"` | `-m "smoke and not wip"` |
| `DataTable` | `datatable` argument in the step function |
| `plugin = "json:target/cucumber.json"` | `--cucumberjson=reports/cucumber.json` (already on) |
