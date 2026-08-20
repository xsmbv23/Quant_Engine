import unittest
from datetime import date, timedelta

from time_index_contract import DayRecord
from tools.research_dataset_admission import admit_research_dataset


class ResearchDatasetAdmissionTests(unittest.TestCase):
    def _records(self, days: int) -> list[DayRecord]:
        start = date(2026, 1, 1)
        return [DayRecord(start + timedelta(days=i), tuple(range(27))) for i in range(days)]

    def test_requires_one_extra_day_for_next_day_target(self):
        result = admit_research_dataset(
            self._records(40), min_train_observations=20, min_test_observations=20
        )
        self.assertEqual(result.status, "DENY")
        self.assertEqual(result.reason, "RESEARCH_SAMPLE_TOO_SMALL")
        self.assertEqual(result.required_days, 41)

    def test_admits_exact_minimum_contiguous_dataset(self):
        result = admit_research_dataset(
            self._records(41), min_train_observations=20, min_test_observations=20
        )
        self.assertEqual(result.status, "ADMITTED")
        self.assertEqual(result.reason, "PASS")
        self.assertTrue(result.contiguous)

    def test_gap_is_hard_deny(self):
        records = self._records(41)
        records.pop(10)
        result = admit_research_dataset(
            records, min_train_observations=20, min_test_observations=20
        )
        self.assertEqual(result.status, "DENY")
        self.assertEqual(result.reason, "TEMPORAL_GAP_DENY")
        self.assertFalse(result.contiguous)
        self.assertEqual(len(result.missing), 1)

    def test_duplicate_date_is_denied_by_temporal_contract(self):
        records = self._records(41)
        records.append(records[-1])
        with self.assertRaises(ValueError):
            admit_research_dataset(records)


if __name__ == "__main__":
    unittest.main()
