"""ROOM_01_SIGNAL — deterministic, dataset-free skeleton.

No trading intelligence is implemented here yet. The room only defines the
execution boundary so the first real canonical-data run can be admitted without
creating hidden state or a second governance layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class SignalReceipt:
    input_hash: str
    output_hash: str
    runtime_ms: float
    memory_bytes: int


def canonical_hash(record: dict) -> str:
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def execute(record: dict, *, runtime_ms: float, memory_bytes: int) -> SignalReceipt:
    """Return a forensic receipt without inventing a signal value.

    Real signal logic is intentionally absent until canonical real data is
    admitted. An empty result is safer than a synthetic signal.
    """
    input_hash = canonical_hash(record)
    output = {"status": "DESIGN_ONLY_NO_SIGNAL"}
    return SignalReceipt(
        input_hash=input_hash,
        output_hash=canonical_hash(output),
        runtime_ms=float(runtime_ms),
        memory_bytes=int(memory_bytes),
    )
