"""First-class temporal identity for Layer 1.

Temporal features are calendar-date aligned, never record-index aligned.
No synthetic day may be fabricated.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Literal

MissingDayPolicy = Literal["STRICT", "GAP_AWARE"]


@dataclass(frozen=True)
class DayRecord:
    date: date
    values: tuple[int, ...]


def validate_domain(values: Iterable[int], *, cardinality: int = 27, min_value: int = 0, max_value: int = 99) -> tuple[int, ...]:
    result = tuple(values)
    if len(result) != cardinality:
        raise ValueError(f"VALUE_DOMAIN_CARDINALITY: expected {cardinality}, got {len(result)}")
    if any(type(v) is not int or v < min_value or v > max_value for v in result):
        raise ValueError(f"VALUE_DOMAIN_RANGE: expected integer {min_value}..{max_value}")
    return result


def canonicalize(records: Iterable[DayRecord], *, max_days: int = 30, missing_day_policy: MissingDayPolicy = "STRICT") -> tuple[DayRecord, ...]:
    records = tuple(records)
    if not records:
        raise ValueError("TIME_INDEX_EMPTY")
    if len(records) > max_days:
        raise ValueError(f"TIME_INDEX_WINDOW_EXCEEDED: {len(records)} > {max_days}")
    if missing_day_policy not in {"STRICT", "GAP_AWARE"}:
        raise ValueError("UNKNOWN_MISSING_DAY_POLICY")

    ordered = tuple(sorted(records, key=lambda r: r.date))
    if len({r.date for r in ordered}) != len(ordered):
        raise ValueError("TIME_INDEX_DUPLICATE_DATE")
    checked = tuple(DayRecord(r.date, validate_domain(r.values)) for r in ordered)

    gaps = []
    for previous, current in zip(checked, checked[1:]):
        expected = previous.date + timedelta(days=1)
        if current.date != expected:
            gaps.append((expected, current.date))
    if gaps and missing_day_policy == "STRICT":
        raise ValueError("MISSING_DAY_STRICT_DENY")
    return checked


def by_date(records: Iterable[DayRecord]) -> dict[date, DayRecord]:
    return {r.date: r for r in records}


def prior_calendar_day(records_by_date: dict[date, DayRecord], anchor: date, days_back: int) -> DayRecord | None:
    return records_by_date.get(anchor - timedelta(days=days_back))
