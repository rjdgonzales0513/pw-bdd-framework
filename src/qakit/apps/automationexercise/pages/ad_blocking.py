"""Keep ads and the consent dialog out of UI tests.

automationexercise.com loads Google ads (googlesyndication, doubleclick, fundingchoices).
They slow pages down, cover buttons, and pop a consent dialog that blocks clicks at random.
Instead of maintaining a list of ad hosts, we allow only the site itself: every request to
another host is aborted before it leaves the browser.
"""

from urllib.parse import urlparse

from playwright.sync_api import BrowserContext, Route


def allow_only_own_host(context: BrowserContext, host: str) -> None:
    """Abort every request whose host isn't ``host`` or one of its subdomains."""

    # A closure: the inner function remembers `host` from the outer call (Java: a lambda
    # capturing an effectively-final variable).
    def handle(route: Route) -> None:
        request_host = urlparse(route.request.url).hostname or ""
        if request_host == host or request_host.endswith("." + host):
            route.continue_()  # continue_ with _: `continue` is a Python keyword
        else:
            route.abort()

    # context.route, not page.route: it covers every page and popup the context opens.
    # "**/*" matches every URL (Java: a Selenium 4 network interceptor with a catch-all filter).
    context.route("**/*", handle)
