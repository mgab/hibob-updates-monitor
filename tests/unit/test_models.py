from hibob_monitor.models import Employee


def test_employee_from_raw_data() -> None:
    raw = {
        "id": "42",
        "email": "user@example.com",
        "fullName": "Jane Doe",
        "status": "active",
        "work": {"department": "R&D", "site": "Paris"},
    }
    emp = Employee.from_raw_data(raw)
    assert emp.id == "42"
    assert emp.email == "user@example.com"
    assert emp.full_name == "Jane Doe"
    assert emp.status == "active"
    assert emp.department == "R&D"
    assert emp.site == "Paris"
