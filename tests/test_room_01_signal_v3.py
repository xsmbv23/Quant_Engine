import unittest

from room_01_signal_v3 import extract_features, select_candidates, feature_semantics
from room_01_contract import validate_contract


class Room01SignalV3Tests(unittest.TestCase):
    def test_contract_is_executable_and_strict(self):
        validate_contract()

    def test_feature_semantics_are_explicit_and_immutable(self):
        semantics = feature_semantics()
        names = tuple(x.name for x in semantics)
        self.assertEqual(names, (
            "frequency_30d", "recency", "temporal_echo_t1", "temporal_echo_t2",
            "temporal_echo_t7", "digit_head_imbalance", "digit_tail_imbalance",
        ))
        self.assertEqual(semantics[0].meaning, "occurrence_count")
        self.assertEqual(semantics[0].scale, "integer_count")
        self.assertEqual(semantics[0].window, 30)

    def test_t1_t2_remain_observable_before_selection(self):
        data = [[10], [20], [30], [40], [50]]
        features = {x.number: x for x in extract_features(data)}
        self.assertTrue(features[40].temporal_echo_t1)
        self.assertTrue(features[30].temporal_echo_t2)
        self.assertFalse(features[10].temporal_echo_t7)

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

    def test_selection_is_deterministic_and_order_stable(self):
        data = [[11, 12], [13, 14], [11, 15], [16, 17], [18, 19]]
        a = select_candidates(extract_features(data))
        b = select_candidates(extract_features(data))
        self.assertEqual(a, b)
        self.assertEqual([x.number for x in a], sorted([x.number for x in a], key=lambda n: next((-x.raw_score, x.frequency_30d, x.number) for x in a if x.number == n)))

    def test_limit_is_bounded(self):
        with self.assertRaises(ValueError):
            select_candidates(extract_features([[1]]), 0)
        with self.assertRaises(ValueError):
            select_candidates(extract_features([[1]]), 11)

    def test_bounded_window(self):
        with self.assertRaises(ValueError):
            extract_features([[1]] * 31)

    def test_no_hidden_state_between_runs(self):
        data = [[11, 12], [13, 14], [11, 15], [16, 17], [18, 19]]
        first = extract_features(data)
        second = extract_features(data)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)


if __name__ == "__main__":
    unittest.main()
