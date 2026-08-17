import ast
import unittest
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from forensic_contract import build_input_identity, canonical_bytes, empty_output_state, feature_snapshot, sha256_canonical


@dataclass(frozen=True)
class Sample:
    b: int
    a: int


class ForensicContractTests(unittest.TestCase):
    def test_key_order_does_not_change_hash(self):
        self.assertEqual(sha256_canonical({"a": 1, "b": 2}), sha256_canonical({"b": 2, "a": 1}))
        self.assertEqual(canonical_bytes({"a": 1, "b": 2}), b'{"a":1,"b":2}')

    def test_dataclass_and_dict_share_hash_domain(self):
        self.assertEqual(sha256_canonical(Sample(2, 1)), sha256_canonical({"a": 1, "b": 2}))

    def test_decimal_and_float_have_explicit_stable_forms(self):
        self.assertEqual(sha256_canonical({"x": Decimal("1.25")}), sha256_canonical({"x": 1.25}))

    def test_feature_snapshot_excludes_runtime_debug_state(self):
        base = [{"number": 12, "raw_score": 7}]
        noisy = [{"number": 12, "raw_score": 7, "debug": "x", "logs": ["noise"], "runtime": "render"}]
        self.assertEqual(sha256_canonical(feature_snapshot(base)), sha256_canonical(feature_snapshot(noisy)))

    def test_source_identity_is_not_hash(self):
        a = build_input_identity("SOURCE-A", {"a": 1})
        b = build_input_identity("SOURCE-B", {"a": 1})
        self.assertEqual(a["input_hash"], b["input_hash"])
        self.assertNotEqual(a["input_source_id"], b["input_source_id"])

    def test_empty_is_valid_state_not_error(self):
        self.assertEqual(empty_output_state([]), "VALID_EMPTY")

    def test_replay_replay_fresh_cross_consistency(self):
        payload = {"source": "REAL-001", "rows": [1, 2, 3]}
        fresh_1 = sha256_canonical(payload)
        receipt = {"payload": payload, "input_hash": fresh_1}
        replay_1 = sha256_canonical(receipt["payload"])
        replay_2 = sha256_canonical(receipt["payload"])
        fresh_2 = sha256_canonical({"rows": [1, 2, 3], "source": "REAL-001"})
        self.assertEqual(fresh_1, replay_1)
        self.assertEqual(replay_1, replay_2)
        self.assertEqual(fresh_1, fresh_2)

    def test_no_wall_clock_in_layer1_modules(self):
        root = Path(__file__).resolve().parents[1]
        targets = [root / "room_01_signal_v4.py", root / "time_index_contract.py", root / "forensic_contract.py"]
        forbidden = {"now", "utcnow", "time", "monotonic", "perf_counter"}
        for path in targets:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in forbidden:
                    self.fail(f"wall-clock dependency found: {path}:{node.attr}")


if __name__ == "__main__":
    unittest.main()
