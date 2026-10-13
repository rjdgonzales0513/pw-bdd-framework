"""Page objects for automationexercise.com: one class per page, plus shared components."""

from qakit.apps.automationexercise.pages.base_page import BasePage
from qakit.apps.automationexercise.pages.cart_page import CartPage
from qakit.apps.automationexercise.pages.home_page import HomePage
from qakit.apps.automationexercise.pages.login_page import LoginPage
from qakit.apps.automationexercise.pages.products_page import ProductsPage
from qakit.apps.automationexercise.pages.signup_page import SignupPage

__all__ = ["BasePage", "CartPage", "HomePage", "LoginPage", "ProductsPage", "SignupPage"]
