"""Bot 2 deterministic coordination worker skeleton.

Purpose: run background-safe Quant/Data coordination tasks without a ChatGPT browser.
This worker does NOT invent analysis or open forensic gates. It only polls the
shared coordination bus, validates/records assigned work, and emits durable
worker receipts. AI reasoning remains a separate admitted capability.
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = os.environ.get("COORDINATION_REPO", "xsmbv23/Project_Brain_AI")
BUS_PATH = os.environ.get("COORDINATION_PATH", "coordination/current_cycle.json")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "60"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
RUN_ONCE = os.environ.get("RUN_ONCE", "0") == "1"
STOP = False


def _stop(_signum, _frame):
    global STOP
    STOP = True


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


def _github_get(path: str) -> dict:
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required for background coordination")
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "quant-bot2-worker",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def _log(event: str, **fields) -> None:
    payload = {
        "worker": "BOT2_QUANT_WORKER",
        "event": event,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    print(json.dumps(payload, sort_keys=True), flush=True)


def poll_once() -> None:
    raw = _github_get(BUS_PATH)
    decoded = raw.get("content", "")
    import base64
    content = base64.b64decode(decoded).decode("utf-8") if decoded else ""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    try:
        cycle = json.loads(content)
    except json.JSONDecodeError:
        _log("BUS_INVALID_JSON", content_sha256=digest)
        return

    _log(
        "CYCLE_OBSERVED",
        cycle_id=cycle.get("cycle_id"),
        status=cycle.get("status"),
        e2e_segment=cycle.get("e2e_segment"),
        blocker=cycle.get("blocker"),
        bus_sha256=digest,
    )


if __name__ == "__main__":
    _log("START")
    while not STOP:
        try:
            poll_once()
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError) as exc:
            _log("POLL_ERROR", error=type(exc).__name__, detail=str(exc))
        if RUN_ONCE:
            break
        for _ in range(POLL_SECONDS):
            if STOP:
                break
            time.sleep(1)
    _log("STOP")
