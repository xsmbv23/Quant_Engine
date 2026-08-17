import hashlib
import importlib.util
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("ketqua16_raw", Path(__file__).parents[1] / "collectors" / "ketqua16_raw.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class _Handler(BaseHTTPRequestHandler):
    payload = b"REAL_SOURCE_RESPONSE_BYTES_FOR_TEST"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.payload)

    def log_message(self, *_args):
        return


class Ketqua16CollectorTests(unittest.TestCase):
    def test_bounded_reader_hashes_exact_bytes(self):
        server = HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            response = __import__("urllib.request").request.urlopen(
                f"http://127.0.0.1:{server.server_port}/", timeout=2
            )
            raw, truncated = MODULE._read_bounded(response)
            self.assertFalse(truncated)
            self.assertEqual(raw, _Handler.payload)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), hashlib.sha256(_Handler.payload).hexdigest())
        finally:
            server.shutdown()
            thread.join(timeout=2)

    def test_business_date_is_explicit(self):
        with self.assertRaises(ValueError):
            MODULE.capture_raw("")

    def test_constants_keep_first_probe_bounded(self):
        self.assertEqual(MODULE.SOURCE_ID, "ketqua16.net")
        self.assertLessEqual(MODULE.MAX_RAW_BYTES, 2 * 1024 * 1024)
        self.assertLessEqual(MODULE.TIMEOUT_SECONDS, 8)


if __name__ == "__main__":
    unittest.main()
