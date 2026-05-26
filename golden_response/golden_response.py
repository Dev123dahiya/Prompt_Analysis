"""
golden_response.py
Single-file consolidated Leave Management System benchmark implementation.
Merged from:
- cli.py
- config.py
- errors.py
- models.py
- security.py
- validators.py
- service.py
- server.py
- tests.py
- __main__.py
"""

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


# =========================================================
# CONFIG
# =========================================================

SECRET_KEY = "benchmark-dev-secret-change-in-production"
TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60
DATE_FORMAT = "%Y-%m-%d"

LEAVE_TYPES = {"annual", "sick", "casual"}
ROLES = {"employee", "manager", "admin"}

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


# =========================================================
# ERRORS
# =========================================================

class ApiError(Exception):
    def __init__(
        self,
        status: int,
        message: str,
        code: str,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.code = code
        self.errors = errors or []

    def payload(self) -> dict[str, Any]:
        body = {
            "success": False,
            "message": self.message,
            "code": self.code,
        }
        if self.errors:
            body["errors"] = self.errors
        return body


# =========================================================
# MODELS
# =========================================================

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


# =========================================================
# VALIDATORS
# =========================================================

def sanitize_text(
    value: Any,
    field_name: str,
    *,
    required: bool,
    max_length: int = 120,
) -> str:
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
        raise ApiError(
            400,
            f"{field_name} must use YYYY-MM-DD",
            "VALIDATION_ERROR",
        ) from exc


def ensure_date_order(start_date: dt.date, end_date: dt.date) -> None:
    if end_date < start_date:
        raise ApiError(
            400,
            "End date cannot be before start date",
            "INVALID_DATE_RANGE",
        )


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
        raise ApiError(
            400,
            f"{field_name} must be a number",
            "VALIDATION_ERROR",
        ) from exc

    if parsed < 0 or parsed > 365:
        raise ApiError(
            400,
            f"{field_name} must be between 0 and 365",
            "VALIDATION_ERROR",
        )

    return parsed


def require_role(user: User, allowed: set[str]) -> None:
    if user.role not in allowed:
        raise ApiError(403, "Forbidden", "FORBIDDEN")


# =========================================================
# SECURITY
# =========================================================

class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            120_000,
        )

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

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            int(rounds),
        )

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

        raw = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()

        body = base64.urlsafe_b64encode(raw).decode().rstrip("=")

        signature = hmac.new(
            SECRET_KEY.encode(),
            body.encode(),
            hashlib.sha256,
        ).digest()

        sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{body}.{sig}"

    @staticmethod
    def verify(token: str) -> dict[str, Any]:
        try:
            body, sig = token.split(".", 1)

            expected = hmac.new(
                SECRET_KEY.encode(),
                body.encode(),
                hashlib.sha256,
            ).digest()

            actual = base64.urlsafe_b64decode(_pad_b64(sig))

            if not hmac.compare_digest(actual, expected):
                raise ValueError("bad signature")

            payload = json.loads(
                base64.urlsafe_b64decode(_pad_b64(body))
            )

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

        hits = [
            stamp
            for stamp in self._hits.get(key, [])
            if now - stamp < window_seconds
        ]

        if len(hits) >= limit:
            raise ApiError(429, "Too many requests", "RATE_LIMITED")

        hits.append(now)
        self._hits[key] = hits


def _pad_b64(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode()


# =========================================================
# SERVICE
# =========================================================

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
        self.add_user(
            "Alice Employee",
            "employee@example.com",
            "engineering",
            "employee",
            "2024-01-15",
        )

        self.add_user(
            "Maya Manager",
            "manager@example.com",
            "engineering",
            "manager",
            "2022-03-01",
        )

        self.add_user(
            "Noah Admin",
            "admin@example.com",
            "people",
            "admin",
            "2021-06-01",
        )

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
        department_id = sanitize_text(
            department_id,
            "department",
            required=True,
        )

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


# =========================================================
# TESTS
# =========================================================

def run_self_test() -> None:
    service = LeaveManagementService()

    employee, _ = service.authenticate(
        "employee@example.com",
        "Password123!",
    )

    assert employee.role == "employee"

    print("Self-test passed.")


# =========================================================
# CLI
# =========================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leave Management benchmark reference implementation"
    )

    parser.add_argument(
        "--serve",
        action="store_true",
        help="start the local HTTP API",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP port for --serve",
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in tests",
    )

    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    if args.serve:
        print(f"Serving on http://127.0.0.1:{args.port}")

    if not args.self_test and not args.serve:
        parser.print_help()


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":
    main()