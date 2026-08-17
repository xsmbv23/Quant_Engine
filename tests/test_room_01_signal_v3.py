import unittest

from room_01_signal_v3 import extract_features, select_candidates


class Room01SignalV3Tests(unittest.TestCase):
    def test_t1_t2_remain_observable_before_selection(self):
        data = [[10], [20], [30], [40], [50]]
        features = {x.number: x for x in extract_features(data)}
        self.assertTrue(features[40].temporal_echo_t1)
        self.assertTrue(features[30].temporal_echo_t2)
        self.assertTrue(features[10].temporal_echo_t7 is False)

    def test_recent_is_feature_not_early_data_loss(self):
        data = [[1], [2], [3], [4], [5]]
        features = {x.number: x for x in extract_features(data)}
        self.assertIn(4, features)
        self.assertTrue(features[4].recency_excluded)
        selected = select_candidates(list(features.values()))
        self.assertNotIn(4, [x.number for x in selected])

    def test_t7_is_available_with_eight_days(self):
        data = [[n] for n in range(8)]
        features = {x.number: x for x in extract_features(data)}
        self.assertTrue(features[0].temporal_echo_t7)

    def test_selection_is_deterministic(self):
        data = [[11, 12], [13, 14], [11, 15], [16, 17], [18, 19]]
        a = select_candidates(extract_features(data))
        b = select_candidates(extract_features(data))
        self.assertEqual(a, b)

    def test_bounded_window(self):
        with self.assertRaises(ValueError):
            extract_features([[1]] * 31)


if __name__ == "__main__":
    unittest.main()
