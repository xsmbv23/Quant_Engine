import unittest
from datetime import date

from tools.data_admission import check_contiguity, source_quorum, strict_admission


class DataAdmissionTests(unittest.TestCase):
    def test_collection_can_be_partial(self):
        report = check_contiguity([date(2026, 8, 1), date(2026, 8, 3)], expected_days=3)
        self.assertEqual(report.actual_days, 2)
        self.assertEqual(report.coverage_ratio, 2 / 3)
        self.assertEqual(report.missing, ("2026-08-02",))

    def test_admission_rejects_gap(self):
        report = check_contiguity([date(2026, 8, 1), date(2026, 8, 3)], expected_days=3)
        result = strict_admission(report, minimum_days=2)
        self.assertEqual(result["status"], "DENY")
        self.assertEqual(result["reason"], "INSUFFICIENT_REAL_HISTORY")

    def test_admission_requires_minimum_days(self):
        report = check_contiguity([date(2026, 8, 1), date(2026, 8, 2)], expected_days=2)
        result = strict_admission(report, minimum_days=10)
        self.assertEqual(result["status"], "DENY")

    def test_admission_passes_only_for_complete_window(self):
        dates = [date(2026, 8, d) for d in range(1, 11)]
        report = check_contiguity(dates, expected_days=10)
        result = strict_admission(report, minimum_days=10)
        self.assertEqual(result["status"], "ADMITTED")

    def test_source_quorum_requires_two(self):
        self.assertEqual(source_quorum({"A": "abc"})["reason"], "QUORUM_NOT_REACHED")

    def test_source_conflict_denies(self):
        result = source_quorum({"A": "abc", "B": "def"})
        self.assertEqual(result["status"], "DENY")
        self.assertEqual(result["reason"], "SOURCE_CONFLICT")

    def test_source_match_passes(self):
        result = source_quorum({"A": "abc", "B": "abc"})
        self.assertEqual(result["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
