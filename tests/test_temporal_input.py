import unittest
from datetime import date

from temporal_input import DayRecord, bounded_latest, resolve_lags


def day(day: date, start: int = 0) -> DayRecord:
    return DayRecord(day, tuple((start + i) % 100 for i in range(27)))


class TemporalInputTests(unittest.TestCase):
    def test_cardinality_and_domain(self):
        with self.assertRaises(ValueError):
            DayRecord(date(2026, 8, 10), (1, 2))
        with self.assertRaises(ValueError):
            DayRecord(date(2026, 8, 10), tuple([1] * 26 + [100]))

    def test_lags_are_date_aligned(self):
        anchor = date(2026, 8, 12)
        records = [
            day(date(2026, 8, 5), 5),
            day(date(2026, 8, 10), 10),
            day(date(2026, 8, 11), 11),
        ]
        result = resolve_lags(records, anchor)
        self.assertEqual(result["T-7"].day, date(2026, 8, 5))
        self.assertEqual(result["T-2"].day, date(2026, 8, 10))
        self.assertEqual(result["T-1"].day, date(2026, 8, 11))

    def test_missing_calendar_day_is_deny(self):
        anchor = date(2026, 8, 12)
        records = [day(date(2026, 8, 11)), day(date(2026, 8, 10))]
        with self.assertRaisesRegex(ValueError, "TEMPORAL_GAP_DENY"):
            resolve_lags(records, anchor)

    def test_duplicate_date_is_deny(self):
        anchor = date(2026, 8, 12)
        records = [day(date(2026, 8, 11)), day(date(2026, 8, 11)), day(date(2026, 8, 10)), day(date(2026, 8, 5))]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_CANONICAL_DATE"):
            resolve_lags(records, anchor)

    def test_bounded_latest_is_sorted_by_date(self):
        records = [day(date(2026, 8, 12)), day(date(2026, 8, 10)), day(date(2026, 8, 11))]
        result = bounded_latest(records, 2)
        self.assertEqual([r.day for r in result], [date(2026, 8, 11), date(2026, 8, 12)])


if __name__ == "__main__":
    unittest.main()
