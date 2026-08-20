"""Date-aligned bounded adapter for canonical Layer 1 research input.

This module deliberately does not infer missing dates and does not fabricate
records. Temporal identity comes from explicit calendar dates.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class DayRecord:
    day: date
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.values) != 27:
            raise ValueError("CANONICAL_CARDINALITY_MUST_BE_27")
        if any(type(v) is not int or not 0 <= v <= 99 for v in self.values):
            raise ValueError("CANONICAL_VALUE_DOMAIN_MUST_BE_INT_0_99")


def index_by_date(records: Iterable[DayRecord]) -> dict[date, DayRecord]:
    indexed: dict[date, DayRecord] = {}
    for record in records:
        if record.day in indexed:
            raise ValueError(f"DUPLICATE_CANONICAL_DATE:{record.day.isoformat()}")
        indexed[record.day] = record
    return indexed


def resolve_lags(records: Iterable[DayRecord], anchor: date) -> dict[str, DayRecord]:
    """Resolve T-1/T-2/T-7 by calendar date only.

    Missing dates are explicit failures; no positional fallback or synthetic
    record is allowed.
    """
    indexed = index_by_date(records)
    targets = {
        "T-1": anchor - timedelta(days=1),
        "T-2": anchor - timedelta(days=2),
        "T-7": anchor - timedelta(days=7),
    }
    missing = [name for name, day in targets.items() if day not in indexed]
    if missing:
        raise ValueError("TEMPORAL_GAP_DENY:" + ",".join(missing))
    return {name: indexed[day] for name, day in targets.items()}


def bounded_latest(records: Iterable[DayRecord], limit: int) -> list[DayRecord]:
    """Return a bounded latest window after explicit date ordering."""
    if limit < 1:
        raise ValueError("BOUND_LIMIT_MUST_BE_POSITIVE")
    ordered = sorted(records, key=lambda r: r.day)
    return ordered[-limit:]
