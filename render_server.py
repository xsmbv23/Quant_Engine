"""Bounded Render runtime for Quant Engine.

This is an execution boundary, not a governance boundary. It exposes only
metadata/health until an explicit research admission contract is satisfied.
No canonical dataset is loaded at process boot, and no synthetic fallback is
allowed. Heavy research must be invoked through bounded, future room-specific
execution paths rather than the health process.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_MEMORY_GUARD_BYTES = 320 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def _write(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._write(200, {
                "project": "XSMB_FORENSIC",
                "component": "QUANT_ENGINE",
                "role": "LAYER_1_EXECUTION_PLANE",
                "runtime": "BOUNDED",
                "dataset_loaded_at_boot": False,
                "synthetic_fallback": False,
                "memory_guard_bytes": MAX_MEMORY_GUARD_BYTES,
                "promotion": "DENY",
                "staircase": "LOCKED",
            })
            return
        if self.path == "/governance":
            self._write(200, {
                "brain_authority": "xsmbv23/Project_Brain_AI",
                "data_authority": "xsmbv23/xsmb-quant",
                "quant_engine": "CALCULATION_ONLY",
                "sensor_authority": "OBSERVATION_ONLY",
                "promotion_authority": "BRAIN_ONLY",
                "action_authority": "DENY",
                "unknown": "NOT_PASS",
            })
            return
        self._write(404, {"status": "NOT_FOUND"})

    def do_HEAD(self) -> None:
        if self.path in ("/health", "/governance"):
            self._write(200, {})
        else:
            self._write(404, {})

    def log_message(self, *_args) -> None:
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.daemon_threads = True
    server.serve_forever()
