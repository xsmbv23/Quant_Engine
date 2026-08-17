import unittest
from datetime import date

from data_buffer.readiness_status import build_readiness_status


class ReadinessStatusTests(unittest.TestCase):
    def test_partial_accumulation_is_visible_but_denied(self):
        status = build_readiness_status(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 8)],
            quorum_ok_days=7,
            conflict_days=0,
        )
        self.assertEqual(status["state"], "EARLY_FREEZE_CANDIDATE_REHEARSAL_ONLY")
        self.assertFalse(status["strict_admission_ready"])
        self.assertEqual(status["promotion"], "DENY")

    def test_complete_window_is_strictly_ready(self):
        status = build_readiness_status(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 11)],
            quorum_ok_days=10,
            conflict_days=0,
        )
        self.assertEqual(status["state"], "STRICT_ADMISSION_READY")
        self.assertTrue(status["strict_admission_ready"])
        self.assertEqual(status["promotion"], "READY")

    def test_conflict_blocks_promotion_even_with_full_coverage(self):
        status = build_readiness_status(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 11)],
            quorum_ok_days=10,
            conflict_days=1,
        )
        self.assertFalse(status["strict_admission_ready"])
        self.assertEqual(status["promotion"], "DENY")


if __name__ == "__main__":
    unittest.main()
