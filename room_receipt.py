"""Forensic receipt helpers for deterministic Layer 1 rooms.

The execution signature identifies the exact room code/runtime/platform context.
No secret values are accepted and no wall-clock value enters the signature.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

from forensic_contract import sha256_canonical


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: object) -> str:
    return sha256_canonical(value)


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def execution_signature(room_version: str, code_path: str | Path, dependency_hash: str = "DECLARED_NONE") -> dict[str, str]:
    return {
        "room_version": room_version,
        "code_hash": file_sha256(code_path),
        "python_version": platform.python_version(),
        "python_implementation": sys.implementation.name,
        "os": platform.system(),
        "platform": platform.platform(aliased=False, terse=False),
        "arch": platform.machine(),
        "dependency_hash": dependency_hash,
    }


def build_receipt(*, input_value: object, feature_value: object, policy_value: object, output_value: object,
                  room_version: str, code_path: str | Path, dependency_hash: str = "DECLARED_NONE") -> dict:
    signature = execution_signature(room_version, code_path, dependency_hash)
    return {
        "input_hash": sha256_json(input_value),
        "feature_snapshot_hash": sha256_json(feature_value),
        "policy_hash": sha256_json(policy_value),
        "output_hash": sha256_json(output_value),
        "execution_signature": signature,
    }
