"""Real-source acquisition status boundary for the accumulation buffer.

Metadata-only: no canonical promotion, no Room 01 execution, no source merging.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterable, Mapping


class AcquisitionState(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    PARTIAL = "PARTIAL"
    READY = "READY"
    CONFLICT = "CONFLICT"
    DRIFT_DETECTED = "DRIFT_DETECTED"


@dataclass(frozen=True)
class AcquisitionObservation:
    business_date: date
    source_id: str
    raw_sha256: str
    provenance_complete: bool
    values_cardinality: int | None = None


@dataclass(frozen=True)
class AcquisitionStatus:
    observed_dates: tuple[date, ...]
    quorum_ok_days: int
    conflict_days: int
    drift_days: int
    state_by_date: tuple[tuple[str, str], ...]
    source_count: int


def build_acquisition_status(
    observations: Iterable[AcquisitionObservation],
    *,
    frozen_hashes: Mapping[tuple[date, str], str] | None = None,
) -> AcquisitionStatus:
    """Observe independent acquisition state without granting any authority.

    ``frozen_hashes`` represents previously accepted raw-artifact hashes. A
    changed hash for an existing (date, source) pair is immutable evidence of
    drift and is never silently replaced.
    """
    rows = tuple(observations)
    by_day: dict[date, list[AcquisitionObservation]] = {}
    frozen = frozen_hashes or {}
    for row in rows:
        if not row.source_id or not row.raw_sha256:
            raise ValueError("acquisition observation requires source_id and raw_sha256")
        by_day.setdefault(row.business_date, []).append(row)

    states: list[tuple[str, str]] = []
    quorum_ok = conflicts = drift = 0
    sources: set[str] = set()

    for day in sorted(by_day):
        day_rows = by_day[day]
        sources.update(r.source_id for r in day_rows)
        hashes = {r.raw_sha256 for r in day_rows}
        has_drift = any(
            frozen.get((r.business_date, r.source_id)) not in (None, r.raw_sha256)
            for r in day_rows
        )
        complete = all(r.provenance_complete for r in day_rows)
        cardinality_ok = all(r.values_cardinality in (None, 27) for r in day_rows)

        if has_drift:
            state = AcquisitionState.DRIFT_DETECTED
            drift += 1
        elif len(hashes) > 1:
            state = AcquisitionState.CONFLICT
            conflicts += 1
        elif not cardinality_ok or not complete:
            state = AcquisitionState.PARTIAL
        elif len(day_rows) >= 2:
            state = AcquisitionState.READY
            quorum_ok += 1
        else:
            state = AcquisitionState.PARTIAL
        states.append((day.isoformat(), state.value))

    return AcquisitionStatus(
        observed_dates=tuple(sorted(by_day)),
        quorum_ok_days=quorum_ok,
        conflict_days=conflicts,
        drift_days=drift,
        state_by_date=tuple(states),
        source_count=len(sources),
    )
