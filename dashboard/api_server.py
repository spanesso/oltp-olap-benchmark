#!/usr/bin/env python3
"""
Minimal live-benchmark API server.  Standard library only — no extra deps.

Run from the project root:
    python dashboard/api_server.py

Endpoints
---------
GET  /api/benchmark/ping          health-check → {"status": "ok"}
POST /api/benchmark/run           run the benchmark and return fresh JSON
     body (optional): {"profile": "full"}   default: "full"

The handler copies results/benchmark_<profile>.json to
dashboard/public/ after every successful run, so the Vite dev server
and the built static site both serve updated numbers immediately.
"""

import json
import os
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = 8788
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _results_path(profile: str) -> Path:
    return PROJECT_ROOT / "results" / f"benchmark_{profile}.json"


def _public_path(profile: str) -> Path:
    return PROJECT_ROOT / "dashboard" / "public" / f"benchmark_{profile}.json"


class Handler(BaseHTTPRequestHandler):
    # ── CORS pre-flight ──────────────────────────────────────────────────
    def do_OPTIONS(self):  # noqa: N802
        self._cors(200)
        self.end_headers()

    # ── Health check ─────────────────────────────────────────────────────
    def do_GET(self):  # noqa: N802
        if self.path == "/api/benchmark/ping":
            self._json(200, {"status": "ok"})
        else:
            self._json(404, {"error": "not found"})

    # ── Run benchmark ────────────────────────────────────────────────────
    def do_POST(self):  # noqa: N802
        if self.path != "/api/benchmark/run":
            self._json(404, {"error": "not found"})
            return

        body: dict = {}
        length = int(self.headers.get("Content-Length", 0))
        if length:
            try:
                body = json.loads(self.rfile.read(length))
            except Exception:
                pass

        profile: str = body.get("profile", "full")
        if profile not in ("full", "quick"):
            self._json(400, {"error": "profile must be 'full' or 'quick'"})
            return

        print(f"[api] running benchmark --profile {profile} …")
        try:
            proc = subprocess.run(
                [sys.executable, "benchmark.py", "run", f"--profile={profile}"],
                capture_output=True,
                text=True,
                timeout=660,
                cwd=str(PROJECT_ROOT),
            )
        except subprocess.TimeoutExpired:
            self._json(504, {"error": "Benchmark timed out after 11 minutes"})
            return
        except Exception as exc:
            self._json(500, {"error": str(exc)})
            return

        # exit 0 = ok + significance reached; exit 1 = ok but significance NOT reached
        if proc.returncode not in (0, 1):
            snippet = (proc.stderr or proc.stdout or "")[-600:]
            self._json(500, {"error": f"benchmark.py exited {proc.returncode}", "detail": snippet})
            return

        src = _results_path(profile)
        if not src.exists():
            self._json(500, {"error": f"results file not found: {src}"})
            return

        # refresh dashboard/public/ so Vite serves the updated JSON
        dst = _public_path(profile)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        print(f"[api] copied {src.name} → {dst}")

        try:
            data = json.loads(src.read_text())
        except Exception as exc:
            self._json(500, {"error": f"could not parse results JSON: {exc}"})
            return

        self._json(200, data)

    # ── helpers ──────────────────────────────────────────────────────────
    def _cors(self, code: int) -> None:
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, payload: object) -> None:
        body = json.dumps(payload).encode()
        self._cors(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # suppress default access-log noise
        pass


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"NYC 311 Benchmark API  →  http://localhost:{PORT}")
    print(f"Project root           →  {PROJECT_ROOT}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[api] stopped.")
