"""
Employee data extraction and filtering
"""

import logging
from functools import partial
from typing import Any

from .config import (
    ACTIVE_STATUS_VALUES,
    API_ENDPOINTS,
    EMPLOYEE_DATA_KEYS,
    EMPLOYEE_FIELDS,
)
from .http_utils import make_request
from .models import EmployeeList

logger = logging.getLogger(__name__)


def _is_employee_object(data: object) -> bool:
    """Check if data looks like an employee object."""
    return isinstance(data, dict) and all(field in data for field in EMPLOYEE_FIELDS)


def _extract_employees_from_response(data: object) -> list[dict[str, Any]]:
    """Extract employee list from API response."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Try known keys for employee arrays
        for key in EMPLOYEE_DATA_KEYS:
            if key in data and isinstance(data[key], list):
                return data[key]

        # Single employee object
        if _is_employee_object(data):
            return [data]

    return []


def _is_employee_active(employee: dict[str, Any]) -> bool:
    """Check if employee is active based on various status fields."""
    if not isinstance(employee, dict):
        return False

    # Check direct status field
    if "status" in employee:
        status = str(employee["status"]).lower()
        return status in ACTIVE_STATUS_VALUES

    # Check employment.status
    if (
        "employment" in employee
        and isinstance(employee["employment"], dict)
        and "status" in employee["employment"]
    ):
        status = str(employee["employment"]["status"]).lower()
        return status in ACTIVE_STATUS_VALUES

    # Check isActive boolean
    if "isActive" in employee:
        return bool(employee["isActive"])

    # Check termination/end dates
    if "terminationDate" in employee:
        return employee["terminationDate"] is None or employee["terminationDate"] == ""

    if "endDate" in employee:
        return employee["endDate"] is None or employee["endDate"] == ""

    # Default to active if no status indicators found
    return True


def _filter_active_employees(employees: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter employees to only include active ones."""
    active_employees = [emp for emp in employees if _is_employee_active(emp)]

    # Log inactive employees for debugging
    inactive_employees = [emp for emp in employees if not _is_employee_active(emp)]
    for emp in inactive_employees:
        logger.warning(
            "⚠️  Employee %s is not active (status: %s)",
            emp.get("id", "unknown"),
            emp.get("status"),
        )

    return active_employees


def _try_endpoint(
    base_url: str, endpoint: str, cookies: dict[str, str]
) -> EmployeeList | None:
    """Try to fetch employees from a specific endpoint."""
    url = f"{base_url}{endpoint}"
    logger.info("🔍 Trying endpoint: %s", endpoint)

    data = make_request(url, cookies)

    if data is not None:
        employees_data = _extract_employees_from_response(data)

        if employees_data:
            active_employees_data = _filter_active_employees(employees_data)

            if active_employees_data:
                employee_list = EmployeeList.from_raw_data(active_employees_data)
                logger.info("✅ Found %s active employees", employee_list.count)
                return employee_list
            logger.warning(
                "⚠️  Found %s employees but none marked as active", len(employees_data)
            )

    return None


def get_active_employees(base_url: str, cookies: dict[str, str]) -> EmployeeList | None:
    """Fetch list of active employees by trying multiple endpoints."""
    endpoint_functions = [
        partial(_try_endpoint, base_url, endpoint, cookies)
        for endpoint in API_ENDPOINTS
    ]

    for endpoint_func in endpoint_functions:
        result = endpoint_func()
        if result is not None:
            return result

    logger.error("❌ Could not find employee data at any known endpoint")
    return None
