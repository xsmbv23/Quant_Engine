"""Forensic canonical-input freeze for Layer 1.

Once a canonical input envelope is frozen, replay and room execution must use
its exact SHA-256 identity. This module is deliberately small and has no
network, database, or decision-engine side effects.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def freeze_input(value: Any) -> dict[str, Any]:
    payload = canonical_json(value)
    return {
        "schema": "CANONICAL_INPUT_FREEZE_V1",
        "immutable": True,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
    }


def assert_frozen_input(value: Any, expected_sha256: str) -> None:
    actual = hashlib.sha256(canonical_json(value)).hexdigest()
    if actual != expected_sha256:
        raise ValueError(
            f"CANONICAL_INPUT_MUTATION: expected={expected_sha256} actual={actual}"
        )


def pin_room_version(room_version: str, receipt: dict[str, Any]) -> None:
    pinned = receipt.get("execution_signature", {}).get("room_version")
    if pinned != room_version:
        raise ValueError(
            f"ROOM_VERSION_MISMATCH: expected={room_version} receipt={pinned}"
        )
