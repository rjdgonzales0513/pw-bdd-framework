"""Client for the automationexercise.com API (https://automationexercise.com/api_list).

The HTTP status is always 200; the real status is ``responseCode`` in the JSON body.
Typed methods check it and raise ApiError; ``send()`` returns the raw body for negative tests.
"""

from typing import Any

from playwright.sync_api import APIRequestContext

from qakit.apps.automationexercise.api.models import (
    ApiResponse,
    BrandsResponse,
    MessageResponse,
    ProductsResponse,
    UserDetailResponse,
)
from qakit.apps.automationexercise.data.users import NewUser

# What Playwright's form= and params= accept. dict is invariant, so a dict[str, str] parameter
# type would not be accepted by Playwright's signature; declaring the full value union avoids it.
type Fields = dict[str, str | float | bool]


class ApiError(Exception):
    """The API answered, but ``responseCode`` was not the expected one."""

    # Java: class ApiError extends RuntimeException, with getters for code and message.
    def __init__(self, endpoint: str, response_code: int, message: str) -> None:
        super().__init__(f"{endpoint} returned responseCode {response_code}: {message}")
        self.endpoint = endpoint
        self.response_code = response_code
        self.message = message


class AutomationExerciseApi:
    """One method per endpoint. Paths start with "/": base_url ends with one."""

    # The context is passed in, not created here (Java: inject the RequestSpecification).
    # The fixture that creates it also disposes it; the client never owns its lifetime.
    def __init__(self, request: APIRequestContext) -> None:
        self._request = request  # leading _ = private by convention (no real `private`)

    def send(
        self, method: str, path: str, *, form: Fields | None = None, params: Fields | None = None
    ) -> dict[str, Any]:
        """Call an endpoint and return the JSON body. Does NOT check ``responseCode``."""
        # The * makes form and params keyword-only: send("POST", path, form={...}).
        # fetch() takes the method as a string (Java: given().formParams(..).request(method)).
        # form= sends application/x-www-form-urlencoded, which this API needs; data= would
        # send JSON and the API would answer "parameter is missing".
        response = self._request.fetch(path, method=method, form=form, params=params)
        # Always 200 for real answers; anything else means the server itself is broken.
        if not response.ok:
            raise ApiError(path, response.status, f"HTTP {response.status} {response.status_text}")
        # .json() parses even though the API sends Content-Type: text/html. It returns Any;
        # the isinstance check narrows it to a dict for mypy and catches non-object bodies.
        body = response.json()
        if not isinstance(body, dict):
            raise ApiError(path, -1, f"expected a JSON object, got {type(body).__name__}")
        return body

    # --- products ------------------------------------------------------------------------

    def products(self) -> ProductsResponse:
        """GET /api/productsList: all products."""
        return self._expect(ProductsResponse, "GET", "/api/productsList")

    def brands(self) -> BrandsResponse:
        """GET /api/brandsList: all brands."""
        return self._expect(BrandsResponse, "GET", "/api/brandsList")

    def search_products(self, term: str) -> ProductsResponse:
        """POST /api/searchProduct. No match gives responseCode 200 with an empty list."""
        form: Fields = {"search_product": term}
        return self._expect(ProductsResponse, "POST", "/api/searchProduct", form=form)

    # --- accounts ------------------------------------------------------------------------

    def create_account(self, user: NewUser) -> MessageResponse:
        """POST /api/createAccount. Answers 201 "User created!"."""
        return self._expect(
            MessageResponse, "POST", "/api/createAccount", form=user.to_form(), expected=201
        )

    def delete_account(self, email: str, password: str) -> MessageResponse:
        """DELETE /api/deleteAccount. Raises ApiError(404) when the user does not exist."""
        form: Fields = {"email": email, "password": password}
        return self._expect(MessageResponse, "DELETE", "/api/deleteAccount", form=form)

    def user_detail(self, email: str) -> UserDetailResponse:
        """GET /api/getUserDetailByEmail. Raises ApiError(404) when the user does not exist."""
        params: Fields = {"email": email}
        return self._expect(UserDetailResponse, "GET", "/api/getUserDetailByEmail", params=params)

    def verify_login(self, email: str, password: str) -> MessageResponse:
        """POST /api/verifyLogin. Raises ApiError(404) when the user does not exist."""
        form: Fields = {"email": email, "password": password}
        return self._expect(MessageResponse, "POST", "/api/verifyLogin", form=form)

    # --- the one place that checks responseCode ------------------------------------------

    # [M: ApiResponse] is a generic method (Java: <M extends ApiResponse> M expect(Class<M>)).
    # The caller passes the class; mypy then knows products() returns a ProductsResponse.
    def _expect[M: ApiResponse](
        self,
        model: type[M],
        method: str,
        path: str,
        *,
        form: Fields | None = None,
        params: Fields | None = None,
        expected: int = 200,
    ) -> M:
        body = self.send(method, path, form=form, params=params)
        # Check the code BEFORE parsing: an error body has no "products", so parsing it into
        # ProductsResponse first would hide the real cause behind a "Field required" error.
        code = body.get("responseCode")
        if code != expected:
            raise ApiError(path, code if isinstance(code, int) else -1, str(body.get("message")))
        return model.model_validate(body)
