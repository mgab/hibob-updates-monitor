"""
Configuration and constants for HiBob Monitor
"""

from typing import Dict, List
from .cache import CacheConfig

# Default HTTP headers
DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Authentication-related cookie keywords
AUTH_KEYWORDS: List[str] = [
    "session",
    "auth",
    "token",
    "login",
    "jwt",
    "bearer",
    "jsessionid",
    "csrf",
    "xsrf",
    "user",
    "account",
]

# API endpoints to test for authentication
TEST_ENDPOINTS: List[str] = [
    "/api/v1/people",
    "/api/people",
    "/api/v1/employees",
    "/api/employees",
]

# API endpoints to try for employee data
API_ENDPOINTS: List[str] = [
    "/api/employees",
    "/api/v1/employees",
    "/api/people",
    "/api/v1/people",
    "/api/v2/people",
]

# Possible keys for employee data in API responses
EMPLOYEE_DATA_KEYS: List[str] = ["employees", "people", "data", "results", "values"]

# Fields that identify an employee object
EMPLOYEE_FIELDS: List[str] = ["id", "email"]

# Priority fields for table display
TABLE_DISPLAY_FIELDS: List[str] = [
    "id",
    "displayName",
    "email",
    "fullName",
    "work.site",
    "work.tenureDurationYears",
    "work.reportsTo.displayName",
]

# Status values that indicate an active employee
ACTIVE_STATUS_VALUES: List[str] = ["active", "employed", "current"]

# Default cache configuration
DEFAULT_CACHE_CONFIG = CacheConfig(max_entries=20, deduplicate_consecutive=True)

IGNORED_EMPLOYEE_PATHS: set[str] = {
    "work.yearsOfService",
    "work.durationOfEmployment",
    "work.tenureDurationYears",
    "work.tenureDuration",
    "work.tenureYears",
    "payroll.timeSinceLastSalaryChange",
    "avatarUrl",
    "about.avatar",
    "work.directReports",
    "work.indirectReports",
}
