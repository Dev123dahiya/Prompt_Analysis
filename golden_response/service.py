import csv
import datetime as dt
from io import StringIO
from typing import Any

from .config import LEAVE_TYPES, ROLES
from .errors import ApiError
from .models import LeaveRequest, Policy, User
from .security import PasswordHasher, RateLimiter, TokenService
from .validators import (
    ensure_date_order,
    parse_date,
    positive_int,
    require_role,
    sanitize_choice,
    sanitize_email,
    sanitize_text,
    weekday_count,
)


class LeaveManagementService:
    def __init__(self) -> None:
        self.policy = Policy()
        self.users: dict[int, User] = {}
        self.requests: dict[int, LeaveRequest] = {}
        self._next_user_id = 1
        self._next_request_id = 1
        self.rate_limiter = RateLimiter()
        self.seed()

    def seed(self) -> None:
        self.add_user("Dev", "dev@gmail.com", "engineering", "employee", "2024-01-15")
        self.add_user("Khushi", "khushi@gmail.com", "engineering", "manager", "2022-03-01")
        self.add_user("Arun", "arun@gmail.com", "people", "admin", "2021-06-01")

    def add_user(
        self,
        name: str,
        email: str,
        department_id: str,
        role: str,
        start_date: str,
        password: str = "Password123!",
    ) -> User:
        name = sanitize_text(name, "name", required=True)
        email = sanitize_email(email)
        department_id = sanitize_text(department_id, "department", required=True)
        role = sanitize_choice(role, ROLES, "role")
        parsed_start = parse_date(start_date, "startDate")
        if any(user.email == email for user in self.users.values()):
            raise ApiError(409, "Email already exists", "EMAIL_EXISTS")
        user = User(
            id=self._next_user_id,
            name=name,
            email=email,
            department_id=department_id,
            role=role,
            start_date=parsed_start,
            password_hash=PasswordHasher.hash_password(password),
        )
        self.users[user.id] = user
        self._next_user_id += 1
        return user

    def authenticate(self, email: str, password: str, ip: str = "local") -> tuple[User, str]:
        self.rate_limiter.check(f"login:{ip}", 5, 15 * 60)
        clean_email = sanitize_email(email)
        user = next((item for item in self.users.values() if item.email == clean_email), None)
        if not user or not user.active or not PasswordHasher.verify(password, user.password_hash):
            raise ApiError(401, "Bad credentials", "BAD_CREDENTIALS")
        return user, TokenService.issue(user)

    def logout(self, user: User) -> None:
        self.rate_limiter.check(f"logout:{user.id}", 10, 60 * 60)

    def get_user(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if not user or not user.active:
            raise ApiError(401, "Bad credentials", "USER_NOT_FOUND")
        return user

    def list_requests(
        self,
        actor: User,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
        search: str = "",
    ) -> dict[str, Any]:
        rows = list(self.requests.values())
        if actor.role == "employee":
            rows = [row for row in rows if row.user_id == actor.id]
        elif actor.role == "manager":
            rows = [row for row in rows if self.users[row.user_id].department_id == actor.department_id]
        elif actor.role != "admin":
            raise ApiError(403, "Forbidden", "FORBIDDEN")
        if status and status != "all":
            rows = [row for row in rows if row.status == status]
        clean_search = sanitize_text(search, "search", required=False).lower()
        if clean_search:
            rows = [row for row in rows if clean_search in self.users[row.user_id].name.lower()]
        rows.sort(key=lambda item: item.submitted_at, reverse=True)
        start = max(page - 1, 0) * limit
        selected = rows[start:start + limit]
        return {
            "success": True,
            "page": page,
            "limit": limit,
            "total": len(rows),
            "data": [row.public(self.users[row.user_id]) for row in selected],
        }

    def create_request(self, actor: User, payload: dict[str, Any]) -> LeaveRequest:
        require_role(actor, {"employee"})
        leave_type, start_date, end_date, reason = self._validate_request_payload(payload)
        days = weekday_count(start_date, end_date)
        self._ensure_no_pending_overlap(actor.id, start_date, end_date)
        self._ensure_balance(actor.id, leave_type, days, exclude_request_id=None)
        request = LeaveRequest(
            id=self._next_request_id,
            user_id=actor.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
        )
        self.requests[request.id] = request
        self._next_request_id += 1
        return request

    def edit_request(self, actor: User, request_id: int, payload: dict[str, Any]) -> LeaveRequest:
        require_role(actor, {"employee"})
        request = self._owned_request(actor, request_id)
        if request.status != "pending":
            raise ApiError(403, "Cannot modify an approved or rejected request", "REQUEST_LOCKED")
        leave_type, start_date, end_date, reason = self._validate_request_payload(payload)
        days = weekday_count(start_date, end_date)
        self._ensure_no_pending_overlap(actor.id, start_date, end_date, exclude_request_id=request_id)
        self._ensure_balance(actor.id, leave_type, days, exclude_request_id=request_id)
        request.leave_type = leave_type
        request.start_date = start_date
        request.end_date = end_date
        request.days = days
        request.reason = reason
        return request

    def delete_request(self, actor: User, request_id: int) -> None:
        require_role(actor, {"employee"})
        request = self._owned_request(actor, request_id)
        if request.status != "pending":
            raise ApiError(403, "Cannot delete an approved or rejected request", "REQUEST_LOCKED")
        del self.requests[request_id]

    def update_status(self, actor: User, request_id: int, status: str, comment: str = "") -> LeaveRequest:
        require_role(actor, {"manager", "admin"})
        request = self._request_or_404(request_id)
        employee = self.users[request.user_id]
        status = sanitize_choice(status, {"approved", "rejected"}, "status")
        comment = sanitize_text(comment, "comment", required=False)
        if status == "rejected" and len(comment) < 5:
            raise ApiError(400, "Rejection comment must be at least 5 characters", "COMMENT_TOO_SHORT")
        if actor.role == "manager":
            if employee.department_id != actor.department_id:
                raise ApiError(403, "Forbidden", "DEPARTMENT_FORBIDDEN")
            if request.status != "pending":
                raise ApiError(403, "Request has already been processed", "REQUEST_LOCKED")
            request.manager_comment = comment
        else:
            request.admin_comment = comment
        request.status = status
        request.decided_by = actor.id
        return request

    def get_balance(self, actor: User) -> dict[str, Any]:
        require_role(actor, {"employee"})
        return {"success": True, "data": self._balance_for(actor.id)}

    def list_users(self, actor: User) -> dict[str, Any]:
        require_role(actor, {"admin"})
        return {"success": True, "data": [user.public() for user in self.users.values() if user.role != "admin"]}

    def update_user(self, actor: User, user_id: int, payload: dict[str, Any]) -> User:
        require_role(actor, {"admin"})
        user = self.users.get(user_id)
        if not user or user.role == "admin":
            raise ApiError(404, "User not found", "USER_NOT_FOUND")
        if "name" in payload:
            user.name = sanitize_text(payload["name"], "name", required=True)
        if "email" in payload:
            user.email = sanitize_email(payload["email"])
        if "department_id" in payload or "department" in payload:
            user.department_id = sanitize_text(
                payload.get("department_id", payload.get("department")),
                "department",
                required=True,
            )
        if "role" in payload:
            user.role = sanitize_choice(payload["role"], {"employee", "manager"}, "role")
        if "active" in payload:
            active = bool(payload["active"])
            if not active and user.active:
                self._reject_pending_for_deactivated_user(user.id)
            user.active = active
        return user

    def update_policy(self, actor: User, payload: dict[str, Any]) -> Policy:
        require_role(actor, {"admin"})
        self.policy = Policy(
            annual=positive_int(payload.get("annual", self.policy.annual), "annual"),
            sick=positive_int(payload.get("sick", self.policy.sick), "sick"),
            casual=positive_int(payload.get("casual", self.policy.casual), "casual"),
        )
        return self.policy

    def generate_report(self, actor: User, start: str, end: str) -> str:
        require_role(actor, {"admin"})
        start_date = parse_date(start, "startDate")
        end_date = parse_date(end, "endDate")
        ensure_date_order(start_date, end_date)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "employee name",
            "email",
            "department",
            "leave type",
            "start date",
            "end date",
            "days",
            "status",
            "manager comment",
        ])
        for request in sorted(self.requests.values(), key=lambda item: item.start_date):
            if request.end_date < start_date or request.start_date > end_date:
                continue
            employee = self.users[request.user_id]
            writer.writerow([
                employee.name,
                employee.email,
                employee.department_id,
                request.leave_type,
                request.start_date.isoformat(),
                request.end_date.isoformat(),
                request.days,
                request.status,
                request.manager_comment,
            ])
        return output.getvalue()

    def _validate_request_payload(self, payload: dict[str, Any]) -> tuple[str, dt.date, dt.date, str]:
        leave_type = sanitize_choice(payload.get("leave_type", payload.get("type")), LEAVE_TYPES, "leaveType")
        start_date = parse_date(payload.get("start_date", payload.get("startDate")), "startDate")
        end_date = parse_date(payload.get("end_date", payload.get("endDate")), "endDate")
        ensure_date_order(start_date, end_date)
        reason = sanitize_text(payload.get("reason", ""), "reason", required=False, max_length=500)
        if weekday_count(start_date, end_date) <= 0:
            raise ApiError(400, "Leave request must include at least one weekday", "NO_WEEKDAYS")
        return leave_type, start_date, end_date, reason

    def _owned_request(self, actor: User, request_id: int) -> LeaveRequest:
        request = self._request_or_404(request_id)
        if request.user_id != actor.id:
            raise ApiError(403, "Forbidden", "FORBIDDEN")
        return request

    def _request_or_404(self, request_id: int) -> LeaveRequest:
        request = self.requests.get(request_id)
        if not request:
            raise ApiError(404, "Request not found", "REQUEST_NOT_FOUND")
        return request

    def _balance_for(self, user_id: int) -> dict[str, int]:
        current_year = dt.date.today().year
        used = {leave_type: 0 for leave_type in LEAVE_TYPES}
        for request in self.requests.values():
            if request.user_id == user_id and request.status == "approved" and request.start_date.year == current_year:
                used[request.leave_type] += request.days
        policy = self.policy.public()
        return {leave_type: max(policy[leave_type] - used[leave_type], 0) for leave_type in LEAVE_TYPES}

    def _ensure_balance(
        self,
        user_id: int,
        leave_type: str,
        requested_days: int,
        exclude_request_id: int | None,
    ) -> None:
        current_year = dt.date.today().year
        approved_days = 0
        for request in self.requests.values():
            if request.id == exclude_request_id:
                continue
            if (
                request.user_id == user_id
                and request.leave_type == leave_type
                and request.status == "approved"
                and request.start_date.year == current_year
            ):
                approved_days += request.days
        remaining = self.policy.public()[leave_type] - approved_days
        if requested_days > remaining:
            raise ApiError(400, "Not enough leave credits", "INSUFFICIENT_BALANCE")

    def _ensure_no_pending_overlap(
        self,
        user_id: int,
        start_date: dt.date,
        end_date: dt.date,
        exclude_request_id: int | None = None,
    ) -> None:
        for request in self.requests.values():
            if request.id == exclude_request_id:
                continue
            if (
                request.user_id == user_id
                and request.status == "pending"
                and start_date <= request.end_date
                and end_date >= request.start_date
            ):
                raise ApiError(409, "Conflict in request", "OVERLAPPING_PENDING_REQUEST")

    def _reject_pending_for_deactivated_user(self, user_id: int) -> None:
        for request in self.requests.values():
            if request.user_id == user_id and request.status == "pending":
                request.status = "rejected"
                request.admin_comment = "Rejected automatically because the user was deactivated."
