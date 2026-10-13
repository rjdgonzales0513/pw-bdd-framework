# 3. Reporting: pytest-html + Cucumber JSON + Playwright traces

Date: 2026-10-12
Status: Accepted

## Context

A failed test must be understandable without re-running it: what was tested (in business
terms for BDD), which step failed, what the page looked like, and what happened before.
Reports must work locally and as CI artifacts, and be readable by people who don't run the
tests.

Options considered:

| Option | For | Against |
| --- | --- | --- |
| **pytest-html** | one self-contained HTML file; no extra tool; pytest-playwright attaches screenshots and trace links to it | plain look; no history/trends |
| **Allure** (allure-pytest / allure-pytest-bdd) | rich UI, history, steps, familiar from Java | needs the Allure CLI (Java or Node) to generate the report; a results folder, not a file; more moving parts in CI |
| **Cucumber JSON** only | standard format for Cucumber tools (Xray, Jenkins) | covers BDD scenarios only, and needs another tool to render |
| Playwright traces | complete recording of a failure | per test, not a run overview |

## Decision

- **pytest-html** is the main report: `reports/report.html`, self-contained, produced by every
  run through `addopts`.
- **qakit.core.reporting** (a pytest11 plugin, app-agnostic) adds a title, the `--env` in the
  Environment table, a **Description** column (BDD: "Feature > Scenario"; plain tests: the
  docstring) and, for BDD scenarios, a **step table** with passed / failed (with error) /
  not run.
- **Cucumber JSON** (`reports/cucumber.json`, built into pytest-bdd) for tools that speak
  Cucumber.
- **Playwright traces and screenshots for failed tests only** (`--tracing retain-on-failure
  --screenshot only-on-failure`). pytest-playwright embeds the screenshot and a trace link in
  the HTML report.
- CI uploads `reports/` on every run and `test-results/` (traces) on failure.

## Consequences

- No install beyond `pip install -e .`: anyone opens the report by double-clicking it.
- No history or trend charts. If those are needed later, add `allure-pytest` alongside. Its
  results can be generated from the same run; nothing in the tests has to change.
- The reporting plugin depends on pytest-html's and pytest-bdd's hook names. Its hooks are
  marked `optionalhook=True`, and `tests/core/test_reporting.py` runs a real pytest session to
  catch breaking changes when either plugin is upgraded.
