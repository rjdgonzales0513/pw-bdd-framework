# 9. Java → Python cheat sheet

For engineers coming from **Selenium + Cucumber-JVM + RestAssured + JUnit/TestNG**. The left
column is what you know; the right column is where it lives in qakit.

## Build, project, tooling

| Java | qakit / Python |
| --- | --- |
| `pom.xml` / `build.gradle` | `pyproject.toml` |
| `mvn install` | `pip install -e ".[dev]"` (editable: no rebuild after code changes) |
| `target/` | `.venv/`, `__pycache__/`, `reports/`, `test-results/` |
| `src/main/java` / `src/test/java` | `src/qakit/` / `tests/` |
| Checkstyle / Spotless | `ruff check` / `ruff format` |
| the compiler's type checks | `mypy --strict` (type hints are checked, not enforced at runtime) |
| `META-INF/services` + `ServiceLoader` | `[project.entry-points.pytest11]` (how pytest finds `qakit.core.plugin`) |
| `application-dev.properties` + `@ConfigurationProperties` | `envs/<app>/dev.env` + a `BaseSettings` class |

## JUnit / TestNG → pytest

| Java | pytest |
| --- | --- |
| `@Test` | a function named `test_*` in a file named `test_*.py` |
| `@BeforeEach` / `@AfterEach` | a fixture with `yield`: code before = setup, after = teardown |
| `@BeforeAll` / `@AfterAll` | `@pytest.fixture(scope="session")` |
| constructor injection / `@Autowired` | name the fixture as a parameter: `def test_x(ae_api): ...` |
| `@ParameterizedTest` + `@CsvSource` | `@pytest.mark.parametrize(("a", "b"), [(1, 2), (3, 4)])` |
| `@Tag("smoke")` / TestNG groups | `@pytest.mark.smoke` → `pytest -m smoke` |
| `assertEquals(a, b)` | `assert a == b` (pytest shows both values on failure) |
| `assertThrows(X.class, ...)` | `with pytest.raises(X, match="..."):` |
| `@Disabled` | `@pytest.mark.skip(reason="...")` |
| JUnit extension / TestNG listener | a pytest **hook** (`core/reporting.py` uses several) |
| `ExtensionContext.Store` | `item.stash[KEY]` |
| surefire XML / Extent report | `--junitxml=...` / pytest-html `reports/report.html` |

## Selenium → Playwright

| Selenium | Playwright (Python) |
| --- | --- |
| `WebDriver` | `Browser` (process) → `BrowserContext` (an incognito profile) → `Page` (a tab) |
| `driver.get(url)` | `page.goto("/path")` (relative to `base_url`) |
| `driver.findElement(By.id("x"))` | `page.locator("#x")`, but prefer `get_by_role/label/test_id` |
| `@FindBy` + PageFactory | locators assigned in `__init__`. They are lazy and never stale |
| `findElements(...).size()` | `expect(locator).to_have_count(n)` |
| `WebDriverWait` + `ExpectedConditions` | not needed: actions and `expect` auto-wait |
| `Thread.sleep(2000)` | never. Use `expect(...)` with the condition you're waiting for |
| `new Select(el).selectByValue("x")` | `locator.select_option("x")` |
| `driver.manage().getCookies()` reuse | `context.storage_state(path=...)` → `new_context(storage_state=...)` |
| BrowserMob proxy / CDP interception | `context.route("**/*", handler)` |
| screenshots in a TestWatcher | `--screenshot only-on-failure` (already on) |
| — | **traces**: `--tracing retain-on-failure` + `playwright show-trace` |

## Cucumber-JVM → pytest-bdd

| Cucumber-JVM | pytest-bdd |
| --- | --- |
| runner `@CucumberOptions(features=...)` | `scenarios("features/x.feature")` |
| `@Given("a {string} user")` | `@given(parsers.parse('a "{kind}" user'))` |
| glue-class fields / PicoContainer | fixtures and `target_fixture="name"` |
| `@Before` / `@After` hooks | fixtures (`yield`) |
| `--tags "@smoke and not @wip"` | `-m "smoke and not wip"` |
| `plugin = "json:..."` | `--cucumberjson=reports/cucumber.json` (on by default) |

## RestAssured + Jackson → Playwright API + pydantic

| Java | Python |
| --- | --- |
| `given().baseUri(...)` spec | `playwright.request.new_context(base_url=...)` (fixture `api_request_context`) |
| `.formParams(map)` | `form={...}` |
| `.queryParams(map)` | `params={...}` |
| `.body(pojo)` (JSON) | `data={...}` (this API doesn't use JSON bodies) |
| `.then().extract().as(Products.class)` | `ProductsResponse.model_validate(response.json())` |
| `@JsonProperty("responseCode")` | `Field(alias="responseCode")` |
| `FAIL_ON_UNKNOWN_PROPERTIES = true` | `ConfigDict(extra="forbid")` |
| `record` / immutable POJO | `ConfigDict(frozen=True)` / `@dataclass(frozen=True)` |

## Language bits you'll meet in this code base

| Java | Python |
| --- | --- |
| `this` | `self` (always the first parameter of a method) |
| `new Foo(x)` | `Foo(x)` |
| `private` | a leading `_` by convention: `self._request` |
| `static final String PATH` | `path: ClassVar[str] = "/login"` |
| `<T extends Base> T load(Class<T> c)` | `def load[T: Base](c: type[T]) -> T:` |
| `Optional<String>` | `str \| None` |
| `List<Product>` / `Map<String, Integer>` | `list[Product]` / `dict[str, int]` |
| `enum Title { MR, MRS }` | `Literal["Mr", "Mrs"]` (or `enum.Enum`) |
| try-with-resources / `AutoCloseable` | `with x:` + `__enter__` / `__exit__`, or `@contextmanager` |
| lambda capturing a variable | a nested function (closure), e.g. in `ad_blocking.py` |
| builder `.withX(1).build()` | keyword arguments: `build_user(faker, country="Canada")` |
| `toBuilder().x(1).build()` | `dataclasses.replace(obj, x=1)` |
| `String.format` | f-strings: `f"{name} has {count} items"` |
| `stream().map(...).collect(toList())` | list comprehension: `[p.name for p in products]` |
| `stream().allMatch(...)` | `all(...)`. Careful: `all([])` is `True` |
