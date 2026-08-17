import unittest
from datetime import date

from data_buffer.forensic_readiness import (
    chain_hash,
    compact_manifest,
    detect_drift,
    early_freeze_candidate,
    readiness_index,
    strict_admission_ready,
)


class ForensicReadinessTests(unittest.TestCase):
    def test_partial_window_never_admits(self):
        r = readiness_index(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 10)],
            quorum_ok_days=9,
            conflict_days=0,
        )
        self.assertEqual(r.coverage_ratio, 0.9)
        self.assertFalse(strict_admission_ready(r))

    def test_ten_consecutive_real_days_can_admit(self):
        r = readiness_index(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 11)],
            quorum_ok_days=10,
            conflict_days=0,
        )
        self.assertEqual(r.contiguous_days, 10)
        self.assertTrue(strict_admission_ready(r))

    def test_early_candidate_is_not_strict_admission(self):
        r = readiness_index(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 8)],
            quorum_ok_days=7,
            conflict_days=0,
        )
        self.assertTrue(early_freeze_candidate(r))
        self.assertFalse(strict_admission_ready(r))

    def test_conflict_destroys_readiness(self):
        r = readiness_index(
            window_days=10,
            observed_dates=[date(2026, 8, d) for d in range(1, 11)],
            quorum_ok_days=10,
            conflict_days=1,
        )
        self.assertLess(r.readiness_score, 1.0)
        self.assertFalse(strict_admission_ready(r))

    def test_drift_is_fail_closed(self):
        self.assertTrue(detect_drift("old", "new"))
        self.assertFalse(detect_drift("same", "same"))
        self.assertFalse(detect_drift(None, "new"))

    def test_hash_chain_is_deterministic(self):
        first = chain_hash("0" * 64, "a" * 64)
        second = chain_hash("0" * 64, "a" * 64)
        self.assertEqual(first, second)
        self.assertNotEqual(first, chain_hash(first, "b" * 64))

    def test_manifest_stays_deny_for_partial(self):
        manifest = compact_manifest(
            window_days=21,
            observed_dates=[date(2026, 8, d) for d in range(1, 8)],
            quorum_ok_days=7,
            conflict_days=0,
        )
        self.assertEqual(manifest["promotion"], "DENY")
        self.assertEqual(manifest["schema_version"], "BUFFER_CAPTURE_V2")


if __name__ == "__main__":
    unittest.main()
