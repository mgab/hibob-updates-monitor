"""
Configuration and constants for HiBob Monitor
"""

from .cache import CacheConfig

# Default HTTP headers
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Authentication-related cookie keywords
AUTH_KEYWORDS: list[str] = [
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
TEST_ENDPOINTS: list[str] = [
    "/api/v1/people",
    "/api/people",
    "/api/v1/employees",
    "/api/employees",
]

# API endpoints to try for employee data
API_ENDPOINTS: list[str] = [
    "/api/employees",
    "/api/v1/employees",
    "/api/people",
    "/api/v1/people",
    "/api/v2/people",
]

# Possible keys for employee data in API responses
EMPLOYEE_DATA_KEYS: list[str] = ["employees", "people", "data", "results", "values"]

# Fields that identify an employee object
EMPLOYEE_FIELDS: list[str] = ["id", "email"]

# Priority fields for table display
TABLE_DISPLAY_FIELDS: list[str] = [
    "id",
    "displayName",
    "email",
    "fullName",
    "work.site",
    "work.tenureDurationYears",
    "work.department",
    "work.reportsTo.displayName",
]

# Default cache configuration
DEFAULT_CACHE_CONFIG = CacheConfig(max_entries=200, deduplicate_consecutive=True)

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
    "employee.orgLevel",
    "work.reportsTo.surname",
    "work.reportsTo.firstName",
    "work.reportsTo.id",
    "work.secondLevelManager",
    "work.manager",
}
