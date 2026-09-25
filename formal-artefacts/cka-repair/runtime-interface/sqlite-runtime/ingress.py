"""Loopback-only experimental HTTP boundary. Not a production web server."""
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3

from ledger import validate_request


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def make_server(ledger, control_token, advice_token):
    if (not all(type(t) is str and t.isascii() and len(t) >= 32 for t in [control_token, advice_token])
            or control_token == advice_token):
        raise ValueError("supply two distinct, randomly generated credentials")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not put credentials or request bodies in test evidence.

        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def reply(self, status, data):
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/command":
                self.reply(404, {"error": "unknown endpoint"})
                return
            headers = self.headers.get_all("Authorization", [])
            if len(headers) != 1 or not headers[0].startswith("Bearer "):
                self.reply(401, {"error": "unknown credential"})
                return
            token = headers[0][7:].encode("utf-8")
            role = None
            for expected, candidate in [(control_token, "control"), (advice_token, "advice")]:
                if hmac.compare_digest(token, expected.encode("ascii")):
                    role = candidate
            if role is None:
                self.reply(401, {"error": "unknown credential"})
                return
            try:
                lengths = self.headers.get_all("Content-Length", [])
                if len(lengths) != 1 or self.headers.get("Transfer-Encoding"):
                    raise ValueError("unambiguous length required")
                length = int(lengths[0])
                if not 0 < length <= 4096 or self.headers.get_content_type() != "application/json":
                    raise ValueError("expected a small JSON body")
                body = json.loads(self.rfile.read(length).decode("utf-8"), object_pairs_hook=unique_object)
                command, arguments = validate_request(body)
                if role == "advice" and command != "Advice":
                    self.reply(403, {"error": "command outside advice authority"})
                    return
                self.reply(200, ledger.apply(command, **arguments))
            except (ValueError, UnicodeError, RecursionError):
                self.reply(400, {"error": "invalid command or conflicting operation"})
            except sqlite3.Error:
                self.reply(503, {"error": "database transaction unavailable; inspect state before retry"})

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
