"""Generic settings loader. Knows no application: each app passes its own Settings class.

Rule from ADR 0001: nothing in qakit.core imports from qakit.apps.
"""

from pathlib import Path

from pydantic_settings import BaseSettings


# [S: BaseSettings] makes this generic, Java: <S extends BaseSettings> S load(Class<S> cls, ...).
# type[S] is the class itself (Java: Class<S>), and -> S tells mypy the result is that same
# class, so callers get AutomationExerciseSettings with its fields, not a bare BaseSettings.
def load_settings[S: BaseSettings](settings_cls: type[S], env: str, envs_dir: Path) -> S:
    """Load ``settings_cls`` from ``envs_dir/<env>.env``; real env vars override the file."""
    # Path's / operator joins paths (Java: envsDir.resolve(env + ".env")).
    env_file = envs_dir / f"{env}.env"
    # pydantic-settings silently ignores a missing _env_file and then reports "Field required"
    # for every field, without naming the file. Fail here with the full path instead.
    # is_file(), not exists(): a folder called nope.env must fail too.
    if not env_file.is_file():
        raise FileNotFoundError(f"No settings file for env '{env}': {env_file.resolve()}")
    # Calling the class creates an instance (no "new"). _env_file is a pydantic-settings
    # constructor option, not a field; the pydantic.mypy plugin lets mypy accept it.
    # Precedence, highest first: constructor args > real env vars > .env file > defaults.
    return settings_cls(_env_file=env_file)
