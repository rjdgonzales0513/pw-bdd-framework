"""qakit's reporting plugin: makes the pytest-html report readable for BDD and plain tests.

What it adds to reports/report.html (pytest-html):
- a title and the run's environment (--env) in the Environment table;
- a Description column: "Feature > Scenario" for BDD tests, the docstring's first line
  for plain tests;
- for every BDD scenario, its Gherkin steps with passed / failed / not run.

Failure screenshots and trace links are added by pytest-playwright itself (>= 0.10) because
--screenshot and --tracing are set in pyproject.toml; this plugin doesn't repeat them.

Registered as its own pytest11 entry point. Knows no application.
"""

import html
from collections.abc import Generator
from dataclasses import dataclass, field

import pytest
from pytest_bdd.parser import Feature, Scenario, Step
from pytest_html import extras
from pytest_metadata.plugin import metadata_key

# Java: a value attached to the test's ExtensionContext store. pytest's stash is a typed,
# per-item dict: the key carries the value's type, so mypy checks reads and writes.
SCENARIO_KEY = pytest.StashKey["ScenarioRecord"]()

_STATUS_COLOURS = {"passed": "#2e7d32", "failed": "#c62828", "not run": "#757575"}


@dataclass
class StepRecord:
    keyword: str  # Given / When / Then / And
    text: str
    status: str = "not run"
    error: str = ""


@dataclass
class ScenarioRecord:
    feature: str
    scenario: str
    steps: list[StepRecord] = field(default_factory=list)  # Java: = new ArrayList<>()

    def find(self, step: Step) -> StepRecord | None:
        """The first not-yet-run record for ``step`` (a step text may appear twice)."""
        for record in self.steps:
            if record.text == step.name and record.status == "not run":
                return record
        return None


# --- pytest-bdd hooks: record each step's outcome on the test item -------------------------
# optionalhook=True: don't fail at startup if the plugin that defines the hook isn't loaded.


@pytest.hookimpl(optionalhook=True)
def pytest_bdd_before_scenario(
    request: pytest.FixtureRequest, feature: Feature, scenario: Scenario
) -> None:
    # Every step starts as "not run": steps after a failure keep that status in the report.
    steps = [StepRecord(step.keyword, step.name) for step in scenario.steps]
    request.node.stash[SCENARIO_KEY] = ScenarioRecord(feature.name, scenario.name, steps)


@pytest.hookimpl(optionalhook=True)
def pytest_bdd_after_step(
    request: pytest.FixtureRequest, feature: Feature, scenario: Scenario, step: Step
) -> None:
    # pluggy passes only the hook arguments a hookimpl names, so unused ones can be left out.
    _mark(request, step, "passed")


@pytest.hookimpl(optionalhook=True)
def pytest_bdd_step_error(
    request: pytest.FixtureRequest,
    feature: Feature,
    scenario: Scenario,
    step: Step,
    exception: Exception,
) -> None:
    _mark(request, step, "failed", f"{type(exception).__name__}: {exception}")


def _mark(request: pytest.FixtureRequest, step: Step, status: str, error: str = "") -> None:
    record = request.node.stash.get(SCENARIO_KEY, None)
    step_record = record.find(step) if record else None
    if step_record is not None:
        step_record.status = status
        step_record.error = error


# --- pytest hooks: put the records into the report ----------------------------------------


# wrapper=True: this hook wraps the others (Java: an around-advice). Everything before
# `yield` runs first, `yield` returns the report the inner hooks built.
@pytest.hookimpl(wrapper=True)
# Generator[yielded, received, returned]: yields nothing, receives the report, returns it.
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield
    record = item.stash.get(SCENARIO_KEY, None)
    report.description = describe(item, record)  # type: ignore[attr-defined]
    if record is not None and report.when == "call":
        # pytest-html reads report.extras; other plugins may already have added some.
        steps = extras.html(render_steps(record))
        report.extras = [*getattr(report, "extras", []), steps]  # type: ignore[attr-defined]
    return report


def describe(item: pytest.Item, record: ScenarioRecord | None) -> str:
    """One line that says what the test checks, for the report's Description column."""
    if record is not None:
        return f"{record.feature} > {record.scenario}"
    function = getattr(item, "function", None)  # pytest.Function has it, other items don't
    doc = function.__doc__ if function else None
    return doc.strip().splitlines()[0] if doc else ""


def render_steps(record: ScenarioRecord) -> str:
    """The scenario's steps as a small HTML table. Every value is escaped."""
    rows = []
    for step in record.steps:
        colour = _STATUS_COLOURS.get(step.status, "inherit")
        error = f"<br><small>{html.escape(step.error)}</small>" if step.error else ""
        rows.append(
            f"<tr><td><b>{html.escape(step.keyword)}</b> {html.escape(step.text)}{error}</td>"
            f'<td style="color:{colour};font-weight:bold">{step.status}</td></tr>'
        )
    return (
        f"<p><b>Feature:</b> {html.escape(record.feature)}<br>"
        f"<b>Scenario:</b> {html.escape(record.scenario)}</p>"
        f'<table style="border-collapse:collapse">{"".join(rows)}</table>'
    )


# --- pytest-html hooks: title, environment, Description column ----------------------------


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report: object) -> None:
    report.title = "qakit test report"  # type: ignore[attr-defined]


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells: list[str]) -> None:
    cells.insert(2, "<th>Description</th>")


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report: pytest.TestReport, cells: list[str]) -> None:
    cells.insert(2, f"<td>{html.escape(getattr(report, 'description', ''))}</td>")


def pytest_configure(config: pytest.Config) -> None:
    """Show which environment the run used in the report's Environment table."""
    # pytest-metadata (a pytest-html dependency) keeps that table in the config's stash.
    config.stash[metadata_key]["Environment (--env)"] = config.getoption("--env", "dev")
