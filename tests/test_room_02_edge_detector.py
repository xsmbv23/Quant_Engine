import unittest
from datetime import date, timedelta

from room_02_edge_detector import detect_frequency_drift
from time_index_contract import DayRecord


class Room02EdgeDetectorTests(unittest.TestCase):
    def _records(self, n=80):
        rows = []
        start = date(2026, 1, 1)
        for i in range(n):
            # Number 42 appears on a deterministic weekly cadence. Other values
            # keep the canonical 27-value daily domain valid.
            values = tuple(((j + i) % 100) for j in range(27))
            if i % 7 == 0:
                values = (42,) + values[1:]
            rows.append(DayRecord(start + timedelta(days=i), values))
        return rows

    def test_deterministic_result(self):
        records = self._records()
        a = detect_frequency_drift(records, 42, permutations=199, seed=7)
        b = detect_frequency_drift(records, 42, permutations=199, seed=7)
        self.assertEqual(a, b)

    def test_small_sample_is_denied(self):
        with self.assertRaises(ValueError):
            detect_frequency_drift(self._records(20), 42)

    def test_payoff_must_be_positive(self):
        with self.assertRaises(ValueError):
            detect_frequency_drift(self._records(), 42, payoff_b=0)

    def test_permutation_is_oos_only(self):
        result = detect_frequency_drift(self._records(), 42, permutations=199, seed=11)
        self.assertEqual(result.test_observations, result.test_days)
        self.assertGreaterEqual(result.permutation_p_value, 0.0)
        self.assertLessEqual(result.permutation_p_value, 1.0)


if __name__ == "__main__":
    unittest.main()
