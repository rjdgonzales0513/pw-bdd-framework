@ui @checkout
Feature: Checkout
  A logged-in shopper buys what is in the cart.

  Background:
    Given a logged-in shopper with "Sauce Labs Backpack" in the cart

  @smoke
  Scenario: A complete order
    When the shopper checks out as a generated customer
    Then the order is confirmed with "Thank you for your order!"

  Scenario Outline: A missing detail is reported
    When the shopper checks out without a <field>
    Then the shopper is told "<message>"

    Examples:
      | field       | message                        |
      | first_name  | Error: First Name is required  |
      | last_name   | Error: Last Name is required   |
      | postal_code | Error: Postal Code is required |
