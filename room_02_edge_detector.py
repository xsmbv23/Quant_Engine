"""ROOM_02_EDGE_DETECTOR v1 — research-only probability drift detector.

Purpose: test whether a feature available at day t contains predictive information
about a target observed at t+1. This room NEVER uses the target day to build the
feature. It is not an execution room and cannot promote a trade.

Design:
- walk-forward train/test separation
- explicit feature/target temporal boundary
- top-quantile conditional probability vs unconditional baseline
- empirical EV under an explicitly supplied payoff model
- deterministic permutation test
- minimum sample gates
- compact output only; no bulk dataset retention
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import math
import random
from typing import Iterable

from time_index_contract import DayRecord, canonicalize

ROOM_VERSION = "ROOM_02_EDGE_DETECTOR_V1"


@dataclass(frozen=True)
class EdgeResult:
    room_version: str
    feature_name: str
    train_days: int
    test_days: int
    test_observations: int
    baseline_probability: float
    conditional_probability: float
    probability_delta: float
    expected_value: float | None
    permutation_p_value: float | None
    status: str


def _presence(day: DayRecord, number: int) -> int:
    return int(number in day.values)


def _feature_frequency_prior(records: tuple[DayRecord, ...], number: int) -> list[tuple[int, int]]:
    """Return (feature, next-day target) pairs using only information <= t."""
    pairs: list[tuple[int, int]] = []
    for i in range(len(records) - 1):
        history = records[: i + 1]
        count = sum(_presence(day, number) for day in history)
        feature = count / len(history)
        target = _presence(records[i + 1], number)
        pairs.append((feature, target))
    return pairs


def _quantile_threshold(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("EDGE_EMPTY_FEATURES")
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))
    return ordered[index]


def _permutation_p_value(
    features: list[float],
    targets: list[int],
    threshold: float,
    observed_delta: float,
    *,
    permutations: int,
    seed: int,
) -> float:
    rng = random.Random(seed)
    hits = 0
    shuffled = list(targets)
    selected = [i for i, x in enumerate(features) if x >= threshold]
    if not selected or len(selected) == len(features):
        return 1.0
    for _ in range(permutations):
        rng.shuffle(shuffled)
        p_all = sum(shuffled) / len(shuffled)
        p_sel = sum(shuffled[i] for i in selected) / len(selected)
        if p_sel - p_all >= observed_delta - 1e-15:
            hits += 1
    return (hits + 1) / (permutations + 1)


def detect_frequency_drift(
    records: Iterable[DayRecord],
    number: int,
    *,
    train_ratio: float = 0.70,
    top_quantile: float = 0.80,
    payoff_b: float | None = None,
    permutations: int = 999,
    seed: int = 2308,
    min_train_observations: int = 20,
    min_test_observations: int = 20,
    alpha: float = 0.05,
    min_delta: float = 0.0,
) -> EdgeResult:
    if not isinstance(number, int) or not 0 <= number <= 99:
        raise ValueError("EDGE_NUMBER_DOMAIN")
    if not 0.50 <= train_ratio < 0.95:
        raise ValueError("EDGE_TRAIN_RATIO")
    if not 0.50 < top_quantile < 1.0:
        raise ValueError("EDGE_TOP_QUANTILE")
    if permutations < 99:
        raise ValueError("EDGE_PERMUTATIONS_TOO_LOW")
    if payoff_b is not None and payoff_b <= 0:
        raise ValueError("EDGE_PAYOFF_MUST_BE_POSITIVE")

    canonical = canonicalize(records, max_days=10_000, missing_day_policy="STRICT")
    pairs = _feature_frequency_prior(canonical, number)
    if len(pairs) < min_train_observations + min_test_observations:
        raise ValueError("EDGE_SAMPLE_TOO_SMALL")

    split = int(len(pairs) * train_ratio)
    train = pairs[:split]
    test = pairs[split:]
    if len(train) < min_train_observations or len(test) < min_test_observations:
        raise ValueError("EDGE_SPLIT_TOO_SMALL")

    # Threshold is learned ONLY from training features.
    threshold = _quantile_threshold([x for x, _ in train], top_quantile)
    test_features = [x for x, _ in test]
    test_targets = [y for _, y in test]
    selected = [y for x, y in test if x >= threshold]
    baseline = sum(test_targets) / len(test_targets)
    conditional = sum(selected) / len(selected) if selected else baseline
    delta = conditional - baseline
    ev = None if payoff_b is None else conditional * payoff_b - (1.0 - conditional)
    p_value = _permutation_p_value(
        test_features,
        test_targets,
        threshold,
        delta,
        permutations=permutations,
        seed=seed,
    )

    status = "EDGE_CANDIDATE" if (
        selected
        and delta > min_delta
        and p_value < alpha
    ) else "NO_EDGE_PROVEN"

    return EdgeResult(
        ROOM_VERSION,
        "frequency_prior",
        len(train),
        len(test),
        len(test_targets),
        baseline,
        conditional,
        delta,
        ev,
        p_value,
        status,
    )
