"""Serve the H1-H10 explainer review UI with a JSON save endpoint."""
from __future__ import annotations

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "review_h1_h10"
EDITS_PATH = APP_DIR / "review_edits.json"


class ReviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/edits":
            if EDITS_PATH.exists():
                try:
                    self._send_json(json.loads(EDITS_PATH.read_text(encoding="utf-8")))
                    return
                except json.JSONDecodeError:
                    pass
            self._send_json({"version": 1, "lessons": {}})
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/save":
            self._send_json({"ok": False, "error": "not found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "invalid json"}, status=400)
            return

        APP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = EDITS_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(EDITS_PATH)
        self._send_json({"ok": True, "path": str(EDITS_PATH)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if not (APP_DIR / "index.html").exists():
        raise FileNotFoundError(APP_DIR / "index.html")

    handler = partial(ReviewHandler)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Serving H1-H10 review UI at http://127.0.0.1:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
