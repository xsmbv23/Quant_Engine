import hashlib
import tempfile
import unittest
from datetime import date
from pathlib import Path

from quant.input_adapter import AdapterError, compute_file_hash, get_window, stream_days


class InputAdapterTests(unittest.TestCase):
    def make_file(self, text: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "days.ndjson"
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def test_raw_hash_is_exact_file_hash(self):
        path = self.make_file('{"day":"2026-08-10","values":[1]}\n')
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(compute_file_hash(path), expected)

    def test_stream_preserves_source_order(self):
        path = self.make_file(
            '{"day":"2026-08-10","values":[1]}\n'
            '{"day":"2026-08-11","values":[2]}\n'
        )
        self.assertEqual([r["day"] for r in stream_days(path)], ["2026-08-10", "2026-08-11"])

    def test_non_causal_order_is_denied(self):
        path = self.make_file(
            '{"day":"2026-08-11","values":[2]}\n'
            '{"day":"2026-08-10","values":[1]}\n'
        )
        with self.assertRaisesRegex(AdapterError, "NON_CAUSAL_ORDER"):
            list(stream_days(path))

    def test_duplicate_day_is_denied(self):
        path = self.make_file(
            '{"day":"2026-08-11","values":[2]}\n'
            '{"day":"2026-08-11","values":[3]}\n'
        )
        with self.assertRaisesRegex(AdapterError, "NON_CAUSAL_ORDER"):
            list(stream_days(path))

    def test_future_day_is_denied(self):
        path = self.make_file('{"day":"2026-08-18","values":[1]}\n')
        with self.assertRaisesRegex(AdapterError, "FUTURE_RECORD"):
            list(stream_days(path, as_of=date(2026, 8, 17)))

    def test_window_is_bounded(self):
        text = "".join(f'{{"day":"2026-08-{day:02d}","values":[{day}]}}\n' for day in range(1, 32))
        path = self.make_file(text)
        result = get_window(path, 30)
        self.assertEqual(result.records_seen, 31)
        self.assertEqual(result.window_size, 30)
        self.assertEqual(result.window[0]["day"], "2026-08-02")
        self.assertEqual(result.window[-1]["day"], "2026-08-31")

    def test_window_above_guard_is_denied(self):
        path = self.make_file('{"day":"2026-08-10","values":[1]}\n')
        with self.assertRaisesRegex(AdapterError, "WINDOW_OUT_OF_BOUNDS"):
            get_window(path, 31)


if __name__ == "__main__":
    unittest.main()
