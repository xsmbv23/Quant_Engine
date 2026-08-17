"""ROOM_01_SIGNAL v2 — deterministic raw-signal extraction.

This is a new immutable room artifact; the original room_01_signal.py remains
untouched as historical evidence. No predictive claim is made.
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


def _validate_window(data: List[Day]) -> List[Day]:
    if not isinstance(data, list) or not data:
        raise ValueError("ROOM_01 requires a non-empty canonical day list")
    if len(data) > 30:
        raise ValueError("ROOM_01 input exceeds bounded 30-day window")
    for day in data:
        if not isinstance(day, list):
            raise TypeError("each canonical day must be a list")
        if any(not isinstance(n, int) or not 0 <= n <= 99 for n in day):
            raise ValueError("ROOM_01 accepts only integer numbers 00..99")
    return data


def _digit_imbalance(numbers: List[int]) -> tuple[int, int]:
    if not numbers:
        return 0, 0
    heads = Counter(n // 10 for n in numbers)
    tails = Counter(n % 10 for n in numbers)
    expected = len(numbers) / 10.0
    return (
        int(round(max(abs(heads.get(i, 0) - expected) for i in range(10)))),
        int(round(max(abs(tails.get(i, 0) - expected) for i in range(10)))),
    )


def extract_signals(data: List[Day], candidate_limit: int = 10) -> List[CandidateSignal]:
    """Extract frequency-gap, recency and T-1/T-2/T-7 temporal features."""
    window = _validate_window(get_last_n_days(data, min(len(data), 30)))
    flat = [n for day in window for n in day]
    frequency = Counter(flat)
    recent = {n for day in window[-3:] for n in day}
    temporal_rows = {
        1: set(window[-2]) if len(window) >= 2 else set(),
        2: set(window[-3]) if len(window) >= 3 else set(),
        7: set(window[-8]) if len(window) >= 8 else set(),
    }
    head_imbalance, tail_imbalance = _digit_imbalance(flat)

    ordered = sorted(frequency.items(), key=lambda item: (item[1], item[0]))
    out: List[CandidateSignal] = []
    for number, freq in ordered:
        if number in recent:
            continue
        t1 = number in temporal_rows[1]
        t2 = number in temporal_rows[2]
        t7 = number in temporal_rows[7]
        temporal_score = int(t1) + int(t2) + int(t7)
        raw_score = temporal_score * 10 + head_imbalance + tail_imbalance
        out.append(CandidateSignal(number, freq, True, t1, t2, t7, temporal_score, head_imbalance, tail_imbalance, raw_score))
        if len(out) >= candidate_limit:
            break
    return sorted(out, key=lambda s: (-s.raw_score, s.frequency_30d, s.number))
