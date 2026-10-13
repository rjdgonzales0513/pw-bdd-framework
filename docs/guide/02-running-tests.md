# 2. Running tests

## First time setup

```powershell
python -m venv .venv                 # Python 3.14
.\.venv\Scripts\Activate.ps1         # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"              # -e: editable, your code changes apply without reinstalling
playwright install chromium          # add firefox / webkit if you need them
```

Run `pip install -e ".[dev]"` again after changing `[project.entry-points]` or dependencies
in `pyproject.toml`. Entry points are install metadata, so pytest won't see a new plugin
until you reinstall.

## Choosing what to run

| You want | Command |
| --- | --- |
| everything | `pytest` |
| one app | `pytest tests/automationexercise` |
| one layer of one app | `pytest tests/automationexercise/api` |
| one file / one test | `pytest tests/saucedemo/ui/test_login_ui.py::test_locked_out_user_is_refused` |
| by name (substring) | `pytest -k "cart and not remove"` |
| by marker / Gherkin tag | `pytest -m smoke`, `pytest -m "account and ui"` |
| only the last failures | `pytest --lf` |
| stop at the first failure | `pytest -x` |

### Markers and tags

Gherkin tags (`@smoke`) become pytest markers, so `-m` selects plain tests and scenarios
the same way. Every marker must be registered in `pyproject.toml`. `--strict-markers` turns
a typo like `@smok` into an error instead of silently selecting nothing.

| Marker | Meaning |
| --- | --- |
| `smoke` | the fast must-pass set |
| `api` | REST API only, no browser |
| `ui` | drives a browser |
| `account` | signup, login, logout |
| `shopping` | products, search, cart |
| `checkout` | placing an order |

## Environments: `--env`

```powershell
pytest --env dev     # default
pytest --env ci
```

`--env ci` loads `envs/<app>/ci.env` for every app in the run. Real environment variables
override the file, so CI can inject secrets without writing them to disk:

```powershell
$env:AE_TIMEOUT_MS = "60000"; pytest --env ci
```

| App | Prefix | Keys |
| --- | --- | --- |
| automationexercise | `AE_` | `ENV_NAME`, `BASE_URL`, `TIMEOUT_MS` |
| saucedemo | `SD_` | `ENV_NAME`, `BASE_URL`, `TIMEOUT_MS`, `USERNAME`, `PASSWORD` |

A missing key, a bad value (`AE_TIMEOUT_MS=abc`) or an unknown env (`--env nope`) stops
the run **before the first test**, with a message that names the field or the file.

## Browsers and watching tests

These options come from pytest-playwright:

```powershell
pytest --browser firefox                  # chromium (default), firefox, webkit
pytest --browser chromium --browser firefox   # each UI test once per browser
pytest --headed --slowmo 500              # see the browser, 500 ms between actions
pytest --device "iPhone 13"               # mobile emulation
PWDEBUG=1 pytest -k login -s              # Playwright Inspector: step through actions
```

In PowerShell, set `PWDEBUG` like this: `$env:PWDEBUG = "1"; pytest -k login -s`.

## Output of every run

| Path | What | Kept |
| --- | --- | --- |
| `reports/report.html` | the HTML report, one self-contained file | every run (overwritten) |
| `reports/cucumber.json` | Cucumber JSON of the BDD scenarios | every run |
| `test-results/<test>/trace.zip` | Playwright trace of a **failed** UI test | failures only |
| `test-results/<test>/test-failed-1.png` | screenshot at the moment of failure | failures only |

The defaults are in `addopts` in `pyproject.toml`. Override any of them on the command
line, e.g. `pytest --tracing on` to keep traces for passing tests too.
See [Reports, traces and CI](07-reporting-and-ci.md).
