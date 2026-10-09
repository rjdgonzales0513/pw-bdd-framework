
"""Fixtures for automationexercise tests. pytest finds this file by its name and shows its
fixtures only to tests in this folder and below, so other apps never see them.

This is the one place that knows both core (load_settings) and the app (its Settings class)
and wires them together (Java: a Spring @Configuration class).
"""

from pathlib import Path

import pytest

from qakit.apps.automationexercise.config import AutomationExerciseSettings
from qakit.core.config import load_settings


# Session-scoped: the file is read once per run. env_name and envs_root are session
# fixtures from qakit.core.plugin; a fixture may only depend on fixtures with the same
# or a wider scope.
# Tests that change env vars with monkeypatch must call load_settings themselves:
# this fixture is built before they run and is never rebuilt.
@pytest.fixture(scope="session")
def settings(env_name: str, envs_root: Path) -> AutomationExerciseSettings:
    """The settings for the env chosen with ``--env``."""
    return load_settings(AutomationExerciseSettings, env_name, envs_root / "automationexercise")