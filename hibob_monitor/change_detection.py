"""
Change detection and logging for employee data using structured models
"""

from typing import Dict, List, Any, Tuple, Set
from itertools import zip_longest
from .models import EmployeeList, Employee, ChangeReport, FieldChange, ModifiedEmployee
from .config import IGNORED_EMPLOYEE_PATHS


def _get_employee_key(employee: Employee) -> Tuple[str, str]:
    """Extract unique identifier (id, email) from employee."""
    return (employee.id, employee.email)


def _build_employee_index(employees: List[Employee]) -> Dict[Tuple[str, str], Employee]:
    """Build index of employees by their unique key."""
    return {_get_employee_key(emp): emp for emp in employees}


def _deep_diff(
    obj1: Any, obj2: Any, path: str = "", ignored_paths: Set[str] = set()
) -> List[FieldChange]:
    """Compare two objects recursively and return detailed changes."""

    def extend_path(path: str, extra: str) -> str:
        """Extend the current path with an additional segment."""
        return f"{path}.{extra}" if path else extra

    changes = []

    if path in ignored_paths:
        return changes

    elif obj1 == obj2:
        return changes

    elif isinstance(obj1, dict) and isinstance(obj2, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            changes += _deep_diff(
                obj1.get(key), obj2.get(key), extend_path(path, key), ignored_paths
            )

    elif isinstance(obj1, list) and isinstance(obj2, list):
        for i, (item1, item2) in enumerate(zip_longest(obj1, obj2)):
            changes += _deep_diff(
                item1, item2, extend_path(path, f"[{i}]"), ignored_paths
            )

    else:
        changes.append(
            FieldChange(
                field_path=path,
                old_value=obj1,
                new_value=obj2,
            )
        )

    return changes


def _compare_employee_data(current: Employee, previous: Employee) -> List[FieldChange]:
    """Compare two employee objects and return list of field changes."""
    return _deep_diff(
        current.raw_data, previous.raw_data, ignored_paths=IGNORED_EMPLOYEE_PATHS
    )


def compare_employee_lists(
    current: EmployeeList, previous: EmployeeList
) -> ChangeReport:
    """Compare current and previous employee lists to detect changes."""
    current_index = _build_employee_index(current.employees)
    previous_index = _build_employee_index(previous.employees)

    current_keys = set(current_index.keys())
    previous_keys = set(previous_index.keys())

    added_employees = []
    removed_employees = []
    modified_employees = []

    # Find added employees
    for key in current_keys - previous_keys:
        added_employees.append(current_index[key])

    # Find removed employees
    for key in previous_keys - current_keys:
        removed_employees.append(previous_index[key])

    # Find modified employees (same key, different data)
    for key in current_keys & previous_keys:
        current_emp = current_index[key]
        previous_emp = previous_index[key]

        field_changes = _compare_employee_data(current_emp, previous_emp)

        if field_changes:  # Only add if there are field changes
            modified_employees.append(
                ModifiedEmployee(
                    id=current_emp.id,
                    email=current_emp.email,
                    full_name=current_emp.full_name,
                    changes=field_changes,
                )
            )

    return ChangeReport(
        current_timestamp=current.timestamp,
        previous_timestamp=previous.timestamp,
        added=added_employees,
        removed=removed_employees,
        modified=modified_employees,
    )
