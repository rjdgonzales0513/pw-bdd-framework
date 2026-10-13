# qakit framework guide

This guide is for test automation engineers who write and maintain tests with qakit.
Each page stands on its own, so read them in any order. If you're new, read 1 → 2 → 3.

| # | Page | Read it when you want to... |
| --- | --- | --- |
| 1 | [Architecture](01-architecture.md) | understand how the pieces fit together |
| 2 | [Running tests](02-running-tests.md) | run, filter, debug, or pick an environment |
| 3 | [Writing BDD tests](03-writing-bdd-tests.md) | add a scenario or a step |
| 4 | [Page objects and locators](04-page-objects.md) | add or change a page object |
| 5 | [API testing](05-api-testing.md) | call or test an endpoint |
| 6 | [Test data and hybrid tests](06-test-data.md) | create users, clean up, skip the login form |
| 7 | [Reports, traces and CI](07-reporting-and-ci.md) | read a failure, set up CI |
| 8 | [Adding an application](08-adding-an-application.md) | test a new app with the framework |
| 9 | [Java → Python cheat sheet](09-java-to-python.md) | translate what you know from Selenium/Cucumber/RestAssured |
| 10 | [Troubleshooting](10-troubleshooting.md) | fix an error message you don't understand |

## The rules in one place

1. **`core` never imports from `apps`.** Code moves into `core` only once a second app needs it.
2. **Fixtures are requested by parameter name**, never imported and called.
3. **Locators:** role > label/placeholder/test id > CSS. Assert with `expect(...)`.
4. **Page objects never assert.** They expose locators and do user actions.
5. **Gherkin is declarative:** business actions ("the shopper logs in"), not clicks.
6. **Every test cleans up what it creates** (the user registry does it for you).
7. **A test compares against an independent source** (the API, a fixed value), never against
   the value it just wrote.
8. **Never make a test green by changing the expected value.** Fix the cause.
9. **Quality gates before every commit:** `ruff check`, `ruff format --check`, `mypy`.

## Glossary

| Term | Meaning |
| --- | --- |
| **Fixture** | A function pytest runs before a test to give it something (a page, a user, a client). Requested by naming it as a parameter. Java: constructor injection + `@BeforeEach`/`@AfterEach`. |
| **Scope** | How long a fixture's value lives: `function` (default, per test) or `session` (once per run). |
| **conftest.py** | A file of fixtures pytest loads automatically for its folder and below. |
| **Marker** | A label on a test (`@pytest.mark.smoke`), used to select tests with `-m`. Gherkin tags become markers. |
| **Step definition** | A Python function bound to a Gherkin step text with `@given/@when/@then`. |
| **Page object** | A class that hides one page's locators behind user actions. |
| **Locator** | A lazy, auto-waiting way to find elements. Never stale. |
| **Storage state** | Cookies + localStorage saved to a file, so a new browser context starts logged in. |
| **Trace** | A Playwright recording of a test (DOM snapshots, network, console) you can replay. |
