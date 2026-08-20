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
    semantic_sha256: str | None = None


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

    Raw hashes identify exact artifacts *within a source*. Independent sources
    are expected to have different HTML/response bytes, so quorum is based on
    a canonical semantic fingerprint, never on equality of cross-source raw
    hashes. A day is READY only when at least two distinct sources provide the
    same valid semantic fingerprint.

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
        distinct_sources = {r.source_id for r in day_rows}
        has_drift = any(
            frozen.get((r.business_date, r.source_id)) not in (None, r.raw_sha256)
            for r in day_rows
        )
        complete = all(r.provenance_complete for r in day_rows)
        cardinality_ok = all(r.values_cardinality in (None, 27) for r in day_rows)
        semantic_values = [r.semantic_sha256 for r in day_rows if r.semantic_sha256]
        semantic_set = set(semantic_values)

        if has_drift:
            state = AcquisitionState.DRIFT_DETECTED
            drift += 1
        elif not complete or not cardinality_ok or len(semantic_values) != len(day_rows):
            state = AcquisitionState.PARTIAL
        elif len(distinct_sources) < 2:
            state = AcquisitionState.PARTIAL
        elif len(semantic_set) > 1:
            state = AcquisitionState.CONFLICT
            conflicts += 1
        elif len(semantic_set) == 1:
            state = AcquisitionState.READY
            quorum_ok += 1
        else:
            state = AcquisitionState.UNVERIFIED
        states.append((day.isoformat(), state.value))

    return AcquisitionStatus(
        observed_dates=tuple(sorted(by_day)),
        quorum_ok_days=quorum_ok,
        conflict_days=conflicts,
        drift_days=drift,
        state_by_date=tuple(states),
        source_count=len(sources),
    )
