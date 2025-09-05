"""
Change detection and logging for employee data using structured models
"""

from collections.abc import Container
from itertools import zip_longest

from .config import IGNORED_EMPLOYEE_PATHS
from .models import ChangeReport, Employee, EmployeeList, FieldChange, ModifiedEmployee


def _get_employee_key(employee: Employee) -> tuple[str, str]:
    """Extract unique identifier (id, email) from employee."""
    return (employee.id, employee.email)


def _build_employee_index(employees: list[Employee]) -> dict[tuple[str, str], Employee]:
    """Build index of employees by their unique key."""
    return {_get_employee_key(emp): emp for emp in employees}


def _deep_diff(
    old_obj: object,
    new_obj: object,
    path: str = "",
    ignored_paths: Container[str] = frozenset(),
) -> list[FieldChange]:
    """Compare two objects recursively and return detailed changes."""

    def extend_path(path: str, extra: str) -> str:
        """Extend the current path with an additional segment."""
        return f"{path}.{extra}" if path else extra

    changes: list[FieldChange] = []

    if path in ignored_paths or old_obj == new_obj:
        return changes

    if isinstance(old_obj, dict) and isinstance(new_obj, dict):
        all_keys = set(old_obj.keys()) | set(new_obj.keys())
        for key in all_keys:
            changes += _deep_diff(
                old_obj.get(key),
                new_obj.get(key),
                extend_path(path, key),
                ignored_paths,
            )

    elif isinstance(old_obj, list) and isinstance(new_obj, list):
        for i, (item1, item2) in enumerate(zip_longest(old_obj, new_obj)):
            changes += _deep_diff(
                item1, item2, extend_path(path, f"[{i}]"), ignored_paths
            )

    else:
        changes.append(
            FieldChange(
                field_path=path,
                old_value=old_obj,
                new_value=new_obj,
            )
        )

    return changes


def _compare_employee_data(current: Employee, previous: Employee) -> list[FieldChange]:
    """Compare two employee objects and return list of field changes."""
    return _deep_diff(
        old_obj=previous.raw_data,
        new_obj=current.raw_data,
        ignored_paths=IGNORED_EMPLOYEE_PATHS,
    )


def compare_employee_lists(
    current: EmployeeList, previous: EmployeeList
) -> ChangeReport:
    """Compare current and previous employee lists to detect changes."""
    current_index = _build_employee_index(current.employees)
    previous_index = _build_employee_index(previous.employees)

    current_keys = set(current_index.keys())
    previous_keys = set(previous_index.keys())

    added_employees: list[Employee] = []
    removed_employees: list[Employee] = []
    modified_employees: list[ModifiedEmployee] = []

    # Find added employees
    added_employees.extend(current_index[key] for key in current_keys - previous_keys)

    # Find removed employees
    removed_employees.extend(
        previous_index[key] for key in previous_keys - current_keys
    )

    # Find modified employees (same key, different data)
    for key in current_keys & previous_keys:
        current_emp = current_index[key]
        previous_emp = previous_index[key]

        field_changes = _compare_employee_data(current_emp, previous_emp)

        if field_changes:  # Only add if there are field changes
            modified_employees.append(
                ModifiedEmployee.from_employee_and_changes(current_emp, field_changes)
            )

    return ChangeReport(
        current_timestamp=current.timestamp,
        previous_timestamp=previous.timestamp,
        added=added_employees,
        removed=removed_employees,
        modified=modified_employees,
    )
