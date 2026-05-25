import json
import logging
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import parse_qs, urlparse

from .config import TOKEN_TTL_SECONDS
from .errors import ApiError
from .security import TokenService
from .service import LeaveManagementService
from .validators import require_role


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
                    user, token = service.authenticate(
                        body.get("email", ""),
                        body.get("password", ""),
                        self.client_address[0],
                    )
                    self._send_json({"success": True, "user": user.public()}, cookie=self._auth_cookie(token))
                    return

                actor = self._actor()

                if method == "POST" and path == "/api/auth/logout":
                    service.logout(actor)
                    self._send_json(
                        {"success": True, "message": "Logged out"},
                        cookie="token=; HttpOnly; SameSite=Lax; Max-Age=0; Path=/",
                    )
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
                        request = service.update_status(
                            actor,
                            request_id,
                            body.get("status", ""),
                            body.get("comment", ""),
                        )
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
                    csv_text = service.generate_report(
                        actor,
                        body.get("start_date", body.get("startDate", "")),
                        body.get("end_date", body.get("endDate", "")),
                    )
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

        def _actor(self):
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
