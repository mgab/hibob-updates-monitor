"""
Authentication functionality
"""

from functools import partial
from typing import Dict, Tuple
from .config import TEST_ENDPOINTS
from .http_utils import make_request
from .domain_utils import normalize_domain, build_base_url
from .cookies import (
    extract_cookies_from_browser,
    filter_auth_cookies,
    SupportedBrowser,
)


def _test_endpoint(base_url: str, endpoint: str, cookies: Dict[str, str]) -> bool:
    """Test if endpoint works with current cookies."""
    url = f"{base_url}{endpoint}"
    result = make_request(url, cookies)
    return result is not None


def test_authentication(base_url: str, cookies: Dict[str, str]) -> bool:
    """Test if current session is authenticated."""
    test_functions = [
        partial(_test_endpoint, base_url, endpoint, cookies)
        for endpoint in TEST_ENDPOINTS
    ]

    for i, test_func in enumerate(test_functions):
        if test_func():
            print(f"✅ Authentication successful! (endpoint: {TEST_ENDPOINTS[i]})")
            return True

    print("❌ Authentication test failed on all endpoints")
    return False


def authenticate_with_browser(
    domain: str, browser: SupportedBrowser
) -> Tuple[bool, Dict[str, str]]:
    """Complete authentication flow using browser cookies."""
    normalized_domain = normalize_domain(domain)
    base_url = build_base_url(domain)

    print(
        f"🔍 Extracting cookies from {browser.value.title()} for {normalized_domain}..."
    )

    # Extract and filter cookies
    all_cookies = extract_cookies_from_browser(browser, normalized_domain)

    if not all_cookies:
        print(f"❌ No cookies found in {browser.value.title()}.")
        print(f"Make sure you're logged into HiBob at https://{normalized_domain}")
        return False, {}

    auth_cookies = filter_auth_cookies(all_cookies)

    if not auth_cookies:
        print("❌ No authentication cookies found.")
        print(f"Available cookies: {list(all_cookies.keys())}")
        return False, {}

    print(
        f"✅ Found {len(auth_cookies)} authentication cookies: {list(auth_cookies.keys())}"
    )

    # Test authentication
    if test_authentication(base_url, auth_cookies):
        return True, auth_cookies
    else:
        return False, {}
