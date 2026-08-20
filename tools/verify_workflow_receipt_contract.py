"""Validate the semantic boundary of a GitHub workflow evidence receipt.

This validator never promotes Brain state. It only proves that a repository
workflow receipt is correctly classified as repository-execution evidence.
"""
from __future__ import annotations

REQUIRED = {
    "event_type": "REAL_GITHUB_WORKFLOW_EXECUTION",
    "execution_status": "PASS",
    "evidence_kind": "REPOSITORY_VERIFIER_EXECUTION",
    "external_runtime_truth": "NOT_PROVEN",
    "promotion": "DENY",
    "pass_inheritance": False,
    "unknown_is_not_pass": True,
}


def validate_receipt(receipt: dict) -> None:
    for key, expected in REQUIRED.items():
        if receipt.get(key) != expected:
            raise ValueError(f"receipt semantic violation: {key}={receipt.get(key)!r}")
    for key in ("repository", "workflow", "run_id", "commit_sha", "tree_hash", "source_set_sha256", "timestamp"):
        if not receipt.get(key):
            raise ValueError(f"receipt missing required field: {key}")
    if receipt.get("layer") != "LAYER_1_ROOM_01":
        raise ValueError("receipt layer must remain scoped to LAYER_1_ROOM_01")
