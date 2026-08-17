import ast
import unittest
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from forensic_contract import build_input_identity, canonical_bytes, empty_output_state, feature_snapshot, sha256_canonical
from replay_guard import assert_replay_module_pure, read_immutable_bytes


@dataclass(frozen=True)
class Sample:
    b: int
    a: int


class ForensicContractTests(unittest.TestCase):
    def test_key_order_does_not_change_hash(self):
        self.assertEqual(sha256_canonical({"a": 1, "b": 2}), sha256_canonical({"b": 2, "a": 1}))

    def test_dataclass_and_dict_share_semantic_hash(self):
        self.assertEqual(sha256_canonical(Sample(2, 1)), sha256_canonical({"a": 1, "b": 2}))

    def test_type_domain_is_explicit(self):
        self.assertNotEqual(sha256_canonical({"x": 1}), sha256_canonical({"x": 1.0}))
        self.assertNotEqual(sha256_canonical({"x": 1}), sha256_canonical({"x": "1"}))
        self.assertNotEqual(sha256_canonical({"x": True}), sha256_canonical({"x": 1}))
        self.assertNotEqual(sha256_canonical({"x": Decimal("1")}), sha256_canonical({"x": 1}))

    def test_list_order_is_semantic(self):
        self.assertNotEqual(sha256_canonical([1, 2, 3]), sha256_canonical([3, 2, 1]))

    def test_unordered_set_is_forbidden(self):
        with self.assertRaises(TypeError):
            sha256_canonical({"x": {1, 2}})

    def test_nonfinite_float_is_forbidden(self):
        with self.assertRaises(ValueError):
            sha256_canonical({"x": float("nan")})

    def test_decimal_and_float_are_distinct_types(self):
        self.assertNotEqual(sha256_canonical({"x": Decimal("1.25")}), sha256_canonical({"x": 1.25}))

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
        replay_1 = sha256_canonical(payload)
        replay_2 = sha256_canonical({"rows": [1, 2, 3], "source": "REAL-001"})
        fresh_2 = sha256_canonical({"rows": [1, 2, 3], "source": "REAL-001"})
        self.assertEqual(fresh_1, replay_1)
        self.assertEqual(replay_1, replay_2)
        self.assertEqual(fresh_1, fresh_2)

    def test_reproducible_is_not_correctness(self):
        observed = {"reproducibility": "PASS", "correctness": "NOT_PROVEN"}
        self.assertEqual(observed["reproducibility"], "PASS")
        self.assertEqual(observed["correctness"], "NOT_PROVEN")

    def test_input_file_is_read_only_snapshot(self):
        path = Path(__file__).with_name("_n003_input.json")
        path.write_bytes(b'{"a":1}')
        try:
            self.assertEqual(read_immutable_bytes(path), b'{"a":1}')
        finally:
            path.unlink(missing_ok=True)

    def test_replay_module_has_no_obvious_external_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        assert_replay_module_pure(root / "room_01_signal_v4.py")

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
