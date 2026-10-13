"""Test users built with Faker. Pure data: nothing here talks to the application.

    build_user(faker)                       a full random user
    build_user(faker, country="Canada")     random, except the field the test cares about

Creating users in the application (and deleting them again) is registry.py's job.
"""

from dataclasses import asdict, dataclass, replace
from typing import Any, Literal
from uuid import uuid4

from faker import Faker

# The only countries the signup form offers (its <select>). The API accepts any string, but a
# user built here must also work for a UI signup.
COUNTRIES = ("India", "United States", "Canada", "Australia", "Israel", "New Zealand", "Singapore")


# frozen=True: no field can change after creation (Java: a record). Make a changed copy with
# replace(user, city="X") (Java: user.toBuilder().city("X").build()).
@dataclass(frozen=True)
class NewUser:
    """Everything the signup form and POST /api/createAccount ask for."""

    name: str
    email: str
    password: str
    title: Literal["Mr", "Mrs"]  # only these two values type-check (Java: an enum)
    birth_day: int
    birth_month: int
    birth_year: int
    first_name: str
    last_name: str
    company: str
    address1: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str
    mobile_number: str

    def to_form(self) -> dict[str, str | float | bool]:
        """The createAccount form fields. The API's names differ from ours in three places."""
        # asdict: every field as a dict (Java: objectMapper.convertValue(user, Map.class)).
        form: dict[str, str | float | bool] = {k: str(v) for k, v in asdict(self).items()}
        form["birth_date"] = form.pop("birth_day")
        form["firstname"] = form.pop("first_name")
        form["lastname"] = form.pop("last_name")
        return form


def build_user(faker: Faker, **overrides: Any) -> NewUser:
    """A NewUser filled with Faker data; keyword arguments replace single fields.

    Every field is generated even when overridden, so a fixed seed always gives the same
    values for the fields that were NOT overridden.
    """
    first_name, last_name = faker.first_name(), faker.last_name()
    user = NewUser(
        name=f"{first_name} {last_name}",
        # NOT faker.email(): pytest's `faker` fixture is reseeded to 0 for every test, so it
        # would hand out the same address in every run, and this site is shared by everyone
        # who practises on it. A uuid is unique per call, whatever the seed.
        email=f"qakit.{uuid4().hex[:12]}@example.com",
        password=faker.password(length=12),
        title=faker.random_element(("Mr", "Mrs")),
        birth_day=faker.random_int(1, 28),  # 28: valid in every month
        birth_month=faker.random_int(1, 12),
        birth_year=faker.random_int(1950, 2005),
        first_name=first_name,
        last_name=last_name,
        company=faker.company(),
        address1=faker.street_address(),
        address2=faker.secondary_address(),
        country=faker.random_element(COUNTRIES),
        state=faker.state(),
        city=faker.city(),
        zipcode=faker.postcode(),
        mobile_number=faker.msisdn(),
    )
    # A typo like frist_name="x" raises TypeError here: replace() checks the field names.
    return replace(user, **overrides)
