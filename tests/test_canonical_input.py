import unittest

from canonical_input import assert_frozen_input, freeze_input, pin_room_version


class CanonicalInputTests(unittest.TestCase):
    def test_freeze_is_stable(self):
        value = {"b": 2, "a": 1}
        first = freeze_input(value)
        second = freeze_input(value)
        self.assertEqual(first, second)
        self.assertTrue(first["immutable"])

    def test_mutation_is_denied(self):
        value = {"records": [{"date": "2026-08-12", "values": [1]}]}
        frozen = freeze_input(value)
        value["records"][0]["values"][0] = 2
        with self.assertRaisesRegex(ValueError, "CANONICAL_INPUT_MUTATION"):
            assert_frozen_input(value, frozen["sha256"])

    def test_room_version_is_pinned(self):
        receipt = {"execution_signature": {"room_version": "ROOM_01_SIGNAL_V4"}}
        pin_room_version("ROOM_01_SIGNAL_V4", receipt)
        with self.assertRaisesRegex(ValueError, "ROOM_VERSION_MISMATCH"):
            pin_room_version("ROOM_01_SIGNAL_V3", receipt)


if __name__ == "__main__":
    unittest.main()
