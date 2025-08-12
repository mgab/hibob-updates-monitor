"""
Browser cookie extraction functionality
"""

import logging
import sys
from enum import Enum
from typing import Dict, Callable, assert_never
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


class SupportedBrowser(Enum):
    """Enumeration of supported browsers."""

    FIREFOX = "firefox"
    CHROME = "chrome"
    SAFARI = "safari"
    EDGE = "edge"

    @property
    def get_cookie_jar(self) -> Callable:
        match self:
            case SupportedBrowser.FIREFOX:
                return browser_cookie3.firefox
            case SupportedBrowser.CHROME:
                return browser_cookie3.chrome
            case SupportedBrowser.SAFARI:
                return browser_cookie3.safari
            case SupportedBrowser.EDGE:
                return browser_cookie3.edge
            case _:
                assert_never(self)


def _extract_domain_cookies(cookie_jar, domain: str) -> Dict[str, str]:
    """Extract cookies for specific domain from cookie jar."""

    def is_domain_match(cookie) -> bool:
        return cookie.domain == domain or cookie.domain == f".{domain}"

    return {
        cookie.name: cookie.value for cookie in cookie_jar if is_domain_match(cookie)
    }


def extract_cookies_from_browser(
    browser: SupportedBrowser, domain: str
) -> Dict[str, str]:
    """Extract cookies from browser for given domain."""
    try:
        jar = browser.get_cookie_jar(domain_name=domain)
        cookies = _extract_domain_cookies(jar, domain)
        logger.info(
            f"📊 Extracted {len(cookies)} total cookies from {browser.value.title()}"
        )
        return cookies
    except Exception as e:
        logger.error(f"❌ Failed to extract cookies from {browser.value.title()}: {e}")
        if browser == SupportedBrowser.FIREFOX:
            logger.info("💡 Make sure Firefox is closed or try using --browser chrome")
        elif browser == SupportedBrowser.CHROME:
            logger.info("💡 You may need to grant keychain access on macOS")
        return {}


def _is_auth_cookie_by_name(name: str) -> bool:
    """Check if cookie name suggests authentication."""
    return any(keyword in name.lower() for keyword in AUTH_KEYWORDS)


def _is_auth_cookie_by_value(value: str) -> bool:
    """Check if cookie value looks like a session token."""
    return len(value) > 32 and any(c.isalnum() for c in value)


def filter_auth_cookies(cookies: Dict[str, str]) -> Dict[str, str]:
    """Filter cookies to keep only authentication-related ones."""
    auth_cookies = {
        name: value
        for name, value in cookies.items()
        if _is_auth_cookie_by_name(name) or _is_auth_cookie_by_value(value)
    }

    # If no specific auth cookies found, use all cookies (might be custom naming)
    if not auth_cookies and len(cookies) <= 10:
        auth_cookies = cookies

    return auth_cookies
