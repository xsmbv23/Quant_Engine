"""Room 01 Input Adapter.

Transport-only boundary for canonical data. It deliberately does not clean,
normalize, enrich, score, or infer signals.
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


def stream_days(path: str | Path, *, as_of: date | None = None) -> Iterator[dict[str, Any]]:
    """Yield canonical NDJSON records in file order.

    The adapter requires an explicit `day` ISO date field. Records must be
    strictly increasing by day. Future records are rejected when `as_of` is
    supplied. No sorting is performed because sorting can conceal source-order
    defects and can introduce causal ambiguity.
    """
    previous: date | None = None
    with open(path, "r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AdapterError(f"INVALID_NDJSON_LINE:{line_number}") from exc
            if not isinstance(record, dict):
                raise AdapterError(f"RECORD_NOT_OBJECT:{line_number}")
            current = _parse_day(record.get("day"))
            if as_of is not None and current > as_of:
                raise AdapterError(f"FUTURE_RECORD:{line_number}")
            if previous is not None and current <= previous:
                raise AdapterError(f"NON_CAUSAL_ORDER:{line_number}")
            previous = current
            yield record


def get_window(path: str | Path, n: int = MAX_WINDOW, *, as_of: date | None = None) -> AdapterResult:
    """Return only the final bounded causal window plus the raw input hash."""
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
