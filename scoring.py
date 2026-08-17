from typing import List


def score_candidates(candidates: List[int]) -> List[int]:
    """N001 baseline: preserve Room 01 ordering without adding hidden factors."""
    return list(candidates)
