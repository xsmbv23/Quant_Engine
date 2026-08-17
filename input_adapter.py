from typing import List


Day = List[int]


def get_last_n_days(data: List[Day], n: int = 30) -> List[Day]:
    """Return the latest bounded execution window from canonical input."""
    return data[-n:]
