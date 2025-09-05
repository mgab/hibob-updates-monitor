from datetime import UTC, datetime, timedelta
from typing import Any

from hibob_monitor.change_detection import compare_employee_lists
from hibob_monitor.models import (
    Employee,
    EmployeeList,
)


def make_employee(  # noqa: PLR0913
    id_: str,
    email: str,
    name: str = "Test User",
    status: str = "active",
    department: str = "",
    site: str = "",
    extra: dict[str, Any] | None = None,
) -> Employee:
    raw = {
        "id": id_,
        "email": email,
        "fullName": name,
        "status": status,
        "work": {"department": department, "site": site},
    }
    if extra:
        raw.update(extra)
    return Employee.from_raw_data(raw)


def test_added_removed_modified() -> None:
    now = datetime.now(tz=UTC)
    before = EmployeeList(
        timestamp=now - timedelta(days=1),
        count=2,
        employees=[
            make_employee("1", "a@x.com", name="A"),
            make_employee("2", "b@x.com", name="B"),
        ],
    )
    after = EmployeeList(
        timestamp=now,
        count=2,
        employees=[
            make_employee("1", "a@x.com", name="A"),
            make_employee("3", "c@x.com", name="C"),
        ],
    )
    report = compare_employee_lists(after, before)
    assert len(report.added) == 1
    assert report.added[0].id == "3"
    assert len(report.removed) == 1
    assert report.removed[0].id == "2"
    assert len(report.modified) == 0


def test_modified_employee() -> None:
    now = datetime.now(tz=UTC)
    before = EmployeeList(
        timestamp=now - timedelta(days=1),
        count=1,
        employees=[
            make_employee("1", "a@x.com", name="A", department="HR"),
        ],
    )
    after = EmployeeList(
        timestamp=now,
        count=1,
        employees=[
            make_employee("1", "a@x.com", name="A", department="IT"),
        ],
    )
    report = compare_employee_lists(after, before)
    assert len(report.added) == 0
    assert len(report.removed) == 0
    assert len(report.modified) == 1
    mod = report.modified[0]
    assert mod.id == "1"
    assert any("department" in str(change) for change in mod.changes)


def test_no_changes() -> None:
    now = datetime.now(tz=UTC)
    emp = make_employee("1", "a@x.com", name="A")
    before = EmployeeList(timestamp=now - timedelta(days=1), count=1, employees=[emp])
    after = EmployeeList(timestamp=now, count=1, employees=[emp])
    report = compare_employee_lists(after, before)
    assert not report.has_changes
