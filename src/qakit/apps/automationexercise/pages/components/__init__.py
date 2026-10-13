"""Component objects: parts that appear on several pages (Java: a WebComponent class)."""

from qakit.apps.automationexercise.pages.components.cart_modal import CartModal
from qakit.apps.automationexercise.pages.components.header import Header

# __all__ lists what this package exports, so ruff knows the imports above are used.
__all__ = ["CartModal", "Header"]
