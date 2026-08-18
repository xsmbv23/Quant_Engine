"""Room 01 Input Adapter.

Strict transport/admission boundary for real-source data. It does not clean,
normalize, enrich, score, infer signals, or promote canonical truth.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator

MAX_WINDOW = 30
MAX_LINE_BYTES = 16 * 1024
VALUE_MIN = 0
VALUE_MAX = 99


class AdapterError(ValueError):
    """Fail-closed input contract violation."""


@dataclass(frozen=True)
class AdapterResult:
    input_hash: str
    window: tuple[dict[str, Any], ...]
    records_seen: int
    window_size: int


def compute_file_hash(path: str | Path, chunk_size: int = 8192) -> str:
    """Hash exact raw file bytes without loading the file into memory."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_day(value: Any) -> date:
    if not isinstance(value, str):
        raise AdapterError("DAY_MISSING_OR_NOT_STRING")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise AdapterError("DAY_NOT_ISO_DATE") from exc


def _validate_record(record: dict[str, Any], line_number: int, *, as_of: date | None) -> date:
    allowed = {"day", "source_id", "values", "raw_sha256"}
    if set(record) != allowed:
        raise AdapterError(f"SCHEMA_MISMATCH:{line_number}")

    current = _parse_day(record.get("day"))
    if as_of is not None and current > as_of:
        raise AdapterError(f"FUTURE_RECORD:{line_number}")

    source_id = record.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip():
        raise AdapterError(f"SOURCE_ID_INVALID:{line_number}")

    values = record.get("values")
    if not isinstance(values, list) or not values:
        raise AdapterError(f"VALUES_INVALID:{line_number}")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or not VALUE_MIN <= value <= VALUE_MAX:
            raise AdapterError(f"VALUE_OUT_OF_DOMAIN:{line_number}")

    raw_hash = record.get("raw_sha256")
    if not isinstance(raw_hash, str) or len(raw_hash) != 64 or any(c not in "0123456789abcdef" for c in raw_hash):
        raise AdapterError(f"RAW_HASH_INVALID:{line_number}")
    return current


def stream_days(path: str | Path, *, as_of: date | None = None) -> Iterator[dict[str, Any]]:
    """Yield strictly causal, validated NDJSON records in source order.

    Blank lines, malformed records, schema drift, future records, duplicate or
    descending dates, invalid source IDs, invalid values and malformed raw
    hashes are all hard-deny conditions. No sorting or silent repair occurs.
    """
    previous: date | None = None
    seen_days: set[date] = set()
    with open(path, "rb") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            if len(raw_line) > MAX_LINE_BYTES:
                raise AdapterError(f"LINE_TOO_LARGE:{line_number}")
            if not raw_line.strip():
                raise AdapterError(f"BLANK_LINE:{line_number}")
            try:
                record = json.loads(raw_line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise AdapterError(f"INVALID_NDJSON_LINE:{line_number}") from exc
            if not isinstance(record, dict):
                raise AdapterError(f"RECORD_NOT_OBJECT:{line_number}")
            current = _validate_record(record, line_number, as_of=as_of)
            if previous is not None and current <= previous:
                raise AdapterError(f"NON_CAUSAL_ORDER:{line_number}")
            if current in seen_days:
                raise AdapterError(f"DUPLICATE_DAY:{line_number}")
            seen_days.add(current)
            previous = current
            yield record


def get_window(path: str | Path, n: int = MAX_WINDOW, *, as_of: date | None = None) -> AdapterResult:
    """Return only the final bounded causal window plus exact raw input hash."""
    if n < 1 or n > MAX_WINDOW:
        raise AdapterError("WINDOW_OUT_OF_BOUNDS")
    buffer: deque[dict[str, Any]] = deque(maxlen=n)
    records_seen = 0
    for record in stream_days(path, as_of=as_of):
        buffer.append(record)
        records_seen += 1
    return AdapterResult(
        input_hash=compute_file_hash(path),
        window=tuple(buffer),
        records_seen=records_seen,
        window_size=len(buffer),
    )
