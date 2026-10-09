
"""qakit's pytest plugin: options and fixtures every app uses. Knows no application.

Registered via [project.entry-points.pytest11] in pyproject.toml, so pytest loads it
automatically in any project where qakit is installed (Java: META-INF/services + ServiceLoader).
Entry points are install metadata: after editing them, run pip install -e . again.
"""

from pathlib import Path

import pytest


# A hook: pytest calls it because of its exact name, there is no decorator or interface.
# A typo in the name (pytest_add_option) means it is silently never called.
# Runs once at startup, before the command line is parsed.
def pytest_addoption(parser: pytest.Parser) -> None:
    """Add ``--env``: which ``envs/<app>/<env>.env`` file to load."""
    # The group puts the option under a "qakit:" heading in pytest --help.
    group = parser.getgroup("qakit")
    group.addoption(
        "--env",
        default="dev",  # plain `pytest` runs against dev; CI passes --env ci explicitly
        # No choices=[...]: core doesn't know which envs each app has. load_settings checks
        # that envs/<app>/<env>.env exists, per app.
        help="environment to run against, e.g. dev or ci (default: dev)",
    )


# scope="session": built once per run and shared by every test (Java: a static field set in
# @BeforeAll, or a singleton bean). --env can't change mid-run, so once is enough.
# pytestconfig is a built-in fixture holding the run's configuration.
@pytest.fixture(scope="session")
def env_name(pytestconfig: pytest.Config) -> str:
    """The value of ``--env``."""
    # getoption returns Any; mypy strict rejects returning Any from a "-> str" function.
    # str(...) makes it a real str (Java: (String) config.get("env"), but checked at runtime).
    return str(pytestconfig.getoption("--env"))


@pytest.fixture(scope="session")
def envs_root(pytestconfig: pytest.Config) -> Path:
    """The ``envs/`` folder at the project root (pytest's rootdir, not the cwd)."""
    # rootpath is the folder with pyproject.toml, wherever pytest is started from.
    # Not Path.cwd() (breaks when run from a subfolder) and not Path(__file__) (points into
    # the installed package, wrong once qakit is installed without -e).
    return pytestconfig.rootpath / "envs"