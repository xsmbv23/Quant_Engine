"""Forensic invariants shared by Layer 1 rooms.

N003 locks the hash domain at the architecture level. Reproducibility is
necessary evidence, never proof of correctness.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from typing import Any


FORBIDDEN_RUNTIME_FIELDS = frozenset({
    "runtime", "debug", "debug_flags", "density_warning", "logs", "log", "trace", "metrics"
})

# N003: floats remain representable, but their type identity is explicit and
# their decimal text is fixed. This prevents 1, 1.0, True and "1" collisions.
FLOAT_PRECISION = 15


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return {
            "__type__": "dict",
            "items": [[str(k), _normalize(value[k])] for k in sorted(value, key=lambda x: str(x))],
        }
    if isinstance(value, (list, tuple)):
        # Sequence order is semantic and therefore immutable in the hash domain.
        return {"__type__": "sequence", "items": [_normalize(v) for v in value]}
    if isinstance(value, (set, frozenset)):
        raise TypeError("CANONICAL_JSON_UNORDERED_SET_FORBIDDEN")
    if isinstance(value, Decimal):
        return {"__type__": "decimal", "value": format(value, "f")}
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("CANONICAL_JSON_NONFINITE_FLOAT")
        return {"__type__": "float", "value": format(value, f".{FLOAT_PRECISION}g")}
    if isinstance(value, bool):
        return {"__type__": "bool", "value": value}
    if isinstance(value, int):
        return {"__type__": "int", "value": value}
    if isinstance(value, str):
        return {"__type__": "str", "value": value}
    if value is None:
        return {"__type__": "null", "value": None}
    raise TypeError(f"CANONICAL_JSON_UNSUPPORTED_TYPE: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """N003 hash domain: typed scalars, sorted dict keys, ordered lists, UTF-8."""
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def feature_snapshot(feature_rows: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    """Return semantic features only; runtime/debug state is outside hash domain."""
    rows: list[dict[str, Any]] = []
    for row in feature_rows:
        clean = {k: v for k, v in row.items() if k not in FORBIDDEN_RUNTIME_FIELDS}
        rows.append(clean)
    return rows


def build_input_identity(source_id: str, payload: Any) -> dict[str, str]:
    if not source_id or not isinstance(source_id, str):
        raise ValueError("INPUT_SOURCE_ID_REQUIRED")
    return {"input_source_id": source_id, "input_hash": sha256_canonical(payload)}


def empty_output_state(candidates: list[Any]) -> str:
    if candidates == []:
        return "VALID_EMPTY"
    return "NON_EMPTY"
