import unittest

from room_01_signal_v2 import extract_signals


class Room01SignalV2Tests(unittest.TestCase):
    def test_bounded_window(self):
        with self.assertRaises(ValueError):
            extract_signals([[1]] * 31)

    def test_empty_window_denied(self):
        with self.assertRaises(ValueError):
            extract_signals([])

    def test_recent_numbers_are_excluded(self):
        data = [[1, 2], [3, 4], [5, 6], [1, 7], [8, 9]]
        result = extract_signals(data)
        numbers = [x.number for x in result]
        self.assertNotIn(1, numbers)
        self.assertNotIn(7, numbers)
        self.assertNotIn(8, numbers)
        self.assertNotIn(9, numbers)

    def test_temporal_t1_and_t2_are_from_prior_rows_only(self):
        data = [[10], [20], [30], [40]]
        result = extract_signals(data)
        by_number = {x.number: x for x in result}
        self.assertFalse(by_number[10].temporal_echo_t1)
        self.assertFalse(by_number[10].temporal_echo_t2)
        self.assertTrue(by_number[20].temporal_echo_t2)

    def test_t7_requires_eight_rows(self):
        data = [[n] for n in range(8)]
        result = extract_signals(data)
        by_number = {x.number: x for x in result}
        # 0 is excluded by the last-three-day recency rule only when present
        # there; row zero is T-7 and therefore not a future observation.
        self.assertTrue(by_number[0].temporal_echo_t7)

    def test_output_is_deterministically_ordered(self):
        data = [[11, 12], [13, 14], [11, 15], [16, 17], [18, 19]]
        a = extract_signals(data)
        b = extract_signals(data)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
