import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from room_01_signal_v4 import extract_features, select_candidates
from replay import replay
from room_receipt import sha256_json
from time_index_contract import DayRecord, canonicalize, validate_domain


def day(d, start=0):
    return DayRecord(d, tuple((start + i) % 100 for i in range(27)))


class TimeIndexContractTests(unittest.TestCase):
    def test_domain_requires_exact_27(self):
        with self.assertRaises(ValueError):
            validate_domain(range(26))
        with self.assertRaises(ValueError):
            validate_domain(list(range(26)) + [100])

    def test_strict_missing_day_denies(self):
        a = day(date(2026, 8, 10))
        b = day(date(2026, 8, 12))
        with self.assertRaisesRegex(ValueError, "MISSING_DAY_STRICT_DENY"):
            canonicalize([a, b], missing_day_policy="STRICT")

    def test_gap_aware_never_fills(self):
        a = day(date(2026, 8, 10))
        b = day(date(2026, 8, 12))
        result = canonicalize([a, b], missing_day_policy="GAP_AWARE")
        self.assertEqual([x.date for x in result], [date(2026, 8, 10), date(2026, 8, 12)])
        self.assertEqual(len(result), 2)

    def test_temporal_lookup_uses_calendar_date(self):
        latest = day(date(2026, 8, 12), 0)
        t2 = day(date(2026, 8, 10), 27)
        # GAP_AWARE means Aug 11 remains absent; t2 must still resolve Aug 10.
        features, policy = extract_features([t2, latest], missing_day_policy="GAP_AWARE")
        self.assertEqual(policy["latest_date"], "2026-08-12")
        self.assertTrue(any(x.temporal_echo_t2 for x in features))
        self.assertTrue(all(not x.temporal_echo_t1 for x in features))
        self.assertTrue(all(x.temporal_gap_t1 for x in features))

    def test_density_contract_is_explicit(self):
        records = [day(date(2026, 8, 10))]
        features, policy = extract_features(records, min_feature_density=0.50)
        self.assertLess(policy["feature_density"], 0.50)
        self.assertEqual(policy["feature_density_status"], "WARNING")
        self.assertTrue(features)


class ReplayTests(unittest.TestCase):
    def test_same_input_replays_identically(self):
        records = [day(date(2026, 8, 10)), day(date(2026, 8, 11)), day(date(2026, 8, 12))]
        features, policy = extract_features(records)
        output = [x.number for x in select_candidates(features, 10)]
        input_value = {
            "records": [{"date": r.date.isoformat(), "values": list(r.values)} for r in records],
            "missing_day_policy": "STRICT",
            "min_feature_density": 0.10,
            "density_action": "WARNING",
            "limit": 10,
        }
        feature_snapshot = [x.__dict__ for x in features]
        receipt = {
            "room_version": "ROOM_01_SIGNAL_V4",
            "input": input_value,
            "input_hash": sha256_json(input_value),
            "expected_feature_snapshot_hash": sha256_json(feature_snapshot),
            "expected_output_hash": sha256_json(output),
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "receipt.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            result = replay(path)
        self.assertEqual(result["replay"], "PASS")
        self.assertTrue(result["input_match"])
        self.assertTrue(result["feature_match"])
        self.assertTrue(result["output_match"])


if __name__ == "__main__":
    unittest.main()
