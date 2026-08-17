"""Small, deterministic primitives for N003 buffer visibility.

These functions only inspect compact metadata. They never promote buffer data,
never fabricate missing dates, and never relax the strict admission gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Readiness:
    window_days: int
    observed_days: int
    contiguous_days: int
    coverage_ratio: float
    quorum_ok_days: int
    conflict_days: int
    readiness_score: float


def longest_contiguous_run(dates: Iterable[date]) -> int:
    ordered = sorted(set(dates))
    if not ordered:
        return 0
    best = current = 1
    for previous, current_day in zip(ordered, ordered[1:]):
        if current_day == previous + timedelta(days=1):
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def readiness_index(
    *,
    window_days: int,
    observed_dates: Sequence[date],
    quorum_ok_days: int,
    conflict_days: int,
) -> Readiness:
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    observed = len(set(observed_dates))
    coverage = min(1.0, observed / window_days)
    quorum_ratio = min(1.0, max(0, quorum_ok_days) / window_days)
    conflict_ratio = min(1.0, max(0, conflict_days) / window_days)
    score = coverage * quorum_ratio * (1.0 - conflict_ratio)
    return Readiness(
        window_days=window_days,
        observed_days=observed,
        contiguous_days=longest_contiguous_run(observed_dates),
        coverage_ratio=coverage,
        quorum_ok_days=max(0, quorum_ok_days),
        conflict_days=max(0, conflict_days),
        readiness_score=score,
    )


def strict_admission_ready(readiness: Readiness, minimum_days: int = 10) -> bool:
    return (
        readiness.coverage_ratio == 1.0
        and readiness.contiguous_days >= minimum_days
        and readiness.conflict_days == 0
        and readiness.quorum_ok_days >= readiness.window_days
    )


def early_freeze_candidate(readiness: Readiness, candidate_days: int = 7) -> bool:
    """Research/replay candidate only; never an N003 admission decision."""
    return (
        readiness.contiguous_days >= candidate_days
        and readiness.conflict_days == 0
        and readiness.quorum_ok_days >= candidate_days
    )


def chain_hash(previous_hash: str, day_hash: str) -> str:
    payload = (previous_hash + day_hash).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def detect_drift(old_hash: str | None, new_hash: str) -> bool:
    """True means an already observed raw artifact changed."""
    return old_hash is not None and old_hash != new_hash


def compact_manifest(*, window_days: int, observed_dates: Sequence[date], quorum_ok_days: int, conflict_days: int) -> dict:
    r = readiness_index(
        window_days=window_days,
        observed_dates=observed_dates,
        quorum_ok_days=quorum_ok_days,
        conflict_days=conflict_days,
    )
    return {
        "schema_version": "BUFFER_CAPTURE_V2",
        "window_days": r.window_days,
        "readiness": {
            "observed_days": r.observed_days,
            "contiguous_days": r.contiguous_days,
            "coverage_ratio": r.coverage_ratio,
            "quorum_ok_days": r.quorum_ok_days,
            "conflict_days": r.conflict_days,
            "readiness_score": r.readiness_score,
        },
        "promotion": "READY" if strict_admission_ready(r) else "DENY",
    }
