"""ROOM_01_SIGNAL v4 — date-aligned, domain-locked, deterministic features.

This is a Layer 1 room. Brain remains the governance authority.
Missing-day policy defaults to STRICT. GAP_AWARE is explicit and never fills data.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from typing import Literal

from time_index_contract import DayRecord, MissingDayPolicy, by_date, canonicalize, prior_calendar_day

ROOM_VERSION = "ROOM_01_SIGNAL_V4"
VALUE_DOMAIN = {"type": "integer", "min": 0, "max": 99, "cardinality": 27}


@dataclass(frozen=True)
class CandidateSignalV4:
    number: int
    frequency_30d: int
    recency_excluded: bool
    temporal_echo_t1: bool
    temporal_echo_t2: bool
    temporal_echo_t7: bool
    temporal_gap_t1: bool
    temporal_gap_t2: bool
    temporal_gap_t7: bool
    temporal_score: int
    digit_head_imbalance: int
    digit_tail_imbalance: int
    raw_score: int


def _imbalance(flat: list[int]) -> tuple[int, int]:
    heads = Counter(n // 10 for n in flat)
    tails = Counter(n % 10 for n in flat)
    expected = len(flat) / 10.0
    return (
        int(round(max(abs(heads.get(i, 0) - expected) for i in range(10)))),
        int(round(max(abs(tails.get(i, 0) - expected) for i in range(10)))),
    )


def _density(features: list[CandidateSignalV4], universe_size: int = 100) -> float:
    return len(features) / universe_size if universe_size else 0.0


def extract_features(
    records: list[DayRecord] | tuple[DayRecord, ...],
    *,
    missing_day_policy: MissingDayPolicy = "STRICT",
    min_feature_density: float = 0.10,
    density_action: Literal["WARNING", "DENY"] = "WARNING",
) -> tuple[list[CandidateSignalV4], dict]:
    window = canonicalize(records, max_days=30, missing_day_policy=missing_day_policy)
    latest = window[-1]
    dates = by_date(window)
    flat = [n for day in window for n in day.values]
    freq = Counter(flat)
    recent_dates = tuple(r.date for r in window if (latest.date - r.date).days <= 2)
    recent = {n for d in recent_dates for n in dates[d].values}
    head, tail = _imbalance(flat)

    result: list[CandidateSignalV4] = []
    for number, count in sorted(freq.items()):
        echoes = {}
        gaps = {}
        for offset, name in ((1, "t1"), (2, "t2"), (7, "t7")):
            prior = prior_calendar_day(dates, latest.date, offset)
            gaps[name] = prior is None
            echoes[name] = bool(prior and number in prior.values)
        temporal = int(echoes["t1"]) + int(echoes["t2"]) + int(echoes["t7"])
        result.append(CandidateSignalV4(
            number, count, number in recent,
            echoes["t1"], echoes["t2"], echoes["t7"],
            gaps["t1"], gaps["t2"], gaps["t7"],
            temporal, head, tail, temporal * 10 + head + tail,
        ))

    density = _density(result)
    if density < min_feature_density and density_action == "DENY":
        raise ValueError(f"FEATURE_DENSITY_DENY: {density:.6f} < {min_feature_density:.6f}")
    return result, {
        "room_version": ROOM_VERSION,
        "latest_date": latest.date.isoformat(),
        "window_start": window[0].date.isoformat(),
        "window_days": len(window),
        "missing_day_policy": missing_day_policy,
        "value_domain": VALUE_DOMAIN,
        "feature_density": density,
        "feature_density_threshold": min_feature_density,
        "feature_density_status": "PASS" if density >= min_feature_density else "WARNING",
    }


def select_candidates(features: list[CandidateSignalV4], limit: int = 10) -> list[CandidateSignalV4]:
    if not isinstance(limit, int) or not 1 <= limit <= 10:
        raise ValueError("candidate limit must be an integer from 1 to 10")
    return sorted((x for x in features if not x.recency_excluded), key=lambda x: (-x.raw_score, x.frequency_30d, x.number))[:limit]
