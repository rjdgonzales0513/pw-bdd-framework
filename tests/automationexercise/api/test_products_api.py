"""Products, brands and search through the REST API (no browser)."""

import pytest

from qakit.apps.automationexercise.api.client import ApiError, AutomationExerciseApi

# Applies the marker to every test in this module: `pytest -m api` selects them.
pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_products_list_returns_products(ae_api: AutomationExerciseApi) -> None:
    """GET /api/productsList returns a non-empty, parsed product list."""
    products = ae_api.products().products

    assert products, "the catalogue should not be empty"
    assert all(product.price.startswith("Rs. ") for product in products)


def test_brands_list_returns_brands(ae_api: AutomationExerciseApi) -> None:
    """GET /api/brandsList returns every brand used by a product."""
    brands = {brand.brand for brand in ae_api.brands().brands}
    used = {product.brand for product in ae_api.products().products}

    # <= on sets is "is a subset of" (Java: brands.containsAll(used)).
    assert used <= brands


# Java: @ParameterizedTest @ValueSource(strings = {"top", "TSHIRT", "jean"}).
@pytest.mark.parametrize("term", ["top", "TSHIRT", "jean"])
def test_search_finds_matching_products(ae_api: AutomationExerciseApi, term: str) -> None:
    """POST /api/searchProduct returns only products whose name or category match."""
    found = ae_api.search_products(term).products

    # Without this line the test would pass on an empty list: all([]) is True.
    assert found, f"search for {term!r} found nothing"
    for product in found:
        haystack = f"{product.name} {product.category.category}".lower()
        assert term.lower() in haystack, f"{product.name} does not match {term!r}"


def test_search_without_match_returns_empty_list(ae_api: AutomationExerciseApi) -> None:
    """No match is still responseCode 200, with an empty list."""
    assert ae_api.search_products("no-such-product-zzz").products == []


# The negative cases use send(): it returns the body without checking responseCode, so the
# test can assert on the code itself. Typed methods would raise before the assert.
@pytest.mark.parametrize(
    ("method", "path", "code", "message"),
    [
        ("POST", "/api/productsList", 405, "This request method is not supported."),
        ("PUT", "/api/brandsList", 405, "This request method is not supported."),
        ("POST", "/api/searchProduct", 400, "Bad request, search_product parameter is missing"),
    ],
    ids=["POST productsList", "PUT brandsList", "search without term"],
)
def test_error_codes_are_in_the_body(
    ae_api: AutomationExerciseApi, method: str, path: str, code: int, message: str
) -> None:
    """The HTTP status is 200 even for errors; the real code is responseCode."""
    body = ae_api.send(method, path)

    assert body["responseCode"] == code
    assert body["message"].startswith(message)


def test_typed_method_raises_on_error_code(ae_api: AutomationExerciseApi) -> None:
    """The typed methods turn a bad responseCode into an ApiError."""
    with pytest.raises(ApiError) as error:
        ae_api.verify_login("nobody@example.invalid", "wrong")

    assert error.value.response_code == 404
    assert error.value.message == "User not found!"
