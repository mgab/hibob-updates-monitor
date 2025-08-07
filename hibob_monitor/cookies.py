"""
Browser cookie extraction functionality
"""

from enum import Enum
from typing import Dict
from .config import AUTH_KEYWORDS


class SupportedBrowsers(Enum):
    """Enumeration of supported browsers."""

    FIREFOX = "firefox"
    CHROME = "chrome"
    SAFARI = "safari"
    EDGE = "edge"


# Try to import browser_cookie3
try:
    import browser_cookie3

    BROWSER_COOKIE3_AVAILABLE = True
except ImportError:
    BROWSER_COOKIE3_AVAILABLE = False
    print(
        "❌ browser_cookie3 not installed. Install it with: pip install browser_cookie3"
    )
    import sys

    sys.exit(1)


def _get_browser_cookie_jar(browser: str, domain: str):
    """Get cookie jar from specified browser."""
    browser_functions = {
        SupportedBrowsers.FIREFOX.value: browser_cookie3.firefox,
        SupportedBrowsers.CHROME.value: browser_cookie3.chrome,
        SupportedBrowsers.SAFARI.value: browser_cookie3.safari,
        SupportedBrowsers.EDGE.value: browser_cookie3.edge,
    }

    if browser not in browser_functions:
        supported = [b.value for b in SupportedBrowsers]
        raise ValueError(f"Unsupported browser: {browser}. Supported: {supported}")

    return browser_functions[browser](domain_name=domain)


def _extract_domain_cookies(cookie_jar, domain: str) -> Dict[str, str]:
    """Extract cookies for specific domain from cookie jar."""

    def is_domain_match(cookie) -> bool:
        return cookie.domain == domain or cookie.domain == f".{domain}"

    return {
        cookie.name: cookie.value for cookie in cookie_jar if is_domain_match(cookie)
    }


def extract_cookies_from_browser(browser: str, domain: str) -> Dict[str, str]:
    """Extract cookies from browser for given domain."""
    try:
        jar = _get_browser_cookie_jar(browser, domain)
        cookies = _extract_domain_cookies(jar, domain)
        print(f"📊 Extracted {len(cookies)} total cookies from {browser.title()}")
        return cookies
    except Exception as e:
        print(f"❌ Failed to extract cookies from {browser.title()}: {e}")
        if browser == "firefox":
            print("💡 Make sure Firefox is closed or try using --browser chrome")
        elif browser == "chrome":
            print("💡 You may need to grant keychain access on macOS")
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
