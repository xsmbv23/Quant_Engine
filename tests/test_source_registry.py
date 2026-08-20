import unittest

from quant.source_registry import admit_source, registered_sources


class SourceRegistryTests(unittest.TestCase):
    def test_primary_sources_are_registered(self):
        ids = {source.source_id for source in registered_sources()}
        self.assertIn("ketqua16", ids)
        self.assertIn("xsmb", ids)

    def test_unregistered_source_denied(self):
        with self.assertRaisesRegex(PermissionError, "SOURCE_UNREGISTERED_DENY"):
            admit_source("unknown_source", adapter_available=True)

    def test_registered_without_adapter_denied(self):
        with self.assertRaisesRegex(PermissionError, "SOURCE_REGISTERED_WITHOUT_ADAPTER_DENY"):
            admit_source("ketqua16", adapter_available=False)

    def test_registered_adapter_is_candidate_only(self):
        result = admit_source("ketqua16", adapter_available=True)
        self.assertEqual(result.role, "PRIMARY_TARGET")
        self.assertEqual(result.status, "CANDIDATE")


if __name__ == "__main__":
    unittest.main()
