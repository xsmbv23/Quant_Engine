import unittest

from forensic_contract import execution_trace_hash, sha256_raw_bytes


class N003ForensicInvariantTests(unittest.TestCase):
    def test_raw_byte_hash_distinguishes_line_endings(self):
        self.assertNotEqual(sha256_raw_bytes(b"A\nB"), sha256_raw_bytes(b"A\r\nB"))

    def test_trace_hash_is_order_sensitive(self):
        a = [{"step": "A"}, {"step": "B"}]
        b = [{"step": "B"}, {"step": "A"}]
        self.assertNotEqual(execution_trace_hash(a), execution_trace_hash(b))

    def test_trace_rejects_runtime_debug_fields(self):
        with self.assertRaises(ValueError):
            execution_trace_hash([{"step": "A", "logs": "debug"}])

    def test_trace_hash_is_stable(self):
        trace = [{"step": "A", "branch": "STRICT"}, {"step": "B", "count": 3}]
        self.assertEqual(execution_trace_hash(trace), execution_trace_hash(trace))


if __name__ == "__main__":
    unittest.main()
