import unittest

from tools.verify_workflow_receipt_contract import validate_receipt


BASE = {
    "event_type": "REAL_GITHUB_WORKFLOW_EXECUTION",
    "execution_status": "PASS",
    "repository": "xsmbv23/Quant_Engine",
    "workflow": "Quant Engine Layer 1 Verification",
    "run_id": "1",
    "commit_sha": "abc",
    "tree_hash": "tree",
    "source_set_sha256": "source",
    "timestamp": "2026-08-21T00:00:00Z",
    "evidence_kind": "REPOSITORY_VERIFIER_EXECUTION",
    "external_runtime_truth": "NOT_PROVEN",
    "layer": "LAYER_1_ROOM_01",
    "promotion": "DENY",
    "pass_inheritance": False,
    "unknown_is_not_pass": True,
}


class WorkflowReceiptContractTests(unittest.TestCase):
    def test_valid_repository_receipt(self):
        validate_receipt(BASE)

    def test_runtime_truth_cannot_be_promoted_by_ci(self):
        receipt = dict(BASE)
        receipt["external_runtime_truth"] = "PASS"
        with self.assertRaises(ValueError):
            validate_receipt(receipt)

    def test_promotion_cannot_be_inherited(self):
        receipt = dict(BASE)
        receipt["promotion"] = "PASS"
        with self.assertRaises(ValueError):
            validate_receipt(receipt)

    def test_layer_scope_is_fixed(self):
        receipt = dict(BASE)
        receipt["layer"] = "BRAIN"
        with self.assertRaises(ValueError):
            validate_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
