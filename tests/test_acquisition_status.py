import unittest
from datetime import date

from data_buffer.acquisition_status import (
    AcquisitionObservation,
    AcquisitionState,
    build_acquisition_status,
)


class AcquisitionStatusTests(unittest.TestCase):
    def obs(self, day, source, sha, complete=True, card=27):
        return AcquisitionObservation(date.fromisoformat(day), source, sha, complete, card)

    def test_two_independent_matching_sources_are_ready(self):
        status = build_acquisition_status([
            self.obs("2026-08-15", "A", "aaa"),
            self.obs("2026-08-15", "B", "aaa"),
        ])
        self.assertEqual(status.quorum_ok_days, 1)
        self.assertEqual(status.conflict_days, 0)
        self.assertEqual(status.state_by_date[0][1], AcquisitionState.READY.value)

    def test_conflict_is_not_merged(self):
        status = build_acquisition_status([
            self.obs("2026-08-15", "A", "aaa"),
            self.obs("2026-08-15", "B", "bbb"),
        ])
        self.assertEqual(status.conflict_days, 1)
        self.assertEqual(status.quorum_ok_days, 0)
        self.assertEqual(status.state_by_date[0][1], AcquisitionState.CONFLICT.value)

    def test_missing_provenance_is_partial(self):
        status = build_acquisition_status([
            self.obs("2026-08-15", "A", "aaa", complete=False),
            self.obs("2026-08-15", "B", "aaa"),
        ])
        self.assertEqual(status.state_by_date[0][1], AcquisitionState.PARTIAL.value)

    def test_existing_hash_change_is_drift(self):
        status = build_acquisition_status(
            [self.obs("2026-08-15", "A", "new")],
            frozen_hashes={(date(2026, 8, 15), "A"): "old"},
        )
        self.assertEqual(status.drift_days, 1)
        self.assertEqual(status.state_by_date[0][1], AcquisitionState.DRIFT_DETECTED.value)

    def test_status_is_observational_only(self):
        status = build_acquisition_status([self.obs("2026-08-15", "A", "aaa")])
        self.assertEqual(status.source_count, 1)
        self.assertEqual(status.quorum_ok_days, 0)
        self.assertNotIn("promotion", status.__dict__)


if __name__ == "__main__":
    unittest.main()
