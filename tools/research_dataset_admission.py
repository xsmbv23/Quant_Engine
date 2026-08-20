"""Research-dataset admission for Layer 1.

This gate converts already-admitted canonical observations into a research
eligible temporal dataset. It does not establish source truth or quorum; those
remain upstream data-authority responsibilities. It only proves that the
records supplied to research have enough contiguous dates for the configured
OOS protocol and preserve date identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

from time_index_contract import DayRecord, canonicalize


@dataclass(frozen=True)
class ResearchDatasetAdmission:
    status: str
    reason: str
    required_days: int
    actual_days: int
    start: str | None
    end: str | None
    contiguous: bool
    missing: tuple[str, ...]
    train_observations: int
    test_observations: int


def admit_research_dataset(
    records: Iterable[DayRecord],
    *,
    min_train_observations: int = 20,
    min_test_observations: int = 20,
) -> ResearchDatasetAdmission:
    """Admit a date-aligned dataset for the current Room 02 OOS protocol.

    The current detector creates one prediction pair for each day that has a
    following target day. Therefore N train + M test observations require at
    least N + M + 1 contiguous calendar days. No gap is filled or shifted.
    """
    if min_train_observations < 1 or min_test_observations < 1:
        raise ValueError("RESEARCH_SAMPLE_MINIMUM_INVALID")

    canonical = canonicalize(records, max_days=10_000, missing_day_policy="GAP_AWARE")
    start = canonical[0].date
    end = canonical[-1].date
    expected = (end - start).days + 1
    present = {record.date for record in canonical}
    missing = tuple(
        (start + timedelta(days=i)).isoformat()
        for i in range(expected)
        if start + timedelta(days=i) not in present
    )
    required_days = min_train_observations + min_test_observations + 1
    contiguous = not missing
    enough = len(canonical) >= required_days

    if not contiguous:
        reason = "TEMPORAL_GAP_DENY"
    elif not enough:
        reason = "RESEARCH_SAMPLE_TOO_SMALL"
    else:
        reason = "PASS"

    return ResearchDatasetAdmission(
        status="ADMITTED" if reason == "PASS" else "DENY",
        reason=reason,
        required_days=required_days,
        actual_days=len(canonical),
        start=start.isoformat(),
        end=end.isoformat(),
        contiguous=contiguous,
        missing=missing,
        train_observations=min_train_observations,
        test_observations=min_test_observations,
    )
