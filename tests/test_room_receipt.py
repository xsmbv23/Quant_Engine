import tempfile
import unittest
from pathlib import Path

from room_receipt import build_receipt


class RoomReceiptTests(unittest.TestCase):
    def test_execution_signature_is_deterministic_for_same_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "room.py"
            path.write_text("ROOM_VERSION = '1'\n", encoding="utf-8")
            a = build_receipt(
                input_value={"days": [[1], [2]]},
                feature_value={"frequency": 1},
                policy_value={"recency_exclusion": True},
                output_value={"candidates": [1]},
                room_version="2.0.0",
                code_path=path,
            )
            b = build_receipt(
                input_value={"days": [[1], [2]]},
                feature_value={"frequency": 1},
                policy_value={"recency_exclusion": True},
                output_value={"candidates": [1]},
                room_version="2.0.0",
                code_path=path,
            )
            self.assertEqual(a, b)
            self.assertEqual(set(a), {"input_hash", "feature_snapshot_hash", "policy_hash", "output_hash", "execution_signature", "python_implementation"})
            self.assertNotIn("password", str(a).lower())
            self.assertNotIn("database_url", str(a).lower())


if __name__ == "__main__":
    unittest.main()
