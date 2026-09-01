"""Minimal status dashboard for the COMSOL MCP server.

Serves a static page that polls ``/api/status`` (session + model info). No
Node/JS build step required.
"""

import http.server
import json
import os
import socketserver

from comsol_mcp.backends import get_backend
from comsol_mcp.backends.session import gui_status
from comsol_mcp.config import config


PORT = config.web_port
DIRECTORY = os.path.dirname(__file__)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/api/status":
            try:
                session = gui_status()
                try:
                    model = get_backend().model_info()
                except Exception as e:  # noqa: BLE001
                    model = {"error": str(e)}
                payload = json.dumps({"session": session, "model": model}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:  # noqa: BLE001
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
            return
        super().do_GET()


def run() -> None:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"COMSOL MCP dashboard running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard stopped")
