"""
Data models for HiBob employee monitoring
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self


@dataclass
class EmployeeDescription:
    id: str
    email: str
    full_name: str
    status: str
    department: str
    site: str


@dataclass
class Employee(EmployeeDescription):
    """Structured employee data with normalized fields."""

    raw_data: dict[str, Any]

    @classmethod
    def from_raw_data(cls, raw_data: dict[str, Any]) -> "Employee":
        """Create Employee from raw API response data."""
        # Extract normalized fields
        emp_id = str(raw_data.get("id", ""))

        # Try different email field locations
        email = (
            raw_data.get("email", "") or raw_data.get("work", {}).get("email", "")
            if isinstance(raw_data.get("work"), dict)
            else "" or raw_data.get("personalEmail", "") or ""
        )

        # Try different name field locations
        full_name = (
            raw_data.get("fullName", "")
            or raw_data.get("displayName", "")
            or raw_data.get("name", "")
            or f"{raw_data.get('firstName', '')} {raw_data.get('lastName', '')}".strip()
            or "Unknown"
        )

        # Extract status
        status = str(raw_data.get("status", "active")).lower()

        department = str(raw_data.get("work", {}).get("department", "")).strip()

        site = str(raw_data.get("work", {}).get("site", "")).strip()

        return cls(
            id=emp_id,
            email=email,
            full_name=full_name,
            status=status,
            department=department,
            site=site,
            raw_data=raw_data,
        )

    def __eq__(self, other: object) -> bool:
        """Compare employees based on raw data for change detection."""
        if not isinstance(other, Employee):
            return False
        return self.raw_data == other.raw_data

    def __hash__(self) -> int:
        """Hash based on id and email for set operations."""
        return hash((self.id, self.email))


@dataclass
class EmployeeList:
    """Container for employee data with metadata."""

    timestamp: datetime
    count: int
    employees: list[Employee] = field(default_factory=list)

    @classmethod
    def from_raw_data(cls, employees_data: list[dict[str, Any]]) -> "EmployeeList":
        """Create EmployeeList from raw API response data."""
        employees = [Employee.from_raw_data(emp_data) for emp_data in employees_data]
        return cls(timestamp=datetime.now(), count=len(employees), employees=employees)

    def __eq__(self, other: object) -> bool:
        """Compare EmployeeLists based on employee data (ignoring timestamp)."""
        if not isinstance(other, EmployeeList):
            return False
        return self.employees == other.employees

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "count": self.count,
            "employees": [emp.raw_data for emp in self.employees],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmployeeList":
        """Create from dictionary (for cache loading)."""
        timestamp = datetime.fromisoformat(data["timestamp"])
        employees_data = data.get("employees", [])
        employees = [Employee.from_raw_data(emp_data) for emp_data in employees_data]
        return cls(
            timestamp=timestamp,
            count=data.get("count", len(employees)),
            employees=employees,
        )


@dataclass
class FieldChange:
    """Represents a change in a specific field."""

    field_path: str
    old_value: Any
    new_value: Any

    def __str__(self) -> str:
        return f"{self.field_path}: {self.old_value} → {self.new_value}"


@dataclass
class ModifiedEmployee(EmployeeDescription):
    """Represents an employee with field changes."""

    changes: list[FieldChange] = field(default_factory=list)

    @classmethod
    def from_employee_and_changes(
        cls: type[Self], employee: EmployeeDescription, changes: list[FieldChange]
    ) -> Self:
        "Create a ModifiedEmployee from an EmployeeDescription and a list of changes."
        return cls(
            id=employee.id,
            email=employee.email,
            full_name=employee.full_name,
            status=employee.status,
            department=employee.department,
            site=employee.site,
            changes=changes,
        )


@dataclass
class ChangeReport:
    """Report of changes between two EmployeeLists."""

    current_timestamp: datetime
    previous_timestamp: datetime
    added: list[Employee] = field(default_factory=list)
    removed: list[Employee] = field(default_factory=list)
    modified: list[ModifiedEmployee] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        """Total number of changes."""
        return len(self.added) + len(self.removed) + len(self.modified)

    @property
    def has_changes(self) -> bool:
        """Whether there are any changes."""
        return self.total_changes > 0
