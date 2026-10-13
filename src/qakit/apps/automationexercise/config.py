"""Settings for https://automationexercise.com, loaded from envs/automationexercise/<env>.env."""

from pydantic import HttpUrl, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


# Java: @ConfigurationProperties(prefix = "ae") @Validated on a record.
# Import BaseSettings from pydantic_settings, never pydantic.v1: that's the old Pydantic 1
# class, which ignores model_config and doesn't satisfy load_settings' [S: BaseSettings].
class AutomationExerciseSettings(BaseSettings):
    """Typed settings; every field is required, so a missing key fails at startup."""

    # model_config is class-level configuration (the annotation in the Java version).
    # env_prefix: field timeout_ms is read from key AE_TIMEOUT_MS (case-insensitive).
    # Keys with the prefix that match no field are rejected (BaseSettings forbids extras),
    # so a typo like AE_URL fails loudly instead of being ignored.
    # env_file_encoding: Windows may otherwise read the file in the system code page.
    model_config = SettingsConfigDict(env_prefix="AE_", env_file_encoding="utf-8")

    # No defaults on purpose: a missing or misspelled key stops the run before the first
    # test, instead of quietly using a default value (fail fast).
    # .env values are always strings; pydantic converts and validates them.
    env_name: str  # dev / ci: lets tests prove which file was loaded
    # HttpUrl validates the URL but is not a str, and always ends in "/".
    # Use str(settings.base_url) where Playwright needs a string; start paths with "/".
    base_url: HttpUrl
    timeout_ms: PositiveInt  # rejects "abc", 0 and negatives (Java: @Positive int)
