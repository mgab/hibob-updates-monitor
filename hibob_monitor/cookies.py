"""
Browser cookie extraction functionality
"""

import logging
import sys
from enum import Enum
from http.cookiejar import Cookie, CookieJar
from typing import Protocol, assert_never

from .config import AUTH_KEYWORDS

logger = logging.getLogger(__name__)

# Try to import browser_cookie3
try:
    import browser_cookie3

    BROWSER_COOKIE3_AVAILABLE = True
except ImportError:
    BROWSER_COOKIE3_AVAILABLE = False
    logger.error(
        "❌ browser_cookie3 not installed. Install it with: pip install browser_cookie3"
    )
    sys.exit(1)


class CookieExtractorCallable(Protocol):
    def __call__(
        self,
        cookie_file: str | None = None,
        domain_name: str = "",
        key_file: str | None = None,
    ) -> CookieJar: ...


class SupportedBrowser(Enum):
    """Enumeration of supported browsers."""

    FIREFOX = "firefox"
    CHROME = "chrome"
    SAFARI = "safari"
    EDGE = "edge"

    @property
    def get_cookie_jar(self) -> CookieExtractorCallable:
        match self:
            case SupportedBrowser.FIREFOX:
                return browser_cookie3.firefox  # type: ignore[no-any-return]
            case SupportedBrowser.CHROME:
                return browser_cookie3.chrome  # type: ignore[no-any-return]
            case SupportedBrowser.SAFARI:
                return browser_cookie3.safari  # type: ignore[no-any-return]
            case SupportedBrowser.EDGE:
                return browser_cookie3.edge  # type: ignore[no-any-return]
            case _:
                assert_never(self)


def _extract_domain_cookies(
    cookie_jar: CookieJar, domain: str
) -> dict[str, str | None]:
    """Extract cookies for specific domain from cookie jar."""

    def is_domain_match(cookie: Cookie) -> bool:
        return cookie.domain in {domain, f".{domain}"}

    return {
        cookie.name: cookie.value for cookie in cookie_jar if is_domain_match(cookie)
    }


def extract_cookies_from_browser(
    browser: SupportedBrowser, domain: str
) -> dict[str, str | None]:
    """Extract cookies from browser for given domain."""
    try:
        jar = browser.get_cookie_jar(domain_name=domain)
        cookies = _extract_domain_cookies(jar, domain)
        logger.info(
            "📊 Extracted %d total cookies from %s", len(cookies), browser.value.title()
        )
    except (RuntimeError, ValueError) as e:
        logger.error(
            "❌ Failed to extract cookies from %s: %s", browser.value.title(), e
        )
        if browser == SupportedBrowser.FIREFOX:
            logger.info("💡 Make sure Firefox is closed or try using --browser chrome")
        elif browser == SupportedBrowser.CHROME:
            logger.info("💡 You may need to grant keychain access on macOS")
        return {}
    else:
        return cookies


def _is_auth_cookie_by_name(name: str) -> bool:
    """Check if cookie name suggests authentication."""
    return any(keyword in name.lower() for keyword in AUTH_KEYWORDS)


def _is_auth_cookie_by_value(value: str) -> bool:
    """Check if cookie value looks like a session token."""
    min_key_length = 32
    return len(value) > min_key_length and any(c.isalnum() for c in value)


def filter_auth_cookies(cookies: dict[str, str | None]) -> dict[str, str]:
    """Filter cookies to keep only authentication-related ones."""
    auth_cookies = {
        name: value
        for name, value in cookies.items()
        if value is not None
        and (_is_auth_cookie_by_name(name) or _is_auth_cookie_by_value(value))
    }

    # If no specific auth cookies found, use all cookies (might be custom naming)
    max_cookies = 10
    if not auth_cookies and len(cookies) <= max_cookies:
        auth_cookies = {
            name: value for name, value in cookies.items() if value is not None
        }

    return auth_cookies
