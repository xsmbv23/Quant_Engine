"""ROOM_01_SIGNAL v3 — feature extraction separated from candidate selection.

Important correction: T-1/T-2 temporal features are observable only when recent
rows are retained as features. Therefore recency is a feature/selection policy,
not an early destructive filter.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import List

from input_adapter import Day, get_last_n_days


@dataclass(frozen=True)
class CandidateSignal:
    number: int
    frequency_30d: int
    recency_excluded: bool
    temporal_echo_t1: bool
    temporal_echo_t2: bool
    temporal_echo_t7: bool
    temporal_score: int
    digit_head_imbalance: int
    digit_tail_imbalance: int
    raw_score: int


def _validate(data: List[Day]) -> List[Day]:
    if not isinstance(data, list) or not data:
        raise ValueError("ROOM_01 requires non-empty canonical data")
    if len(data) > 30:
        raise ValueError("ROOM_01 input exceeds bounded 30-day window")
    for day in data:
        if not isinstance(day, list):
            raise TypeError("each day must be a list")
        if any(not isinstance(n, int) or not 0 <= n <= 99 for n in day):
            raise ValueError("numbers must be integers in 00..99")
    return get_last_n_days(data, min(len(data), 30))


def _imbalance(flat: List[int]) -> tuple[int, int]:
    if not flat:
        return 0, 0
    heads = Counter(n // 10 for n in flat)
    tails = Counter(n % 10 for n in flat)
    expected = len(flat) / 10.0
    return (
        int(round(max(abs(heads.get(i, 0) - expected) for i in range(10)))),
        int(round(max(abs(tails.get(i, 0) - expected) for i in range(10)))),
    )


def extract_features(data: List[Day]) -> List[CandidateSignal]:
    """Extract all measurable features without discarding recent observations."""
    window = _validate(data)
    flat = [n for day in window for n in day]
    freq = Counter(flat)
    recent = {n for day in window[-3:] for n in day}
    rows = {
        1: set(window[-2]) if len(window) >= 2 else set(),
        2: set(window[-3]) if len(window) >= 3 else set(),
        7: set(window[-8]) if len(window) >= 8 else set(),
    }
    head, tail = _imbalance(flat)
    result: List[CandidateSignal] = []
    for number, count in sorted(freq.items(), key=lambda item: item[0]):
        t1 = number in rows[1]
        t2 = number in rows[2]
        t7 = number in rows[7]
        temporal = int(t1) + int(t2) + int(t7)
        result.append(CandidateSignal(number, count, number in recent, t1, t2, t7, temporal, head, tail, temporal * 10 + head + tail))
    return result


def select_candidates(features: List[CandidateSignal], limit: int = 10) -> List[CandidateSignal]:
    """Apply the recency exclusion after temporal features have been measured."""
    eligible = [x for x in features if not x.recency_excluded]
    return sorted(eligible, key=lambda x: (-x.raw_score, x.frequency_30d, x.number))[:limit]


def generate_candidates(data: List[Day]) -> List[int]:
    return [x.number for x in select_candidates(extract_features(data))]
