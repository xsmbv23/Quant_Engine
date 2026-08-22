"""Minimal real-source raw collector for xsmb.com.vn.

Acquisition only. No parsing, normalization, signal generation, or truth
promotion is allowed here. Exact response bytes are hashed before any
interpretation. Missing authorization/reference remains an admission evidence
 gap; it is never treated as permission.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

SOURCE_ID: Final = "xsmb.com.vn"
SOURCE_URL: Final = "https://xsmb.com.vn/"
MAX_RAW_BYTES: Final = 2 * 1024 * 1024
TIMEOUT_SECONDS: Final = 8
USER_AGENT: Final = "XSMB-FORENSIC-RawCollector/1.0"


@dataclass(frozen=True)
class RawCaptureReceipt:
    business_date: str
    source_id: str
    source_url: str
    final_url: str
    retrieved_at_utc: str
    http_status: int
    content_type: str
    raw_bytes: int
    raw_bytes_sha256: str
    raw_artifact_path: str
    truncated: bool
    acquisition_channel: str
    acquisition_reference: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_bounded(response) -> tuple[bytes, bool]:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(64 * 1024, MAX_RAW_BYTES - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_RAW_BYTES:
            allowed = MAX_RAW_BYTES - (total - len(chunk))
            if allowed > 0:
                chunks.append(chunk[:allowed])
            return b"".join(chunks), True
        chunks.append(chunk)
        if total == MAX_RAW_BYTES:
            return b"".join(chunks), bool(response.read(1))
    return b"".join(chunks), False


def capture_raw(business_date: str, *, artifact_root: str | Path = "data_buffer/raw_artifacts") -> RawCaptureReceipt:
    if not business_date:
        raise ValueError("business_date is required and must be explicit")
    channel = os.environ.get("ACQUISITION_CHANNEL", "").strip()
    reference = os.environ.get("ACQUISITION_REFERENCE", "").strip()
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}, method="GET")
    retrieved_at = _utc_now()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = int(response.status)
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
            raw, truncated = _read_bounded(response)
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        raise RuntimeError(f"COLLECTOR_NETWORK_FAIL:{type(exc).__name__}") from exc

    digest = hashlib.sha256(raw).hexdigest()
    day_dir = Path(artifact_root) / business_date
    day_dir.mkdir(parents=True, exist_ok=True)
    raw_path = day_dir / f"{SOURCE_ID.replace('.', '_')}_{digest}.raw"
    raw_path.write_bytes(raw)
    receipt = RawCaptureReceipt(business_date, SOURCE_ID, SOURCE_URL, final_url, retrieved_at, status, content_type, len(raw), digest, str(raw_path), truncated, channel, reference)
    (day_dir / f"{SOURCE_ID.replace('.', '_')}_{digest}.receipt.json").write_text(json.dumps(asdict(receipt), ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return receipt
