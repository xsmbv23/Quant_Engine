from collections import Counter
from typing import List

from input_adapter import Day


def generate_candidates(data: List[Day]) -> List[int]:
    """Generate a small measurable candidate set from the supplied EOD window."""
    flat = [num for day in data for num in day]
    freq = Counter(flat)
    rare = sorted(freq.items(), key=lambda item: (item[1], item[0]))[:20]
    recent = {num for day in data[-3:] for num in day}

    candidates: List[int] = []
    for num, _count in rare:
        if num not in recent:
            candidates.append(num)
        if len(candidates) == 10:
            break
    return candidates
