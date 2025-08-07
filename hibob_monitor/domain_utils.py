"""
Domain and URL utilities
"""


def normalize_domain(domain: str) -> str:
    """Normalize domain by removing protocol prefixes."""
    return domain.replace("https://", "").replace("http://", "")


def build_base_url(domain: str) -> str:
    """Build base URL from domain."""
    return f"https://{normalize_domain(domain)}"
