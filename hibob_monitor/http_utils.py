"""
HTTP request utilities
"""

import json
import urllib.error
import urllib.request
from http import HTTPStatus
from typing import Any

from .config import DEFAULT_HEADERS


def _create_request(
    url: str,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
) -> urllib.request.Request:
    """Create HTTP request with headers and cookies."""
    if not url.startswith(("http:", "https:")):
        msg = "URL must start with 'http:' or 'https:'"
        raise ValueError(msg)

    req = urllib.request.Request(url, headers=headers or DEFAULT_HEADERS)  # noqa: S310

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

        with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
            if response.status == HTTPStatus.OK:
                result: dict[str, Any] = json.loads(response.read().decode("utf-8"))
                return result
            return None

    except urllib.error.HTTPError as e:
        if e.code == HTTPStatus.UNAUTHORIZED:
            msg = "Unauthorized (401). Please check your cookies and domain."
            raise PermissionError(msg) from e
        if e.code == HTTPStatus.FORBIDDEN:
            msg = "Forbidden (403). You don't have permission to access this resource."
            raise PermissionError(msg) from e
        if e.code == HTTPStatus.NOT_FOUND:
            msg = "Not Found (404). The requested resource could not be found."
            raise FileNotFoundError(msg) from e
        if e.code == HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = "Internal Server Error (500). The server encountered an error."
            raise ConnectionError(msg) from e
        msg = f"HTTP error occurred: {e.reason} (status code: {e.code})"
        raise ConnectionError(msg) from e
