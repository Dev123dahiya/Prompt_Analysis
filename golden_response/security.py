import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from .config import SECRET_KEY, TOKEN_TTL_SECONDS
from .errors import ApiError
from .models import User


class PasswordHasher:
    """Small standard-library password hasher for the executable benchmark."""

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


def _pad_b64(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode()
