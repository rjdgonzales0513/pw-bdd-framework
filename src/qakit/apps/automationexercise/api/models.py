"""Response models for the automationexercise.com API (https://automationexercise.com/api_list).

Every body carries its real status in ``responseCode``; the HTTP status is always 200.
"""

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Base for all models: immutable, and unknown JSON fields are an error."""

    # frozen=True: fields can't be reassigned after parsing (Java: a record).
    # extra="forbid": an unexpected field fails parsing (Jackson's default,
    # FAIL_ON_UNKNOWN_PROPERTIES = true). A test framework wants to hear about contract changes.
    model_config = ConfigDict(frozen=True, extra="forbid")


class UserType(ApiModel):
    # The API nests this twice: "category": {"usertype": {"usertype": "Women"}}.
    usertype: str


class Category(ApiModel):
    usertype: UserType
    category: str


class Product(ApiModel):
    id: int
    name: str
    price: str  # "Rs. 500": a display string, not a number
    brand: str
    category: Category


class Brand(ApiModel):
    id: int
    brand: str


class ApiResponse(ApiModel):
    """Fields every response has."""

    # alias = the JSON name (Java: @JsonProperty("responseCode")).
    response_code: int = Field(alias="responseCode")


class ProductsResponse(ApiResponse):
    """GET /api/productsList, POST /api/searchProduct."""

    products: list[Product]


class BrandsResponse(ApiResponse):
    """GET /api/brandsList."""

    brands: list[Brand]


class MessageResponse(ApiResponse):
    """A reply that only carries a message: errors, verifyLogin, createAccount, ..."""

    message: str


class UserDetail(ApiModel):
    # Field names differ from the createAccount form (birth_date there, birth_day here;
    # firstname there, first_name here). The API is inconsistent; the models follow it.
    id: int
    name: str
    email: str
    title: str
    birth_day: str
    birth_month: str
    birth_year: str
    first_name: str
    last_name: str
    company: str
    address1: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str


class UserDetailResponse(ApiResponse):
    """GET /api/getUserDetailByEmail."""

    user: UserDetail
