"""Room 01 streaming NDJSON admission boundary.

This adapter validates records without parsing domain meaning or granting
canonical authority. It is intentionally streaming to protect the Render
512 MiB boundary and rejects lookahead, domain violations, duplicate identity,
and hash mismatches.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from typing import BinaryIO, Iterable

MAX_LINE_BYTES = 16 * 1024
MAX_WINDOW_DAYS = 30


@dataclass(frozen=True)
class InputRecord:
    business_date: date
    source_id: str
    value: int
    raw_sha256: str


def _parse_date(value: object, *, today: date) -> date:
    if not isinstance(value, str):
        raise ValueError("BAD_DATE")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("BAD_DATE") from exc
    if parsed > today:
        raise ValueError("FUTURE_DATE")
    return parsed


def _validate_hash(raw: bytes, declared: object) -> str:
    if not isinstance(declared, str) or len(declared) != 64:
        raise ValueError("BAD_HASH")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != declared.lower() or declared != declared.lower():
        raise ValueError("HASH_MISMATCH")
    return digest


def iter_ndjson(stream: BinaryIO, *, today: date, anchor_date: date | None = None) -> Iterable[InputRecord]:
    """Yield validated records one line at a time; never bulk-load the stream."""
    seen: set[tuple[str, str, int]] = set()
    yielded = 0
    for line_no, raw_line in enumerate(stream, 1):
        if len(raw_line) > MAX_LINE_BYTES:
            raise ValueError(f"OVERSIZED_RECORD:{line_no}")
        raw = raw_line.rstrip(b"\r\n")
        if not raw:
            raise ValueError(f"BLANK_LINE:{line_no}")
        try:
            obj = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"MALFORMED_JSON:{line_no}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"RECORD_NOT_OBJECT:{line_no}")
        required = {"business_date", "source_id", "value", "raw_sha256"}
        if set(obj) != required:
            raise ValueError(f"SCHEMA_MISMATCH:{line_no}")
        day = _parse_date(obj["business_date"], today=today)
        if anchor_date is not None and abs((anchor_date - day).days) > MAX_WINDOW_DAYS:
            raise ValueError(f"WINDOW_EXCEEDED:{line_no}")
        source_id = obj["source_id"]
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(f"BAD_SOURCE_ID:{line_no}")
        value = obj["value"]
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 99:
            raise ValueError(f"VALUE_OUT_OF_DOMAIN:{line_no}")
        digest = _validate_hash(raw, obj["raw_sha256"])
        identity = (day.isoformat(), source_id, value)
        if identity in seen:
            raise ValueError(f"DUPLICATE_IDENTITY:{line_no}")
        seen.add(identity)
        yielded += 1
        yield InputRecord(day, source_id, value, digest)

    if yielded == 0:
        raise ValueError("EMPTY_INPUT")
