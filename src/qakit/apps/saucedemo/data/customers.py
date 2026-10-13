"""Checkout customers built with Faker (ported from the training repo's ex17)."""

from dataclasses import dataclass, replace

from faker import Faker


@dataclass(frozen=True)
class Customer:
    """What the checkout form asks for."""

    first_name: str
    last_name: str
    postal_code: str


def build_customer(faker: Faker, **overrides: str) -> Customer:
    """A Customer with Faker data; keyword arguments replace single fields.

    build_customer(faker, first_name="") is the whole point of a "missing first name" test,
    and the only thing that test has to say.
    """
    customer = Customer(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        postal_code=faker.postcode(),
    )
    return replace(customer, **overrides)
