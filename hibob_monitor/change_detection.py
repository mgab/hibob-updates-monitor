"""
Change detection and logging for employee data using structured models
"""

import os
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


def _deep_diff(obj1: Any, obj2: Any, path: str = "", ignored_paths: Set[str] = set()) -> List[FieldChange]:
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
        changes.append(FieldChange(
            field_path=path,
            old_value=obj1,
            new_value=obj2,
        ))
    
    return changes


def _compare_employee_data(current: Employee, previous: Employee) -> List[FieldChange]:
    """Compare two employee objects and return list of field changes."""
    return _deep_diff(current.raw_data, previous.raw_data, ignored_paths=IGNORED_EMPLOYEE_PATHS)


def compare_employee_lists(current: EmployeeList, previous: EmployeeList) -> ChangeReport:
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
            modified_employees.append(ModifiedEmployee(
                id=current_emp.id,
                email=current_emp.email,
                full_name=current_emp.full_name,
                changes=field_changes
            ))
    
    return ChangeReport(
        current_timestamp=current.timestamp,
        previous_timestamp=previous.timestamp,
        added=added_employees,
        removed=removed_employees,
        modified=modified_employees
    )


def _format_employee_summary(employee: Employee) -> str:
    """Format employee for logging."""
    return f"{employee.full_name} (ID: {employee.id}, Email: {employee.email})"


def log_changes(change_report: ChangeReport, log_file: str) -> None:
    """Log changes to a plain text file."""
    if not change_report.has_changes:
        return  # No changes to log
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        timestamp = change_report.current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        previous_timestamp = change_report.previous_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Changes detected at {timestamp}\n")
            f.write(f"Compared with data from {previous_timestamp}\n")
            f.write(f"{'='*60}\n")
            
            if change_report.added:
                f.write(f"\n📈 ADDED EMPLOYEES ({len(change_report.added)}):\n")
                for emp in change_report.added:
                    f.write(f"  + {_format_employee_summary(emp)}\n")
            
            if change_report.removed:
                f.write(f"\n📉 REMOVED EMPLOYEES ({len(change_report.removed)}):\n")
                for emp in change_report.removed:
                    f.write(f"  - {_format_employee_summary(emp)}\n")
            
            if change_report.modified:
                f.write(f"\n📝 MODIFIED EMPLOYEES ({len(change_report.modified)}):\n")
                for modified_emp in change_report.modified:
                    f.write(f"  ~ {modified_emp.full_name} (ID: {modified_emp.id}, Email: {modified_emp.email})\n")
                    
                    # Show field changes
                    for change in modified_emp.changes:
                        f.write(f"    {change}\n")
            
            f.write(f"\nSummary: {len(change_report.added)} added, {len(change_report.removed)} removed, {len(change_report.modified)} modified\n")
        
        print(f"📝 {change_report.total_changes} changes logged to {log_file}")
        
    except IOError as e:
        print(f"⚠️  Warning: Could not write to log file {log_file}: {e}")
