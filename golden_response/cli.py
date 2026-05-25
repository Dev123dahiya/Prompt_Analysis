import argparse
from http.server import ThreadingHTTPServer

from .server import make_handler
from .service import LeaveManagementService
from .tests import run_self_test


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leave Management benchmark reference implementation"
    )
    parser.add_argument("--serve", action="store_true", help="start the local HTTP API")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port for --serve")
    parser.add_argument("--self-test", action="store_true", help="run built-in tests")
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
