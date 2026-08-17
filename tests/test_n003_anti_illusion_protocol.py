"""N003 anti-illusion gate tests.

These tests validate the proof protocol itself. They deliberately do not claim
that the actual Room 01 replay has passed N003-PROOF. Actual evidence must be
produced by running the real replay path against sufficient real-source
scenarios.
"""
from __future__ import annotations

import unittest

from room_01_signal_v4 import extract_features, select_candidates
from time_index_contract import DayRecord
from datetime import date


class N003AntiIllusionProtocolTests(unittest.TestCase):
    def _two_day_fixture(self):
        return (
            DayRecord(date(2026, 8, 11), (82326, 31773, 64497, 88592)),
            DayRecord(date(2026, 8, 12), (50195, 46812, 80982, 66597)),
        )

    def test_semantic_input_mutation_is_observable(self):
        base = self._two_day_fixture()
        mutated = (
            base[0],
            DayRecord(date(2026, 8, 12), (50195, 46812, 80982, 66598)),
        )
        base_features, _ = extract_features(base)
        mutated_features, _ = extract_features(mutated)
        base_semantic = [x.__dict__ for x in base_features]
        mutated_semantic = [x.__dict__ for x in mutated_features]
        self.assertNotEqual(base_semantic, mutated_semantic)

    def test_feature_information_is_not_assumed_from_replay(self):
        features, _ = extract_features(self._two_day_fixture())
        states = {tuple(x.__dict__.values()) for x in features}
        self.assertGreater(len(states), 1)

    def test_output_is_not_the_only_causal_evidence(self):
        features_a, _ = extract_features(self._two_day_fixture())
        features_b, _ = extract_features(
            (
                DayRecord(date(2026, 8, 11), (82326, 31773, 64497, 88592)),
                DayRecord(date(2026, 8, 12), (50195, 46812, 80982, 66598)),
            )
        )
        output_a = [x.number for x in select_candidates(features_a, 10)]
        output_b = [x.number for x in select_candidates(features_b, 10)]
        # If outputs happen to coincide, the semantic feature evidence still
        # must differ. This prevents final-output-only proof.
        if output_a == output_b:
            self.assertNotEqual(
                [x.__dict__ for x in features_a],
                [x.__dict__ for x in features_b],
            )
        else:
            self.assertNotEqual(output_a, output_b)


if __name__ == "__main__":
    unittest.main()
