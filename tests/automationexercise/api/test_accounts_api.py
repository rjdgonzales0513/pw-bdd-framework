"""Accounts through the REST API, and the user factory's cleanup (M3)."""

import pytest
from faker import Faker

from qakit.apps.automationexercise.api.client import ApiError, AutomationExerciseApi
from qakit.apps.automationexercise.data.registry import UserRegistry
from qakit.apps.automationexercise.data.users import NewUser

pytestmark = [pytest.mark.api, pytest.mark.account]


@pytest.mark.smoke
def test_verify_login_with_valid_credentials(
    ae_api: AutomationExerciseApi, registered_user: NewUser
) -> None:
    """POST /api/verifyLogin accepts a user created through the API."""
    assert ae_api.verify_login(registered_user.email, registered_user.password).message == (
        "User exists!"
    )


def test_verify_login_with_wrong_password(
    ae_api: AutomationExerciseApi, registered_user: NewUser
) -> None:
    """A wrong password is responseCode 404, like an unknown user."""
    body = ae_api.send(
        "POST", "/api/verifyLogin", form={"email": registered_user.email, "password": "wrong"}
    )

    assert body == {"responseCode": 404, "message": "User not found!"}


def test_verify_login_without_email(ae_api: AutomationExerciseApi) -> None:
    """A missing parameter is responseCode 400."""
    body = ae_api.send("POST", "/api/verifyLogin", form={"password": "x"})

    assert body["responseCode"] == 400


def test_user_detail_matches_what_was_created(
    ae_api: AutomationExerciseApi, registered_user: NewUser
) -> None:
    """GET /api/getUserDetailByEmail returns the data the user was created with."""
    detail = ae_api.user_detail(registered_user.email).user

    assert detail.email == registered_user.email
    assert detail.name == registered_user.name
    assert detail.first_name == registered_user.first_name
    assert detail.country == registered_user.country
    assert detail.birth_year == str(registered_user.birth_year)


def test_registry_deletes_every_user_it_created(ae_api: AutomationExerciseApi) -> None:
    """M3: a test creates 3 users, and none of them is left behind afterwards."""
    # The registry is used directly here (not the user_factory fixture), so the test can
    # look at the application AFTER the cleanup has run.
    with UserRegistry(ae_api, Faker()) as users:
        created = [users.create() for _ in range(3)]  # list comprehension: 3 users
        for user in created:
            assert ae_api.user_detail(user.email).user.email == user.email  # they exist

    for user in created:
        with pytest.raises(ApiError) as error:
            ae_api.user_detail(user.email)
        assert error.value.response_code == 404, f"{user.email} was left behind"
