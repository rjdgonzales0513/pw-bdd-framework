"""Settings for https://www.saucedemo.com, loaded from envs/saucedemo/<env>.env."""

from pydantic import HttpUrl, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SauceDemoSettings(BaseSettings):
    """Typed settings; every field is required, so a missing key fails at startup."""

    # SD_ prefix: keys from another app's file (AE_...) can never be read by mistake.
    model_config = SettingsConfigDict(env_prefix="SD_", env_file_encoding="utf-8")

    env_name: str
    base_url: HttpUrl
    timeout_ms: PositiveInt
    username: str
    # SecretStr prints as '**********' in logs, reprs and error messages. Read the real
    # value with .get_secret_value(). For a real app, pass it in as an env var from the
    # CI secret store instead of writing it in the .env file.
    password: SecretStr
