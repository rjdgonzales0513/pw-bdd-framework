# 4. Page objects and locators

## Shape of a page object

```python
class ProductsPage(BasePage):
    path = "/products"                                   # open() goes here; base_url adds the host

    def __init__(self, page: Page) -> None:
        super().__init__(page)                           # sets self.page and self.header
        self.search_box = page.get_by_placeholder("Search Product")
        self.cards = page.locator(".product-image-wrapper")
        self.product_names = self.cards.locator(".productinfo p")

    def search(self, term: str) -> None:                 # a user action, in the page's words
        self.search_box.fill(term)
        self.search_button.click()
```

Used from a test:

```python
products_page.open().search("jean")                      # open() returns self, so calls chain
expect(products_page.product_names).to_have_text(expected)
```

### The rules (checked in review)

1. **No assertions in page objects.** They expose `Locator`s and perform actions; the test
   decides what's correct with `expect(locator)`. `expect` retries until the timeout, but a
   string read once with `inner_text()` doesn't.
2. **Methods are user actions**: `add_to_cart("Blue Top")`, `login(email, password)`, not
   `click_button_3()`.
3. **Take whole objects, not lists of strings.** `SignupPage.create_account(user: NewUser)`
   can't get 15 arguments in the wrong order, and a new field changes one method.
4. **Components for repeated parts.** `Header` and `CartModal` live in `pages/components/`;
   pages hold them by composition (`self.header = Header(page)`).
5. **No waits.** Playwright actions and `expect` auto-wait. There is no `sleep` and no
   `WebDriverWait`.

## Locator order

Use the first one that works:

| Priority | Locator | Example | Why |
| --- | --- | --- | --- |
| 1 | role + name | `get_by_role("button", name="Login")` | what users and screen readers see |
| 2 | label / placeholder / text | `get_by_label("Mr.", exact=True)`, `get_by_placeholder("Search Product")` | visible to the user |
| 2 | test id | `get_by_test_id("login-email")` | stable, made for tests |
| 3 | CSS | `locator("#submit_search")` | last resort; leave a comment saying why |

### Test ids per app

`get_by_test_id("x")` matches the attribute set for the app in `tests/<app>/conftest.py`:

```python
@pytest.fixture(scope="session")
def test_id_attribute() -> str:
    return "data-qa"          # automationexercise; saucedemo uses "data-test"
```

Core sets it before every test (an autouse fixture). A **session-scoped** fixture runs before
that, so if it uses `get_by_test_id` it must set the attribute itself:

```python
with use_test_id_attribute(playwright, test_id_attribute):
    LoginPage(page).open().login(...)
```

### Handy locator patterns

```python
# A row/card that contains something, then a child inside it (no indexes, no XPath):
self.cards.filter(has=page.get_by_text("Blue Top", exact=True)).get_by_text("Add to cart")
self.items.filter(has_text="Men Tshirt").locator(".cart_quantity_delete")

# Scope to a landmark so "Cart" in the header ≠ "View Cart" in a dialog:
page.get_by_role("banner").get_by_role("link", name="Cart")

# exact=True when one name is a prefix/substring of another ("Mr." vs "Mrs.").
```

## Assertions cheat sheet (`from playwright.sync_api import expect`)

| Check | Code |
| --- | --- |
| visible / hidden | `expect(loc).to_be_visible()`, `.to_be_hidden()` |
| exact text / contains | `.to_have_text("Products")`, `.to_contain_text("Logged in as")` |
| list of texts, in order | `expect(names).to_have_text(["Blue Top", "Men Tshirt"])` |
| count | `.to_have_count(6)` |
| URL / title | `expect(page).to_have_url(re.compile(r"/login$"))`, `.to_have_title(...)` |
| input value | `.to_have_value("abc")` |

Avoid `assert loc.count() == 6` and `assert loc.is_visible()`: they read the value once,
don't wait, and fail at random.

## Ads and third-party noise

automationexercise.com loads Google ads and a consent dialog that cover buttons at random.
`pages/ad_blocking.py` aborts **every request to another host** (an allow-list, not a
block-list of ad domains). The app's `new_context` fixture applies it to every browser
context, including the ones tests create themselves.
