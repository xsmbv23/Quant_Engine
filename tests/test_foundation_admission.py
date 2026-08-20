import unittest

from foundation_admission import GateState, admissible_for_quant, assert_prerequisite_only, reachable_gate


class FoundationAdmissionTests(unittest.TestCase):
    def test_first_gate_is_reachable(self):
        self.assertTrue(reachable_gate({}, "DB_EXISTENCE"))

    def test_unknown_or_unreached_stops_next_gate(self):
        self.assertFalse(reachable_gate({"DB_EXISTENCE": GateState.UNKNOWN}, "DB_BINDING"))
        self.assertFalse(reachable_gate({"DB_EXISTENCE": GateState.FAIL}, "DB_BINDING"))
        self.assertFalse(reachable_gate({}, "DB_BINDING"))

    def test_pass_is_prerequisite_only(self):
        states = {"DB_EXISTENCE": GateState.PASS, "DB_BINDING": GateState.UNKNOWN}
        self.assertFalse(admissible_for_quant(states))

    def test_pass_cannot_be_inherited(self):
        states = {"DB_EXISTENCE": GateState.UNKNOWN, "DB_BINDING": GateState.PASS}
        with self.assertRaises(ValueError):
            assert_prerequisite_only(states)

    def test_full_chain_is_only_admissible_with_explicit_passes(self):
        states = {gate: GateState.PASS for gate in (
            "DB_EXISTENCE", "DB_BINDING", "SECRET_RESOLUTION",
            "DB_TLS_ADMISSION", "NETWORK_ORIGIN_PROOF", "DB_ROUND_TRIP", "PROMOTION"
        )}
        self.assertTrue(admissible_for_quant(states))
        assert_prerequisite_only(states)


if __name__ == "__main__":
    unittest.main()
