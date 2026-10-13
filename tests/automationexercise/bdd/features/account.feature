@ui @account
Feature: Customer accounts
  Shoppers create an account once, then log in to see their details and buy faster.

  @smoke
  Scenario: A registered shopper logs in
    Given a registered shopper
    When the shopper logs in
    Then the shopper is welcomed by name

  Scenario: A wrong password is refused
    Given a registered shopper
    When the shopper logs in with a wrong password
    Then the shopper is told the login details are incorrect
    And the shopper is not logged in

  Scenario: A new shopper signs up
    Given a new shopper without an account
    When the shopper signs up
    Then the account is created
    And the shopper is welcomed by name

  Scenario: An email address can only be registered once
    Given a registered shopper
    When someone else signs up with the same email address
    Then they are told the email address is already registered
