import unittest

from src.rooms.room_01_signal import canonical_hash, execute


class Room01ContractTests(unittest.TestCase):
    def test_hash_is_deterministic(self):
        record = {"date": "2026-08-12", "value": 123}
        self.assertEqual(canonical_hash(record), canonical_hash({"value": 123, "date": "2026-08-12"}))

    def test_room_does_not_invent_signal(self):
        receipt = execute({"date": "2026-08-12"}, runtime_ms=1.0, memory_bytes=1024)
        self.assertTrue(receipt.input_hash)
        self.assertTrue(receipt.output_hash)
        self.assertEqual(receipt.memory_bytes, 1024)
        self.assertEqual(receipt.runtime_ms, 1.0)


if __name__ == "__main__":
    unittest.main()
