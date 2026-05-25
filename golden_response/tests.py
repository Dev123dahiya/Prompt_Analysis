from .errors import ApiError
from .service import LeaveManagementService


def run_self_test() -> None:
    service = LeaveManagementService()
    employee, _ = service.authenticate("dev@gmail.com", "Password123!")
    manager, _ = service.authenticate("khushi@gmail.com", "Password123!")
    admin, _ = service.authenticate("arun@gmail.com", "Password123!")

    request = service.create_request(
        employee,
        {
            "leave_type": "annual",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "reason": "Family event",
        },
    )
    assert request.days == 5

    try:
        service.create_request(
            employee,
            {
                "leave_type": "annual",
                "start_date": "2026-06-03",
                "end_date": "2026-06-04",
            },
        )
    except ApiError as exc:
        assert exc.code == "OVERLAPPING_PENDING_REQUEST"
    else:
        raise AssertionError("overlap validation failed")

    service.update_status(manager, request.id, "approved", "Looks fine")
    assert service.get_balance(employee)["data"]["annual"] == 15

    service.update_status(admin, request.id, "rejected", "Admin override")
    assert service.requests[request.id].manager_comment == "Looks fine"
    assert service.requests[request.id].admin_comment == "Admin override"

    report = service.generate_report(admin, "2026-01-01", "2026-12-31")
    assert "Dev" in report
    assert "manager comment" in report

    pending = service.create_request(
        employee,
        {"leave_type": "sick", "start_date": "2026-07-06", "end_date": "2026-07-06"},
    )
    service.update_user(admin, employee.id, {"active": False})
    assert service.requests[pending.id].status == "rejected"

    print("Self-test passed.")
