"""Fail-closed runtime lineage guard for Quant_Engine workers."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

REQUIRED = ("allocation_id", "cycle_id", "task_id", "task_type", "worker_id", "input_artifact", "input_sha256", "model_version")


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_allocation(allocation: dict[str, Any], worker_id: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for key in REQUIRED:
        if not allocation.get(key):
            errors.append(f"missing_{key}")
    if allocation.get("worker_id") and allocation["worker_id"] != worker_id:
        errors.append("worker_identity_mismatch")
    if allocation.get("input_artifact"):
        p = Path(allocation["input_artifact"])
        if not p.is_file():
            errors.append("input_artifact_missing")
        elif allocation.get("input_sha256"):
            actual = sha256_file(p)
            if actual != allocation["input_sha256"]:
                errors.append("input_sha256_mismatch")
    return not errors, errors
