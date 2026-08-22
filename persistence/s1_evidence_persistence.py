"""Prepare an immutable S1 evidence envelope for persistence.

This adapter deliberately does not perform network/database writes. It creates a
canonical JSON envelope that a trusted runtime writer can persist transactionally.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_envelope(*, cycle_id: str, canonical_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    canonical = Path(canonical_path).read_bytes()
    canonical_sha = _sha256(canonical)
    if manifest.get("canonical_sha256") != canonical_sha:
        raise ValueError("canonical_hash_mismatch")
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    manifest_sha = _sha256(manifest_bytes)
    envelope = {
        "schema": "s1-evidence-envelope/v1",
        "cycle_id": cycle_id,
        "canonical_sha256": canonical_sha,
        "evidence_manifest_sha256": manifest_sha,
        "canonical_size_bytes": len(canonical),
        "manifest": manifest,
    }
    return envelope


def serialize_envelope(envelope: dict[str, Any]) -> bytes:
    return json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
