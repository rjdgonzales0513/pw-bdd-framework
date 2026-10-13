@ui @shopping
Feature: Shopping
  Shoppers find products and collect them in their cart before checking out.

  @smoke
  Scenario: A logged-in shopper puts a product in the cart
    Given a logged-in shopper
    When the shopper adds "Blue Top" to the cart
    Then the cart contains "Blue Top"

  Scenario: Removing the only product empties the cart
    Given a guest shopper with "Men Tshirt" in the cart
    When the shopper removes "Men Tshirt" from the cart
    Then the cart is empty

  Scenario Outline: Searching shows the matching products
    Given a guest shopper
    When the shopper searches for "<term>"
    Then the products matching "<term>" are shown

    Examples:
      | term   |
      | top    |
      | jean   |
      | saree  |
