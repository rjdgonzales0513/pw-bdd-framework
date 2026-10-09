"""Settings load per --env, reject bad values, and let real env vars override the file."""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from qakit.apps.automationexercise.config import AutomationExerciseSettings
from qakit.core.config import load_settings


# Function-scoped (the default): rebuilt for every test that asks for it.
# It depends on two other fixtures, like a Spring bean with constructor injection:
# envs_root comes from qakit.core.plugin, monkeypatch is built into pytest.
@pytest.fixture
def ae_dir(envs_root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """This app's envs folder, with any AE_* vars from the shell removed for the test."""
    # A real AE_TIMEOUT_MS in the shell (or in CI) beats the .env file and would make the
    # file-loading tests fail on that machine only. monkeypatch puts the vars back after
    # the test, even when it fails (Java: a try/finally restoring the environment).
    # list(...) copies the keys first: deleting from a dict while looping over it raises
    # an error, like Java's ConcurrentModificationException.
    for name in list(os.environ):
        if name.upper().startswith("AE_"):
            monkeypatch.delenv(name)
    return envs_root / "automationexercise"


def test_settings_fixture_follows_env_option(
    settings: AutomationExerciseSettings, pytestconfig: pytest.Config
) -> None:
    # Compare with the raw option, not with the env_name fixture: settings is built from
    # env_name, so comparing the two would pass even if env_name ignored --env.
    assert settings.env_name == pytestconfig.getoption("--env")


# Java: @ParameterizedTest + @CsvSource({"dev, 10000", "ci, 30000"}).
# Each tuple becomes its own test: test_each_env_file_loads[dev-10000], [ci-30000].
@pytest.mark.parametrize(("env", "timeout_ms"), [("dev", 10_000), ("ci", 30_000)])
def test_each_env_file_loads(ae_dir: Path, env: str, timeout_ms: int) -> None:
    # Calls load_settings directly: the session-scoped settings fixture only ever holds
    # the one env chosen with --env.
    loaded = load_settings(AutomationExerciseSettings, env, ae_dir)

    assert loaded.env_name == env
    assert loaded.timeout_ms == timeout_ms  # differs per file: proves which file was read
    # HttpUrl is not a str and always ends in "/", so convert before comparing.
    assert str(loaded.base_url) == "https://automationexercise.com/"


def test_unknown_env_names_the_missing_file(ae_dir: Path) -> None:
    # Java: assertThrows(FileNotFoundException.class, ...) plus a check on the message.
    # match is a regex searched in the message; r"..." is a raw string, \. is a literal dot.
    with pytest.raises(FileNotFoundError, match=r"nope\.env"):
        load_settings(AutomationExerciseSettings, "nope", ae_dir)


def test_real_env_var_overrides_file(ae_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Precedence: real env var > .env file. CI relies on this to inject values in M7.
    monkeypatch.setenv("AE_TIMEOUT_MS", "12345")

    loaded = load_settings(AutomationExerciseSettings, "dev", ae_dir)

    assert loaded.timeout_ms == 12_345  # dev.env says 10000, the env var wins


# "abc" checks the int conversion; "0" and "-5" check PositiveInt.
@pytest.mark.parametrize("bad_timeout", ["abc", "0", "-5"])
def test_invalid_timeout_is_rejected(
    ae_dir: Path, monkeypatch: pytest.MonkeyPatch, bad_timeout: str
) -> None:
    monkeypatch.setenv("AE_TIMEOUT_MS", bad_timeout)

    # match="timeout_ms": the error must be about this field, not any validation error.
    with pytest.raises(ValidationError, match="timeout_ms"):
        load_settings(AutomationExerciseSettings, "dev", ae_dir)