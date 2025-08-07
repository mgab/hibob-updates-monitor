"""
Output formatting and file operations for structured employee data
"""

import json
import csv
import sys
import io
import contextlib
from enum import Enum
from typing import Dict, List, Any, Optional
from itertools import chain
from .config import PRIORITY_DISPLAY_FIELDS
from .models import EmployeeList


class OutputFormats(Enum):
    """Enumeration of supported output formats."""

    TABLE = "table"
    JSON = "json"
    CSV = "csv"


def _get_nested_value(data: Dict[str, Any], key: str) -> Any:
    """Retrieve a nested value from a dictionary using dot notation."""
    keys = key.split(".")
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return None
    return data


def _get_display_fields(employee_list: EmployeeList) -> List[str]:
    """Determine which fields to display in table."""
    if not employee_list.employees:
        return []

    all_fields = set(
        chain.from_iterable(emp.raw_data.keys() for emp in employee_list.employees)
    )

    # Prioritize important fields, including nested fields
    fields_to_show = [
        f for f in PRIORITY_DISPLAY_FIELDS if f.split(".")[0] in all_fields
    ]

    return fields_to_show


def _format_cell_value(value: Any, max_length: int = 15) -> str:
    """Format a cell value for table display."""
    if isinstance(value, (dict, list)):
        value = str(type(value).__name__)
    return str(value)[:max_length]


def print_table(employee_list: EmployeeList) -> None:
    """Print employees in a simple table format."""
    if not employee_list.employees:
        print("No employees found.")
        return

    fields_to_show = _get_display_fields(employee_list)

    # Determine column widths based on header
    column_widths = {field: max(len(field), 15) for field in fields_to_show}

    # Print header
    header = " | ".join([f"{field:{column_widths[field]}}" for field in fields_to_show])
    print("\n" + header)
    print("-" * len(header))

    # Print rows
    for emp in employee_list.employees:
        row_values = [
            f"{_format_cell_value(_get_nested_value(emp.raw_data, field) or ''):{column_widths[field]}}"
            for field in fields_to_show
        ]
        print(" | ".join(row_values))

    print()  # Empty line at end


def save_to_json(employee_list: EmployeeList, filepath: str) -> None:
    """Save employees to JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [emp.raw_data for emp in employee_list.employees],
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"✅ Data saved to {filepath}")
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")


def _flatten_for_csv(employee: Dict[str, Any], all_fields: List[str]) -> Dict[str, str]:
    """Flatten employee object for CSV export."""
    flattened = {}
    for field in all_fields:
        value = employee.get(field, "")
        if isinstance(value, (dict, list)):
            flattened[field] = json.dumps(value)
        else:
            flattened[field] = str(value)
    return flattened


def save_to_csv(employee_list: EmployeeList, filepath: str) -> None:
    """Save employees to CSV file."""
    if not employee_list.employees:
        print("No data to save.")
        return

    try:
        # Get all unique fields from raw data
        all_fields = sorted(
            set(
                chain.from_iterable(
                    emp.raw_data.keys() for emp in employee_list.employees
                )
            )
        )

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fields)
            writer.writeheader()

            for emp in employee_list.employees:
                flattened = _flatten_for_csv(emp.raw_data, all_fields)
                writer.writerow(flattened)

        print(f"✅ Data saved to {filepath}")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")


def save_table_to_file(employee_list: EmployeeList, filepath: str) -> None:
    """Save table format to file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f_stdout = io.StringIO()
            with contextlib.redirect_stdout(f_stdout):
                print_table(employee_list)
            f.write(f_stdout.getvalue())

        print(f"✅ Table saved to {filepath}")
    except Exception as e:
        print(f"❌ Error saving table: {e}")


def handle_output(
    employee_list: EmployeeList, format_type: str, output_path: Optional[str]
) -> None:
    """Handle output based on format and output path."""
    output_handlers = {
        OutputFormats.JSON.value: (
            save_to_json,
            lambda el: print(
                json.dumps(
                    [emp.raw_data for emp in el.employees], indent=2, ensure_ascii=False
                )
            ),
        ),
        OutputFormats.CSV.value: (
            save_to_csv,
            lambda el: print("❌ CSV format requires --output option") or sys.exit(1),
        ),
        OutputFormats.TABLE.value: (save_table_to_file, print_table),
    }

    if format_type not in output_handlers:
        supported = [fmt.value for fmt in OutputFormats]
        print(f"❌ Unknown format: {format_type}. Supported: {supported}")
        sys.exit(1)

    file_handler, console_handler = output_handlers[format_type]

    if output_path:
        file_handler(employee_list, output_path)
    else:
        console_handler(employee_list)
