# 10. Troubleshooting

Real problems hit while building this framework, with the fix for each.

## Setup and running

| Symptom | Cause | Fix |
| --- | --- | --- |
| `error: unrecognized arguments: --env` | qakit isn't installed in the active venv, or another repo's venv is active | activate **this** repo's `.venv`; `pip install -e ".[dev]"` |
| a new plugin or entry point is ignored | entry points are install metadata | `pip install -e ".[dev]"` again |
| `FileNotFoundError: No settings file for env 'x'` | `--env x` has no `envs/<app>/x.env` | use `dev` / `ci`, or add the file |
| `ValidationError ... timeout_ms` at startup | a bad value in the `.env` file **or** in a real env var | check `$env:AE_TIMEOUT_MS`; env vars beat the file |
| `'smok' not found in markers configuration option` | `--strict-markers` caught a typo or an unregistered tag | fix the tag, or add it to `markers` in `pyproject.toml` |
| `Executable doesn't exist ... chromium` | browsers not downloaded | `playwright install chromium` (or `firefox`, `webkit`) |
| `0 tests collected` / `no tests ran` | wrong path, file not named `test_*.py`, or `-m` matched nothing | `pytest --collect-only -q` shows what pytest sees |
| Git Bash: `Page.goto: ... c:/Program Files/Git/login` | Git Bash turns `/login` into a Windows path | `export MSYS_NO_PATHCONV=1`, or use PowerShell |
| `UnicodeEncodeError: 'charmap' codec` when printing | Windows console code page | `$env:PYTHONIOENCODING = "utf-8"` |

## Fixtures

| Symptom | Cause | Fix |
| --- | --- | --- |
| `fixture 'x' not found` | typo, or the fixture is in another app's `conftest.py` | `pytest --fixtures tests/<app>` lists what a folder can see |
| `ScopeMismatch: You tried to access the function scoped fixture ...` | a session fixture asked for a function fixture (e.g. `faker`) | widen the inner one, or create the value inside (`Faker()`) |
| a session fixture's `get_by_test_id` finds nothing | session fixtures run **before** core's per-test autouse fixture that sets the attribute | wrap the code in `with use_test_id_attribute(playwright, test_id_attribute):` |
| a fixture "doesn't run" | fixtures run only when something requests them by name | add it as a parameter (or `autouse=True` if it really must always run) |

## BDD

| Symptom | Cause | Fix |
| --- | --- | --- |
| `StepDefinitionNotFoundError: Step definition is not found: When "..."` | the step text doesn't match any decorator **exactly** (quotes, spaces, plurals) | copy the text from the error into the decorator; check `parsers.parse` placeholders |
| the scenario runs but uses the wrong `shopper_page`/`account` | two `Given` steps in one scenario set the same `target_fixture` | the last one wins; use one Given per role |
| a tag doesn't select anything | tags become markers **without** the `@` | `pytest -m smoke`, not `-m @smoke` |

## Flaky or failing UI tests

| Symptom | Cause | Fix |
| --- | --- | --- |
| a click hits an ad or a consent dialog | third-party content | already blocked by `allow_only_own_host`; check the context came from `new_context`/`page` |
| `strict mode violation: ... resolved to 2 elements` | the locator matches several elements (e.g. the products page's hover overlay) | scope it: `card.locator(".productinfo")`, `filter(has=...)`, `exact=True` |
| a "contains" check fails because of extra items | `logged_in_page` shares one session and one cart across tests | assert "contains", or use a guest `page` / `registered_user` |
| passes locally, fails in CI | slower machine, other browser | download the trace artifact; never "fix" by adding `sleep` |
| a test passes but shouldn't | `all([])` is `True`, comparing a value with itself, 0 tests collected | add a non-empty check; compare against an independent source; break the code once and watch it fail |
