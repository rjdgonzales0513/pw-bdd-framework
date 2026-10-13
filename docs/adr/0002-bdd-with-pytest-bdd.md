# 2. BDD with pytest-bdd

Date: 2026-10-12
Status: Accepted (ported from python-playwright ADR 0001, adapted to qakit)

## Context

qakit tests business journeys (signup, login, shopping, checkout) for more than one
application. Product owners, business analysts and manual testers want to see what is covered
and how a journey flows, without reading Python. The engineers come from Cucumber-JVM.

Gherkin `.feature` files give non-programmers that view, and they stay true because they run
in CI (living documentation). But BDD adds a layer to every test (feature → step text →
step function → fixture → page object), so we need to decide where it pays off.

Options for running Gherkin in Python: **pytest-bdd** (a pytest plugin) and **behave** (its own
runner).

## Decision

- Use **pytest-bdd**, not behave. Scenarios become ordinary pytest tests, so they share
  fixtures, markers, `--env`, pytest plugins (e.g. pytest-xdist for parallel runs), the HTML report and CI with the plain tests. behave
  would need its own fixtures, hooks and reporting.
- Use BDD for **key business journeys** that a non-technical person reads. Everything else
  (API contracts, edge cases, data variations, framework tests) is **plain pytest**.
- Scenarios are **declarative**: business actions ("the shopper logs in"), never UI steps
  ("I click Login").
- **Steps hold no setup logic.** They request existing fixtures (`registered_user`,
  `logged_in_page`, page objects) by name. Users are created through the API by fixtures and
  deleted after the test.
- One test module per feature file (`scenarios("features/x.feature")` + its steps). A
  `target_fixture` passes values between steps.
- Gherkin tags are pytest markers, registered in `pyproject.toml`. `--strict-markers` rejects
  typos.
- BDD results are reported twice: step-by-step in the HTML report (`qakit.core.reporting`) and
  as Cucumber JSON for Cucumber tools (Xray, Jenkins).

## Consequences

### Good

- Feature files are living documentation, reviewed with the PO/BA.
- No second test runner: one `pytest` command, one report, one CI pipeline.
- `pytest -m smoke` selects plain tests and scenarios alike.

### Bad / costs

- An extra layer: a plain test calls fixtures and page objects directly.
- Step text must match the decorator exactly; a typo is only found when the test runs.
- A failure points at the Python step, not the Gherkin line. Scenario titles and the report's
  step table must make clear what broke.
- The step library needs care, or it fills up with near-duplicates.

### Rule that keeps BDD honest

BDD is kept only while someone outside the automation team reads the scenarios. If nobody
does, the journeys move to plain pytest.
