"""Forensic data collection/admission primitives.

Collection may be partial. Admission is strict. No function here fabricates
missing observations or merges conflicting sources into truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class CoverageReport:
    start: str | None
    end: str | None
    expected_days: int
    actual_days: int
    coverage_ratio: float
    missing: tuple[str, ...]


def check_contiguity(dates: list[date] | tuple[date, ...], expected_days: int | None = None) -> CoverageReport:
    unique = sorted(set(dates))
    if not unique:
        return CoverageReport(None, None, expected_days or 0, 0, 0.0, tuple())
    start, end = unique[0], unique[-1]
    expected = expected_days if expected_days is not None else (end - start).days + 1
    expected = max(expected, 0)
    expected_dates = {start + timedelta(days=i) for i in range((end - start).days + 1)}
    # Coverage evidence is serialized canonically as ISO calendar dates.
    missing = tuple(sorted(d.isoformat() for d in (expected_dates - set(unique))))
    ratio = len(unique) / expected if expected else 0.0
    return CoverageReport(start.isoformat(), end.isoformat(), expected, len(unique), ratio, missing)


def strict_admission(report: CoverageReport, minimum_days: int = 10) -> dict[str, object]:
    contiguous = not report.missing
    enough = report.actual_days >= minimum_days
    coverage_pass = report.coverage_ratio >= 1.0 and contiguous
    admitted = enough and coverage_pass
    return {
        "status": "ADMITTED" if admitted else "DENY",
        "minimum_days": minimum_days,
        "actual_days": report.actual_days,
        "coverage_ratio": report.coverage_ratio,
        "contiguous": contiguous,
        "missing": list(report.missing),
        "reason": "PASS" if admitted else "INSUFFICIENT_REAL_HISTORY",
    }


def source_quorum(observations: dict[str, str], minimum_sources: int = 2) -> dict[str, object]:
    """Compare independently captured canonical payload hashes.

    Equal hashes are quorum evidence. Any disagreement is a hard conflict.
    """
    hashes = list(observations.values())
    if len(hashes) < minimum_sources:
        return {"status": "DENY", "reason": "QUORUM_NOT_REACHED", "sources": len(hashes)}
    if len(set(hashes)) != 1:
        return {"status": "DENY", "reason": "SOURCE_CONFLICT", "sources": len(hashes)}
    return {"status": "PASS", "reason": "QUORUM_MATCH", "sources": len(hashes)}
