"""Metadata-only readiness status for N003 acquisition.

This module observes the accumulation buffer without promoting it. It is safe
for status/health views because it returns compact metadata only. Canonical
truth remains unreachable until strict admission succeeds.
"""
from __future__ import annotations

from datetime import date
from typing import Sequence

from .forensic_readiness import Readiness, early_freeze_candidate, readiness_index, strict_admission_ready


def build_readiness_status(
    *,
    window_days: int,
    observed_dates: Sequence[date],
    quorum_ok_days: int,
    conflict_days: int,
    minimum_days: int = 10,
    preferred_days: int = 21,
) -> dict[str, object]:
    """Return compact visibility metadata; never promote or mutate data."""
    readiness: Readiness = readiness_index(
        window_days=window_days,
        observed_dates=observed_dates,
        quorum_ok_days=quorum_ok_days,
        conflict_days=conflict_days,
    )
    strict = strict_admission_ready(readiness, minimum_days=minimum_days)
    early = early_freeze_candidate(readiness, candidate_days=min(7, minimum_days))
    if strict:
        state = "STRICT_ADMISSION_READY"
    elif early:
        state = "EARLY_FREEZE_CANDIDATE_REHEARSAL_ONLY"
    else:
        state = "ACCUMULATING"

    return {
        "schema_version": "READINESS_STATUS_V1",
        "window_days": readiness.window_days,
        "observed_days": readiness.observed_days,
        "contiguous_days": readiness.contiguous_days,
        "coverage_ratio": readiness.coverage_ratio,
        "quorum_ok_days": readiness.quorum_ok_days,
        "conflict_days": readiness.conflict_days,
        "readiness_score": readiness.readiness_score,
        "minimum_real_history_days": minimum_days,
        "preferred_real_history_days": preferred_days,
        "early_freeze_candidate": early,
        "strict_admission_ready": strict,
        "state": state,
        "promotion": "READY" if strict else "DENY",
        "truth_boundary": "CANONICAL_DATASET_REQUIRES_STRICT_ADMISSION",
    }
