"""Bot 2 coordination worker.

Execution boundary: polls the Project_Brain_AI coordination cycle and exposes
runtime readiness. Optional reasoning is provider-neutral and fail-closed: no
claim of autonomous reasoning is made until an LLM provider is configured.
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bot2_reasoning_adapter import configured as reasoning_configured

REPO = os.environ.get("COORDINATION_REPO", "xsmbv23/Project_Brain_AI")
BRANCH = os.environ.get("COORDINATION_BRANCH", "main")
BUS_PATH = os.environ.get("COORDINATION_PATH", "coordination/current_cycle.json")
RECEIPT_PATH = os.environ.get("BOT2_RECEIPT_PATH", "bot2_runtime_receipt.json")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "60"))
RUN_ONCE = os.environ.get("RUN_ONCE", "0") == "1"
PORT = int(os.environ.get("PORT", "10000"))
STOP = False
LAST_OBSERVATION: dict = {"status": "STARTING"}


def _stop(_signum, _frame):
    global STOP
    STOP = True

signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


def _github_get(path: str) -> str:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "bot2-quant-worker"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8")


def _log(event: str, **fields) -> None:
    payload = {
        "worker": "BOT2_QUANT_WORKER",
        "event": event,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    print(json.dumps(payload, sort_keys=True), flush=True)


def _write_receipt() -> None:
    receipt = {
        "schema": "bot2-runtime-receipt/v1",
        "worker": "BOT2_QUANT_WORKER",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "reasoning": "READY" if reasoning_configured() else "NOT_CONFIGURED",
        "gate_authority": "NONE",
        "promotion": "DENY",
        "observation": LAST_OBSERVATION,
    }
    with open(RECEIPT_PATH, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, sort_keys=True, indent=2)
        handle.write("\n")


def poll_once() -> None:
    global LAST_OBSERVATION
    content = _github_get(BUS_PATH)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    try:
        cycle = json.loads(content)
    except json.JSONDecodeError:
        LAST_OBSERVATION = {"status": "BUS_INVALID_JSON", "bus_sha256": digest}
        _log("BUS_INVALID_JSON", content_sha256=digest)
        _write_receipt()
        return

    LAST_OBSERVATION = {
        "status": "CYCLE_OBSERVED",
        "cycle_id": cycle.get("cycle_id"),
        "cycle_status": cycle.get("status"),
        "e2e_segment": cycle.get("e2e_segment"),
        "blocker": cycle.get("blocker"),
        "bus_sha256": digest,
        "required_action": (cycle.get("required_actions") or {}).get("BOT2_QUANT"),
    }
    _log("CYCLE_OBSERVED", **LAST_OBSERVATION)
    if not reasoning_configured():
        _log("REASONING_BLOCKED", blocker="BOT2_LLM_REASONING_NOT_CONFIGURED")
    _write_receipt()


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {
                "worker": "BOT2_QUANT_WORKER",
                "role": "COORDINATION_EXECUTION",
                "reasoning": "READY" if reasoning_configured() else "NOT_CONFIGURED",
                "gate_authority": "NONE",
                "promotion": "DENY",
                "last_observation": LAST_OBSERVATION,
            })
            return
        self._json(404, {"status": "NOT_FOUND"})

    def log_message(self, *_args) -> None:
        return


def _serve() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    while not STOP:
        server.timeout = 1.0
        server.handle_request()
    server.server_close()


if __name__ == "__main__":
    _log("START", port=PORT, poll_seconds=POLL_SECONDS, reasoning_configured=reasoning_configured())
    server_thread = threading.Thread(target=_serve, daemon=True)
    server_thread.start()
    while not STOP:
        try:
            poll_once()
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            LAST_OBSERVATION.clear()
            LAST_OBSERVATION.update({"status": "POLL_ERROR", "error": type(exc).__name__})
            _log("POLL_ERROR", error=type(exc).__name__, detail=str(exc))
            _write_receipt()
        if RUN_ONCE:
            break
        for _ in range(POLL_SECONDS):
            if STOP:
                break
            time.sleep(1)
    _log("STOP")
