#!/usr/bin/env python3
"""
Local FTE vs. ADP cross-check app.

Serves the dashboard at http://localhost:8765 and backs its "Run cross-check"
button: each run pulls ADP live, re-reads the Approved FTE List files,
reconciles, and rebuilds index.html / fte_planning_app.html / apps_script/Index.html.

Listens on 127.0.0.1 only - ADP credentials never leave this machine.
"""

import os
import json
import threading
import traceback
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

import sync_adp_payroll
import build_webapp_ui

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8765
RUN_LOCK = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/status":
            return self._json(200, {"ok": True, "running": RUN_LOCK.locked()})
        if self.path in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()
        # Only the dashboard itself is served; no browsing of project files
        self.send_error(404)

    def do_POST(self):
        if self.path != "/api/run":
            return self.send_error(404)
        length = int(self.headers.get("Content-Length") or 0)
        opts = json.loads(self.rfile.read(length) or b"{}")
        if not RUN_LOCK.acquire(blocking=False):
            return self._json(409, {"error": "A cross-check is already running."})
        try:
            report = sync_adp_payroll.run_crosscheck(cached=bool(opts.get("cached")))
            build_webapp_ui.generate_files()
            self._json(200, report)
        except Exception as e:
            traceback.print_exc()
            self._json(500, {"error": f"{type(e).__name__}: {e}"})
        finally:
            RUN_LOCK.release()

    def log_message(self, fmt, *args):
        if args and "/api/" in str(args[0]):
            super().log_message(fmt, *args)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}/"
    print(f"FTE vs. ADP cross-check running at {url}  (Ctrl+C to stop)")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
