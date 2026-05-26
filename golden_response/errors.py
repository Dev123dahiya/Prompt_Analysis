from typing import Any


class ApiError(Exception):
    """Structured API-style exception used by the benchmark service."""

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
        body: dict[str, Any] = {
            "success": False,
            "message": self.message,
            "code": self.code,
        }
        if self.errors:
            body["errors"] = self.errors
        return body
