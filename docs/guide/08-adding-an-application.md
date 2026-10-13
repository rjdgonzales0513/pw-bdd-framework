# 8. Adding an application

Adding an app is **additive**: three new folders, and nothing in `core` or in another app
changes. saucedemo was added this way, so use it as the worked example (it's the smaller
of the two).

## Checklist

Replace `myapp` / `MA_` with your app's name and a short, unique prefix.

### 1. Settings: `envs/myapp/` and `src/qakit/apps/myapp/config.py`

```
envs/myapp/dev.env
envs/myapp/ci.env
```

```ini
MA_ENV_NAME=dev
MA_BASE_URL=https://myapp.example.com/
MA_TIMEOUT_MS=10000
```

```python
class MyAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MA_", env_file_encoding="utf-8")

    env_name: str
    base_url: HttpUrl
    timeout_ms: PositiveInt
    # password: SecretStr      # secrets: SecretStr, and an env var in CI
```

No defaults: a missing key should stop the run, not fall back to a default nobody chose.

### 2. App package: `src/qakit/apps/myapp/`

```
__init__.py
config.py
pages/      __init__.py, page objects (one module per page, or one module for a small app)
data/       __init__.py, Faker factories
api/        __init__.py, client.py, models.py        (only if you test an API)
```

Every folder needs an `__init__.py`. Don't add a `py.typed`; there is one already, in
`src/qakit/`.

### 3. Fixtures: `tests/myapp/conftest.py`

These three fixtures are the same in every app. Copy them from `tests/saucedemo/conftest.py`:

```python
@pytest.fixture(scope="session")
def settings(env_name: str, envs_root: Path) -> MyAppSettings:
    return load_settings(MyAppSettings, env_name, envs_root / "myapp")


@pytest.fixture(scope="session")
def test_id_attribute() -> str:
    return "data-testid"          # whatever attribute your app's HTML uses


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], settings: MyAppSettings
) -> dict[str, Any]:
    return {**browser_context_args, "base_url": str(settings.base_url)}
```

Then add one fixture per page object, plus any data or login fixtures.

### 4. Tests: `tests/myapp/`

```
tests/myapp/__init__.py            ← needed: two apps may both have test_login.py
tests/myapp/conftest.py
tests/myapp/ui/__init__.py
tests/myapp/ui/test_*.py
tests/myapp/bdd/__init__.py
tests/myapp/bdd/features/*.feature
tests/myapp/bdd/test_*.py
```

### 5. Markers

Every new Gherkin tag or `pytest.mark.x` goes into `markers` in `pyproject.toml`.
Otherwise `--strict-markers` stops the run.

### 6. Check it

```powershell
pytest tests/myapp --env dev -v
pytest tests/myapp --env nope          # must fail clearly, naming envs/myapp/nope.env
ruff check src tests; ruff format --check src tests; mypy src tests
pytest                                 # all apps together still pass
```

## When does code move into `core`?

When a **second app needs the same thing**. Until then it stays in the app package. A guess
at "generic" code, shaped by one app, is usually wrong for the next one.

| Moved into core | Because |
| --- | --- |
| `load_settings()` | every app has settings |
| `--env`, `env_name`, `envs_root` | every app has environments |
| test id attribute fixture + `use_test_id_attribute()` | automationexercise **and** saucedemo needed it |
| reporting plugin | the report covers every app |

| Stays in its app | Because |
| --- | --- |
| `allow_only_own_host()` (ad blocking) | only automationexercise shows ads |
| `UserRegistry` | depends on automationexercise's account API |
| `BasePage` | each app's base page has a different header |

## Mixing apps in one run

`pytest` (no path) runs every app. Each test gets its own app's fixtures (`settings`,
`test_id_attribute`, …) because pytest picks fixtures from the conftest.py nearest the test.
The test id attribute is a global Playwright setting, so core sets it again **before every
test**.
