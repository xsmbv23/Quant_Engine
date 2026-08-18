"""N003 anti-illusion gate tests.

These tests validate the proof protocol itself. They deliberately do not claim
that the actual Room 01 replay has passed N003-PROOF. Actual evidence must be
produced by running the real replay path against sufficient real-source
scenarios.
"""
from __future__ import annotations

import unittest
from datetime import date

from room_01_signal_v4 import extract_features, select_candidates
from time_index_contract import DayRecord


class N003AntiIllusionProtocolTests(unittest.TestCase):
    def _two_day_fixture(self):
        # Room 01 has an explicit 27-value domain. The overlap creates observable
        # temporal/frequency differences while remaining a bounded test fixture.
        return (
            DayRecord(date(2026, 8, 11), tuple(range(27))),
            DayRecord(date(2026, 8, 12), tuple(range(1, 28))),
        )

    def _mutated_fixture(self):
        return (
            self._two_day_fixture()[0],
            DayRecord(date(2026, 8, 12), tuple(range(1, 27)) + (99,)),
        )

    def test_semantic_input_mutation_is_observable(self):
        base_features, _ = extract_features(self._two_day_fixture())
        mutated_features, _ = extract_features(self._mutated_fixture())
        self.assertNotEqual(
            [x.__dict__ for x in base_features],
            [x.__dict__ for x in mutated_features],
        )

    def test_feature_information_is_not_assumed_from_replay(self):
        features, _ = extract_features(self._two_day_fixture())
        states = {tuple(x.__dict__.values()) for x in features}
        self.assertGreater(len(states), 1)

    def test_output_is_not_the_only_causal_evidence(self):
        features_a, _ = extract_features(self._two_day_fixture())
        features_b, _ = extract_features(self._mutated_fixture())
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
