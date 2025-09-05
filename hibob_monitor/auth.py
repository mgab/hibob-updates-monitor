"""
Authentication functionality
"""

import logging
from functools import partial

from .config import TEST_ENDPOINTS
from .cookies import (
    SupportedBrowser,
    extract_cookies_from_browser,
    filter_auth_cookies,
)
from .domain_utils import build_base_url, normalize_domain
from .http_utils import make_request

logger = logging.getLogger(__name__)


def _test_endpoint(base_url: str, endpoint: str, cookies: dict[str, str]) -> bool:
    """Test if endpoint works with current cookies."""
    url = f"{base_url}{endpoint}"
    result = make_request(url, cookies)
    return result is not None


def test_authentication(base_url: str, cookies: dict[str, str]) -> bool:
    """Test if current session is authenticated."""
    test_functions = [
        partial(_test_endpoint, base_url, endpoint, cookies)
        for endpoint in TEST_ENDPOINTS
    ]

    for i, test_func in enumerate(test_functions):
        if test_func():
            logger.info(
                "✅ Authentication successful! (endpoint: %s)", TEST_ENDPOINTS[i]
            )
            return True

    logger.error("❌ Authentication test failed on all endpoints")
    return False


def authenticate_with_browser(
    domain: str, browser: SupportedBrowser
) -> tuple[bool, dict[str, str]]:
    """Complete authentication flow using browser cookies."""
    normalized_domain = normalize_domain(domain)
    base_url = build_base_url(domain)

    logger.info(
        "🔍 Extracting cookies from %s for %s...",
        browser.value.title(),
        normalized_domain,
    )

    # Extract and filter cookies
    all_cookies = extract_cookies_from_browser(browser, normalized_domain)

    if not all_cookies:
        logger.error("❌ No cookies found in %s.", browser.value.title())
        logger.info(
            "Make sure you're logged into HiBob at https://%s", normalized_domain
        )
        return False, {}

    auth_cookies = filter_auth_cookies(all_cookies)

    if not auth_cookies:
        logger.error("❌ No authentication cookies found.")
        logger.info("Available cookies: %s", list(all_cookies.keys()))
        return False, {}

    logger.info(
        "✅ Found %s authentication cookies: %s",
        len(auth_cookies),
        list(auth_cookies.keys()),
    )

    # Test authentication
    if test_authentication(base_url, auth_cookies):
        return True, auth_cookies
    return False, {}
