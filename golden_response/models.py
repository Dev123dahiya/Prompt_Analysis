import datetime as dt
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class User:
    id: int
    name: str
    email: str
    department_id: str
    role: str
    start_date: dt.date
    password_hash: str
    active: bool = True

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("password_hash")
        data["start_date"] = self.start_date.isoformat()
        return data


@dataclass
class LeaveRequest:
    id: int
    user_id: int
    leave_type: str
    start_date: dt.date
    end_date: dt.date
    days: int
    reason: str = ""
    status: str = "pending"
    submitted_at: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.UTC))
    manager_comment: str = ""
    admin_comment: str = ""
    decided_by: int | None = None

    def public(self, employee: User | None = None) -> dict[str, Any]:
        data = asdict(self)
        data["start_date"] = self.start_date.isoformat()
        data["end_date"] = self.end_date.isoformat()
        data["submitted_at"] = self.submitted_at.isoformat()
        if employee:
            data["employee"] = {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "department_id": employee.department_id,
            }
        return data


@dataclass
class Policy:
    annual: int = 20
    sick: int = 10
    casual: int = 5

    def public(self) -> dict[str, int]:
        return asdict(self)
