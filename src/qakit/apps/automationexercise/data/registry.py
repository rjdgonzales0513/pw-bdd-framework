"""Users created in the application for one test, and deleted again afterwards.

    with UserRegistry(api, faker) as users:
        user = users.create()               created through the API
    # every user is deleted here, even when the block raised

Kept apart from users.py so the API client can import NewUser without an import cycle
(client -> users, registry -> client).
"""

from types import TracebackType
from typing import Any, Self

from faker import Faker

from qakit.apps.automationexercise.api.client import ApiError, AutomationExerciseApi
from qakit.apps.automationexercise.data.users import NewUser, build_user


class UserRegistry:
    """Creates users through the API and deletes every one of them on ``close()``.

    Java: a JUnit 5 extension whose afterEach deletes what the test created. The pytest
    fixture ``user_factory`` wraps this class; the class itself is plain Python, so it can
    also be used (and tested) with ``with UserRegistry(api, faker) as users: ...``.
    """

    def __init__(self, api: AutomationExerciseApi, faker: Faker) -> None:
        self._api = api
        self._faker = faker
        self._users: list[NewUser] = []

    @property
    def users(self) -> tuple[NewUser, ...]:
        """The users this registry will delete, oldest first (read-only copy)."""
        return tuple(self._users)

    def create(self, **overrides: Any) -> NewUser:
        """Build a user, create it through the API, and remember it for cleanup."""
        user = build_user(self._faker, **overrides)
        self._api.create_account(user)
        self._users.append(user)
        return user

    def track(self, user: NewUser) -> NewUser:
        """Remember a user created some other way (a UI signup) so it is deleted too."""
        self._users.append(user)
        return user

    def close(self) -> None:
        """Delete every user. A user the test already deleted (404) is fine."""
        errors: list[str] = []
        # Newest first, like a stack of try/finally blocks unwinding.
        for user in reversed(self._users):
            try:
                self._api.delete_account(user.email, user.password)
            except ApiError as error:
                if error.response_code != 404:
                    errors.append(str(error))  # keep going: delete the others first
        self._users.clear()
        if errors:
            raise RuntimeError("Could not delete test users:\n" + "\n".join(errors))

    # `with UserRegistry(...) as users:` calls these two (Java: AutoCloseable + try-with-resources).
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
