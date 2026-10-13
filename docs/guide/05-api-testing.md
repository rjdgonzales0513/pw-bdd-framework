# 5. API testing

## The client

`src/qakit/apps/automationexercise/api/client.py` wraps Playwright's `APIRequestContext`
(Java: a RestAssured `RequestSpecification`). Tests get it as the `ae_api` fixture.

| Method | Endpoint | Returns | Raises `ApiError` when |
| --- | --- | --- | --- |
| `products()` | `GET /api/productsList` | `ProductsResponse` | responseCode ≠ 200 |
| `brands()` | `GET /api/brandsList` | `BrandsResponse` | responseCode ≠ 200 |
| `search_products(term)` | `POST /api/searchProduct` | `ProductsResponse` | responseCode ≠ 200 |
| `create_account(user)` | `POST /api/createAccount` | `MessageResponse` | responseCode ≠ **201** |
| `delete_account(email, pw)` | `DELETE /api/deleteAccount` | `MessageResponse` | responseCode ≠ 200 |
| `user_detail(email)` | `GET /api/getUserDetailByEmail` | `UserDetailResponse` | responseCode ≠ 200 |
| `verify_login(email, pw)` | `POST /api/verifyLogin` | `MessageResponse` | responseCode ≠ 200 |
| `send(method, path, form=, params=)` | anything | the raw JSON `dict` | **never** for a bad responseCode |

## The quirk you must know: HTTP 200 for everything

automationexercise.com answers **HTTP 200 even for errors**. The real status is in the body:

```json
{"responseCode": 405, "message": "This request method is not supported."}
```

A client that only checked the HTTP status would let every test pass. So every typed method
goes through `_expect()`. It reads `responseCode` **before** parsing the body into a model,
and raises `ApiError(endpoint, code, message)` if it isn't the expected code.

Other quirks:

- Requests send **form fields** (`form=`), not JSON (`data=`). With JSON the API answers
  "parameter is missing".
- The JSON comes with `Content-Type: text/html`; `.json()` parses it anyway.
- A search with no match is **200 with an empty list**, not 404.

## Positive tests: typed methods

```python
def test_search_finds_matching_products(ae_api: AutomationExerciseApi) -> None:
    found = ae_api.search_products("top").products     # typed: list[Product]

    assert found, "search found nothing"               # all([]) is True: guard against empty!
    for product in found:
        assert "top" in f"{product.name} {product.category.category}".lower()
```

## Negative tests: `send()`

The typed methods raise on a bad code, so they can't be used to *assert* on one. `send()`
returns the raw body without checking:

```python
body = ae_api.send("POST", "/api/productsList")
assert body["responseCode"] == 405
```

…or check that the typed method raises:

```python
with pytest.raises(ApiError) as error:
    ae_api.verify_login("nobody@example.invalid", "wrong")
assert error.value.response_code == 404
```

## Response models (pydantic)

`api/models.py` describes each response as a class (Java: a Jackson POJO / record):

```python
class ApiModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

class ApiResponse(ApiModel):
    response_code: int = Field(alias="responseCode")    # Java: @JsonProperty("responseCode")

class ProductsResponse(ApiResponse):
    products: list[Product]
```

- `frozen=True`: parsed responses can't be changed (Java: a record).
- `extra="forbid"`: an **unknown field fails parsing**. We own this contract, so we want to
  hear when the API changes. For a third-party API you only consume, use `"ignore"`.
- `price: str`: the API sends `"Rs. 500"`, a display string. Don't pretend it's a number.

## Adding an endpoint

1. Add the response model to `models.py` (or reuse `MessageResponse`).
2. Add a typed method to the client that calls `self._expect(Model, "METHOD", "/api/...",
   form=..., expected=...)`.
3. Write one positive and one negative test in `tests/automationexercise/api/`.
4. Prove the test can fail: break the expected code once and watch it go red.
