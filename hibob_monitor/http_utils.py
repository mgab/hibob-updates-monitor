"""
HTTP request utilities
"""

import json
import urllib.error
import urllib.request
from typing import Any

from .config import DEFAULT_HEADERS


def _create_request(
    url: str,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
) -> urllib.request.Request:
    """Create HTTP request with headers and cookies."""
    req = urllib.request.Request(url, headers=headers or DEFAULT_HEADERS)

    if cookies:
        cookie_header = "; ".join(
            [f"{name}={value}" for name, value in cookies.items()]
        )
        req.add_header("Cookie", cookie_header)

    return req


def make_request(
    url: str, cookies: dict[str, str] | None = None
) -> dict[str, Any] | None:
    """Make authenticated request to API."""
    try:
        req = _create_request(url, DEFAULT_HEADERS, cookies)

        if not url.startswith(("http:", "https:")):
            msg = "URL must start with 'http:' or 'https:'"
            raise ValueError(msg)

        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
            return None

    except urllib.error.HTTPError as e:
        if e.code != 401:  # Don't log 401 errors, they're expected during testing
            pass
        return None
