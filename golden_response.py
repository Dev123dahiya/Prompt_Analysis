"""
Single-file reference implementation for the Leave Management System prompt.

Run:
    python golden_response.py --self-test

This benchmark implementation uses only the Python standard library. It models
the core backend behavior required by the prompt: role-aware authentication,
weekday leave calculation, balance enforcement, overlap prevention, department
authorization, admin policy management, user deactivation, CSV reporting, and
structured API-style errors.
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import hashlib
import hmac
import html
import json
import logging
import re
import secrets
import time
from dataclasses import asdict, dataclass, field
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from typing import Any
from urllib.parse import parse_qs, urlparse


SECRET_KEY = "benchmark-dev-secret-change-in-production"
TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60
DATE_FORMAT = "%Y-%m-%d"
LEAVE_TYPES = {"annual", "sick", "casual"}
ROLES = {"employee", "manager", "admin"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class ApiError(Exception):
    def __init__(self, status: int, message: str, code: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.code = code
        self.errors = errors or []

    def payload(self) -> dict[str, Any]:
        body: dict[str, Any] = {"success": False, "message": self.message, "code": self.code}
        if self.errors:
            body["errors"] = self.errors
        return body


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


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
        return "pbkdf2_sha256$120000${}${}".format(
            base64.urlsafe_b64encode(salt).decode(),
            base64.urlsafe_b64encode(digest).decode(),
        )

    @staticmethod
    def verify(password: str, encoded: str) -> bool:
        algorithm, rounds, salt_b64, digest_b64 = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64)
        expected = base64.urlsafe_b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)


class TokenService:
    @staticmethod
    def issue(user: User) -> str:
        payload = {
            "userId": user.id,
            "role": user.role,
            "departmentId": user.department_id,
            "exp": int(time.time()) + TOKEN_TTL_SECONDS,
        }
        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        body = base64.urlsafe_b64encode(raw).decode().rstrip("=")
        signature = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest()
        sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        return f"{body}.{sig}"

    @staticmethod
    def verify(token: str) -> dict[str, Any]:
        try:
            body, sig = token.split(".", 1)
            expected = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest()
            actual = base64.urlsafe_b64decode(_pad_b64(sig))
            if not hmac.compare_digest(actual, expected):
                raise ValueError("bad signature")
            payload = json.loads(base64.urlsafe_b64decode(_pad_b64(body)))
        except Exception as exc:
            raise ApiError(401, "Bad credentials", "BAD_TOKEN") from exc
        if payload["exp"] < int(time.time()):
            raise ApiError(401, "Session expired", "TOKEN_EXPIRED")
        return payload


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        hits = [stamp for stamp in self._hits.get(key, []) if now - stamp < window_seconds]
        if len(hits) >= limit:
            raise ApiError(429, "Too many requests", "RATE_LIMITED")
        hits.append(now)
        self._hits[key] = hits


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
        self.add_user("Alice Employee", "employee@example.com", "engineering", "employee", "2024-01-15", "Password123!")
        self.add_user("Maya Manager", "manager@example.com", "engineering", "manager", "2022-03-01", "Password123!")
        self.add_user("Noah Admin", "admin@example.com", "people", "admin", "2021-06-01", "Password123!")

    def add_user(self, name: str, email: str, department_id: str, role: str, start_date: str, password: str = "Password123!") -> User:
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

    def list_requests(self, actor: User, status: str | None = None, page: int = 1, limit: int = 20, search: str = "") -> dict[str, Any]:
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
            user.department_id = sanitize_text(payload.get("department_id", payload.get("department")), "department", required=True)
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
        writer.writerow(["employee name", "email", "department", "leave type", "start date", "end date", "days", "status", "manager comment"])
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

    def _ensure_balance(self, user_id: int, leave_type: str, requested_days: int, exclude_request_id: int | None) -> None:
        current_year = dt.date.today().year
        approved_days = 0
        for request in self.requests.values():
            if request.id == exclude_request_id:
                continue
            if request.user_id == user_id and request.leave_type == leave_type and request.status == "approved" and request.start_date.year == current_year:
                approved_days += request.days
        remaining = self.policy.public()[leave_type] - approved_days
        if requested_days > remaining:
            raise ApiError(400, "Not enough leave credits", "INSUFFICIENT_BALANCE")

    def _ensure_no_pending_overlap(self, user_id: int, start_date: dt.date, end_date: dt.date, exclude_request_id: int | None = None) -> None:
        for request in self.requests.values():
            if request.id == exclude_request_id:
                continue
            if request.user_id == user_id and request.status == "pending" and start_date <= request.end_date and end_date >= request.start_date:
                raise ApiError(409, "Conflict in request", "OVERLAPPING_PENDING_REQUEST")

    def _reject_pending_for_deactivated_user(self, user_id: int) -> None:
        for request in self.requests.values():
            if request.user_id == user_id and request.status == "pending":
                request.status = "rejected"
                request.admin_comment = "Rejected automatically because the user was deactivated."


def sanitize_text(value: Any, field_name: str, *, required: bool, max_length: int = 120) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ApiError(400, f"{field_name} must be text", "VALIDATION_ERROR")
    cleaned = html.escape(value.strip(), quote=True)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)
    if required and not cleaned:
        raise ApiError(400, f"{field_name} is required", "VALIDATION_ERROR")
    if len(cleaned) > max_length:
        raise ApiError(400, f"{field_name} is too long", "VALIDATION_ERROR")
    return cleaned


def sanitize_email(value: Any) -> str:
    email = sanitize_text(value, "email", required=True, max_length=254).lower()
    if not EMAIL_RE.match(email):
        raise ApiError(400, "Invalid email", "INVALID_EMAIL")
    return email


def sanitize_choice(value: Any, allowed: set[str], field_name: str) -> str:
    cleaned = sanitize_text(value, field_name, required=True).lower()
    if cleaned not in allowed:
        raise ApiError(400, f"Invalid {field_name}", "VALIDATION_ERROR")
    return cleaned


def parse_date(value: Any, field_name: str) -> dt.date:
    if not isinstance(value, str):
        raise ApiError(400, f"{field_name} must be a date", "VALIDATION_ERROR")
    try:
        return dt.datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise ApiError(400, f"{field_name} must use YYYY-MM-DD", "VALIDATION_ERROR") from exc


def ensure_date_order(start_date: dt.date, end_date: dt.date) -> None:
    if end_date < start_date:
        raise ApiError(400, "End date cannot be before start date", "INVALID_DATE_RANGE")


def weekday_count(start_date: dt.date, end_date: dt.date) -> int:
    ensure_date_order(start_date, end_date)
    days = 0
    cursor = start_date
    while cursor <= end_date:
        if cursor.weekday() < 5:
            days += 1
        cursor += dt.timedelta(days=1)
    return days


def positive_int(value: Any, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(400, f"{field_name} must be a number", "VALIDATION_ERROR") from exc
    if parsed < 0 or parsed > 365:
        raise ApiError(400, f"{field_name} must be between 0 and 365", "VALIDATION_ERROR")
    return parsed


def require_role(user: User, allowed: set[str]) -> None:
    if user.role not in allowed:
        raise ApiError(403, "Forbidden", "FORBIDDEN")


def _pad_b64(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode()


def make_handler(service: LeaveManagementService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "LeaveBenchmark/1.0"

        def do_POST(self) -> None:
            self._dispatch("POST")

        def do_GET(self) -> None:
            self._dispatch("GET")

        def do_PUT(self) -> None:
            self._dispatch("PUT")

        def do_DELETE(self) -> None:
            self._dispatch("DELETE")

        def log_message(self, fmt: str, *args: Any) -> None:
            logging.info("%s - %s", self.address_string(), fmt % args)

        def _dispatch(self, method: str) -> None:
            try:
                parsed = urlparse(self.path)
                path = parsed.path
                query = parse_qs(parsed.query)
                body = self._read_json()

                if method == "POST" and path == "/api/auth/login":
                    user, token = service.authenticate(body.get("email", ""), body.get("password", ""), self.client_address[0])
                    self._send_json({"success": True, "user": user.public()}, cookie=self._auth_cookie(token))
                    return

                actor = self._actor()

                if method == "POST" and path == "/api/auth/logout":
                    service.logout(actor)
                    self._send_json({"success": True, "message": "Logged out"}, cookie="token=; HttpOnly; SameSite=Lax; Max-Age=0; Path=/")
                    return

                if method == "GET" and path == "/api/leave/requests":
                    response = service.list_requests(
                        actor,
                        status=query.get("status", [None])[0],
                        page=int(query.get("page", ["1"])[0]),
                        limit=min(int(query.get("limit", ["20"])[0]), 100),
                        search=query.get("search", [""])[0],
                    )
                    self._send_json(response)
                    return

                if method == "POST" and path == "/api/leave/request":
                    request = service.create_request(actor, body)
                    self._send_json({"success": True, "data": request.public()}, status=201)
                    return

                if method in {"PUT", "DELETE"} and path.startswith("/api/leave/request/"):
                    parts = path.strip("/").split("/")
                    request_id = int(parts[3])
                    if len(parts) == 5 and parts[4] == "status" and method == "PUT":
                        request = service.update_status(actor, request_id, body.get("status", ""), body.get("comment", ""))
                        self._send_json({"success": True, "data": request.public()})
                        return
                    if len(parts) == 4 and method == "PUT":
                        request = service.edit_request(actor, request_id, body)
                        self._send_json({"success": True, "data": request.public()})
                        return
                    if len(parts) == 4 and method == "DELETE":
                        service.delete_request(actor, request_id)
                        self._send_json({"success": True, "message": "Request deleted"})
                        return

                if method == "GET" and path == "/api/leave/balance":
                    self._send_json(service.get_balance(actor))
                    return

                if method == "GET" and path == "/api/admin/users":
                    self._send_json(service.list_users(actor))
                    return

                if method == "POST" and path == "/api/admin/users":
                    require_role(actor, {"admin"})
                    user = service.add_user(
                        body.get("name", ""),
                        body.get("email", ""),
                        body.get("department_id", body.get("department", "")),
                        body.get("role", "employee"),
                        body.get("start_date", body.get("startDate", "")),
                        body.get("password", "Password123!"),
                    )
                    self._send_json({"success": True, "data": user.public()}, status=201)
                    return

                if method == "PUT" and path.startswith("/api/admin/users/"):
                    user = service.update_user(actor, int(path.rsplit("/", 1)[1]), body)
                    self._send_json({"success": True, "data": user.public()})
                    return

                if method == "GET" and path == "/api/admin/policy":
                    require_role(actor, {"admin"})
                    self._send_json({"success": True, "data": service.policy.public()})
                    return

                if method == "PUT" and path == "/api/admin/policy":
                    policy = service.update_policy(actor, body)
                    self._send_json({"success": True, "data": policy.public()})
                    return

                if method == "POST" and path == "/api/admin/report":
                    csv_text = service.generate_report(actor, body.get("start_date", body.get("startDate", "")), body.get("end_date", body.get("endDate", "")))
                    self._send_text(csv_text, "text/csv")
                    return

                raise ApiError(404, "Route not found", "ROUTE_NOT_FOUND")
            except ApiError as exc:
                logging.error("%s %s -> %s %s", method, self.path, exc.status, exc.code)
                self._send_json(exc.payload(), status=exc.status)
            except Exception:
                logging.exception("Unhandled error for %s %s", method, self.path)
                self._send_json(ApiError(500, "Internal server error", "INTERNAL_ERROR").payload(), status=500)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            if length == 0:
                return {}
            try:
                parsed = json.loads(self.rfile.read(length))
            except json.JSONDecodeError as exc:
                raise ApiError(400, "Invalid JSON", "INVALID_JSON") from exc
            if not isinstance(parsed, dict):
                raise ApiError(400, "Request body must be an object", "VALIDATION_ERROR")
            return parsed

        def _actor(self) -> User:
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            token = cookie.get("token")
            if not token:
                raise ApiError(401, "Bad credentials", "NO_TOKEN")
            payload = TokenService.verify(token.value)
            return service.get_user(int(payload["userId"]))

        def _auth_cookie(self, token: str) -> str:
            return f"token={token}; HttpOnly; Secure; SameSite=Lax; Max-Age={TOKEN_TTL_SECONDS}; Path=/"

        def _send_json(self, payload: dict[str, Any], status: int = 200, cookie: str | None = None) -> None:
            encoded = json.dumps(payload, default=str).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self._security_headers(cookie)
            self.end_headers()
            self.wfile.write(encoded)

        def _send_text(self, payload: str, content_type: str, status: int = 200) -> None:
            encoded = payload.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self._security_headers(None)
            self.end_headers()
            self.wfile.write(encoded)

        def _security_headers(self, cookie: str | None) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Access-Control-Allow-Origin", "https://frontend.example.com")
            self.send_header("Access-Control-Allow-Credentials", "true")
            if cookie:
                self.send_header("Set-Cookie", cookie)

    return Handler


def run_self_test() -> None:
    service = LeaveManagementService()
    employee, _ = service.authenticate("employee@example.com", "Password123!")
    manager, _ = service.authenticate("manager@example.com", "Password123!")
    admin, _ = service.authenticate("admin@example.com", "Password123!")

    request = service.create_request(employee, {"leave_type": "annual", "start_date": "2026-06-01", "end_date": "2026-06-05", "reason": "Family event"})
    assert request.days == 5

    try:
        service.create_request(employee, {"leave_type": "annual", "start_date": "2026-06-03", "end_date": "2026-06-04"})
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
    assert "Alice Employee" in report
    assert "manager comment" in report

    pending = service.create_request(employee, {"leave_type": "sick", "start_date": "2026-07-06", "end_date": "2026-07-06"})
    service.update_user(admin, employee.id, {"active": False})
    assert service.requests[pending.id].status == "rejected"
    print("Self-test passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Leave Management benchmark reference implementation")
    parser.add_argument("--serve", action="store_true", help="start the local HTTP API server")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port for --serve")
    parser.add_argument("--self-test", action="store_true", help="run built-in behavioral tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    if args.serve:
        service = LeaveManagementService()
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(service))
        print(f"Serving on http://127.0.0.1:{args.port}")
        server.serve_forever()

    if not args.self_test and not args.serve:
        parser.print_help()


if __name__ == "__main__":
    main()
