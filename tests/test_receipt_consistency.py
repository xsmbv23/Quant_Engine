import unittest

from receipt_consistency import ReceiptEvidence, compare_receipts


class ReceiptConsistencyTests(unittest.TestCase):
    def test_no_receipts_denied(self):
        result = compare_receipts([])
        self.assertEqual(result.status, "UNKNOWN")
        self.assertEqual(result.canonical_admission, "DENY")

    def test_one_source_cannot_admit(self):
        result = compare_receipts([
            ReceiptEvidence("2026-08-18", "ketqua16.net", "raw-a", "semantic-a")
        ])
        self.assertEqual(result.status, "INSUFFICIENT_INDEPENDENCE")
        self.assertEqual(result.canonical_admission, "DENY")

    def test_raw_hash_difference_is_not_conflict_by_itself(self):
        result = compare_receipts([
            ReceiptEvidence("2026-08-18", "ketqua16.net", "raw-a"),
            ReceiptEvidence("2026-08-18", "xsmb.com.vn", "raw-b"),
        ])
        self.assertEqual(result.status, "OBSERVED_NO_SEMANTIC_ADMISSION")
        self.assertFalse(result.raw_byte_identity)
        self.assertEqual(result.canonical_admission, "DENY")

    def test_two_independent_semantic_matches_admit(self):
        result = compare_receipts([
            ReceiptEvidence("2026-08-18", "ketqua16.net", "raw-a", "semantic-a"),
            ReceiptEvidence("2026-08-18", "xsmb.com.vn", "raw-b", "semantic-a"),
        ])
        self.assertEqual(result.status, "SEMANTIC_CONSENSUS")
        self.assertTrue(result.semantic_consensus)
        self.assertEqual(result.canonical_admission, "ADMIT")

    def test_semantic_conflict_denies(self):
        result = compare_receipts([
            ReceiptEvidence("2026-08-18", "ketqua16.net", "raw-a", "semantic-a"),
            ReceiptEvidence("2026-08-18", "xsmb.com.vn", "raw-b", "semantic-b"),
        ])
        self.assertEqual(result.status, "CONFLICT")
        self.assertEqual(result.canonical_admission, "DENY")

    def test_same_source_duplicates_do_not_create_independence(self):
        result = compare_receipts([
            ReceiptEvidence("2026-08-18", "ketqua16.net", "raw-a", "semantic-a"),
            ReceiptEvidence("2026-08-18", "ketqua16.net", "raw-b", "semantic-a"),
        ])
        self.assertEqual(result.status, "INSUFFICIENT_INDEPENDENCE")
        self.assertEqual(result.independent_source_count, 1)
        self.assertEqual(result.canonical_admission, "DENY")


if __name__ == "__main__":
    unittest.main()
