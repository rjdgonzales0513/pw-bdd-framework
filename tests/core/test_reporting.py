"""The reporting plugin: step records, HTML rendering, and a real pytest-html report."""

import html

import pytest

from qakit.core.reporting import ScenarioRecord, StepRecord, render_steps


def test_render_steps_shows_every_status() -> None:
    record = ScenarioRecord(
        "Checkout",
        "A complete order",
        [
            StepRecord("Given", "a cart", "passed"),
            StepRecord("When", "I pay", "failed", "AssertionError: boom"),
            StepRecord("Then", "I see a receipt"),  # default status: never reached
        ],
    )

    rendered = render_steps(record)

    assert "<b>Given</b> a cart" in rendered
    assert ">passed<" in rendered
    assert ">failed<" in rendered
    assert "AssertionError: boom" in rendered
    assert ">not run<" in rendered


def test_render_steps_escapes_html() -> None:
    """Step text comes from .feature files and exceptions: it must not inject markup."""
    record = ScenarioRecord("F", "S", [StepRecord("Given", "<script>alert(1)</script>")])

    rendered = render_steps(record)

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


# pytester runs a whole pytest session on a throw-away project, like a test harness for a
# Maven plugin. runpytest_subprocess: a separate process, because Playwright's sync API can't
# start a second time inside this process.
def test_failed_scenario_lists_its_steps_in_the_html_report(pytester: pytest.Pytester) -> None:
    pytester.makefile(
        ".feature",
        demo="""
Feature: Demo feature
  Scenario: Second step fails
    Given a passing step
    When a failing step
    Then a step that never runs
""",
    )
    pytester.makepyfile(
        test_demo="""
from pytest_bdd import given, scenarios, then, when

scenarios("demo.feature")

@given("a passing step")
def _():
    pass

@when("a failing step")
def _():
    raise AssertionError("boom")

@then("a step that never runs")
def _():
    pass
"""
    )

    result = pytester.runpytest_subprocess("--html=report.html", "--self-contained-html")

    result.assert_outcomes(failed=1)
    report = (pytester.path / "report.html").read_text(encoding="utf-8")
    assert "qakit test report" in report
    # pytest-html stores the results as HTML-escaped JSON inside the page: unescape first.
    text = html.unescape(report)
    for expected in (
        "<b>Feature:</b> Demo feature",
        "<b>Given</b> a passing step",
        # The failed step's own row: the error under the step text, then "failed". (The bare
        # message isn't enough: it is also in the report's traceback section.)
        "a failing step<br><small>AssertionError: boom</small>",
        ">failed<",
        ">not run<",
    ):
        assert expected in text, f"{expected!r} missing from the report"
