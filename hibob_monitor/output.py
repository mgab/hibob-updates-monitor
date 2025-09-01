"""
Output formatting for structured employee data and change reports
"""

import csv
import io
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, assert_never

from .config import TABLE_DISPLAY_FIELDS
from .models import ChangeReport, EmployeeDescription, EmployeeList

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Enumeration of supported output formats."""

    TABLE = "table"
    JSON = "json"
    CSV = "csv"

    def format(self, employee_list: EmployeeList) -> str:
        """Format employee list based on the selected output format."""
        match self:
            case OutputFormat.TABLE:
                return format_employees_as_table(employee_list)
            case OutputFormat.JSON:
                return format_employees_as_json(employee_list)
            case OutputFormat.CSV:
                return format_employees_as_csv(employee_list)
            case _:
                assert_never(self)


def _get_table_display_fields(flat_employee_data: list[dict[str, Any]]) -> list[str]:
    """Determine which fields to display in table."""
    if not flat_employee_data:
        return []

    all_fields = {field for emp in flat_employee_data for field in emp}

    return [f for f in TABLE_DISPLAY_FIELDS if f in all_fields]


def _flatten_dict(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Flatten a nested dict (of dicts and lists) to a single level dict."""

    def _flatten_recursive(data: Any, path: str = "") -> dict[str, Any]:  # noqa: ANN401
        """Recursive helper to flatten dict."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                new_key = f"{path}.{key}" if path else key
                result.update(_flatten_recursive(value, new_key))
            return result
        if isinstance(data, list):
            result = {}
            for i, item in enumerate(data):
                new_key = f"{path}.[{i}]" if path else f"[{i}]"
                result.update(_flatten_recursive(item, new_key))
            return result
        return {path: data}

    return _flatten_recursive(data)


def format_employees_as_table(
    employee_list: EmployeeList, max_col_width: int = 15
) -> str:
    """Format employee list as a table."""
    if not employee_list.employees:
        return "No employees found."

    # Get all employee data as flatten dicts
    flattened_employee_data = [
        _flatten_dict(emp.raw_data) for emp in employee_list.employees
    ]

    fields = _get_table_display_fields(flattened_employee_data)
    if not fields:
        return "No data to display."

    col_widths = [max(len(field), max_col_width) for field in fields]

    # Create table header
    header = " | ".join(f"{field:<{col_widths[i]}}" for i, field in enumerate(fields))
    separator = "-" * len(header)

    # Create table rows
    rows = []
    for flat_emp in flattened_employee_data:
        row_values = []
        for i, field in enumerate(fields):
            value = str(flat_emp.get(field, ""))[: col_widths[i]]
            row_values.append(f"{value:<{col_widths[i]}}")
        rows.append(" | ".join(row_values))

    # Combine all parts
    table_parts = [header, separator, *rows]
    return "\n".join(table_parts)


def format_employees_as_json(employee_list: EmployeeList) -> str:
    """Format employee list as JSON."""
    return json.dumps(employee_list.to_dict(), indent=2, ensure_ascii=False)


def format_employees_as_csv(employee_list: EmployeeList) -> str:
    """Format employee list as CSV."""
    if not employee_list.employees:
        return ""

    # Get all employee data as flatten dicts
    flattened_employee_data = [
        _flatten_dict(emp.raw_data) for emp in employee_list.employees
    ]

    # Get all possible fields from all employees
    all_fields = sorted({field for emp in flattened_employee_data for field in emp})

    # Create CSV output
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_fields)
    writer.writeheader()

    for emp in flattened_employee_data:
        writer.writerow(emp)

    return output.getvalue()


def _format_employee_summary(employee: EmployeeDescription) -> str:
    """Format employee for logging."""
    return (
        f"{employee.full_name} (ID: {employee.id}, Email: {employee.email}, "
        f"Department: {employee.department}, Site: {employee.site})"
    )


def format_change_report_as_text(change_report: ChangeReport) -> str:
    """Format change report as readable text."""
    if not change_report.has_changes:
        return "No changes detected."

    lines = []
    lines.append("\n" + "=" * 60)
    lines.append(
        "Changes detected at "
        f"{change_report.current_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    lines.append(
        "Compared with data from "
        f"{change_report.previous_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    lines.append("=" * 60)

    if change_report.added:
        lines.append(f"\n📈 ADDED EMPLOYEES ({len(change_report.added)}):")
        lines.extend(
            f"  + {_format_employee_summary(emp)}" for emp in change_report.added
        )

    if change_report.removed:
        lines.append(f"\n📉 REMOVED EMPLOYEES ({len(change_report.removed)}):")
        lines.extend(
            f"  - {_format_employee_summary(emp)}" for emp in change_report.removed
        )

    if change_report.modified:
        lines.append(f"\n📝 MODIFIED EMPLOYEES ({len(change_report.modified)}):")
        for modified_emp in change_report.modified:
            lines.append(f"  ~ {_format_employee_summary(modified_emp)}")

            # Show field changes
            lines.extend(f"    {change}" for change in modified_emp.changes)

    lines.append(
        f"\nSummary: {len(change_report.added)} added,"
        f" {len(change_report.removed)} removed, "
        f"{len(change_report.modified)} modified"
    )

    return "\n".join(lines) + "\n\n"


def write_to_file(content: str, filepath: Path) -> bool:
    """Write content to a file, creating directory if needed."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        msg = f"Error writing to {filepath}: {e}"
        logger.error(msg)
        return False
    else:
        return True


def append_to_file(content: str, filepath: Path) -> bool:
    """Append content to a file, creating directory if needed."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("a", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        msg = f"Error appending to {filepath}: {e}"
        logger.error(msg)
        return False
    else:
        return True
