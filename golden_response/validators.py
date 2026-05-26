import datetime as dt
import html
import re
from typing import Any

from .config import DATE_FORMAT
from .errors import ApiError
from .models import User

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


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
